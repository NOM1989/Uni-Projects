# Maze explorer by Nicholas Michau (Nov+Dec 2022)
# Python 3.8.10

# Reads a map from WORLD_MAP_STRING which provides the world map which
#  the script queries for information about the environment from.
# This functionality was to allow me to test quickly without
#  a connection to the Miro simulation.
# The Miro starts with no knowledge of the map and must explore it,
#  making appropriate queries to learn what lies in each cell.

# The MiroSimulation class responds to environment percept queries
#  while the MiroHandler class handles mapping and logic

# **WORKS WITH ANY SIZE MAP!**

### CONFIG ###

# Assumes map is a square,
#  map_size is how many cells make up one side of the map
MAP_SIZE = 4

# Add delay between the actions so we can see what is happening
#  in real time
ARTIFICIAL_DELAY = 0.6

## KEY ##
# - or | : Wall
# + : Wall intersection
# . : No wall
# o : Empty cell
# x : Pit
# w : Treasure
# arrow : Direction Miro facing
WORLD_MAP_STRING = """
+  -  +  -  +  -  +  -  +
|  o  .  o  .  w  .  o  |
+  .  +  .  +  -  +  .  +
|  o  .  x  .  o  .  o  |
+  -  +  .  +  .  +  .  +
|  o  .  o  .  o  .  o  |
+  .  +  .  +  .  +  .  +
|  o  .  o  .  x  .  o  |
+  -  +  -  +  -  +  -  +
""".strip(
    "\n"
)

### END CONFIG ###

from typing import Literal
from time import sleep

# Custom type
Direction = Literal["north", "east", "south", "west"]

# Used to determine the next direction when turning and scanning
DIRECTIONS = ("north", "east", "south", "west")


class Position:
    """Stores vector like data (coordinates and a direction)"""

    class Offset:
        """Helper class for offset coordinate readability"""

        def __init__(self, x, y):
            self.x = x
            self.y = y

    def __init__(
        self,
        x_start: int,
        y_start: int,
        direction_start: Direction = None,
    ):
        # Vars
        self.x = x_start
        self.y = y_start
        self.direction: Direction = direction_start

    def right_of(self, direction: Direction = None):
        """Rerurns the direction to the right of the direction specified, utilising list indexing"""
        if direction == None:
            direction = self.direction
        possible_direction_index = DIRECTIONS.index(direction) + 1
        return DIRECTIONS[
            possible_direction_index if possible_direction_index <= 3 else 0
        ]

    def left_of(self, direction: Direction = None):
        """Rerurns the direction to the left of the direction specified, utilising list indexing"""
        if direction == None:
            direction = self.direction
        return DIRECTIONS[DIRECTIONS.index(direction) - 1]

    def handle_direction(
        self, step_type: Literal["walls", "cells"], direction: Direction = None
    ):
        """
        Converts north/east/etc. into coordinate offsets

        step_type specifies how large the offset should be
        (are we incrimenting on the cells or wall planes)

        direction allows us to specify a direction to generate an offset for
        """
        step = 2
        if step_type == "walls":
            step = 1

        if direction == None:
            direction = self.direction

        if direction == "north":
            offset = self.Offset(0, -step)
        elif direction == "east":
            offset = self.Offset(step, 0)
        elif direction == "south":
            offset = self.Offset(0, step)
        else:
            offset = self.Offset(-step, 0)
        return offset


class MiroSimulation:
    """
    Handles miro esque queries without connection to miro,
        by querying the parsed world_map_string
    """

    def __init__(self, world_map_string: str, current_miro_position_pointer: Position):
        # Constants
        self.WORLD_MAP_STRING = world_map_string

        self.NO_WALL = 0
        self.WALL = 1
        self.WALL_INTERSECTION = "+"

        # These can also use 0 and 1
        # as walls and cells can be differenciated by their column
        self.CELL = 0
        self.PIT = 1
        self.WIN = 2

        # Current map of the world (read from file)
        #  - Not availble to the miro (it has to discover it)
        self.world_map: list[list] = self.generate_world_map_from_file()

        # For ease of use on initialisation we pass a pointer to the miro's current position
        # so the simulation always has access to the current miro position
        self.current_position_pointer = current_miro_position_pointer

    def generate_world_map_from_file(self):
        """Generated when class is initialised,
        builds a world map the program can interpret from a map file"""
        world_map = []
        for line in self.WORLD_MAP_STRING.split("\n"):
            current_line = []
            for char in line:
                if char != " ":
                    if char == "+":
                        current_line.append(self.WALL_INTERSECTION)
                    elif char in ("-", "|"):
                        current_line.append(self.WALL)
                    elif char == ".":
                        current_line.append(self.NO_WALL)
                    elif char == "o":
                        current_line.append(self.CELL)
                    elif char == "x":
                        current_line.append(self.PIT)
                    elif char == "w":
                        current_line.append(self.WIN)
            world_map.append(current_line)
        return world_map

    def generate_world_map_from_list(
        self, world_map: "list[list]", current_position: Position
    ):
        """Generates a human readable output of the world map"""
        output_map = ""
        arrow_map = {"north": "↑", "east": "→", "south": "↓", "west": "←"}
        for i in range(len(world_map)):
            even_row = True if i % 2 == 0 else False
            current_line = ""
            for j in range(len(world_map[i])):
                to_append = None
                char = world_map[i][j]
                even_column = True if j % 2 == 0 else False

                if current_position.y == i and current_position.x == j:
                    to_append = arrow_map[current_position.direction] + " "
                elif char == None:
                    to_append = "? "
                elif even_row and not even_column:
                    # Wall -
                    if char == self.WALL:
                        to_append = "- "
                    else:
                        to_append = ". "
                elif not even_row and even_column:
                    # Wall |
                    if char == self.WALL:
                        to_append = "| "
                    else:
                        to_append = ". "
                elif not even_row and not even_column:
                    # Cell
                    if char == self.CELL:
                        to_append = "o "
                    elif char == self.PIT:
                        to_append = "x "
                    else:
                        to_append = "w "
                else:
                    # Intersection
                    to_append = "+ "

                current_line += to_append

            output_map += current_line + "\n"

        print("-----------------\n")
        print(output_map)

    def check_wall_infront(self):
        """Returns true if there is a wall currently in front of the miro else false"""
        position = self.current_position_pointer
        offset = position.handle_direction("walls")
        if self.world_map[position.y + offset.y][position.x + offset.x]:
            return True
        return False

    def check_pit_infront(self):
        """Returns true if there is a pit in the cell infront of miro else false"""
        position = self.current_position_pointer
        offset = position.handle_direction("cells")
        if self.world_map[position.y + offset.y][position.x + offset.x] == 1:
            return True
        return False

    def check_treasure_infront(self):
        """Returns true if the treasure is in the cell infront of miro else false"""
        position = self.current_position_pointer
        offset = position.handle_direction("cells")
        if self.world_map[position.y + offset.y][position.x + offset.x] == 2:
            return True
        return False


class MiroHandler:
    """Handles the on the fly map generation and movement of our Miro"""

    def __init__(self, map_dimensions: int, starting_position: Position):
        # Constants
        self._MAP_DIMENSIONS = map_dimensions

        self._NO_WALL = 0
        self._WALL = 1
        self._WALL_INTERSECTION = "+"

        # These can also use 0 and 1
        # as walls and cells can be differenciated by their column
        self._CELL = 0
        self._PIT = 1
        self._WIN = 2

        # Current position of the miro (on the world map)
        self._current_postion = starting_position

        # Current map of the world (starts unknown, miro has to discover it)
        self._world_map: list[list] = self._generate_world_map()

    def _generate_world_map(self):
        """Generates an empty (unknown) map for us to record our surroundings into"""

        WALL = self._WALL
        SECT = self._WALL_INTERSECTION

        # Dynamically generate our world map based on map size,
        #   it will look similar to this:
        # world_map = [[SECT, WALL, SECT, WALL, SECT],
        #              [WALL, None, None, None, WALL],
        #              [SECT, None, SECT, None, SECT],
        #              [WALL, None, None, None, WALL],
        #              [SECT, WALL, SECT, WALL, SECT]]
        world_map = [[SECT] + [WALL, SECT] * (self._MAP_DIMENSIONS // 2)]
        for i in range(self._MAP_DIMENSIONS - 2):
            if i % 2 == 0:
                world_map.append([WALL] + [None] * (self._MAP_DIMENSIONS - 2) + [WALL])
            else:
                world_map.append([SECT] + [None, SECT] * (self._MAP_DIMENSIONS // 2))
        world_map.append([SECT] + [WALL, SECT] * (self._MAP_DIMENSIONS // 2))

        # Add current cell to explored
        world_map[self._current_postion.y][self._current_postion.x] = self._CELL

        return world_map

    @property
    def position(self):
        """Current position of our Miro"""
        return self._current_postion

    @property
    def direction(self):
        """Current direction of our Miro"""
        return self.position.direction

    def move_forward(self):
        """Moves the miro forward one cell"""
        offset = self._current_postion.handle_direction("cells")
        self._current_postion.x += offset.x
        self._current_postion.y += offset.y

    def move_backward(self):
        """Moves the miro backward one cell"""
        offset = self._current_postion.handle_direction("cells")
        self._current_postion.x -= offset.x
        self._current_postion.y -= offset.y

    def turn_left(self):
        """Turns the miro left 90 degrees"""
        self._current_postion.direction = self._current_postion.left_of()

    def turn_right(self):
        """Turns the miro right 90 degrees"""
        self._current_postion.direction = self._current_postion.right_of()

    def turn_to_face(self, direction: Direction):
        """Turns Miro to face the target direction"""
        direction_order = DIRECTIONS * 2

        # Offset intial index to allow for us to count back though them
        start_index = direction_order.index(self.direction) + 4

        current_index = start_index
        while direction_order[current_index] != direction:
            current_index -= 1
        left_count = start_index - current_index
        if left_count == 1:
            self.turn_left()
        elif left_count == 2:
            self.turn_left()
            self.turn_left()
        elif left_count == 3:
            # Right must be 1, turn right
            self.turn_right()
        # Else would be stay in same direction

    def _get_cell_in_direction(self, positon: Position, target_direction: Direction):
        """Returns the value of the 'cell' spcae in the specified direction from the position"""
        offset = positon.handle_direction("cells", target_direction)
        return self._world_map[positon.y + offset.y][positon.x + offset.x]

    def _get_wall_in_direction(self, positon: Position, target_direction: Direction):
        """Returns the value of the 'wall' space between the position and the target direction"""
        offset = positon.handle_direction("walls", target_direction)
        return self._world_map[positon.y + offset.y][positon.x + offset.x]

    def check_valid_path(self, target_direction: Direction):
        """
        Returns True if there is a valid path between the current cell and a target ADJACENT cell
         - Assumes all adjacent cells have been recorded.
        """
        pos = self._current_postion

        # Check there is not a wall between
        if not self._get_wall_in_direction(pos, target_direction):
            # Check that the target cell is not a pit
            offset = pos.handle_direction("cells", target_direction)
            if not self._world_map[pos.y + offset.y][pos.x + offset.x] == self._PIT:
                return True
        return False

    def record_wall_infront(self, wall_infront: bool):
        """Records a wall value into our map for the possible wall infront of Miro"""
        pos = self._current_postion
        offset = pos.handle_direction("walls")
        self._world_map[pos.y + offset.y][pos.x + offset.x] = (
            self._WALL if wall_infront else self._NO_WALL
        )
        return wall_infront

    def record_pit_infront(self, pit_infront: bool):
        """Records a cell value into our map for the cell infront of Miro"""
        pos = self._current_postion
        offset = pos.handle_direction("cells")
        self._world_map[pos.y + offset.y][pos.x + offset.x] = (
            self._PIT if pit_infront else self._CELL
        )
        return pit_infront

    def direction_recorded(self, direction: Direction):
        """Returns True if the direction has already been recorded"""
        # Check if the wall has been scanned
        wall_value = self._get_wall_in_direction(self.position, direction)
        if wall_value == 0:
            # If so check if cell has been scanned
            if self._get_cell_in_direction(self.position, direction) == None:
                return False
        elif wall_value == None:
            return False
        return True

    def generate_direction_priority(
        self, order: Literal["pathfinding", "scanning"] = None
    ):
        """Generates a list of directions based on the order:
        - Forward, Left, Right, Back (pathfinding)
        OR
        - Forward, Left, Back, Right (scanning)"""

        if order == None:
            order = "pathfinding"

        if order == "pathfinding":
            # Forward direction is left of currently facing as we do not turn back
            # to face the start after scanning as it is pointless
            forward_direction = self.position.left_of()
        else:
            forward_direction = self.direction

        direction_priority = (
            forward_direction,  # Inital direction (forward)
            self.position.left_of(forward_direction),  # Left of initial)
        )

        # Vary second half of direction
        backward = self.position.left_of(self.position.left_of(self.direction))
        if order == "pathfinding":
            direction_priority += (
                self.position.right_of(forward_direction),  # Right of initial
                backward,  # Backwards
            )
        else:
            direction_priority += (
                backward,  # Backwards
                self.position.right_of(forward_direction),  # Right of initial
            )
        return direction_priority

    def count_surrounding_unexplored(self, scanning_start_cell: Position):
        """For each direction from the scanning_start_cell check
        unexplored accessible cells surrounding it"""

        unexplored_cells_count = 0
        for scan_direction in DIRECTIONS:
            # Check there is not a known wall in the scan direction
            if (
                not self._get_wall_in_direction(scanning_start_cell, scan_direction)
                == self._WALL
            ):
                # If not then we could be able to access the cell

                offset = scanning_start_cell.handle_direction("cells", scan_direction)
                cell_in_scanning_direction = Position(
                    scanning_start_cell.x + offset.x,
                    scanning_start_cell.y + offset.y,
                )

                if (
                    self._world_map[cell_in_scanning_direction.y][
                        cell_in_scanning_direction.x
                    ]
                    == None
                ):
                    # If cell has not been recoded then add to unexplored count
                    unexplored_cells_count += 1

        return unexplored_cells_count

    def find_best_direction(self):
        """Finds the direction leading to the most unexplored cells,
        counts how many unknown cells border cells adjacent to Miro's current position"""

        # Will be a dict of {unknown count : [directions with this count]}
        # We later select the first direction with the highest unknown count
        # If there are multiple with the same count our direction priority is fallen back on
        unexplored_dict: "dict[int, list]" = {}

        # The possible directions miro can move in from current cell
        for move_direction in self.generate_direction_priority():

            # Now check if the move_direction is valid (we can move there)
            if self.check_valid_path(move_direction):

                offset = self.position.handle_direction("cells", move_direction)

                unexplored_cells_in_move_direction = self.count_surrounding_unexplored(
                    Position(
                        self.position.x + offset.x,
                        self.position.y + offset.y,
                    )
                )

                # Add it to our unexplored_dict
                if unexplored_cells_in_move_direction not in unexplored_dict:
                    unexplored_dict[unexplored_cells_in_move_direction] = []
                unexplored_dict[unexplored_cells_in_move_direction].append(
                    move_direction
                )

        return unexplored_dict[max(unexplored_dict)][0]


### The plan (Logic) ###

# Check cell infront and add to data
# Loop 3 times:
#   turn anticlock 90
#   Check cell infront and add to data
#   if treasure:
#       Go to it and break
# Now facing 90 clockwise of start

# while not accessible_cell
#   check cells in anticlock dir from first dir
#   First cell that we can access we will route to

# Alternative to above block: Target unexplored cells
# check each direction and go in the one with the most unexplored surrounding it,
# if multiple resolve using the above

# Loop above

############

miro_handler = MiroHandler(MAP_SIZE * 2 + 1, Position(1, MAP_SIZE * 2 - 1, "east"))

# Start the simulation
miro_simulation = MiroSimulation(WORLD_MAP_STRING, miro_handler.position)

# Display the current map state
miro_simulation.generate_world_map_from_list(
    miro_handler._world_map, miro_handler.position
)

goal_reached = False
while not goal_reached:
    # General loop
    directions = miro_handler.generate_direction_priority("scanning")
    for scan_direction in directions:
        # Has the direction already been recorded? (Proceed if not)
        if not miro_handler.direction_recorded(scan_direction):
            # Turn to face direction we need to scan
            miro_handler.turn_to_face(scan_direction)

            # Is there a wall infront of Miro? (Proceed if not)
            if not miro_handler.record_wall_infront(
                miro_simulation.check_wall_infront()
            ):
                # Is there treasure infront?
                if miro_simulation.check_treasure_infront():
                    goal_reached = True
                    miro_handler.move_forward()
                    break
                else:
                    # Record if there is a pit infront or not
                    miro_handler.record_pit_infront(miro_simulation.check_pit_infront())

            # Display the current map state
            miro_simulation.generate_world_map_from_list(
                miro_handler._world_map, miro_handler.position
            )

            # Artificial delay for testing
            sleep(ARTIFICIAL_DELAY)

    if not goal_reached:
        target_drection = miro_handler.find_best_direction()
        miro_handler.turn_to_face(target_drection)
        miro_handler.move_forward()

    # Display the current map state
    miro_simulation.generate_world_map_from_list(
        miro_handler._world_map, miro_handler.position
    )

    # Artificial delay for testing
    sleep(ARTIFICIAL_DELAY)

print(
    f"Treasure Located - Cell: ({miro_handler.position.x}, {miro_handler.position.y})\nNote: (0, 0) is the '+' in the top left corner"
)
