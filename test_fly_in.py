import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from parser import Parser
from router import Router
from simulator import Simulation


class FlyInTests(unittest.TestCase):
    """Regression tests for parser, routing, and simulation behavior."""

    def test_linear_map_finishes_under_easy_target(self) -> None:
        """The provided linear map should finish well under six turns."""
        parser = Parser("src/01_linear_path.txt")
        config = parser.parse()
        graph = parser.build_graph(config)
        drones = Router(graph).create_drones(config.nb_drones)
        simulation = Simulation(graph, drones)

        with contextlib.redirect_stdout(io.StringIO()):
            simulation.run()

        self.assertLessEqual(simulation.turn, 6)

    def test_challenger_map_beats_reference_record(self) -> None:
        """The challenger map should beat the 45-turn reference target."""
        parser = Parser("src/01_the_impossible_dream.txt")
        config = parser.parse()
        graph = parser.build_graph(config)
        drones = Router(graph).create_drones(config.nb_drones)
        simulation = Simulation(graph, drones)

        with contextlib.redirect_stdout(io.StringIO()):
            simulation.run()

        self.assertLess(simulation.turn, 45)

    def test_parser_rejects_duplicate_connections(self) -> None:
        """Duplicate bidirectional connections must be rejected."""
        content = "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: a 1 0",
                "end_hub: end 2 0",
                "connection: start-a",
                "connection: a-start",
                "connection: a-end",
            ]
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
        ) as file:
            file.write(content)
            filename = file.name

        try:
            with self.assertRaises(ValueError):
                Parser(filename).parse()
        finally:
            Path(filename).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
