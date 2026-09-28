import argparse
import sys

from parser import Parser
from router import Router
from simulator import Simulation


DEFAULT_MAP = "maps/challenger/01_the_impossible_dream.txt"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Route drones from the start hub to the end hub.",
    )
    parser.add_argument(
        "map_file",
        nargs="?",
        default=DEFAULT_MAP,
        help=f"Path to the map file. Defaults to {DEFAULT_MAP}.",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="Enable ANSI colored terminal output.",
    )

    return parser.parse_args()


def main() -> int:
    """Run the Fly-in simulation."""
    args = parse_args()

    try:
        parser = Parser(args.map_file)
        config = parser.parse()
        graph = parser.build_graph(config)
        router = Router(graph)
        drones = router.create_drones(config.nb_drones)
        simulation = Simulation(graph, drones, use_color=args.color)
        simulation.run()
        print(
            f"All {config.nb_drones} drones arrived "
            f"in {simulation.turn} turns.",
            file=sys.stderr,
        )
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
