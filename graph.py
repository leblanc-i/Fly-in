import heapq

from connection import Connection
from hub import Hub


class Graph:
    """Graph representation of hubs and bidirectional connections."""

    def __init__(
        self,
        hubs: list[Hub],
        connections: list[Connection],
        start_hub: Hub,
        end_hub: Hub,
    ) -> None:
        """Build adjacency and lookup tables for the simulation."""
        self.hubs: dict[str, Hub] = {hub.name: hub for hub in hubs}
        self.connections: list[Connection] = connections
        self.start_hub: Hub = start_hub
        self.end_hub: Hub = end_hub
        self.adjacency: dict[str, list[Connection]] = {
            hub.name: [] for hub in hubs
        }
        self.connection_by_key: dict[tuple[str, str], Connection] = {}

        for connection in connections:
            self.adjacency[connection.hub1].append(connection)
            self.adjacency[connection.hub2].append(connection)
            self.connection_by_key[connection.key()] = connection

    def dijkstra(self, start: Hub, goal: Hub) -> list[str] | None:
        """Compute the cheapest path from start to goal."""
        return self.shortest_path(start.name, goal.name)

    def shortest_path(
        self,
        start_name: str,
        goal_name: str,
        penalties: dict[tuple[str, str], float] | None = None,
    ) -> list[str] | None:
        """Compute a cheapest path while optionally penalizing used edges."""
        start = self.hubs[start_name]
        goal = self.hubs[goal_name]

        if start.zone == "blocked" or goal.zone == "blocked":
            return None

        penalties = penalties or {}
        distances: dict[str, float] = {
            hub_name: float("inf") for hub_name in self.hubs
        }
        parents: dict[str, str | None] = {start_name: None}
        queue: list[tuple[float, str]] = [(0.0, start_name)]
        distances[start_name] = 0.0

        while queue:
            current_cost, hub_name = heapq.heappop(queue)
            if current_cost > distances[hub_name]:
                continue
            if hub_name == goal_name:
                break

            for connection in self.adjacency[hub_name]:
                neighbor_name = connection.other(hub_name)
                neighbor = self.hubs[neighbor_name]
                if neighbor.zone == "blocked":
                    continue

                edge_key = connection.key()
                next_cost = (
                    current_cost
                    + self.movement_cost(neighbor_name)
                    + penalties.get(edge_key, 0.0)
                )

                if next_cost < distances[neighbor_name]:
                    distances[neighbor_name] = next_cost
                    parents[neighbor_name] = hub_name
                    heapq.heappush(queue, (next_cost, neighbor_name))

        if distances[goal_name] == float("inf"):
            return None

        return self._rebuild_path(parents, goal_name)

    def candidate_paths(self, count: int) -> list[list[str]]:
        """Return several useful start-to-end paths for drone assignment.

        The method repeatedly runs Dijkstra and adds small penalties to edges
        that were already selected. This keeps the implementation explainable
        while encouraging path diversity on maps with forks.
        """
        paths: list[list[str]] = []
        penalties: dict[tuple[str, str], float] = {}

        for _ in range(count):
            path = self.shortest_path(
                self.start_hub.name,
                self.end_hub.name,
                penalties,
            )
            if path is None or path in paths:
                break

            paths.append(path)
            for edge_key in self.path_connections(path):
                connection = self.connection_by_key[edge_key]
                penalties[edge_key] = (
                    penalties.get(edge_key, 0.0)
                    + 1.0 / connection.max_capacity
                )

        return paths

    def connection_between(self, hub1: str, hub2: str) -> Connection:
        """Return the connection joining two hubs."""
        key = self.edge_key(hub1, hub2)
        try:
            return self.connection_by_key[key]
        except KeyError as exc:
            message = f"No connection between {hub1} and {hub2}"
            raise ValueError(message) from exc

    def movement_cost(self, destination_name: str) -> int:
        """Return the number of turns needed to enter a destination hub."""
        zone = self.hubs[destination_name].zone
        if zone == "restricted":
            return 2
        if zone in {"normal", "priority"}:
            return 1
        if zone == "blocked":
            return 10**9
        raise ValueError(f"Unknown zone: {zone}")

    def path_cost(self, path: list[str]) -> int:
        """Return the total movement cost of a path."""
        return sum(self.movement_cost(hub_name) for hub_name in path[1:])

    def path_connections(self, path: list[str]) -> list[tuple[str, str]]:
        """Return the stable edge keys used by a path."""
        return [
            self.edge_key(path[index], path[index + 1])
            for index in range(len(path) - 1)
        ]

    @staticmethod
    def edge_key(hub1: str, hub2: str) -> tuple[str, str]:
        """Return a stable two-item key for an undirected edge."""
        if hub1 <= hub2:
            return (hub1, hub2)
        return (hub2, hub1)

    @staticmethod
    def _rebuild_path(
        parents: dict[str, str | None],
        goal_name: str,
    ) -> list[str]:
        """Rebuild a path from the parent table produced by Dijkstra."""
        path: list[str] = []
        current: str | None = goal_name

        while current is not None:
            path.append(current)
            current = parents[current]

        path.reverse()
        return path
