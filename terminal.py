from graph import Graph
from movement import Movement


class TerminalVisualizer:
    """Render simulation movements with optional ANSI colors."""

    COLOR_CODES: dict[str, str] = {
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "purple": "35",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "gray": "90",
        "grey": "90",
        "orange": "33",
        "gold": "33",
        "brown": "33",
        "maroon": "31",
        "darkred": "31",
        "crimson": "31",
        "violet": "35",
    }

    def __init__(self, graph: Graph, use_color: bool = False) -> None:
        """Store display preferences."""
        self.graph = graph
        self.use_color = use_color

    def render_turn(self, movements: list[Movement]) -> str:
        """Return one formatted output line for a simulation turn."""
        return " ".join(
            self._render_movement(movement) for movement in movements
        )

    def _render_movement(self, movement: Movement) -> str:
        """Return one mandatory movement token, optionally colorized."""
        token = f"D{movement.drone.id}-{movement.label}"
        if not self.use_color or movement.destination is None:
            return token

        hub = self.graph.hubs[movement.destination]
        if hub.color is None:
            return token

        color_code = self.COLOR_CODES.get(hub.color.lower())
        if color_code is None:
            return token

        return f"\033[{color_code}m{token}\033[0m"
