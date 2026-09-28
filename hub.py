from dataclasses import dataclass


@dataclass
class Hub:
    """A zone in the drone network.

    Attributes:
        name: Unique hub name used by connections and output.
        pos_x: X coordinate from the map file.
        pos_y: Y coordinate from the map file.
        zone: Movement category: normal, restricted, priority, or blocked.
        color: Optional display color name.
        max_drones: Maximum number of drones allowed in this hub.
    """

    name: str
    pos_x: int
    pos_y: int
    zone: str = "normal"
    color: str | None = None
    max_drones: int = 1
