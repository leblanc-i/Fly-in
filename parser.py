from hub import Hub
from connection import Connection
from graph import Graph
from dataclasses import dataclass


@dataclass
class Config:
    """Parsed project configuration loaded from a map file."""

    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    connections: list[Connection]


ALLOWED_ZONES: set[str] = {"normal", "blocked", "restricted", "priority"}


class Parser:
    """Parse and validate Fly-in map files."""

    def __init__(self, filename: str):
        """Store the map filename to parse."""
        self.filename = filename

    def parse(self) -> Config:
        """Read, build, and validate a map configuration."""
        rawdata: list[str] = self._read()
        config: Config = self._build_config(rawdata)
        self._validate_config(config)
        return config

    def _read(self) -> list[str]:
        """Read the map file as UTF-8 text lines."""
        with open(self.filename, "r", encoding="utf-8") as file:
            return file.readlines()

    def _build_config(self, rawdata: list[str]) -> Config:
        """Convert raw text lines into a typed configuration object."""
        if not rawdata:
            raise ValueError("Empty file")

        known_hubs = set()

        self._validate_first_line(rawdata)

        nb_drones: int | None = None
        start_hub: Hub | None = None
        end_hub: Hub | None = None
        hubs: list[Hub] = []
        connections: list[Connection] = []

        for line, data in enumerate(rawdata, start=1):
            data = data.strip()

            if not data or data.startswith("#"):
                continue

            if ":" not in data:
                raise ValueError(f"Bad data format - line: {line}")

            key, value = data.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not key or not value:
                raise ValueError(f"Empty 'key' or 'value' - line: {line}")

            match key:
                case "nb_drones":
                    if nb_drones is not None:
                        raise ValueError(f"Duplicate nb_drones - line: {line}")
                    nb_drones = self._parse_nb_drones(value, line)

                case "start_hub":
                    if start_hub is not None:
                        raise ValueError(f"Duplicate start_hub - line: {line}")
                    start_hub = self._parse_hub(value, line)
                    known_hubs.add(start_hub.name)

                case "end_hub":
                    if end_hub is not None:
                        raise ValueError(f"Duplicate end_hub - line: {line}")
                    end_hub = self._parse_hub(value, line)
                    known_hubs.add(end_hub.name)

                case "hub":
                    hub = self._parse_hub(value, line)
                    hubs.append(hub)
                    known_hubs.add(hub.name)

                case "connection":
                    connection = self._parse_connection(value, line)
                    if connection.hub1 not in known_hubs:
                        raise ValueError(
                            f"Unknown hub '{connection.hub1}' - line: {line}")

                    if connection.hub2 not in known_hubs:
                        raise ValueError(
                            f"Unknown hub '{connection.hub2}' - line: {line}")

                    connections.append(connection)

                case _:
                    raise ValueError(f"Unknown key '{key}' - line: {line}")

        if nb_drones is None:
            raise ValueError("Missing nb_drones")
        if start_hub is None:
            raise ValueError("Missing start_hub")
        if end_hub is None:
            raise ValueError("Missing end_hub")

        return Config(
            nb_drones=nb_drones,
            start_hub=start_hub,
            end_hub=end_hub,
            hubs=hubs,
            connections=connections
        )

    @staticmethod
    def _parse_nb_drones(value: str, line: int) -> int:
        """Parse and validate the drone count."""
        try:
            nb_drones = int(value)
        except ValueError:
            raise ValueError(f"nb_drones must be an integer - line: {line}")

        if nb_drones <= 0:
            raise ValueError(f"nb_drones must be positive - line: {line}")

        return nb_drones

    @staticmethod
    def _parse_hub(value: str, line: int) -> Hub:
        """Parse one start, end, or regular hub definition."""
        if not value:
            raise ValueError(f"Empty 'value' in parse_hub - line: {line}")

        value = value.strip()
        data_list = value.split(maxsplit=3)

        if len(data_list) < 3:
            raise ValueError(f"Missing mandatory hub fields - line: {line}")

        name = data_list[0]

        if "-" in name or " " in name:
            raise ValueError(
                f"Invalid hub name '{name}' - dashes "
                f"and spaces not allowed - line: {line}"
            )

        zone: str = "normal"
        color: str | None = None
        max_drones: int = 1

        try:
            pos_x = int(data_list[1])
            pos_y = int(data_list[2])

        except ValueError as e:
            raise ValueError(
                f"{data_list[1]} and {data_list[2]} "
                f"must be integers - line: {line}"
            ) from e

        if len(data_list) > 3:
            options = data_list[3]

            if not (options.startswith("[") and options.endswith("]")):
                raise ValueError(
                    f"Options must be in '[]' - line: {line}"
                )

            for option in options.strip("[]").split():
                if "=" not in option:
                    raise ValueError(
                        f"invalid option format: {option} - line: {line}"
                    )

                option_key, option_value = option.split("=", 1)
                option_key = option_key.strip()
                option_value = option_value.strip()

                match option_key:
                    case "color":
                        color = option_value
                        if " " in color:
                            raise ValueError(
                                f"Bad format for color name - line: {line}"
                            )

                    case "zone":
                        zone = option_value
                        if zone not in ALLOWED_ZONES:
                            raise ValueError(f"Not allowed zone - line {line}")

                    case "max_drones":
                        try:
                            max_drones = int(option_value)
                            if max_drones <= 0:
                                raise ValueError(
                                    f"max_drones must be "
                                    f"greater than 0 - line: {line}"
                                )

                        except ValueError:
                            raise ValueError(
                                f"max_drones must be "
                                f"integer - line: {line}"
                            )

                    case _:
                        raise ValueError(
                            f"Unknown hub option: "
                            f"{option_key} - line: {line}"
                        )

        return Hub(
            name=name,
            pos_x=pos_x,
            pos_y=pos_y,
            zone=zone,
            color=color,
            max_drones=max_drones
        )

    @staticmethod
    def _parse_connection(value: str, line: int) -> Connection:
        """Parse one bidirectional connection definition."""
        if not value:
            raise ValueError(
                f"Empty 'value' in connection - line: {line}"
            )

        value = value.strip()
        data_list = value.split()

        if len(data_list) == 0:
            raise ValueError(
                f"Connection list must be greater "
                f"than 0 - line: {line}"
            )

        if len(data_list) > 2:
            raise ValueError(
                f"Too many tokens in connection - line: {line}"
            )

        mandatory = data_list[0]
        if "-" not in mandatory:
            raise ValueError(
                f"Bad connection format - line: {line}"
            )

        hub1, hub2 = mandatory.strip().split("-", 1)
        if not hub1 or not hub2:
            raise ValueError(f"Missing hub name - line: {line}")

        max_capacity: int = 1

        if len(data_list) > 1:
            option = data_list[1]
            if not (option.startswith("[") and option.endswith("]")):
                raise ValueError(
                    f"Option must be in '[]' - line: {line}"
                )

            option_str = option.strip("[]")
            if "=" not in option_str:
                raise ValueError(
                    f"Bad option format - line: {line}"
                )

            option_key, option_value = option_str.split("=", 1)
            option_key = option_key.strip()
            option_value = option_value.strip()

            if not option_key or not option_value:
                raise ValueError(
                    f"Missing option 'key' or 'value' - line: {line}"
                )

            match option_key:
                case "max_link_capacity":
                    try:
                        max_capacity = int(option_value)
                        if max_capacity <= 0:
                            raise ValueError(
                                f"max_link_capacity must be "
                                f"greater than 0 - line: {line}"
                            )

                    except ValueError as e:
                        raise ValueError(
                            f"max_link_capacity must be "
                            f"integer - line: {line}"
                        ) from e

                case _:
                    raise ValueError(
                        f"Unknown connection option: "
                        f"{option_key} - line: {line}"
                    )

        return Connection(hub1=hub1, hub2=hub2, max_capacity=max_capacity)

    def _validate_first_line(self, rawdata: list[str]) -> None:
        """Ensure the first useful line defines nb_drones."""
        if not rawdata:
            raise ValueError("No data in this file")

        first_useful_line: str | None = None

        for data in rawdata:
            line = data.strip()
            if not line or line.startswith("#"):
                continue

            first_useful_line = line
            break

        if first_useful_line is None:
            raise ValueError("No useful data in file")

        if ":" not in first_useful_line:
            raise ValueError(
                "Bad format on first line, expected 'nb_drones'"
            )

        key0 = first_useful_line.split(":", 1)[0].strip()

        if key0 != "nb_drones":
            raise ValueError("The first line must define nb_drones")

    def _validate_config(self, config: Config) -> None:
        """Validate cross-line constraints after parsing."""
        all_hubs = [config.start_hub, *config.hubs, config.end_hub]
        seen_name = set()
        duplicate_name = set()

        for hub in all_hubs:
            if hub.name in seen_name:
                duplicate_name.add(hub.name)
            seen_name.add(hub.name)

        if duplicate_name:
            raise ValueError(
                f"Duplicate hub names: {', '.join(duplicate_name)}"
            )

        hub_by_name = {hub.name: hub for hub in all_hubs}
        seen_connections = set()

        for conn in config.connections:
            if conn.hub1 not in hub_by_name or conn.hub2 not in hub_by_name:
                raise ValueError(
                    f"Connection {conn.hub1}-{conn.hub2} "
                    f"uses unknown hub(s)"
                )
            if conn.max_capacity <= 0:
                raise ValueError(
                    f"Connection {conn.hub1}-{conn.hub2} "
                    f"has non-positive capacity"
                )

            hub_pair = tuple(sorted([conn.hub1, conn.hub2]))

            if hub_pair in seen_connections:
                raise ValueError(
                    f"Duplicate connection between "
                    f"{conn.hub1} and {conn.hub2}")

            seen_connections.add(hub_pair)

        if config.nb_drones <= 0:
            raise ValueError("nb_drones must be greater than 0")

    def build_graph(self, config: Config) -> Graph:
        """Build a graph from a parsed configuration."""
        all_hubs = [
            config.start_hub,
            *config.hubs,
            config.end_hub,
        ]

        return Graph(
            all_hubs,
            config.connections,
            config.start_hub,
            config.end_hub,
        )
