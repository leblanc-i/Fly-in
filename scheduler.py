from drone import Drone
from graph import Graph
from movement import Movement


class Scheduler:
    """Choose valid drone movements for one simulation turn."""

    def __init__(self, graph: Graph) -> None:
        """Store the graph used for capacity and cost checks."""
        self.graph = graph

    def schedule_turn(self, drones: list[Drone]) -> list[Movement]:
        """Schedule all movements that can happen during the current turn."""
        movements: list[Movement] = []
        hub_occupancy = self._compute_hub_occupancy(drones)
        link_occupancy = self._compute_link_occupancy(drones)

        finished_drones: set[int] = set()
        movements.extend(
            self._advance_in_flight_drones(
                drones,
                hub_occupancy,
                finished_drones,
            )
        )
        movements.extend(
            self._start_new_movements(
                drones,
                hub_occupancy,
                link_occupancy,
                finished_drones,
            )
        )

        return sorted(movements, key=lambda movement: movement.drone.id)

    def _advance_in_flight_drones(
        self,
        drones: list[Drone],
        hub_occupancy: dict[str, int],
        finished_drones: set[int],
    ) -> list[Movement]:
        """Decrease travel time and complete restricted-zone movements."""
        movements: list[Movement] = []

        for drone in drones:
            if drone.has_arrived or not drone.is_in_flight:
                continue

            drone.remaining_travel_time -= 1
            if drone.remaining_travel_time > 0:
                movements.append(
                    Movement(drone=drone, label=self._connection_label(drone))
                )
                continue

            destination = drone.travel_destination
            if destination is None:
                raise ValueError("In-flight drone has no destination")

            hub_occupancy[destination] = hub_occupancy.get(destination, 0) + 1
            drone.finish_travel()
            finished_drones.add(drone.id)
            movements.append(
                Movement(
                    drone=drone,
                    label=destination,
                    destination=destination,
                )
            )

        return movements

    def _start_new_movements(
        self,
        drones: list[Drone],
        hub_occupancy: dict[str, int],
        link_occupancy: dict[tuple[str, str], int],
        finished_drones: set[int],
    ) -> list[Movement]:
        """Start every valid one-turn or multi-turn movement."""
        movements: list[Movement] = []
        candidates = sorted(
            drones,
            key=lambda drone: (drone.path_index, -drone.id),
            reverse=True,
        )

        for drone in candidates:
            if drone.id in finished_drones or drone.has_arrived:
                continue
            if drone.is_in_flight:
                continue

            origin = drone.current_hub_name
            destination = drone.next_hub()
            if destination is None:
                drone.has_arrived = True
                continue

            connection = self.graph.connection_between(origin, destination)
            edge_key = connection.key()
            used_capacity = link_occupancy.get(edge_key, 0)
            if used_capacity >= connection.max_capacity:
                continue

            self._release_hub(origin, hub_occupancy)
            if not self._can_enter_hub(destination, hub_occupancy):
                hub_occupancy[origin] = hub_occupancy.get(origin, 0) + 1
                continue

            link_occupancy[edge_key] = used_capacity + 1
            travel_time = self.graph.movement_cost(destination)

            if travel_time == 1:
                hub_occupancy[destination] = (
                    hub_occupancy.get(destination, 0) + 1
                )
                drone.start_travel(destination, travel_time, edge_key)
                drone.remaining_travel_time = 0
                drone.finish_travel()
                movements.append(
                    Movement(
                        drone=drone,
                        label=destination,
                        destination=destination,
                        connection_key=edge_key,
                    )
                )
            else:
                drone.start_travel(destination, travel_time - 1, edge_key)
                movements.append(
                    Movement(
                        drone=drone,
                        label=self._connection_label(drone),
                        connection_key=edge_key,
                    )
                )

        return movements

    def _compute_hub_occupancy(self, drones: list[Drone]) -> dict[str, int]:
        """Count drones currently occupying each hub."""
        occupancy: dict[str, int] = {}

        for drone in drones:
            if drone.has_arrived or drone.is_in_flight:
                continue
            hub_name = drone.current_hub_name
            occupancy[hub_name] = occupancy.get(hub_name, 0) + 1

        return occupancy

    @staticmethod
    def _compute_link_occupancy(
        drones: list[Drone],
    ) -> dict[tuple[str, str], int]:
        """Count drones currently travelling on each connection."""
        occupancy: dict[tuple[str, str], int] = {}

        for drone in drones:
            if not drone.is_in_flight or drone.travel_connection is None:
                continue
            key = drone.travel_connection
            occupancy[key] = occupancy.get(key, 0) + 1

        return occupancy

    def _can_enter_hub(
        self,
        hub_name: str,
        occupancy: dict[str, int],
    ) -> bool:
        """Return True if one more drone can enter the hub."""
        hub = self.graph.hubs[hub_name]
        if hub.name in {self.graph.start_hub.name, self.graph.end_hub.name}:
            return True
        return occupancy.get(hub_name, 0) < hub.max_drones

    def _release_hub(self, hub_name: str, occupancy: dict[str, int]) -> None:
        """Free one slot in a hub when a drone leaves it."""
        if hub_name in {self.graph.start_hub.name, self.graph.end_hub.name}:
            return

        current = occupancy.get(hub_name, 0)
        if current <= 1:
            occupancy.pop(hub_name, None)
        else:
            occupancy[hub_name] = current - 1

    @staticmethod
    def _connection_label(drone: Drone) -> str:
        """Return the output label for a drone travelling on a connection."""
        if drone.travel_connection is None:
            raise ValueError("Drone has no active connection")
        return "-".join(drone.travel_connection)
