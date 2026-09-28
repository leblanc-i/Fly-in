from dataclasses import dataclass


@dataclass
class Connection:
    """A bidirectional edge between two hubs."""

    hub1: str
    hub2: str
    max_capacity: int = 1

    def other(self, hub_name: str) -> str:
        """Return the opposite endpoint of this connection."""
        if hub_name == self.hub1:
            return self.hub2

        if hub_name == self.hub2:
            return self.hub1

        raise ValueError(
            f"{hub_name} is not connected by this edge"
        )

    def key(self) -> tuple[str, str]:
        """Return a stable key for capacity checks."""
        if self.hub1 <= self.hub2:
            return (self.hub1, self.hub2)
        return (self.hub2, self.hub1)
