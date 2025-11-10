########################################################################################################################################################
# Environment creation and management
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import time
import random

## Specific
import pygame

## Local
import session
from quests import Questlog
from entities import create_entity, create_NPC

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

    def build_env(self, name, area):
        if name == 'womb':        return self.build_womb(area)
        elif name == 'garden':    return self.build_garden(area)
        elif name == 'home':      return self.build_home(area)
        elif name == 'overworld': return self.build_overworld(area)
        elif name == 'dungeon':   return self.build_dungeon(area)
        elif name == 'cave':      return self.build_cave(area)

    # Underworld
    def build_garden(self, area):
        """ Generates the overworld environment. """
        
        ###############################################################
        ## Initialize environment
        env = Environment(
            envs       = self,
            name       = 'garden',
            lvl_num    = 0,
            size       = 1,
            soundtrack = ['menu'],
            img_names  = ['floors', 'grass4'],
            floors     = ['floors', 'grass4'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'],
            blocked    = False,
            hidden     = False,
            area       = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': 0,
            'clouds':    False}
        env.weather = Weather(env, light_set=0, clouds=False)
        
        ## Generate biomes
        biomes = [['forest', ['floors', 'grass4']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        # Construct rooms
        width  = 19
        height = 14
        x      = 0
        y      = 0
        
        ## Construct room
        new_room = Room(
            name    = 'garden',
            env     = env,
            x1      = x,
            y1      = y,
            width   = width,
            height  = height,
            biome   = 'forest',
            hidden  = False,
            objects = False,
            floor   = env.floors,
            walls   = env.walls,
            roof    = None,
            unbreakable = True)
        center = new_room.center()
        
        ###############################################################
        # Generate items and entities
        items    = [['forest', 'tree',       10]]
        entities = [['forest', 'red radish', 50, [None]]]
        place_objects(env, items, entities)
        
        x = center[0] + random.randint(1, 5)
        y = center[1] + random.randint(1, 5)
        item = session.items.create_item('jug_of_water')
        place_object(item, (x, y), env)

        # Place player in first room
        x, y = center
        env.player_coordinates   = center
        env.map[x][y].item       = None
        env.entity               = self.player_obj.ent
        self.player_obj.ent.tile = env.map[x][y]
        env.center = center
        
        return env

    def build_womb(self, area):
        """ Generates the overworld environment. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs       = self,
            name       = 'womb',
            lvl_num    = 0,
            size       = 1,
            soundtrack = ['menu'],
            img_names  = ['floors', 'dark green floor'],
            floors     = ['floors', 'dark green floor'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'],
            blocked    = False,
            hidden     = True,
            area       = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': 0,
            'clouds':    False}
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
            floor   = env.floors,
            walls   = env.walls,
            roof    = None)
        x, y = new_room.center()[0], new_room.center()[1]
        
        ###############################################################
        # Place player in first room
        env.player_coordinates = [x, y]
        env.map[x][y].item     = None
        env.entity = self.player_obj.ent
        self.player_obj.ent.tile = env.map[x][y]
        env.center = new_room.center()
        
        return env

    # Overworld
    def build_home(self, area):
        """ Generates player's home. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs       = self,
            name       = 'home',
            lvl_num    = 0,
            size       = 5,
            soundtrack = ['home'],
            img_names  = ['walls', 'gray'],
            floors     = ['floors', 'green floor'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'],
            area       = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        center = [14, 14]
        
        # Set weather
        env.weather_backup = {
            'light_set': 32,
            'clouds':    False}
        env.weather = Weather(env, light_set=32)
        
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
            floor   = env.floors,
            walls   = env.walls,
            roof    = None,
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
            floor   = env.floors,
            walls   = env.walls,
            roof    = None)
        
        ###############################################################
        # Hidden objects
        x, y = center[0]+10, center[1]+9
        item = session.items.create_item('blood_sword')
        place_object(item, [x, y], env)
        x, y = center[0]+5, center[1]+10
        item = session.items.create_item('iron_shield')
        place_object(item, [x, y], env)
        
        # Bug fix
        x, y = 0, 0
        item = session.items.create_item('scroll_of_fireball')
        place_object(item, [x, y], env)
        
        # Door
        x, y = center[0]-3, center[1]+1
        item = session.items.create_item('door')
        item.name = 'overworld'
        place_object(item, [x, y], env)
        env.map[x][y].blocked = False
        env.map[x][y].unbreakable = False
        
        # Friend
        x, y = center[0]+1, center[1]
        ent = create_entity('friend')
        place_object(ent, [x, y], env)
        
        ###############################################################
        # Quests
        area.questlog.load_quest('tutorial')
        
        # Initial position
        env.player_coordinates = env.center
        
        return env

    def build_overworld(self, area):
        """ Generates the overworld environment. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs       = self,
            name       = 'overworld',
            lvl_num    = 0,
            size       = 10,
            soundtrack = [
                'overworld 1',
                'overworld 2',
                'overworld 3',
                'overworld 4'],
            img_names  = ['floors', 'grass3'],
            floors     = ['floors', 'grass3'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'],
            blocked    = False,
            hidden     = False,
            area       = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': None,
            'clouds':    True}
        env.weather = Weather(env, clouds=True)
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
                
                ## Construct room
                new_room = Room(
                    name   = 'overworld room',
                    env    = env,
                    x1     = x,
                    y1     = y,
                    width  = width,
                    height = height,
                    biome   = 'city',
                    hidden = False,
                    objects = False,
                    floor  = ['floors', 'dark green floor'],
                    walls  = env.walls,
                    roof   = env.roofs,
                    plan = create_text_room(width, height))

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
                    name    = 'home room',
                    env     = env,
                    x1      = x,
                    y1      = y,
                    width   = self.room_max_size,
                    height  = self.room_max_size,
                    biome   = 'city',
                    hidden  = False,
                    objects = False,
                    floor   = ['floors', 'dark green floor'],
                    walls   = env.walls,
                    roof    = env.roofs,
                    plan = ['  -----     ',
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
                item = session.items.create_item('door')
                item.name = 'home'
                place_object(item, [door_x, door_y], env)
                env.map[door_x][door_y].blocked = False
                env.map[door_x][door_y].unbreakable = False
                
                room_counter += 1
            
            # Spawn rooms elsewhere if needed
            else: counter += 1
            if counter > num_rooms:
                counter = 0
                (x_1, y_1) = (0, 0)
        
        ## Create church
        main_room = Room(
            name    = 'church',
            env     = env,
            x1      = 20,
            y1      = 20,
            width   = self.room_max_size,
            height  = self.room_max_size,
            biome   = 'any',
            hidden  = False,
            objects = False,
            floor   = ['floors', 'red floor'],
            walls   = env.walls,
            roof    = env.roofs,
            plan = ['  --------------           ---------- ',
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
            ['forest', 'tree',   100],
            ['forest', 'leafy',  10],
            ['forest', 'blades', 1],
            ['desert', 'plant',  1000],
            ['desert', 'cave',  100]]
        entities = [
            ['forest', 'red radish', 50,   [None]],
            ['wet',    'frog',       500,  [None]],
            ['forest', 'grass',      1000, [None]],
            ['desert', 'rock',       50,   [None]]]
        place_objects(env, items, entities)
        
        env.center             = [door_x, door_y]
        env.player_coordinates = [door_x, door_y]
        env.entity             = self.player_obj.ent
        self.player_obj.ent.tile    = env.map[door_x][door_y]
        
        ## Place NPCs
        bools = lambda room, i: [
            env.map[room.center()[0]+i][room.center()[1]+i].item,
            env.map[room.center()[0]+i][room.center()[1]+i].entity]
        
        # Set named characters to spawn
        for name in ['Kyrio', 'Kapno', 'Erasti', 'Merci', 'Oxi', 'Aya', 'Zung', 'Lilao']:
            
            # Create NPC if needed
            if name not in self.player_obj.ents.keys(): self.player_obj.ents[name] = create_NPC(name)
            
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
            place_object(self.player_obj.ents[name], (x, y), env)
        
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
        area.questlog.load_quest('greet_the_town')
        #self.player_obj.ent.questlines['Friendly Faces'] = FriendlyFaces()
        #self.player_obj.ent.questlines['Friendly Faces'].making_an_introduction()
            
        return env

    def build_cave(self, area, lvl_num=0):
        """ Generates a cave environment. """
        
        ###############################################################
        # Initialize environment
        if not lvl_num:
            if not self.areas['cave'].levels: lvl_num = 1
            else:                             lvl_num = 1 + self.areas['cave'][-1].lvl_num
                
        env = Environment(
            envs       = self,
            name       = 'cave',
            lvl_num    = lvl_num,
            size       = 1,
            soundtrack = [f'dungeon {lvl_num}'],
            img_names  = ['walls',  'dark red'],
            floors     = ['floors', 'dirt1'],
            walls      = ['walls',  'dark red'],
            roofs      = None,
            blocked    = True,
            hidden     = True,
            area       = area)
        
        # Set weather
        env.weather_backup = {
            'light_set': 16,
            'clouds':    False}
        env.weather = Weather(env, light_set=16)
        
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)

        # Generate biomes
        biomes = [['dungeon', ['walls', 'dark red']]]
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
                floor   = env.floors,
                walls   = env.walls,
                roof    = env.roofs)
        
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
                    env.create_v_tunnel(y_1, y_2, y_1, img_set=new_room.floor)
                    env.create_h_tunnel(x_1, x_2, y_2, img_set=new_room.floor)
        
        ###############################################################
        # Generate items and entities
        items = [
            ['dungeon', 'jug of cement',  100],
            ['dungeon', 'shovel',         500],
            ['dungeon', 'bones',          500],
            ['dungeon', 'sword',          1000//env.lvl_num]]
        
        entities = [
            ['dungeon', 'red radish',     1000, [None]],
            ['dungeon', 'red',            300,  [None]],
            ['dungeon', 'round3',         50,   [None]]]
        
        place_objects(env, items, entities)
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.entity = self.player_obj.ent
        env.center = new_room.center()
        self.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-1].center()
        stairs = session.items.create_item('cave')
        stairs.img_names = ['floors', 'dirt2']
        place_object(stairs, [x, y], env)

        return env

    # Dungeon
    def build_dungeon(self, area, lvl_num=0):
        """ Generates the overworld environment. """
        
        ###############################################################
        # Initialize environment
        if not lvl_num:
            if not self.areas['dungeon'].levels: lvl_num = 1
            else:                                lvl_num = 1 + self.areas['dungeon'][-1].lvl_num
        
        env = Environment(
            envs       = self,
            name       = 'dungeon',
            lvl_num    = lvl_num,
            size       = 2 * (1 + lvl_num//3),
            soundtrack = [f'dungeon {lvl_num}'],
            img_names  = ['walls', 'gray'],
            floors     = ['floors', 'dark green floor'],
            walls      = ['walls', 'gray'],
            roofs      = None,
            blocked    = True,
            hidden     = True,
            area       = area)
        
        # Set weather
        env.weather_backup = {
            'light_set': None,
            'clouds':    False}
        env.weather = Weather(env, clouds=False)
        
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
            
            floor = random.choice([
                ['floors', 'dark green floor'],
                ['floors', 'dark green floor'],
                ['floors', 'green floor']])
            
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
                floor   = floor,
                walls   = env.walls,
                roof    = env.roofs)
        
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
            ['land', 'jug of blood',   10],
            ['land', 'bones',          50],
            ['land', 'sword',          1000//env.lvl_num],
            ['land', 'iron shield',    1000//env.lvl_num],
            ['land', 'skeleton',       500],
            ['land', 'fire',           100]]
        
        entities = [
            ['land', 'plant',          300,   [None]],
            ['land', 'eye',            15,    [None]],
            ['land', 'red radish',     1000,  [None]],
            ['land', 'round1',         30,    [None]]]
        
        place_objects(env, items, entities)
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.entity = self.player_obj.ent
        env.center = new_room.center()
        self.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-2].center()
        stairs = session.items.create_item('door')
        stairs.name = 'dungeon'
        place_object(stairs, [x, y], env)
        
        return env

    # Hallucination
    def build_hallucination(self, area, lvl_num=0):
        """ Generates the overworld environment. """
        
        ###############################################################
        ## Initialize environment
        if not lvl_num:
            if not self.areas['hallucination'].levels: lvl_num = 1
            else:                                      lvl_num = 1 + self.areas['hallucination'][-1].lvl_num        
        
        env = Environment(
            envs       = self,
            name       = 'hallucination',
            lvl_num    = lvl_num,
            size       = 3,
            soundtrack = [f'hallucination {lvl_num}'],
            img_names  = ['walls',  'gold'],
            floors     = ['floors', 'green floor'],
            walls      = ['walls',  'gold'],
            roofs      = None,
            blocked    = True,
            hidden     = True,
            area       = area)
        
        # Set weather
        env.weather_backup = {
            'light_set': 32,
            'clouds':    False}
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
                floor   = env.floors,
                walls   = env.walls,
                roof    = env.roofs)
        
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
                    floor  = ['floors', 'dark green floor'],
                    walls  = env.walls,
                    roof   = env.roofs,
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
            ['any', 'jug of grapes',  100],
            ['any', 'shrooms',        10],
            ['any', 'shrooms',        10],
            ['any', 'purple bulbs',   10],
            ['any', 'cup shroom',     25],
            ['any', 'sword',          1000//env.lvl_num],
            ['any', 'yellow dress',   200]]
        
        entities = [
            ['any', 'triangle',       200,  [None]],
            ['any', 'tentacles',      100,  [None]],
            ['any', 'red radish',     1000, [None]],
            ['any', 'star',           150,  [None]]]
        
        place_objects(env, items, entities)
        
        # Change player into tentacles
        self.player_obj.ent.img_names_backup = self.player_obj.ent.img_names
        self.player_obj.ent.img_names = ['tentacles', 'front']
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.entity = self.player_obj.ent
        env.center = new_room.center()
        self.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-2].center()
        stairs = session.items.create_item('portal')
        stairs.name = 'hallucination'
        place_object(stairs, [x, y], env)

        return env

    # Bitworld
    def build_bitworld(self, area):
        """ Generates the bitworld environment. """

        ###############################################################
        ## Initialize environment
        env = Environment(
            envs       = self,
            name       = 'bitworld',
            lvl_num    = 0,
            size       = 7,
            soundtrack = [
                'overworld 1',
                'overworld 2',
                'overworld 3',
                'overworld 4'],
            img_names  = ['floors', 'grass3'],
            floors     = ['floors', 'grass3'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'],
            blocked    = False,
            hidden     = False,
            area       = area)
        env.camera = Camera(self.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': None,
            'clouds':    False}
        env.weather = Weather(env, clouds=False)

        ## Generate biomes
        biomes = [
            ['forest', ['floors', 'grass2']]]
        voronoi_biomes(env, biomes)
        
        ###############################################################
        ## Construct rooms
        num_rooms             = 20
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
                    elif env.map[x+u][y+v].room:                             failed = True
            if not failed:
                
                ## Construct room
                new_room = Room(
                    name   = 'bitworld room',
                    env    = env,
                    x1     = x,
                    y1     = y,
                    width  = width,
                    height = height,
                    biome   = 'city',
                    hidden = False,
                    objects = False,
                    floor  = ['floors', ' floor'],
                    walls  = env.walls,
                    roof   = env.roofs,
                    plan = create_text_room(width, height))

                room_counter += 1
                x, y = new_room.center()[0], new_room.center()[1]
            
            # Spawn rooms elsewhere if needed
            else: counter += 1
            if counter > num_rooms:
                counter = 0
                (x_1, y_1) = (0, 0)
        
        ## Create player's house
        main_room = Room(
            name    = 'home room',
            env     = env,
            x1      = env.center[0],
            y1      = env.center[1],
            width   = self.room_max_size,
            height  = self.room_max_size,
            biome   = 'any',
            hidden  = False,
            objects = False,
            floor   = ['floors', 'dark green floor'],
            walls   = env.walls,
            roof    = env.roofs,
            plan = ['  -----     ',
                    ' --...----- ',
                    ' -........--',
                    ' -.........-',
                    '--.........|',
                    '-.........--',
                    '--.....---- ',
                    ' --...--    ',
                    '  -----     '])
        
        # Door
        x, y = center[0]+1, center[1]+5
        item = session.items.create_item('door')
        item.name = 'home'
        place_object(item, [x, y], env)
        env.map[x][y].blocked = False
        env.map[x][y].unbreakable = False
        
        ## Create church
        main_room = Room(
            name    = 'church',
            env     = env,
            x1      = 20,
            y1      = 20,
            width   = self.room_max_size,
            height  = self.room_max_size,
            biome   = 'any',
            hidden  = False,
            objects = False,
            floor   = ['floors', 'red floor'],
            walls   = env.walls,
            roof    = env.roofs,
            plan = ['  --------------           ---------- ',
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
            ['forest', 'tree',   100],
            ['forest', 'leafy',  10],
            ['forest', 'blades', 1]]
        
        entities = [
            ['forest', 'red radish', 50,   [None]],
            ['wet',    'frog',       500,  [None]],
            ['forest', 'grass',      1000, [None]]]
        
        place_objects(env, items, entities)
        
        env.player_coordinates = env.center # [0, 10]
        env.entity = self.player_obj.ent
        self.player_obj.ent.tile = env.map[0][10]
        
        ## Place NPCs
        bools = lambda room, i: [
            env.map[room.center()[0]+i][room.center()[1]+i].item,
            env.map[room.center()[0]+i][room.center()[1]+i].entity]
        
        # Set number of random characters
        for _ in range(15):
            
            # Create entity
            ent = create_NPC('random')
            
            # Select room not occupied by player
            room = random.choice(env.rooms)
            while room == env.rooms[-1]:
                room = random.choice(env.rooms)
            
            # Select spawn location
            for i in range(3):
                occupied = bools(room, i-1)
                if occupied[0] == occupied[1]:
                    (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
            
            # Spawn entity
            place_object(ent, (x, y), env)

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

        self.questlog   = Questlog()

    def add_level(self, name):
        self.levels[name] = self.envs.build_env(name, self)

    def __getitem__(self, key):
        if isinstance(key, int):   return list(self.levels.values())[key]
        elif isinstance(key, str): return self.levels[key]

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """
    
    def __init__(self, envs, name, size, soundtrack, lvl_num, walls, floors, roofs, blocked=True, hidden=True, img_names=['', ''], area=None):
        """ Environment parameters
            ----------------------
            envs        : Environments object; owner

            name        : string
            floor       : int or string
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
            img_names   : list of strings
            
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
        self.walls  = walls
        self.floors = floors
        self.roofs  = roofs
        self.rooms  = []
        
        # Generate map tiles
        self.map = []
        X_range  = [0, self.size * pyg.screen_width]
        Y_range  = [0, self.size * pyg.screen_height]
        number    = 0
        for X in range(X_range[0], X_range[1]+1, pyg.tile_width):
            row = [] 
            for Y in range(Y_range[0], Y_range[1]+1, pyg.tile_height):
                number += 1
                
                # Handle edges
                if (X in X_range) or (Y in Y_range):
                    tile = Tile(
                        env         = self,

                        number      = number,
                        room        = None,
                        entity      = None,
                        item        = None,
                        
                        img_names   = img_names,
                        walls       = walls,
                        floor       = floors,
                        roof        = roofs,
                        timer       = random.randint(0, 3) * 2,

                        X           = X,
                        Y           = Y,
                        rand_X      = random.randint(-pyg.tile_width, pyg.tile_width),
                        rand_Y      = random.randint(-pyg.tile_height, pyg.tile_height),
                        
                        biome       = None,
                        blocked     = True,
                        hidden      = hidden,
                        unbreakable = True,
                        placed      = False)
                
                # Handle bulk
                else:
                    tile = Tile(
                        env         = self,

                        number      = number,
                        room        = None,
                        entity      = None,
                        item        = None,
                        
                        img_names   = img_names,
                        walls       = walls,
                        floor       = floors,
                        roof        = roofs,
                        timer       = random.randint(0, 3) * 2,

                        X           = X,
                        Y           = Y,
                        rand_X      = random.randint(-pyg.tile_width, pyg.tile_width),
                        rand_Y      = random.randint(-pyg.tile_height, pyg.tile_height),
                        
                        biome       = None,
                        blocked     = blocked,
                        hidden      = hidden,
                        unbreakable = False,
                        placed      = False)
                
                row.append(tile)
            self.map.append(row)
        
        # Other
        self.entities = []
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
                if tile.room: img_set = tile.room.floor
                else:         img_set = self.floors
            
            # Empty and alter tile
            tile.blocked   = False
            tile.img_names = img_set
            if tile.entity:
                self.entities.remove(tile.entity)
                tile.entity = None

    def create_v_tunnel(self, y1, y2, x, img_set=None):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        
        # Sort through tiles
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tile = self.map[x][y]
            
            # Find image
            if not img_set:
                if tile.room: img_set = tile.room.floor
                else:         img_set = self.floors
            
            # Empty and alter tile
            tile.blocked   = False
            tile.img_names = img_set
            if tile.entity:
                self.entities.remove(tile.entity)
                tile.entity = None

    def build_room(self, obj):
        """ Checks if a placed tile has other placed tiles around it.
            If so, it creates a room if these placed tiles form a closed shape. """
        
        from mechanics import get_vicinity

        # Make a list of the tile and its neighbors
        first_neighbors = [obj]        # list of initial set of tiles; temporary
        for first_neighbor in get_vicinity(obj).values():
            if first_neighbor.placed:
                first_neighbors.append(first_neighbor)
        
        # Look for a chain of adjacent-placed tiles
        connected = dict()             # final dictionary of connected tiles
        queue = list(first_neighbors)  # holds additional tiles outside of nearest neighbors
        visited = set()                # avoids revisiting tiles
        while queue:
            tile = queue.pop(0)
            if tile in visited: continue
            visited.add(tile)
            connected[tile] = []
            
            # Add new links to the chain
            for neighbor in get_vicinity(tile).values():
                if neighbor.placed:
                    connected[tile].append(neighbor)
                    if neighbor not in visited and neighbor not in queue:
                        queue.append(neighbor)
        
        # Check if the chain forms a closed boundary
        def has_closed_boundary(graph):
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
        
        # Look for enclosed tiles and create room
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
        
            main_room = Room(
                name     = 'placed',
                env      = self,
                x1       = min_x,
                y1       = min_y,
                width    = int(max_x - min_x),
                height   = int(max_y - min_y),
                biome    = 'city',
                hidden   = False,
                objects  = True,
                floor    = ['floors', 'wood'],
                walls    = obj.img_names,
                roof     = self.roofs,
                boundary = boundary)

    def combine_rooms(self):
        """ Removes walls of intersecting rooms, then recombines them into a single room. """
    
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
                            
                            ## Convert internal walls into floors and remove from lists
                            for tile in intersections_1:

                                # Keep shared walls
                                if tile not in rooms_copy[j].walls_list:
                                    tile.blocked   = False
                                    tile.item      = None
                                    tile.img_names = tile.room.floor  
                                    
                                    if tile in rooms_copy[i].walls_list:      self.rooms[j].walls_list.append(tile)
                                    if tile in rooms_copy[i].corners_list:    self.rooms[j].corners_list.append(tile)
                                    if tile in rooms_copy[i].noncorners_list: self.rooms[j].noncorners_list.append(tile)

                                if tile.roof and tile.room.roof:
                                    tile.roof = tile.room.roof
                                    tile.img_names = tile.room.roof                            
                            
                            for tile in intersections_2:

                                # Keep shared walls
                                if tile not in rooms_copy[i].walls_list:
                                    tile.blocked   = False
                                    tile.item      = None
                                    tile.img_names = tile.room.floor  
                                    
                                    # Remove from lists
                                    if tile in self.rooms[j].walls_list:      self.rooms[j].walls_list.remove(tile)
                                    if tile in self.rooms[j].corners_list:    self.rooms[j].corners_list.remove(tile)
                                    if tile in self.rooms[j].noncorners_list: self.rooms[j].noncorners_list.remove(tile)

                                if tile.roof and tile.room.roof:
                                    tile.roof = tile.room.roof
                                    tile.img_names = tile.room.roof  
                            
                            for tile in self.rooms[i].tiles_list:
                                tile.room = self.rooms[j]
                                self.rooms[j].tiles_list.append(tile)
                                self.rooms[i].tiles_list.remove(tile)
        
        for room in self.rooms[:]:
            if room.delete:
                self.rooms.remove(room)

    def __getstate__(self):
        state = self.__dict__.copy()
        if "weather" in state:
            del state["weather"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.weather = Weather(
            env       = self,
            light_set = self.weather_backup['light_set'],
            clouds    = self.weather_backup['clouds'])

class Room:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, name, env, x1, y1, width, height, hidden, floor, walls, roof, objects, biome, plan=None, boundary=None, unbreakable=False):
        """ Assigns tiles to a room and adjusts their properties.

            Parameters
            ----------
            name               : str
            env                : Environment object
            x1, y1             : int; top left corner in tile coordinates
            width              : int; extends rightward from x1
            height             : int; extends downward from y1
            hidden             : bool; black tiles until the room is entered
            floor              : list of str; img.dict names
            walls              : list of str; img.dict names
            roof               : list of str; img.dict names
            
            x2, y2             : int; bottom right corner in tile coordinates
            endpoints          : list of int; [x1, y1, x2, y2]
            player_coordinates : list of int; last known coordinates
            
            tiles_list         : list of Tile objects; all tiles
            walls_list         : list of Tile objects; all outer tiles
            corners_list       : list of Tile objects; corner tiles
            noncorners_list    : list of Tile objects; all outer tiles that are not corners
            
            plan               : list of str; custom floorplan
            boundary           : list of Tile objects; custom walls_list
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
        
        # Name
        self.name = name
        
        # Location
        self.x1        = x1
        self.y1        = y1
        self.x2        = x1 + width
        self.y2        = y1 + height
        self.endpoints = [self.x1, self.y1, self.x2, self.y2]
        self.biome     = biome
        env.player_coordinates = self.center()
        
        # Image names and environment
        self.floor = floor
        self.walls = walls
        self.roof  = roof
        self.env   = env
        self.env.rooms.append(self)

        # Tiles
        self.tiles_list      = []
        self.walls_list      = []
        self.corners_list    = []
        self.noncorners_list = []
        
        # Properties
        self.hidden      = hidden
        self.delete      = False
        self.objects     = objects
        self.plan        = plan
        self.boundary    = boundary
        self.unbreakable = unbreakable
        
        # Create square room or text-based design
        if self.plan:       self.from_plan()
        elif self.boundary: self.from_boundary()
        else:               self.from_size()

    def from_size(self):
        
        # Assign tiles to room
        for x in range(self.x1, self.x2+1):
            for y in range(self.y1, self.y2+1):
                tile = self.env.map[x][y]
                
                # Apply properties to bulk
                tile.room   = self
                tile.hidden = self.hidden
                
                if self.roof: tile.img_names = self.roof
                else:         tile.img_names = self.floor
                tile.blocked = False

                # Change biome
                tile.biome = self.biome
                
                # Remove items and entities
                if not self.objects:
                    tile.item = None
                    if tile.entity:
                        self.env.entities.remove(tile.entity)
                        tile.entity = None
                
                # Handle tiles
                self.tiles_list.append(tile)
                
                # Handle walls
                if (x == self.x1) or (x == self.x2) or (y == self.y1) or (y == self.y2):
                    tile.img_names   = self.env.walls
                    tile.blocked     = True
                    tile.unbreakable = self.unbreakable
                    self.walls_list.append(tile)
                    
                    # Remove items and entities
                    tile.item = None
                    if tile.entity:
                        self.env.entities.remove(tile.entity)
                        tile.entity = None
                
                    # Handle corners
                    if   (x == self.x1) and (y == self.y1): self.corners_list.append(tile)
                    elif (x == self.x1) and (y == self.y2): self.corners_list.append(tile)
                    elif (x == self.x2) and (y == self.y1): self.corners_list.append(tile)
                    elif (x == self.x2) and (y == self.y2): self.corners_list.append(tile)
        
        self.noncorners_list = list(set(self.walls_list) - set(self.corners_list))

    def from_plan(self):
        try:
            self.from_plan_fr()
        
        except:
            try:
                self.x1 -= 5
                self.y1 -= 5
                self.from_plan_fr()
            except:
                self.x1 += 10
                self.y1 += 10
                self.from_plan_fr()

    def from_plan_fr(self):

        for y in range(len(self.plan)):
            layer = list(self.plan[y])
            for x in range(len(layer)):
                tile_x, tile_y = self.x1+x, self.y1+y
                tile = self.env.map[tile_x][tile_y]
                tile.item = None
                tile.entity = None
                
                # Place things indoors
                if layer[x] not in [' ', 'L']:
                    
                    ## Apply properties
                    tile.room   = self
                    tile.hidden = self.hidden
                    self.tiles_list.append(tile)

                    if self.roof: tile.img_names = self.roof
                    else:         tile.img_names = self.floor
                    tile.blocked = False

                    # Change biome
                    tile.biome = self.biome
                    
                    # Remove items and entities
                    if not self.objects:
                        tile.item = None
                        if tile.entity:
                            self.env.entities.remove(tile.entity)
                            tile.entity = None
                    
                    ## Handle symbols
                    # Place walls and doors
                    if self.plan[y][x] in ['-', '|']:
                        tile.img_names = self.env.walls
                        tile.blocked   = True
                        self.walls_list.append(tile)
                        if self.plan[y][x] != '|':
                            tile.unbreakable = self.unbreakable
                            
                            # Remove items and entities
                            tile.item = None
                            if tile.entity:
                                self.env.entities.remove(tile.entity)
                                tile.entity = None
                        
                        else:
                            
                            # Place door
                            tile.blocked = False
                            place_object(session.items.create_item('door'), [tile_x, tile_y], self.env)           
                    
                    # Place floor
                    if self.plan[y][x] == '.':
                        tile.blocked   = False
                    
                    # Place furniture
                    elif self.plan[y][x] == '=': place_object(session.items.create_item('red_bed'),         [tile_x, tile_y], self.env)                    
                    elif self.plan[y][x] == 'b': place_object(session.items.create_item('red_chair_left'),  [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == 'T': place_object(session.items.create_item('table'),           [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == 'd': place_object(session.items.create_item('red_chair_right'), [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == '[': place_object(session.items.create_item('shelf_left'),      [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == ']': place_object(session.items.create_item('shelf_right'),     [tile_x, tile_y], self.env)
                    
                    # Place items
                    elif self.plan[y][x] == 'g': place_object(session.items.create_item('jug_of_grapes'),   [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == 'c': place_object(session.items.create_item('jug_of_cement'),   [tile_x, tile_y], self.env)
                    
                # Place things outside
                else:
                    
                    # Place items
                    if self.plan[y][x] == 'L':   place_object(session.items.create_item('lights'),          [tile_x, tile_y], self.env)

    def from_boundary(self):
        
        # Import details
        walls = self.boundary['boundary tiles']
        boundary_coords = self.boundary['boundary coordinates']
        min_x, max_x = self.boundary['min x'], self.boundary['max x']
        min_y, max_y = self.boundary['min y'], self.boundary['max y']
        
        visited = set()
        queue = []
        
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
        for wall in walls:
            wall.room = self
            wall.hidden = self.hidden
            self.tiles_list.append(wall)
            wall.biome = self.biome
            self.walls_list.append(wall)
        for floor in floors:
            floor.room = self
            floor.hidden = self.hidden
            self.tiles_list.append(floor)
            floor.biome = self.biome
            if self.roof and (self.env.envs.player_obj.ent.tile not in self.tiles_list):
                floor.img_names = self.roof
            else:
                floor.img_names = self.floor

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

class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            env         : Environment object; owner of this tile

            number      : int; identifier for convenience
            room        : Room object
            entity      : Entity object; entity that occupies the tile
            item        : Item object; entity that occupies the tile
            
            img_names   : list of str; current image names
            walls       : list of str; default image name for wall
            floor       : list of str; default image name for floor
            roof        : list of str; default image name for roof
            timer       : int; fixed amount of time between animations
            
            X           : int; location of the tile in screen coordinate
            Y           : int; location of the tile in screen coordinate
            rand_X      : int; fixed amount of shift allowed in horizontal direction
            rand_Y      : int; fixed amount of shift allowed in vertical direction
            
            biome       : str; identifier for assigning biomes
            blocked     : bool; prevents items and entities from occupying the tile 
            hidden      : bool; prevents player from seeing the tile
            unbreakable : bool; prevents player from changing the tile
            placed      : bool; notifies custom placement via CatalogMenu """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def draw(self):
        
        # Set location
        X = self.X - self.env.camera.X
        Y = self.Y - self.env.camera.Y
        
        # Load tile
        if self.timer:
            if (time.time() // self.timer) % self.timer == 0: image = session.img.other_alt[self.img_names[0]][self.img_names[1]]
            else:                                             image = session.img.other[self.img_names[0]][self.img_names[1]]
        else:                                                 image = session.img.other[self.img_names[0]][self.img_names[1]]

        ## (Optional) Add shift effect
        if self.img_names[0] != 'roofs':
            if self.img_names[1] != 'wood':                   image = session.img.shift(image, [abs(self.rand_X), abs(self.rand_Y)])
                
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

        # Dark blue background
        self.sky = pygame.Surface((pyg.screen_width*10, pyg.screen_height*10), pygame.SRCALPHA)
        
        self.last_hour = time.localtime().tm_hour + 1
        self.last_min  = time.localtime().tm_min + 1

        self.lamp_list = []
        
        self.light_set = light_set
        self.cloudy = clouds
        self.clouds = []

    def run(self):
        self.sky.fill((0, 0, 0, 255))
        
        # Set day
        if (time.localtime().tm_hour + 1) != self.last_hour:
            self.last_hour = time.localtime().tm_hour + 1
            self.env.env_date = ((self.env.env_date+1) % 8) + 1
        
        # Set time of day
        if int(time.localtime().tm_min / 10) != self.last_min:
            self.last_min = int(time.localtime().tm_min / 10)
            self.env.env_time = (self.env.env_time + 1) % 8
        
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
            self.sky.set_alpha(self.light_set)

    def set_day_and_time(self, day=None, time=None, increment=False):
        
        # Set a specific day and time
        if not increment:
            if day is not None:  self.env.env_date = (day % 8) + 1
            if time is not None: self.env.env_time = time % 8
        
        # Move forwards in time by one step
        else: self.env.env_time = (self.env.env_time + 1) % 8

    def update_brightness(self):
        if self.env.env_time == 0:   alpha = 170 # 🌖
        elif self.env.env_time == 1: alpha = 85  # 🌗
        elif self.env.env_time == 2: alpha = 34  # 🌘
        elif self.env.env_time == 3: alpha = 0   # 🌑
        elif self.env.env_time == 4: alpha = 34  # 🌒
        elif self.env.env_time == 5: alpha = 85  # 🌓
        elif self.env.env_time == 6: alpha = 170 # 🌔
        elif self.env.env_time == 7: alpha = 255 # 🌕
        self.sky.set_alpha(alpha)

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
        data   = []
        
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
                                        image = session.img.shift(session.img.dict['concrete']['gray floor'], [int((x_char+y_char)*13)%32, int(abs(x_char-y_char)*10)%32])
                                        
                                        # Set transparency
                                        if char == '-':   image.set_alpha(64)
                                        elif char == '.': image.set_alpha(128)
                                        else:             image.set_alpha(96)
                                        
                                        # Set the corresponding map tile
                                        X = x * pyg.tile_width - self.env.camera.X
                                        Y = y * pyg.tile_height - self.env.camera.Y
                                        
                                        self.sky.blit(image, (X, Y))

        return data

    def update_lamps(self):
        pyg = session.pyg

        for lamp in self.lamp_list:
            
            # Center light on entity
            if lamp.owner and lamp.equipped:
                X = lamp.owner.X - self.env.camera.X
                Y = lamp.owner.Y - self.env.camera.Y
                failed = False
            
            # Or center light on item
            elif not lamp.owner:
                X = lamp.X - self.env.camera.X
                Y = lamp.Y - self.env.camera.Y
                failed = False
            
            else:  failed = True
            if not failed:
                
                # Render
                size   = lamp.effect.other
                width  = pyg.tile_width * size
                height = pyg.tile_height * size
                alpha  = 255//size
                left   = X - size*pyg.tile_width//2
                top    = Y - size*pyg.tile_height//2
                for i in range(size+1):
                    transparent_rect = pygame.Rect(
                        left   + (i+1) * 16,
                        top    + (i+1) * 16,
                        width  - i * 32,
                        height - i * 32)
                    self.sky.fill((0, 0, 0, 255-alpha*i), transparent_rect)

    def render(self):
        """ Creates a black overlay and cuts out regions for lighting.
            Light is shown for any of the following conditions.
                1. The object has self.lamp as an effect and is not owned by an entity.
                2. The object has self.lamp as an effect and is equipped by an entity. """

        # Check for lights
        self.update_lamps()

        # Check for clouds
        if self.cloudy: self.update_clouds()

        session.pyg.display_queue.append([self.sky, (0, 0)])

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
                    img_names    = biomes[i][1]
                    region_num   = i
            
            # Set tile image and properties
            tile.biome = biome
            
            # Check for image variants
            #if floor_name[-1].isdigit() and not random.randint(0, 1):
            #    try:    floor_name = floor_name[:-1] + str((int(floor_name[-1])+1))
            #    except: continue
            
            tile.img_names = img_names

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
                        item = session.items.create_item(item_selection[1])
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
                                obj = session.items.create_item(item)
                                session.items.pick_up(entity, obj)
                                if obj.equippable:
                                    session.items.toggle_equip(obj)
                                    if obj.effect:
                                        obj.effect.trigger = 'passive'
                        
                        entity.biome = env.map[x][y].biome
                        env.entities.append(entity)
                        place_object(entity, [x, y], env)

def place_object(obj, loc, env, names=None):
    """ Places a single object in the given location.

        Parameters
        ----------
        obj   : class object in [Tile, Item, Entity]; object to be placed
        loc   : list of int; tile coordinates
        env   : Environment object; desired location
        names : list of str; Image dictionary names """  
      
    pyg = session.pyg

    from environments import Tile
    from entities import Entity
    from items import Item

    # Place tile
    if type(obj) == Tile:
        env.map[loc[0]][loc[1]].img_names = names
        
        # Set properties
        if names[1] in session.img.biomes['sea']:
            env.map[loc[0]][loc[1]].biome   = 'water'
        elif names[0] in ['walls']:
            env.map[loc[0]][loc[1]].blocked = True
            env.map[loc[0]][loc[1]].item    = None
        else:
            env.map[loc[0]][loc[1]].blocked = False
    
    # Place item
    elif type(obj) == Item:
        obj.X    = loc[0] * pyg.tile_width
        obj.X0   = loc[0] * pyg.tile_width
        obj.Y    = loc[1] * pyg.tile_height
        obj.Y0   = loc[1] * pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].item    = obj
        env.map[loc[0]][loc[1]].blocked = obj.blocked
    
    # Place entity
    elif type(obj) == Entity:
        obj.X    = loc[0] * pyg.tile_width
        obj.X0   = loc[0] * pyg.tile_width
        obj.Y    = loc[1] * pyg.tile_height
        obj.Y0   = loc[1] * pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].entity = obj
        env.map[loc[0]][loc[1]].blocked = False
        env.entities.append(obj)

def create_text_room(width=5, height=5, doors=True):
    
    ## Initialize size
    if not width:  width = random.randint(5, 7)
    if not height: height = random.randint(5, 7)
    plan = [['' for x in range(width)] for y in range(height)]

    ## Create a floor
    last_left = 1
    last_right = width - 1
    for i in range(height):
        
        if not random.choice([0, 1]):
            for j in range(width):
                if last_left <= j <= last_right: plan[i][j] = '.'
                else:                            plan[i][j] = ' '
        
        left = random.randint(1, width//2-1)
        right = random.randint(width//2+1, width-1)
        if (abs(left - last_left) < 2) or (abs(right - last_right) < 2):
            for j in range(width):
                if left <= j <= right: plan[i][j] = '.'
                else:                  plan[i][j] = ' '
        
        elif random.choice([0, 1]):
            left = random.choice([left, last_left])
            right = random.choice([right, last_right])
            for j in range(width):
                if left <= j <= right: plan[i][j] = '.'
                else:                  plan[i][j] = ' '
        
        else:
            for j in range(width):
                if last_left <= j <= last_right: plan[i][j] = '.'
                else:                            plan[i][j] = ' '
        
        last_left  = left
        last_right = right

    ## Surround the floor with walls
    plan[0] = [' ' for _ in range(width)]
    plan[1] = [' ' for _ in range(width)]
    plan.append([' ' for _ in range(width)])
    for i in range(len(plan)): plan[i].append(' ')

    for i in range(len(plan)):
        for j in range(len(plan[0])):
            for key in plan[i][j]:
                if key == '.':
                    if plan[i-1][j-1] != key: plan[i-1][j-1] = '-'
                    if plan[i-1][j] != key:   plan[i-1][j]   = '-'
                    if plan[i-1][j+1] != key: plan[i-1][j+1] = '-'
                    if plan[i][j-1] != key:   plan[i][j-1]   = '-'
                    if plan[i][j+1] != key:   plan[i][j+1]   = '-'
                    if plan[i+1][j-1] != key: plan[i+1][j-1] = '-'
                    if plan[i+1][j] != key:   plan[i+1][j]   = '-'
                    if plan[i+1][j+1] != key: plan[i+1][j+1] = '-'

    ## Place a door or two
    if doors:
        plan[0] = [' ' for _ in range(width)]
        plan.append([' ' for _ in range(width)])
        for i in range(len(plan)): plan[i].append(' ')

        placed = False
        for i in range(len(plan)):
            for j in range(len(plan[0])):
                if not placed:
                    if plan[i][j] == '-':
                        vertical = [
                            plan[i-1][j],
                            plan[i+1][j]]
                        horizontal = [
                            plan[i][j-1],
                            plan[i][j+1]]
                        if ('-' in vertical) and ('-' in horizontal):
                            placed = False
                        elif (' ' not in vertical) and (' ' not in horizontal):
                            placed = False
                        else:
                            if not random.randint(0, 10):
                                plan[i][j] = '|'
                                if random.randint(0, 1): placed = True
                    else: placed = False
        if not placed:
            for i in range(len(plan)):
                for j in range(len(plan[0])):
                    if not placed:
                        if plan[i][j] == '-':
                            vertical = [
                                plan[i-1][j],
                                plan[i+1][j]]
                            horizontal = [
                                plan[i][j-1],
                                plan[i][j+1]]
                            if ('-' in vertical) and ('-' in horizontal):
                                placed = False
                            elif (' ' not in vertical) and (' ' not in horizontal):
                                placed = False
                            else:
                                if not random.randint(0, 10):
                                    plan[i][j] = '|'
                                    placed = True
                        else: placed = False

    ## Place furniture and decorations
    def neighbors(i, j):
        neighbors = [
            plan[i-1][j-1], plan[i-1][j], plan[i-1][j+1],
            plan[i][j-1],                 plan[i][j+1], 
            plan[i+1][j-1], plan[i+1][j], plan[i+1][j+1]]
        return neighbors
    
    ### Place one of each of these
    bed    = False
    dining = False
    shelf  = False
    lights = False
    
    # Look through tiles
    for i in range(len(plan)):
        for j in range(len(plan[0])):
            if random.randint(0, 1):
                
                # Look for floors tiles indoors
                if (plan[i][j] == '.') and ('|' not in neighbors(i, j)):
                    if (plan[i][j+1] == '.') and ('|' not in neighbors(i, j+1)):
                        
                        # Three open spaces
                        if (plan[i][j+2] == '.') and ('|' not in neighbors(i, j+2)):
                            
                            # Table and chairs
                            if not dining and not random.randint(0, 5):
                                plan[i][j]          = 'b'
                                plan[i][j+1]        = 'T'
                                plan[i][j+2]        = 'd'
                                dining = True
                        
                        # Two open spaces
                        else:
                            
                            # Bed
                            if not bed and not random.randint(0, 3):
                                plan[i][j]          = '='
                                if not random.randint(0, 2): bed = True
                            
                            # Shelf
                            else:
                                if (not shelf) and (plan[i-1][j] == '-') and (plan[i-1][j+1] == '-'):
                                    plan[i][j]      = '['
                                    plan[i][j+1]    = ']'
                                    shelf = True
                
                # Look outdoors
                elif plan[i][j] == ' ':
                    try:
                        if '|' not in neighbors(i, j):
                            
                            # Lights
                            if not lights:
                                plan[i][j]              = 'L'
                                lights = True
                    
                    except: continue
    
    ## Wrap things up
    export = []
    for row in plan:
        export.append("".join(row))
    return export

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
        place_object(session.items.create_item('door'), loc, room.env)
        room.env.map[loc[0]][loc[1]].blocked   = False
        room.env.map[loc[0]][loc[1]].img_names = room.floor
        try:    room.walls_list.remove(room.env.map[loc[0]][loc[1]])
        except: pass
        
        ## Create wide entryway and clear items
        if not random.randint(0, 1):
            for i in range(3):
                for j in range(3):
                    try:
                        
                        # Make floors
                        if list(room.env.map[x][y].img_names) != list(room.walls):
                            x, y = loc[0]+i-1, loc[1]+j-1
                            
                            # Add roof
                            if room.env.map[x][y] in room.tiles_list:
                                room.env.map[x][y].roof      = room.roof
                                room.env.map[x][y].img_names = room.roof
                            else:
                                room.env.map[x][y].img_names = room.floor
                            
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
                            
                            # Make floors
                            if list(room.env.map[loc[0]+i-1][loc[1]+j-1].img_names) != list(room.walls):
                                x, y = loc[0]+i-1, loc[1]+j-1
                                
                                # Add roof
                                if room.env.map[x][y] in room.tiles_list:
                                    room.env.map[x][y].roof      = room.roof
                                    room.env.map[x][y].img_names = room.roof
                                else:
                                    room.env.map[x][y].img_names = room.floor
                                
                                # Clear items, but keep doors
                                if ((i-1) or (j-1)):
                                    room.env.map[x][y].item    = None
                                    room.env.map[x][y].blocked = False
                                    
                                room.env.map[x][y].biome == 'city'
                        
                        except:
                            continue

########################################################################################################################################################