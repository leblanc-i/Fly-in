from dataclasses import dataclass
from drone import Drone


@dataclass
class Movement:
    """One output event produced during a simulation turn."""

    drone: Drone
    label: str
    destination: str | None = None
    connection_key: tuple[str, str] | None = None
