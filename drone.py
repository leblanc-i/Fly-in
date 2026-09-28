from dataclasses import dataclass, field


@dataclass
class Drone:
    """Runtime state for a single drone during the simulation."""

    id: int
    path: list[str] = field(default_factory=list)
    path_index: int = 0
    remaining_travel_time: int = 0
    travel_destination: str | None = None
    travel_connection: tuple[str, str] | None = None
    has_arrived: bool = False

    @property
    def current_hub_name(self) -> str:
        """Return the hub occupied by the drone while it is not in flight."""
        return self.path[self.path_index]

    @property
    def is_in_flight(self) -> bool:
        """Return True when the drone is travelling on a connection."""
        return self.remaining_travel_time > 0

    def next_hub(self) -> str | None:
        """Return the next hub on the assigned path, if any."""
        next_index = self.path_index + 1
        if next_index >= len(self.path):
            return None
        return self.path[next_index]

    def start_travel(
        self,
        destination: str,
        travel_time: int,
        connection_key: tuple[str, str],
    ) -> None:
        """Put the drone on a connection toward its next hub."""
        self.travel_destination = destination
        self.travel_connection = connection_key
        self.remaining_travel_time = travel_time

    def finish_travel(self) -> None:
        """Move the drone from its connection into the destination hub."""
        if self.travel_destination is None:
            raise ValueError("Cannot finish travel without a destination")

        self.path_index += 1
        self.remaining_travel_time = 0
        self.travel_destination = None
        self.travel_connection = None

        if self.path_index >= len(self.path) - 1:
            self.has_arrived = True
