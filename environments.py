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
from entities import create_entity, create_NPC
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

        # Owner
        self.player_obj = player_obj

        # Parameters
        self.room_max_size = 10
        self.room_min_size = 4
        self.max_rooms     = 3

        # Environment container
        self.areas = {}

    def add_area(self, name, permadeath=False):
        self.areas[name] = Area(name, self, permadeath)
        return self.areas[name]

    # Underworld
    def build_garden(self, area):
        """ Generates the overworld environment. """
        
        ###############################################################
        ## Initialize environment
        env = Environment(
            envs          = self,
            name          = 'garden',
            lvl_num       = 0,
            size          = 1,
            soundtrack    = ['menu'],
            img_IDs       = ['floors', 'grass4'],
            floor_img_IDs = ['floors', 'grass4'],
            wall_img_IDs  = ['walls', 'gray'],
            roof_img_IDs  = ['roofs', 'tiled'],
            blocked       = False,
            hidden        = False,
            area          = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather = Weather(env, light_set=0, clouds=False)
        
        ## Generate biomes
        biomes = [['forest', ['floors', 'grass4']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        # Construct room
        new_room = Room(
            name          = 'garden',
            env           = env,
            biome         = 'forest',

            width         = 19,
            height        = 14,
            x1            = 0,
            y1            = 0,

            floor_img_IDs = env.floor_img_IDs,
            wall_img_IDs  = env.wall_img_IDs,
            roof_img_IDs  = None,

            hidden        = False,
            unbreakable   = True,
            objects       = False)
        
        center = new_room.center()
        
        ###############################################################
        # Generate items and entities
        items    = [['forest', 'tree',       10]]
        entities = [['forest', 'red_radish', 50, [None]]]
        place_objects(env, items, entities)
        
        x = center[0] + random.randint(1, 5)
        y = center[1] + random.randint(1, 5)
        item = create_item('jug_of_water')
        place_object(item, (x, y), env)

        # Place player in first room
        x, y = center
        env.player_coordinates   = center
        env.map[x][y].item       = None
        self.player_obj.ent.tile = env.map[x][y]
        env.center = center
        
        ###############################################################
        # Quests
        session.questlogs.load_quest('garden_build_a_shed', area)
        session.questlogs.load_quest('garden_provide_water', area)
        
        ###############################################################
        # Pets
        env.pet_stats = {
            "stamina":  1,
            "strength": 1,
            "appeal":   1}
        
        env.pet_moods = {
            "happiness": 5,
            "sadness":   0,
            "anger":     0,
            "boredom":   0,
            "lethargy":  0,
            "confusion": 0}

        return env

    def build_womb(self, area):
        """ Generates the overworld environment. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs          = self,
            name          = 'womb',
            lvl_num       = 0,
            size          = 1,
            soundtrack    = ['menu'],
            img_IDs       = ['floors', 'dark_green_floor'],
            floor_img_IDs = ['floors', 'dark_green_floor'],
            wall_img_IDs  = ['walls', 'gray'],
            roof_img_IDs  = ['roofs', 'tiled'],
            blocked       = False,
            hidden        = True,
            area          = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather = Weather(env, light_set=0, clouds=False)
        
        ## Generate biomes
        biomes = [['forest', ['floors', 'grass4']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        # Construct rooms
        width  = 19
        height = 14
        x = 12
        y = 5
        
        ## Construct room
        new_room = Room(
            name    = 'womb',
            env     = env,
            x1      = x,
            y1      = y,
            width   = 4,
            height  = 4,
            biome   = 'forest',
            hidden  = True,
            objects = False,
            floor_img_IDs   = env.floor_img_IDs,
            wall_img_IDs   = env.wall_img_IDs,
            roof_img_IDs    = None)
        x, y = new_room.center()[0], new_room.center()[1]
        
        ###############################################################
        # Place player in first room
        env.player_coordinates = [x, y]
        env.map[x][y].item     = None
        self.player_obj.ent.tile = env.map[x][y]
        env.center = new_room.center()
        
        return env

    # Overworld
    def build_home(self, area):
        """ Generates player's home. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs          = self,
            name          = 'home',
            lvl_num       = 0,
            size          = 5,
            soundtrack    = ['home'],
            img_IDs       = ['walls', 'gray'],
            floor_img_IDs = ['floors', 'green_floor'],
            wall_img_IDs  = ['walls', 'gray'],
            roof_img_IDs  = ['roofs', 'tiled'],
            area          = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        center = [14, 14]
        
        # Set weather
        env.weather = Weather(env, light_set=32, clouds=False)
        
        ###############################################################
        ## Construct rooms
        main_room = Room(
            name    = 'home room',
            env     = env,
            x1      = center[0]-4,
            y1      = center[1]-4,
            width   = self.room_max_size,
            height  = self.room_max_size,
            biome   = 'any',
            hidden  = False,
            objects = False,
            floor_img_IDs   = env.floor_img_IDs,
            wall_img_IDs   = env.wall_img_IDs,
            roof_img_IDs    = None,
            plan = ['  -----     ',
                    ' --[].----- ',
                    ' -=.......--',
                    ' -........g-',
                    '--........c-',
                    '-.........--',
                    '--.....---- ',
                    ' --bTd--    ',
                    '  -----     '])
        env.center = [center[0]-1, center[1]-2]

        secret_room = Room(
            name    = 'secret room',
            env     = env,
            x1      = center[0]+8,
            y1      = center[1]+7,
            width   = self.room_min_size*2,
            height  = self.room_min_size*2,
            biome   = 'any',
            hidden  = True,
            objects = False,
            floor_img_IDs   = env.floor_img_IDs,
            wall_img_IDs   = env.wall_img_IDs,
            roof_img_IDs    = None)
        
        ###############################################################
        # Items and entities
        ## Hidden objects
        x, y = center[0]+10, center[1]+9
        item = create_item('blood_sword')
        place_object(item, [x, y], env)
        x, y = center[0]+5, center[1]+10
        item = create_item('iron_shield')
        place_object(item, [x, y], env)
        
        ## Bug fix
        x, y = 0, 0
        item = create_item('scroll_of_fireball')
        place_object(item, [x, y], env)
        
        ## Door
        x, y   = center[0]-3, center[1]+1
        stairs = create_item('overworld_entrance')
        place_object(stairs, [x, y], env)
        
        ## Friend
        x, y     = center[0]+1, center[1]
        ent      = create_entity('friend')
        ent.role = 'NPC'
        item     = create_item('mysterious_note')
        session.items.pick_up(ent, item, silent=True)
        place_object(ent, [x, y], env)
        
        ###############################################################
        # Quests
        session.questlogs.load_quest('tutorial', area)
        
        # Initial position
        env.player_coordinates = env.center
        
        return env

    def build_overworld(self, area):
        """ Generates the overworld environment. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs          = self,
            name          = 'overworld',
            lvl_num       = 0,
            size          = 10,
            soundtrack    = [
                'overworld 1',
                'overworld 2',
                'overworld 3',
                'overworld 4'],
            img_IDs       = ['floors', 'grass3'],
            floor_img_IDs = ['floors', 'grass3'],
            wall_img_IDs  = ['walls', 'gray'],
            roof_img_IDs  = ['roofs', 'tiled'],
            blocked       = False,
            hidden        = False,
            area          = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather = Weather(env, light_set=None, clouds=True)
        for _ in range(random.randint(0, 10)):
            env.weather.create_cloud()

        ## Generate biomes
        biomes = [
            ['forest', ['floors', 'grass3']],
            ['forest', ['floors', 'grass3']],
            ['forest', ['floors', 'grass3']],
            ['forest', ['floors', 'grass3']],
            ['desert', ['floors', 'sand1']],
            ['desert', ['floors', 'sand1']],
            ['desert', ['floors', 'sand1']],
            ['desert', ['floors', 'sand1']],
            ['water',  ['floors', 'water']],
            ['water',  ['floors', 'water']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        ## Construct rooms
        num_rooms             = 20
        room_counter, counter = 0, 0
        center                = env.center
        (x_1, y_1)            = center
        x_2                   = lambda width:  len(env.map)    - width  - 5
        y_2                   = lambda height: len(env.map[0]) - height - 5
        while room_counter < num_rooms:
            
            # Generate location
            width  = random.randint(self.room_min_size, self.room_max_size)
            height = random.randint(self.room_min_size, self.room_max_size)
            x      = random.randint(x_1, x_2(width))
            y      = random.randint(y_1, y_2(height))
            
            # Check for solid ground
            failed = False
            for u in range(width):
                for v in range(height):
                    if env.map[x+u][y+v].biome in session.img.biomes['sea']: failed = True
                    elif env.map[x+u][y+v].room:                     failed = True
            if not failed:
                
                ## Construct room
                new_room = Room(
                    name           = f"room {room_counter + 1}",
                    env            = env,
                    x1             = x,
                    y1             = y,
                    width          = width,
                    height         = height,
                    biome          = 'city',
                    hidden         = False,
                    objects        = False,
                    floor_img_IDs  = ['floors', 'dark_green_floor'],
                    wall_img_IDs   = env.wall_img_IDs,
                    roof_img_IDs   = env.roof_img_IDs,
                    unbreakable    = True,
                    plan           = create_text_room(width, height))

                room_counter += 1
                x, y = new_room.center()[0], new_room.center()[1]
            
            # Spawn rooms elsewhere if needed
            else: counter += 1
            if counter > num_rooms:
                counter = 0
                (x_1, y_1) = (0, 0)
        
        ## Construct home
        num_rooms             = 1
        room_counter, counter = 0, 0
        (x_1, y_1)            = env.center
        x_2                   = lambda width:  len(env.map)    - width  - 1
        y_2                   = lambda height: len(env.map[0]) - height - 1
        while room_counter < num_rooms:
            
            # Generate location
            width  = random.randint(self.room_min_size, self.room_max_size)
            height = random.randint(self.room_min_size, self.room_max_size)
            x      = random.randint(x_1, x_2(width))
            y      = random.randint(y_1, y_2(height))
            
            # Check for solid ground
            failed = False
            for u in range(width):
                for v in range(height):
                    if env.map[x+u][y+v].biome in session.img.biomes['sea']: failed = True
                    elif env.map[x+u][y+v].room:                     failed = True
            if not failed:
                
                main_room = Room(
                    name          = 'home room',
                    env           = env,
                    x1            = x,
                    y1            = y,
                    width         = self.room_max_size,
                    height        = self.room_max_size,
                    biome         = 'city',
                    hidden        = False,
                    objects       = False,
                    floor_img_IDs = ['floors', 'dark_green_floor'],
                    wall_img_IDs  = env.wall_img_IDs,
                    roof_img_IDs  = env.roof_img_IDs,
                    unbreakable   = True,
                    plan = [
                        '  -----     ',
                        ' --...----- ',
                        ' -........--',
                        ' -.........-',
                        '--.........|',
                        '-.........--',
                        '--.....---- ',
                        ' --...--    ',
                        '  -----     '])
                
                # Door
                door_x, door_y = x+1, y+5
                stairs = create_item('home_entrance')
                place_object(stairs, [door_x, door_y], env)
                
                room_counter += 1
            
            # Spawn rooms elsewhere if needed
            else: counter += 1
            if counter > num_rooms:
                counter = 0
                (x_1, y_1) = (0, 0)
        
        ## Create church
        main_room = Room(
            name          = 'church',
            env           = env,
            x1            = 20,
            y1            = 20,
            width         = self.room_max_size,
            height        = self.room_max_size,
            biome         = 'any',
            hidden        = False,
            objects       = False,
            floor_img_IDs = ['floors', 'red_floor'],
            wall_img_IDs  = env.wall_img_IDs,
            roof_img_IDs  = env.roof_img_IDs,
            unbreakable   = True,
            plan = [
                '  --------------           ---------- ',
                ' --............-----      --........--',
                ' -.................-      -..........-',
                ' -.................--------..........-',
                ' -...................................-',
                '--.................---------........--',
                '-..................-       -----..--- ',
                '--...........-------           -||-   ',
                ' --.....------                        ',
                '  -.....-                             ',
                '  -.....-                             ',
                '  --...--                             ',
                '   --.--                              ',
                '    -|-                               '])
        
        ###############################################################
        # Generate items and entities
        items = [
            ['forest', 'tree',       100],
            ['forest', 'leafy',      10],
            ['forest', 'blades',     1],
            ['desert', 'plant_drug', 1000],
            ['desert', 'enter_cave', 100]]
        entities = [
            ['forest', 'red_radish', 50,   [None]],
            ['wet',    'frog_ent',   500,  [None]],
            ['forest', 'grass_ent',  1000, [None]],
            ['desert', 'rock_ent',   50,   [None]]]
        place_objects(env, items, entities)
        
        env.center               = [door_x, door_y]
        env.player_coordinates   = [door_x, door_y]
        self.player_obj.ent.tile = env.map[door_x][door_y]
        
        ## Place NPCs
        bools = lambda room, i: [
            env.map[room.center()[0]+i][room.center()[1]+i].item,
            env.map[room.center()[0]+i][room.center()[1]+i].ent]
        
        # Set named characters to spawn
        room_list = ['home room', 'church']
        for name in ['Kyrio', 'Kapno', 'Erasti', 'Merci', 'Oxi', 'Aya', 'Zung', 'Lilao']:
            
            # Create NPC if needed
            ent = create_NPC(name)
            
            # Select room not occupied by player
            room = random.choice(env.rooms)
            while room.name in room_list:
                room = random.choice(env.rooms)
            room_list.append(room.name)
            
            # Select spawn location
            for i in range(3):
                occupied = bools(room, i-1)
                if occupied[0] == occupied[1]:
                    (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
            
            # Spawn entity
            place_object(ent, (x, y), env)
        
        # Set number of random characters
        for _ in range(5):
            
            # Create entity
            ent = create_NPC('random')
            
            # Select room not occupied by player
            room = random.choice(env.rooms)
            while room.name in ['home room', 'church']:
                room = random.choice(env.rooms)
            
            # Select spawn location
            for i in range(3):
                occupied = bools(room, i-1)
                if occupied[0] == occupied[1]:
                    (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
            
            # Spawn entity
            place_object(ent, (x, y), env)
        
        ###############################################################
        # Quests
        session.questlogs.load_quest('greet_the_town', area)
            
        return env

    def build_cave(self, area, lvl_num):
        """ Generates a cave environment. """
        
        ###############################################################
        # Initialize environment
        env = Environment(
            envs          = self,
            name          = 'cave',
            lvl_num       = lvl_num,
            size          = 1,
            soundtrack    = [f'dungeon {lvl_num}'],
            img_IDs       = ['walls',  'dark_red'],
            floor_img_IDs = ['floors', 'dirt1'],
            wall_img_IDs  = ['walls',  'dark_red'],
            roof_img_IDs  = None,
            blocked       = True,
            hidden        = True,
            area          = area)
        
        # Set weather
        env.weather = Weather(env, light_set=16, clouds=False)
        
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)

        # Generate biomes
        biomes = [['dungeon', ['walls', 'dark_red']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        # Construct rooms
        num_rooms = random.randint(2, 10)
        for i in range(num_rooms):
            
            # Construct room
            width    = random.randint(self.room_min_size, self.room_max_size)
            height   = random.randint(self.room_min_size, self.room_max_size)
            x        = random.randint(0, len(env.map)    - width  - 1)
            y        = random.randint(0, len(env.map[0]) - height - 1)
            
            new_room = Room(
                name    = 'cave room',
                env     = env,
                x1      = x,
                y1      = y,
                width   = width,
                height  = height,
                biome   = 'cave',
                hidden  = True,
                objects = True,
                floor_img_IDs   = env.floor_img_IDs,
                wall_img_IDs   = env.wall_img_IDs,
                roof_img_IDs    = env.roof_img_IDs)
        
        # Combine rooms and add doors
        env.combine_rooms()
        
        # Paths
        for i in range(len(env.rooms)):
            room_1, room_2 = env.rooms[i], env.rooms[i-1]
            chance_1, chance_2 = 0, random.randint(0, 1)
            if not chance_1:
                (x_1, y_1), (x_2, y_2) = room_1.center(), room_2.center()
                if not chance_2:
                    try:
                        env.create_h_tunnel(x_1, x_2, y_1)
                        env.create_v_tunnel(y_1, y_2, x_2)
                    except: raise Exception('Error')
                else:
                    env.create_v_tunnel(y_1, y_2, y_1, img_set=new_room.floor_img_IDs)
                    env.create_h_tunnel(x_1, x_2, y_2, img_set=new_room.floor_img_IDs)
        
        ###############################################################
        # Generate items and entities
        items = [
            ['dungeon', 'jug_of_cement',  100],
            ['dungeon', 'shovel',         500],
            ['dungeon', 'bones',          500],
            ['dungeon', 'sword',          1000//env.lvl_num]]
        entities = [
            ['dungeon', 'red_radish',     1000, [None]],
            ['dungeon', 'red_ent',        300,  [None]],
            ['dungeon', 'round3_ent',     50,   [None]]]
        place_objects(env, items, entities)
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.center = new_room.center()
        self.player_obj.ent.tile = env.map[x][y]
        
        # Generate acending stairs under player
        stairs = create_item('descend_cave')
        place_object(stairs, [x, y], env)

        # Generate stairs in the last room
        (x, y) = env.rooms[-1].center()
        if lvl_num == 1:
            stairs = create_item('overworld_entrance')
            stairs.img_IDs = ['stairs', 'ladder_up']
        else:
            stairs = create_item('ascend_cave')
        place_object(stairs, [x, y], env)

        return env

    # Dreams
    def build_dungeon(self, area, lvl_num):
        """ Generates the overworld environment. """
        
        ###############################################################
        # Initialize environment
        env = Environment(
            envs          = self,
            name          = 'dungeon',
            lvl_num       = lvl_num,
            size          = 2 * (1 + lvl_num//3),
            soundtrack    = [f'dungeon {lvl_num}'],
            img_IDs       = ['walls', 'gray'],
            floor_img_IDs = ['floors', 'dark_green_floor'],
            wall_img_IDs  = ['walls', 'gray'],
            roof_img_IDs  = None,
            blocked       = True,
            hidden        = True,
            area          = area)
        
        # Set weather
        env.weather = Weather(env, light_set=0, clouds=False)
        
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)

        # Generate biomes
        biomes = [['dungeon', ['walls', 'gray']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        # Construct rooms
        num_rooms = int(self.max_rooms * env.lvl_num) + 3
        for i in range(num_rooms):
            
            # Construct room
            width    = random.randint(self.room_min_size, self.room_max_size)
            height   = random.randint(self.room_min_size, self.room_max_size)
            x        = random.randint(0, len(env.map)    - width  - 1)
            y        = random.randint(0, len(env.map[0]) - height - 1)
            
            floor_img_IDs = random.choice([
                ['floors', 'dark_green_floor'],
                ['floors', 'dark_green_floor'],
                ['floors', 'green_floor']])
            
            new_room = Room(
                name    = 'dungeon room',
                env     = env,
                x1      = x,
                y1      = y,
                width   = width,
                height  = height,
                biome   = 'any',
                hidden  = True,
                objects = True,
                floor_img_IDs   = floor_img_IDs,
                wall_img_IDs   = env.wall_img_IDs,
                roof_img_IDs    = env.roof_img_IDs)
        
        # Combine rooms and add doors
        env.combine_rooms()
        
        # Paths
        for i in range(len(env.rooms)):
            room_1, room_2 = env.rooms[i], env.rooms[i-1]
            chance_1, chance_2 = 0, random.randint(0, 1)
            if not chance_1:
                (x_1, y_1), (x_2, y_2) = room_1.center(), room_2.center()
                if not chance_2:
                    try:
                        env.create_h_tunnel(x_1, x_2, y_1)
                        env.create_v_tunnel(y_1, y_2, x_2)
                    except: raise Exception('Error')
                else:
                    env.create_v_tunnel(y_1, y_2, y_1)
                    env.create_h_tunnel(x_1, x_2, y_2)
        
        ###############################################################
        # Generate items and entities
        items = [
            ['land', 'jug_of_blood', 10],
            ['land', 'bones',        50],
            ['land', 'sword',        1000//env.lvl_num],
            ['land', 'iron_shield',  1000//env.lvl_num],
            ['land', 'skeleton',     500],
            ['land', 'fire',         100]]
        entities = [
            ['land', 'plant_ent',    300,   [None]],
            ['land', 'eye_ent',      15,    [None]],
            ['land', 'red_radish',   1000,  [None]],
            ['land', 'round1_ent',   30,    [None]]]
        place_objects(env, items, entities)
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.center = new_room.center()
        self.player_obj.ent.tile = env.map[x][y]

        # Generate stairs in the last room
        stairs = create_item('descend_dungeon')
        place_object(stairs, [x, y], env)

        # Generate acending stairs under player
        if lvl_num != 1:
            (x, y) = env.rooms[-1].center()
            stairs = create_item('ascend_dungeon')
            place_object(stairs, [x, y], env)

        return env

    def build_bitworld(self, area):
        from pygame_utilities import bw_binary
        current_level = session.player_obj.ent.env.name

        area.envs.areas['bitworld'] = copy.deepcopy(area.envs.areas['overworld'])
        
        area.envs.areas['bitworld'].name       = 'bitworld'
        area.envs.areas['bitworld'].permadeath = False
        area.envs.areas['bitworld'].last_env   = None

        area.envs.areas['bitworld'].questlog   = {}
        session.questlogs.load_quest('kill_the_town', area)

        area.envs.areas['bitworld'].display_fx = bw_binary

        for env in area.envs.areas['bitworld']:
            env.weather.cloudy    = False
            env.weather.clouds    = []
            env.weather.light_set = env.weather.alpha_hours[4]
            env.camera = Camera(session.player_obj.ent)

            if env.name == current_level:
                x, y = session.player_obj.ent.get_pos()
                session.player_obj.ent.tile = env.map[x][y]

                # Update environment
                env.map[x][y].ent = None
                for ent in env.ents:
                    if ent.name == 'player':
                        env.ents.remove(ent)
                    else:
                        ent.role       = 'enemy'
                        ent.aggression = 5

    def build_hallucination(self, area, lvl_num=0):
        """ Generates the overworld environment. """
        
        ###############################################################
        ## Initialize environment
        if not lvl_num:
            if not self.areas['hallucination'].levels: lvl_num = 1
            else:                                      lvl_num = 1 + self.areas['hallucination'][-1].lvl_num        
        
        env = Environment(
            envs          = self,
            name          = 'hallucination',
            lvl_num       = lvl_num,
            size          = 3,
            soundtrack    = [f'hallucination {lvl_num}'],
            img_IDs       = ['walls',  'gold'],
            floor_img_IDs = ['floors', 'green_floor'],
            wall_img_IDs  = ['walls',  'gold'],
            roof_img_IDs  = None,
            blocked       = True,
            hidden        = True,
            area          = area)
        
        # Set weather
        env.weather = Weather(env, light_set=32, clouds=False)

        ## Generate biomes
        biomes = [
            ['any', ['walls', 'gold']],
            ['any', ['walls', 'gold']],
            ['any', ['walls', 'gold']],
            ['any', ['walls', 'gold']]]
        voronoi_biomes(env, biomes)
        
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        ###############################################################
        # Construct rooms
        num_rooms = int(self.max_rooms*2 * env.lvl_num) + 2
        for i in range(num_rooms):
            
            # Construct room
            width    = random.randint(self.room_min_size*2, self.room_max_size*2)
            height   = random.randint(self.room_min_size*2, self.room_max_size*2)
            x        = random.randint(0, len(env.map)    - width  - 1)
            y        = random.randint(0, len(env.map[0]) - height - 1)
            
            new_room = Room(
                name    = 'hallucination backdrop',
                env     = env,
                x1      = x,
                y1      = y,
                width   = width,
                height  = height,
                biome   = 'any',
                hidden  = True,
                objects = True,
                floor_img_IDs   = env.floor_img_IDs,
                wall_img_IDs   = env.wall_img_IDs,
                roof_img_IDs    = env.roof_img_IDs)
        
        # Combine rooms and add doors
        env.combine_rooms()
        
        ## Construct rooms
        num_rooms             = 5
        room_counter, counter = 0, 0
        center                = env.center
        (x_1, y_1)            = center
        x_2                   = lambda width:  len(env.map)    - width  - 1
        y_2                   = lambda height: len(env.map[0]) - height - 1
        while room_counter < num_rooms:
            
            # Generate location
            width  = random.randint(self.room_min_size, self.room_max_size)
            height = random.randint(self.room_min_size, self.room_max_size)
            x      = random.randint(x_1, x_2(width))
            y      = random.randint(y_1, y_2(height))
            
            # Check for solid ground
            failed = False
            for u in range(width):
                for v in range(height):
                    if env.map[x+u][y+v].biome in session.img.biomes['sea']: failed = True
            if not failed:
                
                ## Construct room
                new_room = Room(
                    name   = 'hallucination room',
                    env    = env,
                    x1     = x,
                    y1     = y,
                    width  = width,
                    height = height,
                    biome   = 'city',
                    hidden = False,
                    objects = False,
                    floor_img_IDs  = ['floors', 'dark_green_floor'],
                    wall_img_IDs  = env.wall_img_IDs,
                    roof_img_IDs   = env.roof_img_IDs,
                    plan = create_text_room(width, height, doors=False))

                room_counter += 1
                x, y = new_room.center()[0], new_room.center()[1]
            
            # Spawn rooms elsewhere if needed
            else: counter += 1
            if counter > num_rooms:
                counter = 0
                (x_1, y_1) = (0, 0)
        
        # Paths
        for i in range(len(env.rooms)):
            room_1, room_2 = env.rooms[i], env.rooms[i-1]
            chance_1, chance_2 = 0, random.randint(0, 1)
            if not chance_1:
                (x_1, y_1), (x_2, y_2) = room_1.center(), room_2.center()
                if not chance_2:
                    try:
                        env.create_h_tunnel(x_1, x_2, y_1)
                        env.create_v_tunnel(y_1, y_2, x_2)
                    except: raise Exception('Error')
                else:
                    env.create_v_tunnel(y_1, y_2, y_1)
                    env.create_h_tunnel(x_1, x_2, y_2)
        
        ###############################################################
        # Generate items and entities
        items = [
            ['any', 'jug_of_grapes',  100],
            ['any', 'shrooms',        10],
            ['any', 'purple_bulbs',   10],
            ['any', 'cup_shroom',     25],
            ['any', 'sword',          1000//env.lvl_num],
            ['any', 'yellow_dress',   200]]
        entities = [
            ['any', 'tentacles_ent',      100,  [None]],
            ['any', 'red_radish',     1000, [None]]]
        place_objects(env, items, entities)
        
        # Change player into tentacles
        self.player_obj.ent.img_names_backup = self.player_obj.ent.img_IDs
        self.player_obj.ent.img_IDs = ['tentacles_ent', 'front']
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.center = new_room.center()
        self.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-2].center()
        stairs = create_item('portal')
        stairs.name = 'hallucination'
        place_object(stairs, [x, y], env)

        return env

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
        if name       == 'womb':      env = self.envs.build_womb(self)
        elif name     == 'garden':    env = self.envs.build_garden(self)
        elif name     == 'home':      env = self.envs.build_home(self)
        elif name     == 'overworld': env = self.envs.build_overworld(self)
        elif name     == 'bitworld':  env = self.envs.build_bitworld(self)
        elif name[:7] == 'dungeon':   env = self.envs.build_dungeon(self, lvl_num)
        elif name[:4] == 'cave':      env = self.envs.build_cave(self,    lvl_num)

        if env:
            self.levels[name] = env

    def __getitem__(self, key):
        """ Allows the instance to be treated as a dictionary with levels as values. """

        if isinstance(key, int):   return list(self.levels.values())[key]
        elif isinstance(key, str): return self.levels[key]

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """
    
    def __init__(self, envs, name, size, soundtrack, lvl_num, wall_img_IDs, floor_img_IDs, roof_img_IDs, blocked=True, hidden=True, img_IDs=['', ''], area=None):
        """ Environment parameters
            ----------------------
            envs        : Environments object; owner

            name        : string
            floor_img_IDs       : int or string
            size        : string in ['small', 'medium', 'large']
            soundtrack  : list of pygame audio files
            entities    : list of Entity objects
            camera      : Camera object 
            
            Tile parameters
            ---------------
            name        : str; identifier for image
            room        : Room object
            entity      : Entity object; entity that occupies the tile
            item        : Item object; entity that occupies the tile
            img_IDs   : list of strings
            
            X           : int; location of the tile in screen coordinate
            Y           : int; location of the tile in screen coordinate

            blocked     : bool; prevents items and entities from occupying the tile 
            hidden      : bool; prevents player from seeing the tile
            unbreakable : bool; prevents player from changing the tile 
            """
        
        pyg = session.pyg

        # Global mechanisms
        self.envs = envs
        self.area = area

        # Identity
        self.name       = name
        self.lvl_num    = lvl_num
        self.size       = size
        self.soundtrack = soundtrack
        
        # World clock
        self.env_date = 0
        self.env_time = 3
        
        # Images and rooms
        self.wall_img_IDs  = wall_img_IDs
        self.floor_img_IDs = floor_img_IDs
        self.roof_img_IDs  = roof_img_IDs
        self.rooms         = []
        
        # Generate map tiles
        self.map = []
        X_range  = [0, self.size * pyg.screen_width]
        Y_range  = [0, self.size * pyg.screen_height]
        for X in range(X_range[0], X_range[1]+1, pyg.tile_width):
            row = [] 
            for Y in range(Y_range[0], Y_range[1]+1, pyg.tile_height):

                tile               = create_tile(img_IDs[1])
                tile.env           = self
                tile.wall_img_IDs  = wall_img_IDs
                tile.floor_img_IDs = floor_img_IDs
                tile.roof_img_IDs  = roof_img_IDs
                tile.X             = X
                tile.Y             = Y
                
                # Handle edges
                if (X in X_range) or (Y in Y_range):
                    tile.blocked     = True
                    tile.hidden      = hidden
                    tile.unbreakable = True
                
                # Handle bulk
                else:
                    tile.blocked     = blocked
                    tile.hidden      = hidden
                    tile.unbreakable = False
                
                row.append(tile)
            self.map.append(row)
        
        # Other
        self.ents = []
        self.player_coordinates = [0, 0]
        self.camera             = None
        self.center             = [int(len(self.map)/2), int(len(self.map[0])/2)]

    def create_h_tunnel(self, x1, x2, y, img_set=None):
        """ Creates horizontal tunnel. min() and max() are used if x1 is greater than x2. """
        
        # Sort through tiles
        for x in range(min(x1, x2), max(x1, x2) + 1):
            tile = self.map[x][y]
            
            # Find image
            if not img_set:
                if tile.room: img_set = tile.room.floor_img_IDs
                else:         img_set = self.floor_img_IDs
            
            # Empty and alter tile
            tile.blocked   = False
            tile.img_IDs = img_set
            if tile.ent:
                self.ents.remove(tile.ent)
                tile.ent = None

    def create_v_tunnel(self, y1, y2, x, img_set=None):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        
        # Sort through tiles
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tile = self.map[x][y]
            
            # Find image
            if not img_set:
                if tile.room: img_set = tile.room.floor_img_IDs
                else:         img_set = self.floor_img_IDs
            
            # Empty and alter tile
            tile.blocked   = False
            tile.img_IDs = img_set
            if tile.ent:
                self.ents.remove(tile.ent)
                tile.ent = None

    def build_room(self, obj):
        """ Checks if a placed tile has other placed tiles around it.
            If so, it creates a room if these placed tiles form a closed shape.
            Called by place_object when a wall is placed by the player.
        """
        
        from mechanics import get_vicinity

        # List of placed tile and its immediate neighbors
        first_neighbors = [obj]
        for first_neighbor in get_vicinity(obj).values():
            if first_neighbor.placed:
                first_neighbors.append(first_neighbor)
        
        # Chains of adjacent-placed tiles
        connected = dict()                # final dictionary of connected tiles
        queue     = list(first_neighbors) # all tiles to check
        visited   = set()                 # avoids revisiting tiles
        while queue:

            # Create dictionary entry for placed tile
            tile = queue.pop(0)
            if tile in visited: continue
            visited.add(tile)
            connected[tile] = []
            
            # Look at all neighbors of placed tile
            for neighbor in get_vicinity(tile).values():

                # Add neighboring placed tiles to chain
                if neighbor.placed:
                    connected[tile].append(neighbor)

                    # Queue to check for neighboring placed tiles
                    if (neighbor not in visited) and (neighbor not in queue):
                        queue.append(neighbor)
        
        # Check if the chain forms a closed boundary
        def has_closed_boundary(graph):
            """ This is a ChatGPT algorithm; don't ask. """

            visited = set()

            def dfs(node, parent, path):
                visited.add(node)
                path.append(node)
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        if dfs(neighbor, node, path):
                            return True
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
        
        if has_closed_boundary(connected):
            
            # Get bounds of the area to check
            boundary_coords = set((tile.X//32, tile.Y//32) for tile in connected.keys())
            xs = [tile.X//32 for tile in connected.keys()]
            ys = [tile.Y//32 for tile in connected.keys()]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        
            boundary = {
                'boundary tiles':       list(connected.keys()),
                'boundary coordinates': boundary_coords,
                'min x':                min_x,
                'max x':                max_x,
                'min y':                min_y,
                'max y':                max_y}
        
            room = Room(
                name     = 'placed',
                env      = self,
                x1       = min_x,
                y1       = min_y,
                width    = int(max_x - min_x),
                height   = int(max_y - min_y),
                biome    = 'city',
                hidden   = False,
                objects  = True,
                floor_img_IDs    = ['floors', 'wood'],
                wall_img_IDs    = obj.img_IDs,
                roof_img_IDs     = self.roof_img_IDs,
                boundary = boundary)

    def combine_rooms(self):
        """ Removes wall_img_IDs of intersecting rooms, then recombines them into a single room. """
    
        # Sort through each room
        cache = []
        rooms_copy = list(self.rooms)
        for i in range(len(rooms_copy)):
            for j in range(len(rooms_copy)):
                if rooms_copy[i] != rooms_copy[j]:
                    
                    # Prevent double counting
                    if {rooms_copy[i], rooms_copy[j]} not in cache:
                        cache.append({rooms_copy[i], rooms_copy[j]})
                        
                        # Find region of overlap
                        intersections_1 = self.rooms[i].intersect(self.rooms[j])
                        intersections_2 = self.rooms[j].intersect(self.rooms[i])
                        
                        # True if intersections are found
                        if intersections_1 and intersections_2:
                            self.rooms[i].delete = True
                            
                            ## Convert internal wall into floor and remove from lists
                            for tile in intersections_1:

                                # Keep shared wall_img_IDs
                                if tile not in rooms_copy[j].walls_list:
                                    tile.blocked   = False
                                    tile.item      = None
                                    tile.img_IDs = tile.room.floor_img_IDs  
                                    
                                    if tile in rooms_copy[i].walls_list:      self.rooms[j].walls_list.append(tile)
                                    if tile in rooms_copy[i].corners_list:    self.rooms[j].corners_list.append(tile)
                                    if tile in rooms_copy[i].noncorners_list: self.rooms[j].noncorners_list.append(tile)

                                if tile.roof_img_IDs and tile.room.roof_img_IDs:
                                    tile.roof_img_IDs = tile.room.roof_img_IDs
                                    tile.img_IDs = tile.room.roof_img_IDs                            
                            
                            for tile in intersections_2:

                                # Keep shared wall_img_IDs
                                if tile not in rooms_copy[i].walls_list:
                                    tile.blocked   = False
                                    tile.item      = None
                                    tile.img_IDs = tile.room.floor_img_IDs  
                                    
                                    # Remove from lists
                                    if tile in self.rooms[j].walls_list:      self.rooms[j].walls_list.remove(tile)
                                    if tile in self.rooms[j].corners_list:    self.rooms[j].corners_list.remove(tile)
                                    if tile in self.rooms[j].noncorners_list: self.rooms[j].noncorners_list.remove(tile)

                                if tile.roof_img_IDs and tile.room.roof_img_IDs:
                                    tile.roof_img_IDs = tile.room.roof_img_IDs
                                    tile.img_IDs = tile.room.roof_img_IDs  
                            
                            for tile in self.rooms[i].tiles_list:
                                tile.room = self.rooms[j]
                                self.rooms[j].tiles_list.append(tile)
                                self.rooms[i].tiles_list.remove(tile)
        
        for room in self.rooms[:]:
            if room.delete:
                self.rooms.remove(room)

class Room:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, **kwargs):
        """ Assigns tiles to a room and adjusts their properties.

            Parameters
            ----------
            name               : str
            env                : Environment object
            x1, y1             : int; top left corner in tile coordinates
            width              : int; extends rightward from x1
            height             : int; extends downward from y1
            hidden             : bool; black tiles until the room is entered
            floor_img_IDs              : list of str; img.dict names
            wall_img_IDs              : list of str; img.dict names
            roof_img_IDs               : list of str; img.dict names
            
            x2, y2             : int; bottom right corner in tile coordinates
            endpoints          : list of int; [x1, y1, x2, y2]
            player_coordinates : list of int; last known coordinates
            
            tiles_list         : list of tile objects; all tiles
            walls_list         : list of tile objects; all outer tiles
            corners_list       : list of tile objects; corner tiles
            noncorners_list    : list of tile objects; all outer tiles that are not corners
            
            plan               : list of str; custom floorplan
            boundary           : list of tile objects; custom walls_list
            delete             : bool; mark to be removed from environment
            
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
        width              = kwargs.get('width',  1)
        height             = kwargs.get('height', 1)
        self.x1            = kwargs.get('x1',     0)
        self.y1            = kwargs.get('y1',     0)
        self.x2            = self.x1 + width
        self.y2            = self.y1 + height
        self.endpoints     = [self.x1, self.y1, self.x2, self.y2]
        self.env.player_coordinates = self.center()
        
        # Image names and environment
        self.floor_img_IDs = kwargs.get('floor_img_IDs', None)
        self.wall_img_IDs  = kwargs.get('wall_img_IDs',  None)
        self.roof_img_IDs  = kwargs.get('roof_img_IDs',  None)

        # Properties
        self.plan          = kwargs.get('plan',        None)
        self.hidden        = kwargs.get('hidden',      False)
        self.objects       = kwargs.get('objects',     False)
        self.boundary      = kwargs.get('boundary',    None)
        self.unbreakable   = kwargs.get('unbreakable', False)
        self.delete        = False
        
        # Tiles
        self.tiles_list      = []
        self.walls_list      = []
        self.corners_list    = []
        self.noncorners_list = []
        
        # Create square room or text-based design
        if self.plan:       self.from_plan()
        elif self.boundary: self.from_boundary()
        else:               self.from_size()

    def from_size(self):
        
        for x in range(self.x1, self.x2+1):
            for y in range(self.y1, self.y2+1):
                
                # Find position of tile within room
                tile = self.env.map[x][y]
                
                # Apply properties to bulk
                tile.room   = self
                tile.hidden = self.hidden
                
                if self.roof_img_IDs: tile.img_IDs = self.roof_img_IDs
                else:         tile.img_IDs = self.floor_img_IDs
                tile.blocked = False

                # Change biome
                tile.biome = self.biome
                
                # Remove items and entities
                if not self.objects:
                    tile.item = None
                    if tile.ent:
                        self.env.ents.remove(tile.ent)
                        tile.ent = None
                
                # Handle tiles
                self.tiles_list.append(tile)
                
                # Handle wall_img_IDs
                if (x == self.x1) or (x == self.x2) or (y == self.y1) or (y == self.y2):
                    tile.img_IDs   = self.env.wall_img_IDs
                    tile.blocked     = True
                    tile.unbreakable = self.unbreakable
                    self.walls_list.append(tile)
                    
                    # Remove items and entities
                    tile.item = None
                    if tile.ent:
                        self.env.ents.remove(tile.ent)
                        tile.ent = None
                
                    # Handle corners
                    if   (x == self.x1) and (y == self.y1): self.corners_list.append(tile)
                    elif (x == self.x1) and (y == self.y2): self.corners_list.append(tile)
                    elif (x == self.x2) and (y == self.y1): self.corners_list.append(tile)
                    elif (x == self.x2) and (y == self.y2): self.corners_list.append(tile)
        
        self.noncorners_list = list(set(self.walls_list) - set(self.corners_list))

    def from_plan(self):
        outside = find_outside(self.plan)

        for y in range(len(self.plan)):
            for x in range(len(self.plan[y])):

                # Skip blank spaces
                if self.plan[y][x] == ' ':
                    continue

                # Find position of tile within room
                tile_x = self.x1 + x
                tile_y = self.y1 + y
                tile   = self.env.map[tile_x][tile_y]

                # Clean title properties
                tile.blocked     = False
                tile.item        = None
                tile.unbreakable = False

                # Optionally remove items and entities
                if not self.objects:
                    tile.item = None
                    if tile.ent:
                        self.env.ents.remove(tile.ent)
                        tile.ent = None

                # Set tile details
                if not outside[y][x]:
                    
                    # Room properties
                    tile.biome  = self.biome
                    tile.room   = self
                    tile.hidden = self.hidden
                    self.tiles_list.append(tile)

                    # Set initial image
                    if self.roof_img_IDs: tile.img_IDs = self.roof_img_IDs
                    else:                 tile.img_IDs = self.floor_img_IDs

                    # Walls
                    if self.plan[y][x] == '-':

                        tile.img_IDs = self.wall_img_IDs
                        self.walls_list.append(tile)

                        tile.blocked = True
                        tile.unbreakable = self.unbreakable

                    # Doors
                    elif self.plan[y][x] == '|':

                        tile.img_IDs = self.wall_img_IDs
                        self.walls_list.append(tile)
                
                        tile.blocked = False
                        place_object(create_item('door'), [tile_x, tile_y], self.env)
                    
                # Add furniture
                if self.plan[y][x] == '=':   place_object(create_item('red_bed'),         [tile_x, tile_y], self.env)                    
                elif self.plan[y][x] == 'b': place_object(create_item('red_chair_left'),  [tile_x, tile_y], self.env)
                elif self.plan[y][x] == 'T': place_object(create_item('table'),           [tile_x, tile_y], self.env)
                elif self.plan[y][x] == 'd': place_object(create_item('red_chair_right'), [tile_x, tile_y], self.env)
                elif self.plan[y][x] == '[': place_object(create_item('shelf_left'),      [tile_x, tile_y], self.env)
                elif self.plan[y][x] == ']': place_object(create_item('shelf_right'),     [tile_x, tile_y], self.env)
                
                # Add items
                elif self.plan[y][x] == 'g': place_object(create_item('jug_of_grapes'),   [tile_x, tile_y], self.env)
                elif self.plan[y][x] == 'c': place_object(create_item('jug_of_cement'),   [tile_x, tile_y], self.env)
                elif self.plan[y][x] == 'L': place_object(create_item('lights'),          [tile_x, tile_y], self.env)

    def from_boundary(self):
        
        # Import details
        wall_img_IDs    = self.boundary['boundary tiles']
        boundary_coords = self.boundary['boundary coordinates']
        min_x, max_x    = self.boundary['min x'], self.boundary['max x']
        min_y, max_y    = self.boundary['min y'], self.boundary['max y']
        
        visited = set()
        queue   = []
        
        # Add all boundary-adjacent tiles from the outer edge of the bounding box
        for x in range(min_x, max_x + 1):
            if (x, min_y) not in boundary_coords:
                queue.append((x, min_y))
            if (x, max_y) not in boundary_coords:
                queue.append((x, max_y))
        for y in range(min_y + 1, max_y):
            if (min_x, y) not in boundary_coords:
                queue.append((min_x, y))
            if (max_x, y) not in boundary_coords:
                queue.append((max_x, y))
        
        # Flood-fill all reachable, unplaced tiles from outside
        while queue:
            x, y = queue.pop(0)  # pop from front of list = BFS
            if (x, y) in visited:
                continue
            if not (0 <= x < len(self.env.map) and 0 <= y < len(self.env.map[0])):
                continue
            
            tile = self.env.map[x][y]
            if tile.placed:
                continue  # Skip placed tiles — they are solid
            
            visited.add((x, y))
            
            # Add 4-connected neighbors
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    queue.append((nx, ny))
        
        # Anything inside bounds and not reachable = enclosed
        floors = []
        for x in range(min_x + 1, max_x):
            for y in range(min_y + 1, max_y):
                if (x, y) not in visited and (x, y) not in boundary_coords:
                    floors.append(self.env.map[x][y])
        
        # Assign tiles to room
        for wall in wall_img_IDs:
            wall.room = self
            wall.hidden = self.hidden
            self.tiles_list.append(wall)
            wall.biome = self.biome
            self.walls_list.append(wall)
        for tile in floors:
            tile.room = self
            tile.hidden = self.hidden
            self.tiles_list.append(tile)
            tile.biome = self.biome
            if self.roof_img_IDs and (self.env.envs.player_obj.ent.tile not in self.tiles_list):
                tile.img_IDs = self.roof_img_IDs
            else:
                tile.img_IDs = self.roof_img_IDs # (?)

    def center(self):
        """ Finds the center of the rectangle. """
        
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)
 
    def intersect(self, other):
        """ Returns true if this rectangle intersects with another one. """
        
        # Check if the rooms intersect
        intersecting_wall = []
        if (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1):
            
            # Filter out tiles that are obviously not intersecting
            for wall_1 in self.walls_list:
                if (wall_1.X >= other.x1*32) and (wall_1.X <= other.x2*32):
                    if (wall_1.Y >= other.y1*32) and (wall_1.Y <= other.y2*32):
                        
                        # Filter out corners
                        if wall_1 not in other.walls_list:
                            intersecting_wall.append(wall_1)

        return intersecting_wall

    def __eq__(self, other):
        if other:
            return self.endpoints == other.endpoints

    def __hash__(self):
        return hash((self.x1, self.y1))

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
            if (time.time() // self.img_ID_timer) % self.img_ID_timer == 0: image = session.img.other_alt[self.img_IDs[0]][self.img_IDs[1]]
            else:                                             image = session.img.other[self.img_IDs[0]][self.img_IDs[1]]
        else:                                                 image = session.img.other[self.img_IDs[0]][self.img_IDs[1]]

        ## (Optional) Add shift effect
        if self.img_IDs[0] != 'roofs':
            if self.img_IDs[1] != 'wood':                   image = session.img.shift(image, [abs(self.rand_X), abs(self.rand_Y)])
                
        ## (Optional) Apply static effect
        if self.biome in session.img.biomes['sea']:           image = session.img.static(image, offset=20, rate=100)
        
        # Return result for rendering
        return image, (X, Y)

    def __eq__(self, other):
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
    """ Creates and returns an object.
    
        Parameters
        ----------
        names  : string or list of strings; name of object
        effect : bool or Effect object; True=default, False=None, effect=custom """
    
    # Create object
    tile_id   = tile_id.replace(" ", "_")
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
            if not is_blocked(env, [x, y]):

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