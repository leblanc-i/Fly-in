*This project has been created as part of the 42 curriculum by <*idamadou*>.*

# Fly-in

## Description

Fly-in is a Python drone-routing simulation. The program reads a map file made of
hubs and bidirectional connections, then routes every drone from the start hub to the
end hub while respecting zone and connection constraints.

The main objective is to minimize the number of simulation turns. Drones can move at
the same time, but they must not exceed hub capacity (`max_drones`) or connection
capacity (`max_link_capacity`). Blocked hubs are ignored, restricted hubs require two
turns to enter, and priority hubs are preferred during pathfinding.

## Instructions

Install dependencies:

```sh
make install
```

Run the default challenger map:

```sh
make run
```

Run a specific map:

```sh
python3 main.py 01_linear_path.txt
```

Enable colored terminal output:

```sh
python3 main.py 01_the_impossible_dream.txt --color
```

Run tests:

```sh
python3 -m unittest discover -s tests
```

Run linting:

```sh
make lint
```

## Algorithm And Implementation Strategy

The project is object-oriented and split into clear responsibilities:

- `Parser` reads and validates the map format.
- `Graph` stores hubs, connections, adjacency lists, costs, and candidate paths.
- `Router` assigns drones to useful paths before the simulation starts.
- `Scheduler` decides which movements are valid during each turn.
- `Simulation` runs the turn loop and prints the mandatory output format.

Pathfinding is implemented manually with Dijkstra. Graph libraries such as `networkx`
are not used. To find multiple useful paths, the graph repeatedly runs Dijkstra while
adding small penalties to edges that were already selected. This encourages path
diversity without making the algorithm difficult to explain.

Drone assignment favors the lowest-cost paths first, then balances drones between
paths with the same estimated cost. This is especially effective on the challenger map,
where the best result comes from splitting the fleet between the two shortest routes.

The scheduler is greedy and deterministic. During each turn it:

1. Advances drones that are already travelling on a restricted-zone connection.
2. Processes drones closest to the end first, so moving drones free capacity behind
   them during the same turn.
3. Checks hub capacity and connection capacity before starting any movement.
4. Prints only drones that moved during the current turn.

## Visual Representation

The default output stays plain so it matches the required `D<ID>-<zone>` format.
When `--color` is enabled, destination hubs with a known color are rendered with ANSI
terminal colors. This gives quick visual feedback while keeping the mandatory output
available for automated checks.

## Performance

On the included maps:

- `01_linear_path.txt`: 2 drones finish in 4 turns.
- `01_the_impossible_dream.txt`: 25 drones finish in 43 turns.

The challenger result beats the reference record target of 45 turns for the provided
map.

## Resources

- Python documentation: https://docs.python.org/3/
- `heapq` priority queue documentation: https://docs.python.org/3/library/heapq.html
- `unittest` documentation: https://docs.python.org/3/library/unittest.html
- Dijkstra's algorithm overview: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

AI was used as a review and implementation assistant to compare the existing project
against the subject, identify missing requirements, propose a clean architecture, and
help create documentation and regression tests. The final code remains intentionally
small and explainable so it can be reviewed and defended during peer evaluation.
