from drone import Drone
from graph import Graph


class Router:
    """Assign drones to useful paths before the turn-by-turn simulation."""

    def __init__(self, graph: Graph) -> None:
        """Store the graph used to evaluate candidate paths."""
        self.graph = graph
        self.drone_count: int = 1

    def create_drones(self, drone_count: int) -> list[Drone]:
        """Create drones and distribute them across candidate paths."""
        self.drone_count = drone_count
        paths = self.graph.candidate_paths(max(1, min(20, drone_count)))
        if not paths:
            raise ValueError("No valid path found from start to end")

        assigned_counts = [0 for _ in paths]
        drones: list[Drone] = []

        for drone_id in range(1, drone_count + 1):
            path_index = self._choose_path(paths, assigned_counts)
            assigned_counts[path_index] += 1
            drones.append(
                Drone(
                    id=drone_id,
                    path=paths[path_index].copy(),
                )
            )

        return drones

    def describe_paths(self) -> list[str]:
        """Return human-readable descriptions of current candidate paths."""
        paths = self.graph.candidate_paths(10)
        return [
            f"{index + 1}: cost={self.graph.path_cost(path)} path={path}"
            for index, path in enumerate(paths)
        ]

    def _choose_path(
        self,
        paths: list[list[str]],
        assigned_counts: list[int],
    ) -> int:
        """Choose the path with the best estimated completion time."""
        best_index = 0
        best_score = float("inf")

        for index, path in enumerate(paths):
            bottleneck = self._path_bottleneck(path)
            weighted_cost = self.graph.path_cost(path) * (
                self.drone_count + 1
            )
            score = weighted_cost + assigned_counts[index] / bottleneck
            if score < best_score:
                best_score = score
                best_index = index

        return best_index

    def _path_bottleneck(self, path: list[str]) -> int:
        """Estimate the throughput of the narrowest edge or hub on a path."""
        capacities: list[int] = []

        for hub_name in path[1:-1]:
            capacities.append(self.graph.hubs[hub_name].max_drones)

        for edge_key in self.graph.path_connections(path):
            connection = self.graph.connection_by_key[edge_key]
            capacities.append(connection.max_capacity)

        return max(1, min(capacities, default=1))
