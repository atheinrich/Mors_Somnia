########################################################################################################################################################
# Environment creation and management
#
# Environments (player_obj.envs)
# - Area (envs.areas[area])
# -- Environment (areas[area][env])
# --- Tiles (env.map)
# --- Rooms (env.rooms)
# --- Weather (env.weather)
# --- Entities (env.ents)
# -- Questlog (areas[area].questlog)
#
# General usage:
# - env_def: hard-code environment; use others as template
# - Environments.add_area: add area to player file
# - Area.add_level: add environment to player file in given area
# -- Area functions as a dictionary, so environment can be accessed with areas[area][env]
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import time
import random
import copy

## Specific
import pygame

## Local
import session
from entities import create_entity
from items import create_item
from data_management import tile_dicts

########################################################################################################################################################
# Classes
class Environments:

    # Core
    def __init__(self, player_obj):
        """ Holds environments for user. All environments in a given area (ex. dungeons) are grouped
            under an Area object.

            Example
            -------
            player_obj.envs = Environments(player_obj)
            player_obj.envs.add_area('area name')
            player_obj.envs.areas['area name'].add_level('environment name')
        """

        self.player_obj = player_obj
        self.areas = {}

    def add_area(self, name, permadeath=False):
        self.areas[name] = Area(name, self, permadeath)
        return self.areas[name]

class Area:

    # Core
    def __init__(self, name, envs, permadeath):
        """ Holds environments associated with the same area.
        
            Parameters
            ----------
            name       : str; identifier for the set of environments
            envs       : Environments object; parent
            permadeath : bool; triggers awakening if False

            levels     : dict; keys are names of Environment objects, which are the values
            last_env   : Environment object; last occupied by player before switching areas

            Example
            -------
            player_obj.envs.add_area('area name')
            player_obj.envs.areas['area name'].add_level('environment name')
            env = player_obj.envs.areas['area name']['environment name']
        """
        
        self.name       = name
        self.envs       = envs
        self.permadeath = permadeath

        self.levels     = {}
        self.last_env   = None

        self.questlog   = {}

        self.display_fx = None

    def add_level(self, name, lvl_num=None):
        from env_def import _registry

        nickname = name[:4]
        if nickname in _registry.keys():
            env = _registry[nickname](self, lvl_num)

        if env is not None:
            self.levels[name] = env

    def __getitem__(self, key):
        """ Allows the instance to be treated as a dictionary with levels as values. """

        if isinstance(key, int):   return list(self.levels.values())[key]
        elif isinstance(key, str): return self.levels[key]

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """

    # Core
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            # Class instances
            envs               : environments instance; convenient reference
            area               : area instance; convenient reference
            map                : 2D list of tile instances; environment grid
            rooms              : list of room instances; ?
            ents               : list of entity instances; ?
            camera             : camera instance; saves zoom

            # Environment identifiers
            name               : str; identifier visible to player
            lvl_num            : int; identifier
            size               : str in ['small', 'medium', 'large']; used in initialization
            soundtrack         : list of str; identifiers for audio files

            # Image identifiers
            wall_img_IDs       : list of str; identifiers for default wall image
            floor_img_IDs      : list of str; identifiers for default floor image
            roof_img_IDs       : list of str; identifiers for default roof image
            img_IDs            : list of str; identifiers for default tile image

            # Transient details
            env_date           : int; day of the week; should move to Area
            env_time           : int; time of the day; should move to Area; 8 is midday
            player_coordinates : list of int; coordinates of last occupied tile by player in this environment
            center             : list of int; coordinates of the center of this environment

            # Default tile parameters
            blocked            : bool; if True, blocks entity and item placement unless set tilewise
            hidden             : bool; if True, prevents rendering unless set tilewise
        """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Map
        self.blocked = kwargs.get('blocked', True)
        self.hidden  = kwargs.get('hidden',  True)
        self.img_IDs = kwargs.get('img_IDs', ['', ''])
        self.map     = self._generate_map()

        # Other
        self.rooms              = []
        self.ents               = []
        self.player_coordinates = [0, 0]
        self.center             = [int(len(self.map)/2), int(len(self.map[0])/2)]
        self.env_date           = kwargs.get('env_date', 1)
        self.env_time           = kwargs.get('env_time', 6)
        self.camera             = None
        self.stairs             = {}

    def _generate_map(self):
        """ Creates a list of lists with individual entries as tile instances. """

        pyg = session.pyg

        # Set size as integer multiple of default screen size
        map      = []
        X_range  = [0, self.size * 640]
        Y_range  = [0, self.size * 480]
        X_ends   = [0, X_range[1] - pyg.tile_width]
        Y_ends   = [0, Y_range[1] - pyg.tile_height]

        # Loop through each grid point
        for X in range(X_range[0], X_range[1], pyg.tile_width):
            row = [] 
            for Y in range(Y_range[0], Y_range[1], pyg.tile_height):
                
                # Create tile
                tile               = create_tile(self.img_IDs[1])
                tile.X             = X
                tile.Y             = Y
                tile.env           = self
                
                # Image IDs
                tile.wall_img_IDs  = self.wall_img_IDs
                tile.floor_img_IDs = self.floor_img_IDs
                tile.roof_img_IDs  = self.roof_img_IDs
                
                # Handle edges
                if (X in X_ends) or (Y in Y_ends):
                    tile.blocked     = True
                    tile.hidden      = self.hidden
                    tile.unbreakable = True
                
                # Handle bulk
                else:
                    tile.blocked     = self.blocked
                    tile.hidden      = self.hidden
                    tile.unbreakable = False
                
                row.append(tile)
            map.append(row)
        
        return map

    # Paths
    def _create_h_tunnel(self, x_1, x_2, y):
        """ Creates a horizontal tunnel given initial and final coordinates. """
        
        for x in range(min(x_1, x_2), max(x_1, x_2) + 1):
            tile = self.map[x][y]
            
            # Find floor image
            if tile.room: img = tile.room.floor_img_IDs
            else:         img = self.floor_img_IDs
            
            # Empty and update tile
            tile.img_IDs = img
            tile.blocked = False

    def _create_v_tunnel(self, y_1, y_2, x):
        """ Creates vertical tunnel given initial and final coordinates. """
        
        # Sort through tiles
        for y in range(min(y_1, y_2), max(y_1, y_2) + 1):
            tile = self.map[x][y]
            
            # Find floor image
            if tile.room: img_set = tile.room.floor_img_IDs
            else:         img_set = self.floor_img_IDs
            
            # Empty and update tile
            tile.blocked   = False
            tile.img_IDs = img_set

    # Other
    def build_room(self, placed_tile):
        """ Constructs a room if the player places connecting walls.
            Called by place_object when a wall is placed by the player.
            Basically, it looks for a chain of placed tiles connected to the originally placed tile.

            Process
            -------
            1) Checks if a placed tile has other placed tiles around it.
            2) If so, it creates a room if these placed tiles form a closed shape.
        """
        
        # Find chains of placed tiles
        connected = self._find_placed_tiles(placed_tile)

        # Check if this chain forms a closed boundary
        closed = self._has_closed_boundary(connected)

        # Create a room given that boundary
        if closed:
            
            # Get bounds of the area to check
            boundary_locs = set((tile.X//32, tile.Y//32) for tile in connected.keys())
            plan, x_1, y_1, _, _ = self._create_text_room(boundary_locs)
        
            room = Room(
                name          = 'placed',
                env           = self,
                biome         = 'city',

                floor_img_IDs = ['floors', 'wood'],
                wall_img_IDs  = placed_tile.img_IDs,
                roof_img_IDs  = self.roof_img_IDs,

                hidden        = False,
                objects       = True,

                x1            = x_1,
                y1            = y_1,
                boundary      = plan)

    def _find_placed_tiles(self, placed_tile):
        """ Returns a dictionary of placed tiles and their neighboring placed tiles. """

        from mechanics import get_vicinity

        # Find original tile and its immediate neighbors
        first_neighbors = [placed_tile]
        for first_neighbor in get_vicinity(placed_tile).values():
            if first_neighbor is None:
                continue
            if first_neighbor.placed:
                first_neighbors.append(first_neighbor)
        
        # Find chains of adjacent placed tiles
        connected = dict()                # final dictionary of connected tiles
        queue     = list(first_neighbors) # all tiles to check; updated with new adjacent tiles
        visited   = set()                 # avoids revisiting tiles
        while queue:

            # Create dictionary entry for placed tile
            tile = queue.pop(0)
            if tile in visited: continue
            visited.add(tile)
            connected[tile] = []
            
            # Look at all neighbors of this tile
            for neighbor in get_vicinity(tile).values():
                if neighbor is None:
                    continue

                # Add neighboring placed tiles to chain
                if neighbor.placed:
                    connected[tile].append(neighbor)

                    # Queue to check for neighboring placed tiles
                    if (neighbor not in visited) and (neighbor not in queue):
                        queue.append(neighbor)
            
        return connected
    
    def _has_closed_boundary(self, graph):
        """ Returns True if the provided dictionary of connected tiles yields a closed boundary.
            
            Each key is a node whose value is a list of neighboring nodes.
        """

        # Avoid revisiting tiles
        visited = set()

        # Depth-first search
        def dfs(node, parent, path):
            """ Looks for a closed path of connected tiles.

                Parameters
                ----------
                node   : current node
                parent : previous node upon recursion
                path   : current path of nodes
            """

            visited.add(node)
            path.append(node)

            for neighbor in graph[node]:

                # Recursively look at connected nodes
                if neighbor not in visited:
                    if dfs(neighbor, node, path):
                        return True
                
                # Look for a boundary
                elif neighbor != parent:
                    cycle_start_index = path.index(neighbor)
                    cycle_length = len(path) - cycle_start_index
                    if cycle_length >= 4:
                        return True
            path.pop()
            return False

        for node in graph:
            if node not in visited:
                if dfs(node, None, []):
                    return True
        
        return False

    def _create_text_room(self, boundary_locs):
        """ Creates a text plan representing the boundary of the room to be created. """

        # Set size
        x_1    = min(loc[0] for loc in boundary_locs)
        y_1    = min(loc[1] for loc in boundary_locs)
        width  = max(loc[0] for loc in boundary_locs) - min(loc[0] for loc in boundary_locs)
        height = max(loc[1] for loc in boundary_locs) - min(loc[1] for loc in boundary_locs)

        x_range = [0, width+1]
        y_range = [0, height+1]

        # Initialize containers
        plan = [list(' ' * (width+1)) for _ in range(height+1)]

        # Set walls
        for y in range(y_range[0], y_range[1]):
            for x in range(x_range[0], x_range[1]):
                x_rel, y_rel = x + x_1, y + y_1
                if (x_rel, y_rel) in boundary_locs:
                    plan[y][x] = '-'
                else:
                    print((x_rel, y_rel))

        # Freeze to strings if needed
        plan = [''.join(row) for row in plan]
        
        return plan, x_1, y_1, width, height

    def combine_rooms(self):
        """ Removes walls of intersecting rooms, then recombines them into a single room. """

        # Find overlapping rooms and convert walls to floors where necessary
        overlap_groups = self._find_overlapping_rooms()
        self._convert_overlapping_walls(overlap_groups)

        # Combine into single rooms
        new_rooms = []
        for i in range(len(overlap_groups)):
            new_room = self.rooms[overlap_groups[i][0]]
            for j in range(1, len(overlap_groups[i])):
                new_room.tile_locs  = list(set(self.rooms[overlap_groups[i][j]].tile_locs + new_room.tile_locs))
                new_room.wall_locs  = list(set(self.rooms[overlap_groups[i][j]].wall_locs + new_room.wall_locs))
                new_room.floor_locs = list(set(self.rooms[overlap_groups[i][j]].floor_locs + new_room.floor_locs))
            new_rooms.append(new_room)
        self.rooms = new_rooms

    def _find_overlapping_rooms(self):
        """ Return lists of indices corresponding to overlapping rooms.
        
            Schematic
            ---------
            rooms = [room_1, room_2, room_3, room_4]
            room_1 overlaps with room_2 and room_3
            components = [[0, 1, 2], [3]]
        """

        floor_sets = [set(room.floor_locs) for room in self.rooms]
        n          = len(self.rooms)

        graph = [[] for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                if floor_sets[i] & floor_sets[j]:
                    graph[i].append(j)
                    graph[j].append(i)

        visited = [False] * n
        components = []

        for i in range(n):
            if not visited[i]:
                stack = [i]
                visited[i] = True
                component = []

                while stack:
                    current = stack.pop()
                    component.append(current)

                    for neighbor in graph[current]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            stack.append(neighbor)

                components.append(component)

        return components

    def _convert_overlapping_walls(self, overlap_groups):
        """ Checks if any walls overlap floors, then converts them to floors.
            Uses sets to improve membership lookup speed.
        """

        for group in overlap_groups:
            floor_sets = {}
            for i in group:
                floor_sets[i] = set(self.rooms[i].floor_locs)

            # Look at each wall in a given room
            for i in group:
                room             = self.rooms[i]
                new_wall_locs    = []
                extra_floor_locs = []

                for loc in room.wall_locs:
                    keep = True

                    # Convert wall to floor
                    for j in group:
                        if (i != j) and (loc in floor_sets[j]):
                            extra_floor_locs.append(loc)
                            keep = False
                            
                            # Update tile
                            tile = self.map[loc[0]][loc[1]]
                            tile.item        = None
                            tile.blocked     = False
                            tile.unbreakable = False
                            tile.img_IDs     = self.roof_img_IDs if self.roof_img_IDs else self.floor_img_IDs
                            break
                    
                    # Do nothing
                    if keep: new_wall_locs.append(loc)

                room.wall_locs   = new_wall_locs
                room.floor_locs += extra_floor_locs

class Room:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            # Name and location
            name            : str; identifier visible to player
            biome           : str; identifier for entity and item placement
            env             : environment instance; convenient reference
            
            # Size
            x1, y1          : ints; top left corner in tile coordinates
            
            # Image names and environment
            wall_img_IDs    : list of str; identifiers for default wall image
            floor_img_IDs   : list of str; identifiers for default floor image
            roof_img_IDs    : list of str; identifiers for default roof image

            # Properties
            plan            : list of str; custom floorplan
            hidden          : bool; black tiles until the room is discovered
            boundary        : list of tile objects; custom walls_list
            unbreakable     : 
            delete          : bool; mark to be removed from environment
            
            # Tiles
            tiles_list      : list of tile objects; all tiles
            walls_list      : list of tile objects; all outer tiles
            corners_list    : list of tile objects; corner tiles
            noncorners_list : list of tile objects; all outer tiles that are not corners
            
            Plan details
            ------------
            - : wall
            . : floor
            | : door
            
            = : bed
            b : left chair
            d : right chair
            [ : left shelf
            ] : right shelf
            
            g : jug of grapes
            c : jug of cement
            L : light
            
            Construction methods
            --------------------
            standard : square room; uses from_size()
            plan     : custom room by floorplan; uses from_plan()
            boundary : custom room by boundary; uses from_boundary() """
        
        # Name and location
        self.name          = kwargs.get('name',  'room')
        self.biome         = kwargs.get('biome', 'any')
        self.env           = kwargs.get('env',   None)
        self.env.rooms.append(self)
        
        # Size
        self.x1            = kwargs.get('x1', 0)
        self.y1            = kwargs.get('y1', 0)
        
        # Image names and environment
        self.floor_img_IDs = kwargs.get('floor_img_IDs', None)
        self.wall_img_IDs  = kwargs.get('wall_img_IDs',  None)
        self.roof_img_IDs  = kwargs.get('roof_img_IDs',  None)

        # Properties
        self.plan          = kwargs.get('plan',        None)
        self.boundary      = kwargs.get('boundary',    None)
        self.hidden        = kwargs.get('hidden',      False)
        self.unbreakable   = kwargs.get('unbreakable', False)
        self.delete        = False
        
        # Create square room or text-based design
        x_1      = kwargs.get('x1',       0)
        y_1      = kwargs.get('y1',       0)
        width    = kwargs.get('width',    0)
        height   = kwargs.get('height',   0)
        plan     = kwargs.get('plan',     None)
        boundary = kwargs.get('boundary', None)

        if width:      locs = self.from_size(x_1, y_1, width, height)
        elif plan:     locs = self.from_plan(x_1, y_1, plan)
        elif boundary: locs = self.from_boundary(x_1, y_1, boundary)
        
        self.tile_locs  = locs[0]
        self.wall_locs  = locs[1]
        self.floor_locs = locs[2]

    def from_size(self, x_1, y_1, width, height):
        """ Assigns and updates tiles within a rectangular region.

            Parameters
            ----------
            x_1, y_1 : ints; tile coordinates of top left corner
            width    : int; horizontal length of room in number of tiles
            height   : int; vertical length of room in number of tiles

            Returns
            -------
            tile_locs  : list of int tuples; coordinates of all tiles in the room
            wall_locs  : list of int tuples; coordinates of all walls in the room
            floor_list : list of int tuples; coordinates of all floors in the room
        """

        # Initialize containers
        tile_locs  = []
        wall_locs  = []
        floor_locs = []

        # Set size
        x_range = [x_1,        x_1 + width]
        y_range = [y_1,        y_1 + height]
        x_ends  = [x_range[0], x_range[1] - 1]
        y_ends  = [y_range[0], y_range[1] - 1]

        # Loop through each grid point
        for x in range(x_range[0], x_range[1]):
            for y in range(y_range[0], y_range[1]):
                tile = self.env.map[x][y]
                tile_locs.append((x, y))

                ############################################
                # Update base properties
                ## Remove items and entities
                tile.item = None
                if tile.ent:
                    self.env.ents.remove(tile.ent)
                    tile.ent = None
                
                ## Update tile properties
                tile.room   = self
                tile.biome  = self.biome
                tile.hidden = self.hidden
                
                ############################################
                # Handle edges
                if (x in x_ends) or (y in y_ends):
                    wall_locs.append((x, y))

                    # Update properties
                    tile.blocked     = True
                    tile.unbreakable = self.unbreakable
                    tile.img_IDs     = self.env.wall_img_IDs
                
                ############################################
                # Handle bulk
                else:
                    floor_locs.append((x, y))

                    # Update properties
                    tile.blocked     = False
                    tile.unbreakable = False
                    tile.img_IDs     = self.roof_img_IDs if self.roof_img_IDs else self.floor_img_IDs
        
        return tile_locs, wall_locs, floor_locs

    def from_plan(self, x_1, y_1, plan):
        """ Assigns and updates tiles within a custom region, then placed items.

            Parameters
            ----------
            x_1, y_1 : ints; tile coordinates of top left corner
            plan     : 2D list of str; human readable custom map

            Returns
            -------
            tile_locs  : list of int tuples; coordinates of all tiles in the room
            wall_locs  : list of int tuples; coordinates of all walls in the room
            floor_list : list of int tuples; coordinates of all floors in the room
        """

        outside = find_outside(plan)
        item_dict = {
            '|': 'door',
            '=': 'red_bed',
            'b': 'red_chair_left',
            'T': 'table',
            'd': 'red_chair_right',
            '[': 'shelf_left',
            ']': 'shelf_right',
            'g': 'jug_of_grapes',
            'c': 'jug_of_cement',
            'L': 'lights'}

        # Initialize containers
        tile_locs  = []
        wall_locs  = []
        floor_locs = []

        # Set size
        x_range = [x_1, x_1 + len(plan[0])]
        y_range = [y_1, y_1 + len(plan)]

        # Loop through each grid point
        for x in range(x_range[0], x_range[1]):
            for y in range(y_range[0], y_range[1]):
                x_rel, y_rel = x - x_1, y - y_1
                tile = self.env.map[x][y]
                
                ############################################
                # Update base properties
                ## Remove items and entities
                tile.item = None
                if tile.ent:
                    self.env.ents.remove(tile.ent)
                    tile.ent = None
                
                if not outside[y_rel][x_rel]:
                    tile_locs.append((x, y))

                    # Update tile properties
                    tile.room   = self
                    tile.biome  = self.biome
                    tile.hidden = self.hidden
                    
                    ############################################
                    # Handle edges
                    if plan[y_rel][x_rel] in ['-', '|']:
                        wall_locs.append((x, y))

                        # Update properties
                        tile.blocked     = True
                        tile.unbreakable = self.unbreakable
                        tile.img_IDs     = self.env.wall_img_IDs

                    ############################################
                    # Handle bulk
                    else:
                        floor_locs.append((x, y))

                        # Update properties
                        tile.blocked     = False
                        tile.unbreakable = False
                        tile.img_IDs     = self.roof_img_IDs if self.roof_img_IDs else self.floor_img_IDs
        
                # Add items
                if plan[y_rel][x_rel] not in ['-', '.', ' ']:
                    place_object(create_item(item_dict[plan[y_rel][x_rel]]), [x, y], self.env)

        return tile_locs, wall_locs, floor_locs

    def from_boundary(self, x_1, y_1, plan):
        """ Assigns and updates tiles within a custom region, then placed items.

            Parameters
            ----------
            x_1, y_1 : ints; tile coordinates of top left corner
            plan     : 2D list of str; human readable custom map

            Returns
            -------
            tile_locs  : list of int tuples; coordinates of all tiles in the room
            wall_locs  : list of int tuples; coordinates of all walls in the room
            floor_list : list of int tuples; coordinates of all floors in the room
        """

        outside = find_outside(plan)

        # Initialize containers
        tile_locs  = []
        wall_locs  = []
        floor_locs = []

        # Set size
        x_range = [x_1, x_1 + len(plan[0])]
        y_range = [y_1, y_1 + len(plan)]

        # Loop through each grid point
        for x in range(x_range[0], x_range[1]):
            for y in range(y_range[0], y_range[1]):
                x_rel, y_rel = x - x_1, y - y_1
                tile = self.env.map[x][y]
                
                ############################################
                # Update base properties
                if not outside[y_rel][x_rel]:
                    tile_locs.append((x, y))

                    # Update tile properties
                    tile.room  = self
                    tile.biome = self.biome
                    
                    ############################################
                    # Handle edges
                    if plan[y_rel][x_rel] in ['-', '|']:
                        wall_locs.append((x, y))
                        
                        # Update properties
                        tile.blocked     = True
                        tile.unbreakable = self.unbreakable

                    ############################################
                    # Handle bulk
                    else:
                        floor_locs.append((x, y))
                        tile.img_IDs = self.roof_img_IDs if self.roof_img_IDs else self.floor_img_IDs
        
        return tile_locs, wall_locs, floor_locs

    def center(self):
        """ Finds the center of the rectangle. """
        
        x_1 = min(loc[0] for loc in self.tile_locs)
        x_2 = max(loc[0] for loc in self.tile_locs)
        y_1 = min(loc[1] for loc in self.tile_locs)
        y_2 = max(loc[1] for loc in self.tile_locs)

        center_x = int((x_1 + x_2) / 2)
        center_y = int((y_1 + y_2) / 2)
        return (center_x, center_y)

class TextRoom:
    """ Generates a text-based room layout with walls, floors, doors, and furniture. """

    def __init__(self, width=5, height=5, doors=True):
        self.width  = width if width else random.randint(5, 7)
        self.height = height if height else random.randint(5, 7)
        self.doors  = doors
        self.plan   = [['' for x in range(self.width)] for y in range(self.height)]

    def neighbors(self, i, j):
        """ Possibly redundant; see get_vicinity. """

        # Return all 8 neighbors of a tile
        neighbors = [
            self.plan[i-1][j-1], self.plan[i-1][j], self.plan[i-1][j+1],
            self.plan[i][j-1],                      self.plan[i][j+1],
            self.plan[i+1][j-1], self.plan[i+1][j], self.plan[i+1][j+1]]
        return neighbors

    def create_floor(self):
        last_left  = 1
        last_right = self.width - 1

        for i in range(self.height):

            # Randomly decide if row matches last row or new offsets
            if not random.choice([0, 1]):
                for j in range(self.width):
                    if last_left <= j <= last_right: self.plan[i][j] = '.'
                    else:                            self.plan[i][j] = ' '

            # Generate new left and right bounds
            left  = random.randint(1, self.width//2-1)
            right = random.randint(self.width//2+1, self.width-1)

            # If bounds are too close to previous, use them to fill row
            if (abs(left - last_left) < 2) or (abs(right - last_right) < 2):
                for j in range(self.width):
                    if left <= j <= right: self.plan[i][j] = '.'
                    else:                  self.plan[i][j] = ' '

            # Randomly choose previous bounds
            elif random.choice([0, 1]):
                left  = random.choice([left,  last_left])
                right = random.choice([right, last_right])
                for j in range(self.width):
                    if left <= j <= right: self.plan[i][j] = '.'
                    else:                  self.plan[i][j] = ' '

            # Keep last row's bounds
            else:
                for j in range(self.width):
                    if last_left <= j <= last_right: self.plan[i][j] = '.'
                    else:                            self.plan[i][j] = ' '

            last_left  = left
            last_right = right

    def surround_with_walls(self):

        # Add empty rows/columns at borders
        self.plan[0] = [' ' for _ in range(self.width)]
        self.plan[1] = [' ' for _ in range(self.width)]
        self.plan.append([' ' for _ in range(self.width)])
        for i in range(len(self.plan)): self.plan[i].append(' ')

        # Replace neighboring tiles around floor with walls
        for i in range(len(self.plan)):
            for j in range(len(self.plan[0])):
                for key in self.plan[i][j]:
                    if key == '.':
                        if self.plan[i-1][j-1] != key: self.plan[i-1][j-1] = '-'
                        if self.plan[i-1][j]   != key: self.plan[i-1][j]   = '-'
                        if self.plan[i-1][j+1] != key: self.plan[i-1][j+1] = '-'
                        if self.plan[i][j-1]   != key: self.plan[i][j-1]   = '-'
                        if self.plan[i][j+1]   != key: self.plan[i][j+1]   = '-'
                        if self.plan[i+1][j-1] != key: self.plan[i+1][j-1] = '-'
                        if self.plan[i+1][j]   != key: self.plan[i+1][j]   = '-'
                        if self.plan[i+1][j+1] != key: self.plan[i+1][j+1] = '-'

    def place_doors(self):
        if not self.doors: return

        # Ensure top/bottom and right borders exist
        self.plan[0] = [' ' for _ in range(self.width)]
        self.plan.append([' ' for _ in range(self.width)])
        for i in range(len(self.plan)): self.plan[i].append(' ')

        # Try to place doors
        placed = False
        for i in range(len(self.plan)):
            for j in range(len(self.plan[0])):
                if not placed:
                    if self.plan[i][j] == '-':
                        vertical = [self.plan[i-1][j], self.plan[i+1][j]]
                        horizontal = [self.plan[i][j-1], self.plan[i][j+1]]

                        # Skip corners and fully enclosed walls
                        if ('-' in vertical) and ('-' in horizontal): placed = False
                        elif (' ' not in vertical) and (' ' not in horizontal): placed = False
                        else:
                            if not random.randint(0, 10):
                                self.plan[i][j] = '|'
                                if random.randint(0, 1): placed = True
                    else: placed = False

        # Second pass if no doors placed
        if not placed:
            for i in range(len(self.plan)):
                for j in range(len(self.plan[0])):
                    if not placed and self.plan[i][j] == '-':
                        vertical = [self.plan[i-1][j], self.plan[i+1][j]]
                        horizontal = [self.plan[i][j-1], self.plan[i][j+1]]
                        if ('-' in vertical) and ('-' in horizontal):           placed = False
                        elif (' ' not in vertical) and (' ' not in horizontal): placed = False
                        else:
                            if not random.randint(0, 10):
                                self.plan[i][j] = '|'
                                placed = True
                    else: placed = False

    def place_furniture(self):
        bed    = False
        dining = False
        shelf  = False
        lights = False

        for i in range(len(self.plan)):
            for j in range(len(self.plan[0])):
                if random.randint(0, 1):

                    # Check for indoor floor tiles for furniture
                    if (self.plan[i][j] == '.') and ('|' not in self.neighbors(i, j)):
                        if (self.plan[i][j+1] == '.') and ('|' not in self.neighbors(i, j+1)):

                            # Check for 3 consecutive open floor tiles
                            if (self.plan[i][j+2] == '.') and ('|' not in self.neighbors(i, j+2)):

                                # Place table and chairs
                                if not dining and not random.randint(0, 5):
                                    self.plan[i][j]   = 'b'
                                    self.plan[i][j+1] = 'T'
                                    self.plan[i][j+2] = 'd'
                                    dining = True
                            else:

                                # Place bed if 2 open spaces
                                if not bed and not random.randint(0, 3):
                                    self.plan[i][j] = '='
                                    if not random.randint(0, 2): bed = True
                                else:

                                    # Place shelf near wall
                                    if (not shelf) and (self.plan[i-1][j] == '-') and (self.plan[i-1][j+1] == '-'):
                                        self.plan[i][j]   = '['
                                        self.plan[i][j+1] = ']'
                                        shelf = True

                    # Outdoor tiles for lights
                    elif self.plan[i][j] == ' ':
                        try:
                            if '|' not in self.neighbors(i, j):
                                if not lights and not random.randint(0, 3):
                                    self.plan[i][j] = 'L'
                                    lights = True
                        except:
                            continue

    def export(self):
        export = []
        for row in self.plan:
            export.append("".join(row))
        return export

    def create(self):
        self.create_floor()
        self.surround_with_walls()
        self.place_doors()
        self.place_furniture()
        return self.export()

class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    
    def __init__(self, tile_id, **kwargs):
        """ Parameters
            ----------
            env           : environment object; owner of this tile

            room          : room instance
            entity        : entity instance; entity that occupies the tile
            item          : item instance; entity that occupies the tile
            
            img_IDs       : list of str; current image names
            wall_img_IDs  : list of str; default image name for wall
            floor_img_IDs : list of str; default image name for floor
            roof_img_IDs  : list of str; default image name for roof
            img_ID_timer  : int; fixed amount of time between animations
            
            X             : int; location of the tile in screen coordinate
            Y             : int; location of the tile in screen coordinate
            rand_X        : int; fixed amount of shift allowed in horizontal direction
            rand_Y        : int; fixed amount of shift allowed in vertical direction
            
            biome         : str; identifier for assigning biomes
            blocked       : bool; prevents items and entities from occupying the tile 
            hidden        : bool; prevents player from seeing the tile
            unbreakable   : bool; prevents player from changing the tile
            placed        : bool; notifies custom placement via CatalogMenu """
        
        pyg = session.pyg

        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self.tile_id = tile_id

        # Seed a seed for individual adjustments
        self.img_ID_timer = random.randint(0, 3) * 2
        self.rand_X       = random.randint(-pyg.tile_width, pyg.tile_width)
        self.rand_Y       = random.randint(-pyg.tile_height, pyg.tile_height)

    def draw(self):
        
        # Set location
        X = self.X - self.env.camera.X
        Y = self.Y - self.env.camera.Y
        
        # Load tile
        if self.img_ID_timer:
            time_diff = (time.time() // self.img_ID_timer) % self.img_ID_timer
            if time_diff == 0:                      image = session.img.other_alt[self.img_IDs[0]][self.img_IDs[1]]
            else:                                   image = session.img.other[self.img_IDs[0]][self.img_IDs[1]]
        else:                                       image = session.img.other[self.img_IDs[0]][self.img_IDs[1]]

        ## (Optional) Add shift effect
        if self.img_IDs[0] != 'roofs':
            if self.img_IDs[1] != 'wood':           image = session.img.shift(image, [abs(self.rand_X), abs(self.rand_Y)])
                
        ## (Optional) Apply static effect
        if self.biome in session.img.biomes['sea']: image = session.img.static(image, offset=20, rate=100)
        
        # Return result for rendering
        return image, (X, Y)

    def __eq__(self, other):
        if other is not None:
            return (self.X == other.X) and (self.Y == other.Y)

    def __hash__(self):
        return hash((self.X, self.Y))

class Weather:

    def __init__(self, env, light_set=None, clouds=True):
        
        pyg = session.pyg

        # Global mechanisms
        self.env = env

        # Surfaces
        self.sky_surface   = pygame.Surface((pyg.screen_width*10, pyg.screen_height*10), pygame.SRCALPHA)
        self.cloud_surface = pygame.Surface((pyg.screen_width*10, pyg.screen_height*10), pygame.SRCALPHA)

        self.last_hour = time.localtime().tm_hour + 1
        self.last_min  = time.localtime().tm_min  + 1

        self.hours = [
            0, 1,  2,  3,  4,  5,  6,  7,
            8, 9, 10, 11, 12, 13, 14, 15]
        self.alpha_hours = [
            255, 245, 218, 176, 128,  79,  37,  10,
            0,    10,  37,  79, 127, 176, 218, 245]
        self.symbols = [
            "🌕", "🌕", "🌖", "🌖", "🌗", "🌗", "🌘", "🌘",
            "🌑", "🌑", "🌒", "🌒", "🌓", "🌓", "🌔", "🌔"]
        
        self.light_list = []
        
        self.light_set = light_set
        self.cloudy    = clouds
        self.clouds    = []

    def run(self):

        # Reset sky
        self.sky_surface.fill((0, 0, 0, 255))
        self.cloud_surface.fill((0, 0, 0, 0))
        
        # Set day (1 in-game day per 8 hours)
        if (time.localtime().tm_hour + 1) != self.last_hour:
            self.last_hour = time.localtime().tm_hour + 1
            self.env.env_date = ((self.env.env_date+1) % 8) + 1
        
        # Set time of day (1 in-game hour per 10 minutes; 8 in-game hours per in-game day)
        if int(time.localtime().tm_min / 10) != self.last_min:
            self.last_min = int(time.localtime().tm_min / 10)
            self.env.env_time = (self.env.env_time + 1) % 16
        
        # Change the weather
        if self.light_set is None:
            
            # Make days bright and nights dark
            self.update_brightness()
            
            # Create and move clouds
            if self.cloudy:
                if not random.randint(0, 20+len(self.clouds)*2): self.create_cloud()
                self.move_clouds()
        
        # Set a constant brightness
        else:
            self.sky_surface.set_alpha(self.light_set)
            self.cloud_surface.set_alpha(self.light_set)

    def set_day_and_time(self, day=None, time=None, increment=False):
                
        # Set a specific day and time
        if not increment:
            if day is not None:  self.env.env_date = (day % 8) + 1
            if time is not None: self.env.env_time = time % 16
        
        # Move forwards in time by one step
        else: self.env.env_time = (self.env.env_time + 1) % 16

    def update_brightness(self):
        self.alpha = self.alpha_hours[self.env.env_time]
        self.sky_surface.set_alpha(self.alpha)
        self.cloud_surface.set_alpha(124)

    def create_cloud(self):

        pyg = session.pyg

        # Set direction of travel
        env       = self.env
        x_range   = [0, (env.size * pyg.screen_width) // pyg.tile_width]
        y_range   = [0, (env.size * pyg.screen_height) // pyg.tile_height]
        direction = random.choice(['up', 'down', 'left', 'right'])
        position = [random.randint(x_range[0], x_range[1]), random.randint(y_range[0], y_range[1])]
        
        # Set delay and time
        delay     = random.randint(1, 10)
        last_time = time.time()
        
        # Create shape
        width  = random.randint(5, 20)
        height = random.randint(5, 20)
        shape  = create_text_room(width, height)
        
        # Add cloud to list
        self.clouds.append({
            'position':  position,
            'shape':     shape,
            'delay':     delay,
            'direction': direction,
            'time':      last_time})

    def move_clouds(self):
        # check time and speed; move if sufficient
        # remove if out of map
        for cloud in self.clouds:
            if cloud:
                if time.time()-cloud['time'] > cloud['delay']:
                    cloud['time'] = time.time()
                    
                    if cloud['direction'] == 'up':      cloud['position'][1] -= 1
                    elif cloud['direction'] == 'down':  cloud['position'][1] += 1
                    elif cloud['direction'] == 'left':  cloud['position'][0] -= 1
                    elif cloud['direction'] == 'right': cloud['position'][0] += 1
            
            # Remove clouds
            if not random.randint(0, 2000):
                self.clouds.remove(cloud)

    def update_clouds(self):
        pyg    = session.pyg
        camera = self.env.camera
        
        # Draw visible tiles
        for y in range(int(camera.Y/32), int(camera.bottom/pyg.tile_height + 1)):
            for x in range(int(camera.X/32), int(camera.right/pyg.tile_width + 1)):
                try:    tile = self.env.map[x][y]
                except: continue
                
                if not tile.hidden:
                    for cloud in self.clouds:
                        if cloud:
                            
                            # Check if the tile is in the cloud
                            if x in range(cloud['position'][0], cloud['position'][0]+len(cloud['shape'])):
                                if y in range(cloud['position'][1], cloud['position'][1]+len(cloud['shape'][0])):
                                    x_char, y_char = x-cloud['position'][0], y-cloud['position'][1]
                                    char = cloud['shape'][x_char][y_char]
                                    if char != ' ':
                                        
                                        # Set image and pixel shift
                                        image = session.img.shift(session.img.dict['floors']['gray_floor'], [int((x_char+y_char)*13)%32, int(abs(x_char-y_char)*10)%32])
                                        
                                        # Set transparency
                                        if char == '-':   image.set_alpha(220)
                                        elif char == '.': image.set_alpha(255)
                                        else:             image.set_alpha(190)
                                        
                                        # Set the corresponding map tile
                                        X = x * pyg.tile_width - self.env.camera.X
                                        Y = y * pyg.tile_height - self.env.camera.Y
                                        
                                        self.cloud_surface.blit(image, (X, Y))

        return

    def update_lighting(self):
        pyg = session.pyg

        for effect_obj in self.light_list:
            
            # Center light on entity
            X = effect_obj.owner.X - self.env.camera.X
            Y = effect_obj.owner.Y - self.env.camera.Y
            
            # Render
            size   = effect_obj.size
            width  = pyg.tile_width * size
            height = pyg.tile_height * size
            alpha  = 255 // size
            left   = X - size * pyg.tile_width//2 + pyg.tile_width//2
            top    = Y - size * pyg.tile_height//2 + pyg.tile_width//2

            light_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            for i in range(size + 1):
                a = max(0, alpha * i)
                transparent_rect = pygame.Rect(
                    i * 16,
                    i * 16,
                    width - i * 32,
                    height - i * 32
                )
                pygame.draw.rect(light_surface, (255, 255, 255, a), transparent_rect)
            
            # Blend this light onto the main sky surface with "brightest wins"
            self.sky_surface.blit(light_surface, (left, top), special_flags=pygame.BLEND_RGBA_SUB)

    def render(self):
        """ Creates a black overlay and cuts out regions for lighting.
            Light is shown for any of the following conditions.
                1. The object has self.lamp as an effect and is not owned by an entity.
                2. The object has self.lamp as an effect and is equipped by an entity. """

        # Check for clouds
        if self.cloudy: self.update_clouds()

        # Check for lights
        self.update_lighting()
        
        session.pyg.display_queue.append([self.cloud_surface, (0, 0)])
        session.pyg.display_queue.append([self.sky_surface,   (0, 0)])

    def __getstate__(self):
        state = self.__dict__.copy()

        del state['sky_surface']
        del state['cloud_surface']

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        
        pyg = session.pyg
        self.sky_surface   = pygame.Surface((pyg.screen_width*10, pyg.screen_height*10), pygame.SRCALPHA)
        self.cloud_surface = pygame.Surface((pyg.screen_width*10, pyg.screen_height*10), pygame.SRCALPHA)

class Camera:
    """ Defines a camera to follow the player. """
    
    def __init__(self, ent):
        """ Defines a camera and its parameters. 
            
            Parameters
            ----------
            ent             : Entity object; focus of camera
            width           : int; number of visible tiles in screen coordinates
            height          : int; number of visible tiles in screen coordinates
            tile_map_width  : int; number of visible tiles in tile coordinates
            tile_map_height : int; number of visible tiles in tile coordinates
            
            X               : int; top left in screen coordinates
            Y               : int; top left in screen coordinates
            tile_map_x      : int; top left in tile coordinates
            tile_map_y      : int; top left in tile coordinates
            
            right           : int; number of visible tiles + displacement in screen coordinates
            bottom          : int; number of visible tiles + displacement in screen coordinates
            x_range         : int; number of visible tiles + displacement in tile coordinates
            y_range         : int; number of visible tiles + displacement in tile coordinates
            (questionable)
            
            fix_position    : bool; prevents adjustment of parameters
        """
        
        pyg = session.pyg

        self.ent             = ent
        self.width           = pyg.screen_width
        self.height          = pyg.screen_height + pyg.tile_height
        self.tile_map_width  = int(self.width / pyg.tile_width)
        self.tile_map_height = int(self.height / pyg.tile_height)
        
        self.X               = int(self.ent.X - int(self.width / 2))
        self.Y               = int(self.ent.Y - int(self.height / 2))
        self.tile_map_x      = int(self.X / pyg.tile_width)
        self.tile_map_y      = int(self.Y / pyg.tile_height)
        
        self.right           = self.X + self.width
        self.bottom          = self.Y + self.height
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        
        self.center_X        = int(self.X + int(self.width / 2))
        self.center_Y        = int(self.Y + int(self.height / 2))
        
        self.zoom            = 1
        self.min_zoom        = 2
        self.max_zoom        = 0.5
        self.fixed           = False
        self.fix_position()

    def update(self):
        """ ? """
        
        pyg = session.pyg

        if not self.fixed:
            X_move          = int(self.ent.X - self.center_X)
            self.X          = int(self.X + X_move)
            self.center_X   = int(self.center_X + X_move)
            self.right      = int(self.right + X_move)
            self.tile_map_x = int(self.X / pyg.tile_width)
            self.x_range    = int(self.tile_map_x + self.tile_map_width)

            Y_move          = int(self.ent.Y - self.center_Y)
            self.Y          = int(self.Y + Y_move)
            self.center_Y   = int(self.center_Y + Y_move)
            self.bottom     = int(self.bottom + Y_move)
            self.tile_map_y = int(self.Y / pyg.tile_height)
            self.y_range    = int(self.tile_map_y + self.tile_map_height)
            
            self.fix_position()

    def fix_position(self):
        """ ? """

        pyg = session.pyg

        if self.X < 0:
            self.X          = 0
            self.center_X   = self.X + int(self.width / 2)
            self.right      = self.X + self.width
            self.tile_map_x = int(self.X / (pyg.tile_width / self.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        elif self.right > (len(self.ent.env.map)-1) * pyg.tile_width:
            self.right      = (len(self.ent.env.map)) * pyg.tile_width
            self.X          = self.right - self.width
            self.center_X   = self.X + int(self.width / 2)
            self.tile_map_x = int(self.X / (pyg.tile_width / self.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        if self.Y < 0:
            self.Y          = 0
            self.center_Y   = self.Y + int(self.height / 2)
            self.bottom     = (self.Y + self.height + 320) / self.zoom
            self.tile_map_y = int(self.Y / (pyg.tile_height / self.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height
        
        elif self.bottom > (len(self.ent.env.map[0])) * pyg.tile_height:
            self.bottom     = (len(self.ent.env.map[0])) * pyg.tile_height
            self.Y          = self.bottom - self.height
            self.center_Y   = self.Y + int(self.height / 2)
            self.tile_map_y = int(self.Y / (pyg.tile_height / self.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height

    def zoom_in(self, factor=0.1, custom=None):
        """ Zoom in by reducing the camera's width and height. """
        
        pyg = session.pyg

        # Set to a specific value
        if custom and (self.zoom != custom):
            self.zoom = custom
            pyg.update_gui()
            self.width  = int(pyg.screen_width / self.zoom)
            self.height = int(pyg.screen_height / self.zoom)
            pyg.display = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self._recalculate_bounds()
        
        elif (not custom) and (not self.fixed) and (self.zoom < self.min_zoom):
            self.zoom += factor
            pyg.update_gui()
            self.width  = int(pyg.screen_width / self.zoom)
            self.height = int(pyg.screen_height / self.zoom)
            pyg.display = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self._recalculate_bounds()

    def zoom_out(self, factor=0.1, custom=None):
        """ Zoom out by increasing the camera's width and height. """
        
        pyg = session.pyg

        if (not self.fixed) and (self.zoom > self.max_zoom):
            if round(self.zoom, 2) > factor:

                if custom: self.zoom = custom
                else:      self.zoom = round(self.zoom - factor, 1)
                
                pyg.update_gui()
                self.width  = int(pyg.screen_width / self.zoom)
                self.height = int(pyg.screen_height / self.zoom)
                pyg.display = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self._recalculate_bounds()

    def _recalculate_bounds(self):
        """ Recalculate dependent properties after zooming. """

        pyg = session.pyg

        self.X               = self.ent.X - int(self.width / 2)
        self.Y               = self.ent.Y - int(self.height / 2)
        self.center_X        = self.X + int(self.width / 2)
        self.center_Y        = self.Y + int(self.height / 2)
        self.right           = self.X + self.width
        self.bottom          = self.Y + self.height
        self.tile_map_width  = int(self.width / pyg.tile_width)
        self.tile_map_height = int(self.height / pyg.tile_height)
        self.tile_map_x      = int(self.X / pyg.tile_width)
        self.tile_map_y      = int(self.Y / pyg.tile_height)
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        self.fix_position()

########################################################################################################################################################
# Tools
def voronoi_biomes(env, biomes):
    """ Partitions environment map into random regions. Not yet generalized for arbitrary applications.
    
        Parameters
        ----------
        biomes : list of dictionaries of objects
                 [<wall/floor name>, [<item name 1>, ...]], {...}] """
    
    pyg = session.pyg

    # Generate region centers and sizes
    num_regions    = len(biomes)
    region_centers = [[random.randint(0, len(env.map[0])), random.randint(0, len(env.map))] for _ in range(num_regions)]
    region_weights = [random.uniform(1, 3) for _ in range(num_regions)]
    seeds_with_ids = [[i, center, weight] for i, (center, weight) in enumerate(zip(region_centers, region_weights))]

    # Assign each tile to the nearest weighted region
    for y in range(len(env.map[0])):
        for x in range(len(env.map)):
            tile         = env.map[x][y]
            min_distance = float('inf')
            biome        = None
            
            # Look for the shortest path to a region center
            for i in range(len(seeds_with_ids)):
                region_center = [seeds_with_ids[i][1][0] * pyg.tile_width, seeds_with_ids[i][1][1] * pyg.tile_height]
                weight        = seeds_with_ids[i][2]
                distance      = (abs(region_center[0] - tile.X) + abs(region_center[1] - tile.Y)) / weight
                if distance < min_distance:
                    min_distance = distance
                    biome        = biomes[i][0]
                    img_IDs    = biomes[i][1]
                    region_num   = i
            
            # Set tile image and properties
            tile.biome = biome
            
            # Check for image variants
            #if floor_name[-1].isdigit() and not random.randint(0, 1):
            #    try:    floor_name = floor_name[:-1] + str((int(floor_name[-1])+1))
            #    except: continue
            
            tile.img_IDs = img_IDs

def create_tile(tile_id):
    """ Creates and returns an instance. """
    
    json_data = copy.deepcopy(tile_dicts[tile_id])
    tile      = Tile(tile_id, **json_data)
    return tile

def place_objects(env, items, entities):
    """ Places entities and items according to probability and biome.

        Parameters
        ----------
        env      : Environment object; location to be placed
        items    : list of lists; [[<biome str>, <object str>, <unlikelihood int>], ...]
        entities :  """
    
    from mechanics import is_blocked

    # Sort through each tile
    for y in range(len(env.map[0])):
        for x in range(len(env.map)):
            
            # Check that the space is not already occupied
            if not is_blocked(env.map[x][y]):

                ## Randomly select and place an item
                item_selection = random.choice(items)
                
                # Check that the object matches the biome
                if env.map[x][y].biome in session.img.biomes[item_selection[0]]:
                    if not random.randint(0, item_selection[2]) and not env.map[x][y].item:
                        
                        ## Place object
                        item = create_item(item_selection[1])
                        place_object(item, [x, y], env)
                
                ## Randomly select and place an entity
                ent_selection = random.choice(entities)
                
                # Check that the entity matches the biome
                if env.map[x][y].biome in session.img.biomes[ent_selection[0]]:
                    if not random.randint(0, ent_selection[2]) and not env.map[x][y].item:
                        
                        ## Create and place entity
                        entity = create_entity(ent_selection[1])
                        for item in ent_selection[3]:
                            if item:
                                obj = create_item(item)
                                session.items.pick_up(entity, obj)
                                if obj.equippable:
                                    session.items.toggle_equip(obj)
                                    if obj.effect:
                                        obj.effect.trigger = 'passive'
                        
                        entity.biome = env.map[x][y].biome
                        env.ents.append(entity)
                        place_object(entity, [x, y], env)

def place_object(obj, loc, env, names=None):
    """ Places a single object in the given location.

        Parameters
        ----------
        obj   : class object in [tile, item, entity]; object to be placed
        loc   : list of int; tile coordinates
        env   : Environment object; desired location
        names : list of str; Image dictionary names """  
      
    pyg = session.pyg

    from entities import Entity
    from items import Item

    # Place tile
    if type(obj) == Tile:
        
        # Update object
        obj.env    = env
        obj.X      = loc[0] * pyg.tile_width
        obj.Y      = loc[1] * pyg.tile_height
        obj.item   = env.map[loc[0]][loc[1]].item
        obj.ent    = env.map[loc[0]][loc[1]].ent
        
        # Update environment
        env.map[loc[0]][loc[1]] = obj

        ## Check structures
        if obj.img_IDs[0] == 'walls':
            obj.placed = True
            session.player_obj.ent.env.build_room(obj)

    # Place item
    elif type(obj) == Item:

        # Update object
        obj.X    = loc[0] * pyg.tile_width
        obj.X0   = loc[0] * pyg.tile_width
        obj.Y    = loc[1] * pyg.tile_height
        obj.Y0   = loc[1] * pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]

        # Update environment
        env.map[loc[0]][loc[1]].item        = obj
        env.map[loc[0]][loc[1]].blocked     = obj.blocked
        env.map[loc[0]][loc[1]].unbreakable = obj.blocked

        if obj.effect:
            session.effects.toggle_effect(obj.tile, obj.effect)
    
    # Place entity
    elif type(obj) == Entity:

        # Update object
        obj.X    = loc[0] * pyg.tile_width
        obj.X0   = loc[0] * pyg.tile_width
        obj.Y    = loc[1] * pyg.tile_height
        obj.Y0   = loc[1] * pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]

        # Update environment
        env.map[loc[0]][loc[1]].ent = obj
        env.map[loc[0]][loc[1]].blocked = False
        env.ents.append(obj)

def add_doors(room):
    """ Add one or two doors to a room, and adds a entryway. """
    
    # Add two doors
    if not random.randint(0, 10): num_doors = 2
    else:                         num_doors = 1
    
    for _ in range(num_doors):
    
        ## Avoid corners
        selected_tile = random.choice(room.noncorners_list)
        loc = [selected_tile.X // 32, selected_tile.Y // 32]
        
        # Add to map
        place_object(create_item('door'), loc, room.env)
        room.env.map[loc[0]][loc[1]].blocked   = False
        room.env.map[loc[0]][loc[1]].img_IDs = room.floor_img_IDs
        try:    room.walls_list.remove(room.env.map[loc[0]][loc[1]])
        except: pass
        
        ## Create wide entryway and clear items
        if not random.randint(0, 1):
            for i in range(3):
                for j in range(3):
                    try:
                        
                        # Make floor
                        if list(room.env.map[x][y].img_IDs) != list(room.wall_img_IDs):
                            x, y = loc[0]+i-1, loc[1]+j-1
                            
                            # Add roof
                            if room.env.map[x][y] in room.tiles_list:
                                room.env.map[x][y].roof_img_IDs      = room.roof_img_IDs
                                room.env.map[x][y].img_IDs = room.roof_img_IDs
                            else:
                                room.env.map[x][y].img_IDs = room.floor_img_IDs
                            
                            # Clear items, but keep doors
                            if ((i-1) or (j-1)):
                                room.env.map[x][y].item    = None
                                room.env.map[x][y].blocked = False
                            
                            room.env.map[x][y].biome == 'city'
                    
                    except: continue
        
        # Create narrow entryway and clear items
        else:
            for i in range(3):
                for j in range(3):
                    if not ((i-1) and (j-1)):
                        try:
                            
                            # Make floor
                            if list(room.env.map[loc[0]+i-1][loc[1]+j-1].img_IDs) != list(room.wall_img_IDs):
                                x, y = loc[0]+i-1, loc[1]+j-1
                                
                                # Add roof
                                if room.env.map[x][y] in room.tiles_list:
                                    room.env.map[x][y].roof_img_IDs      = room.roof_img_IDs
                                    room.env.map[x][y].img_IDs = room.roof_img_IDs
                                else:
                                    room.env.map[x][y].img_IDs = room.floor_img_IDs
                                
                                # Clear items, but keep doors
                                if ((i-1) or (j-1)):
                                    room.env.map[x][y].item    = None
                                    room.env.map[x][y].blocked = False
                                    
                                room.env.map[x][y].biome == 'city'
                        
                        except:
                            continue

def create_text_room(width=5, height=5, doors=True):
    generator = TextRoom(width, height, doors)
    return generator.create()

def find_outside(plan):
    """
    plan: list of strings
    Returns a 2D mask where True = outside.
    """
    H = len(plan)
    W = len(plan[0])

    # What counts as blocking the outside?
    BLOCKERS = {'-', '|'}   # you can easily adjust this

    outside = [[False]*W for _ in range(H)]
    queue = []

    # 1. Seed the BFS with all outer-edge *non-blocking* tiles
    for i in range(H):
        for j in (0, W-1):
            if plan[i][j] not in BLOCKERS:
                outside[i][j] = True
                queue.append((i,j))
    for j in range(W):
        for i in (0, H-1):
            if plan[i][j] not in BLOCKERS:
                if not outside[i][j]:
                    outside[i][j] = True
                    queue.append((i,j))

    # 2. BFS flood-fill through non-blockers only
    while queue:
        i,j = queue.pop(0)

        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            ni, nj = i+di, j+dj

            # in bounds
            if 0 <= ni < H and 0 <= nj < W:

                # must not already be marked
                if outside[ni][nj]:
                    continue

                # must not be a wall / blocker
                if plan[ni][nj] in BLOCKERS:
                    continue

                outside[ni][nj] = True
                queue.append((ni,nj))

    return outside

########################################################################################################################################################