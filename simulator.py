from drone import Drone
from graph import Graph
from movement import Movement
from scheduler import Scheduler
from terminal import TerminalVisualizer


class Simulation:
    """Run the drone simulation until every drone reaches the end hub."""

    def __init__(
        self,
        graph: Graph,
        drones: list[Drone],
        use_color: bool = False,
    ) -> None:
        """Validate initial state and prepare the scheduler."""
        if not drones:
            raise ValueError("Empty list of drones")

        for drone in drones:
            if len(drone.path) < 2:
                raise ValueError("Drone path must contain at least two hubs")

        self.drones = drones
        self.graph = graph
        self.turn: int = 0
        self.scheduler = Scheduler(graph)
        self.visualizer = TerminalVisualizer(graph, use_color)

    def run(self, max_turns: int = 10000) -> None:
        """Run the simulation and print one output line per active turn."""
        idle_turns = 0

        while any(not drone.has_arrived for drone in self.drones):
            if self.turn >= max_turns:
                message = "Simulation exceeded the maximum turn limit"
                raise RuntimeError(message)

            self.turn += 1
            movements = self.scheduler.schedule_turn(self.drones)

            if not movements:
                idle_turns += 1
                if idle_turns > len(self.drones) + len(self.graph.hubs):
                    message = "Simulation is blocked"
                    raise RuntimeError(message)
                continue

            idle_turns = 0
            self.display_turn(movements, self.visualizer)

    @staticmethod
    def display_turn(
        movements: list[Movement],
        visualizer: TerminalVisualizer,
    ) -> None:
        """Print movements using the mandatory D<ID>-<zone> format."""
        print(visualizer.render_turn(movements))
