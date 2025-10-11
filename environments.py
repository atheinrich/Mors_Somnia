########################################################################################################################################################
# Environment creation and management
#
# Everything about environments should occur here, and all data is saved.
# - All environment data for a given save file
# - Details for rendering tiles
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import time
import copy
import random
import pygame

## Modules
import session
from main import Camera
from items_entities import create_item, create_entity, create_NPC
from mechanics import place_object, place_objects, create_text_room
from quests import Quest, Bloodkin, FriendlyFaces
from utilities import get_vicinity

########################################################################################################################################################
# Classes
class Environments:

    def __init__(self):
        """ Holds environments for user. """

        # Parameters
        self.room_max_size = 10
        self.room_min_size = 4
        self.max_rooms     = 3

    def build_garden(self):
        """ Generates the overworld environment. """
        
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
            hidden     = False)
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': 0,
            'clouds':    False}
        env.weather = Weather(light_set=0, clouds=False)
        
        ## Generate biomes
        biomes = [['forest', ['floors', 'grass4']]]
        voronoi_biomes(env, biomes)
        
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
            floor   = session.player_obj.envs['garden'].floors,
            walls   = session.player_obj.envs['garden'].walls,
            roof    = None)
        x, y = new_room.center()[0], new_room.center()[1]
        
        # Generate items and entities
        items    = [['forest', 'tree',       10]]
        entities = [['forest', 'red radish', 50, [None]]]
        place_objects(env, items, entities)
        
        # Place player in first room
        env.player_coordinates = [x, y]
        env.map[x][y].item     = None
        session.player_obj.envs['garden'].entity = session.player_obj.ent
        session.player_obj.ent.tile = session.player_obj.envs['garden'].map[x][y]
        session.player_obj.envs['garden'].center = new_room.center()
        
        return env

    def build_womb(self):
        """ Generates the overworld environment. """
        
        ## Initialize environment
        env = Environment(
            name       = 'womb',
            lvl_num    = 0,
            size       = 1,
            soundtrack = ['menu'],
            img_names  = ['floors', 'dark green'],
            floors     = ['floors', 'dark green'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'],
            blocked    = False,
            hidden     = True)
        session.player_obj.envs['womb'] = env
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': 0,
            'clouds':    False}
        env.weather = Weather(light_set=0, clouds=False)
        
        ## Generate biomes
        biomes = [['forest', ['floors', 'grass4']]]
        voronoi_biomes(env, biomes)
        
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
            floor   = session.player_obj.envs['womb'].floors,
            walls   = session.player_obj.envs['womb'].walls,
            roof    = None)
        x, y = new_room.center()[0], new_room.center()[1]
        
        # Place player in first room
        env.player_coordinates = [x, y]
        env.map[x][y].item     = None
        env.entity = session.player_obj.ent
        session.player_obj.ent.tile = env.map[x][y]
        env.center = new_room.center()
        
        return env

    def build_home(self):
        """ Generates player's home. """

        ## Initialize environment
        env = Environment(
            name       = 'home',
            lvl_num    = 0,
            size       = 5,
            soundtrack = ['home'],
            img_names  = ['walls', 'gray'],
            floors     = ['floors', 'green'],
            walls      = ['walls', 'gray'],
            roofs      = ['roofs', 'tiled'])
        session.player_obj.envs['home'] = env
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = True
        env.camera.zoom_in(custom=1)
        center = [14, 14]
        
        # Set weather
        env.weather_backup = {
            'light_set': 32,
            'clouds':    False}
        env.weather = Weather(light_set=32)
        
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
        
        # Hidden objects
        x, y = center[0]+10, center[1]+9
        item = create_item('blood sword')
        place_object(item, [x, y], env)
        x, y = center[0]+5, center[1]+10
        item = create_item('iron shield')
        place_object(item, [x, y], env)
        
        # Bug fix
        x, y = 0, 0
        item = create_item('scroll of fireball')
        place_object(item, [x, y], env)
        
        # Door
        x, y = center[0]-3, center[1]+1
        item = create_item('door')
        item.name = 'overworld'
        place_object(item, [x, y], env)
        env.map[x][y].blocked = False
        env.map[x][y].unbreakable = False
        
        # Friend
        x, y = center[0]+1, center[1]
        ent = create_entity('friend')
        place_object(ent, [x, y], env)
        ent.dialogue = "Walk into something to interact with it, or press Enter (↲) if you're above it."
        session.player_obj.ent.questlines = {}
        session.player_obj.ent.questlines['Bloodkin'] = Bloodkin()
        ent.quest    = Quest(
            name     = "Making a friend",
            notes    = ["I wonder who this is. Maybe I should say hello."],
            tasks    = ["☐ Say hello to the creature.",
                        "☐ Get to know them."],
            category = 'Side',
            function = session.player_obj.ent.questlines['Bloodkin'].making_a_friend)
        ent.quest.content = ent.quest.notes + ent.quest.tasks
        session.player_obj.ent.questlog['Making a friend'] = ent.quest
        
        # Initial position
        env.player_coordinates = env.center
        
        return env

    def build_dungeon_level(self, lvl_num=0):
        """ Generates the overworld environment. """
        
        # Initialize environment
        if lvl_num:                               lvl_num = lvl_num
        elif not session.player_obj.envs['dungeon']: lvl_num = 1
        else:                                     lvl_num = 1 + session.player_obj.envs['dungeon'][-1].lvl_num
        
        env = Environment(
            name       = 'dungeon',
            lvl_num    = lvl_num,
            size       = 2 * (1 + lvl_num//3),
            soundtrack = [f'dungeon {lvl_num}'],
            img_names  = ['walls', 'gray'],
            floors     = ['floors', 'dark green'],
            walls      = ['walls', 'gray'],
            roofs      = None,
            blocked    = True,
            hidden     = True)
        
        # Set weather
        env.weather_backup = {
            'light_set': None,
            'clouds':    False}
        env.weather = Weather(clouds=False)
        
        session.player_obj.envs['dungeon'].append(env)
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)

        # Generate biomes
        biomes = [['dungeon', ['walls', 'gray']]]
        voronoi_biomes(env, biomes)
        
        # Construct rooms
        rooms, room_counter, counter = [], 0, 0
        num_rooms = int(self.max_rooms * env.lvl_num) + 2
        for i in range(num_rooms):
            
            # Construct room
            width    = random.randint(self.room_min_size, self.room_max_size)
            height   = random.randint(self.room_min_size, self.room_max_size)
            x        = random.randint(0, len(env.map)    - width  - 1)
            y        = random.randint(0, len(env.map[0]) - height - 1)
            
            floor = random.choice([
                ['floors', 'dark green'],
                ['floors', 'dark green'],
                ['floors', 'green']])
            
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
            ['land', 'eye',            15,    ['eye']],
            ['land', 'red radish',     1000,  [None]],
            ['land', 'round1',         30,    [None]]]
        place_objects(env, items, entities)
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.entity = session.player_obj.ent
        env.center = new_room.center()
        session.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-2].center()
        stairs = create_item('door')
        stairs.name = 'dungeon'
        place_object(stairs, [x, y], session.player_obj.envs['dungeon'][-1])

    def build_hallucination_level(self):
        """ Generates the overworld environment. """
        
        ## Initialize environment
        if not session.player_obj.envs['hallucination']: lvl_num = 1
        else:                                    lvl_num = 1 + session.player_obj.envs['hallucination'][-1].lvl_num
        env = Environment(
            name       = 'hallucination',
            lvl_num    = lvl_num,
            size       = 3,
            soundtrack = [f'hallucination {lvl_num}'],
            img_names  = ['walls',  'gold'],
            floors     = ['floors', 'green'],
            walls      = ['walls',  'gold'],
            roofs      = None,
            blocked    = True,
            hidden     = True)
        
        # Set weather
        env.weather_backup = {
            'light_set': 32,
            'clouds':    False}
        env.weather = Weather(light_set=32, clouds=False)

        ## Generate biomes
        biomes = [
            ['any', ['walls', 'gold']],
            ['any', ['walls', 'gold']],
            ['any', ['walls', 'gold']],
            ['any', ['walls', 'gold']]]
        voronoi_biomes(env, biomes)
        
        session.player_obj.envs['hallucination'].append(env)
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        # Construct rooms
        rooms, room_counter, counter = [], 0, 0
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
        rooms                 = []
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
                    floor  = ['floors', 'dark green'],
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
        session.player_obj.ent.img_names_backup = session.player_obj.ent.img_names
        session.player_obj.ent.img_names = ['tentacles', 'front']
        
        # Place player in first room
        (x, y) = env.rooms[0].center()
        env.player_coordinates = [x, y]
        env.entity = session.player_obj.ent
        env.center = new_room.center()
        session.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-2].center()
        stairs = create_item('portal')
        stairs.name = 'hallucination'
        place_object(stairs, [x, y], env)

    def build_overworld(self):
        """ Generates the overworld environment. """

        ## Initialize environment
        env = Environment(
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
            hidden     = False)
        session.player_obj.envs['overworld'] = env
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': None,
            'clouds':    True}
        env.weather = Weather(clouds=True)
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
        
        ## Construct rooms
        num_rooms             = 20
        rooms                 = []
        room_counter, counter = 0, 0
        center                = session.player_obj.envs['overworld'].center
        (x_1, y_1)            = center
        x_2                   = lambda width:  len(session.player_obj.envs['overworld'].map)    - width  - 1
        y_2                   = lambda height: len(session.player_obj.envs['overworld'].map[0]) - height - 1
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
                    floor  = ['floors', 'dark green'],
                    walls  = session.player_obj.envs['overworld'].walls,
                    roof   = session.player_obj.envs['overworld'].roofs,
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
                    floor   = ['floors', 'dark green'],
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
                item = create_item('door')
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
        
        env.center             = [door_x, door_y]
        env.player_coordinates = [door_x, door_y]
        env.entity             = session.player_obj.ent
        session.player_obj.ent.tile    = env.map[door_x][door_y]
        
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
            floor   = ['floors', 'red'],
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
        
        ## Place NPCs
        bools = lambda room, i: [
            env.map[room.center()[0]+i][room.center()[1]+i].item,
            env.map[room.center()[0]+i][room.center()[1]+i].entity]
        
        # Set named characters to spawn
        for name in ['Kyrio', 'Kapno', 'Erasti', 'Merci', 'Oxi', 'Aya', 'Zung', 'Lilao']:
            
            # Create NPC if needed
            if name not in session.player_obj.ents.keys(): session.player_obj.ents[name] = create_NPC(name)
            
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
            place_object(session.player_obj.ents[name], (x, y), env)
        
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
        
        session.player_obj.ent.questlines['Friendly Faces'] = FriendlyFaces()
        session.player_obj.ent.questlines['Friendly Faces'].making_an_introduction()

    def build_bitworld(self):
        """ Generates the bitworld environment. """

        ## Initialize environment
        env = Environment(
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
            hidden     = False)
        session.player_obj.envs['bitworld'] = env
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)
        
        # Set weather
        env.weather_backup = {
            'light_set': None,
            'clouds':    False}
        env.weather = Weather(clouds=False)

        ## Generate biomes
        biomes = [
            ['forest', ['floors', 'grass2']]]
        voronoi_biomes(env, biomes)
        
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
        
        ## Construct rooms
        num_rooms             = 20
        rooms                 = []
        room_counter, counter = 0, 0
        center                = session.player_obj.envs['bitworld'].center
        (x_1, y_1)            = center
        x_2                   = lambda width:  len(session.player_obj.envs['bitworld'].map)    - width  - 1
        y_2                   = lambda height: len(session.player_obj.envs['bitworld'].map[0]) - height - 1
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
                    name   = 'bitworld room',
                    env    = env,
                    x1     = x,
                    y1     = y,
                    width  = width,
                    height = height,
                    biome   = 'city',
                    hidden = False,
                    objects = False,
                    floor  = ['floors', 'dark green'],
                    walls  = session.player_obj.envs['bitworld'].walls,
                    roof   = session.player_obj.envs['bitworld'].roofs,
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
            env     = session.player_obj.envs['bitworld'],
            x1      = session.player_obj.envs['bitworld'].center[0],
            y1      = session.player_obj.envs['bitworld'].center[1],
            width   = self.room_max_size,
            height  = self.room_max_size,
            biome   = 'any',
            hidden  = False,
            objects = False,
            floor   = ['floors', 'dark green'],
            walls   = session.player_obj.envs['bitworld'].walls,
            roof    = session.player_obj.envs['bitworld'].roofs,
            plan = ['  -----     ',
                    ' --...----- ',
                    ' -........--',
                    ' -.........-',
                    '--.........|',
                    '-.........--',
                    '--.....---- ',
                    ' --...--    ',
                    '  -----     '])
        env.player_coordinates = session.player_obj.envs['bitworld'].center # [0, 10]
        session.player_obj.envs['bitworld'].entity = session.player_obj.ent
        session.player_obj.ent.tile                 = session.player_obj.envs['bitworld'].map[0][10]
        
        # Door
        x, y = center[0]+1, center[1]+5
        item = create_item('door')
        item.name = 'home'
        place_object(item, [x, y], session.player_obj.envs['bitworld'])
        session.player_obj.envs['bitworld'].map[x][y].blocked = False
        session.player_obj.envs['bitworld'].map[x][y].unbreakable = False
        
        ## Create church
        main_room = Room(
            name    = 'church',
            env     = session.player_obj.envs['bitworld'],
            x1      = 20,
            y1      = 20,
            width   = self.room_max_size,
            height  = self.room_max_size,
            biome   = 'any',
            hidden  = False,
            objects = False,
            floor   = ['floors', 'red'],
            walls   = session.player_obj.envs['bitworld'].walls,
            roof    = session.player_obj.envs['bitworld'].roofs,
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
        
        ## Place NPCs
        bools = lambda room, i: [
            env.map[room.center()[0]+i][room.center()[1]+i].item,
            env.map[room.center()[0]+i][room.center()[1]+i].entity]
        
        # Set number of random characters
        for _ in range(15):
            
            # Create entity
            ent = create_NPC('random')
            
            # Select room not occupied by player
            room = random.choice(session.player_obj.envs['bitworld'].rooms)
            while room == session.player_obj.envs['bitworld'].rooms[-1]:
                room = random.choice(session.player_obj.envs['bitworld'].rooms)
            
            # Select spawn location
            for i in range(3):
                occupied = bools(room, i-1)
                if occupied[0] == occupied[1]:
                    (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
            
            # Spawn entity
            place_object(ent, (x, y), env)

    def build_cave_level(self):
        """ Generates a cave environment. """
        
        # Initialize environment
        if not session.player_obj.envs['cave']: lvl_num = 1
        else:                           lvl_num = 1 + session.player_obj.envs['cave'][-1].lvl_num
        
        env = Environment(
            name       = 'cave',
            lvl_num    = lvl_num,
            size       = 1,
            soundtrack = [f'dungeon {lvl_num}'],
            img_names  = ['walls',  'dark red'],
            floors     = ['floors', 'dirt1'],
            walls      = ['walls',  'dark red'],
            roofs      = None,
            blocked    = True,
            hidden     = True)
        
        # Set weather
        env.weather_backup = {
            'light_set': 16,
            'clouds':    False}
        env.weather = Weather(light_set=16)
        
        session.player_obj.envs['cave'].append(env)
        env.camera = Camera(session.player_obj.ent)
        env.camera.fixed = False
        env.camera.zoom_in(custom=1)

        # Generate biomes
        biomes = [['dungeon', ['walls', 'dark red']]]
        voronoi_biomes(env, biomes)
        
        # Construct rooms
        rooms, room_counter, counter = [], 0, 0
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
        env.entity = session.player_obj.ent
        env.center = new_room.center()
        session.player_obj.ent.tile = env.map[x][y]
        
        # Generate stairs in the last room
        (x, y) = env.rooms[-1].center()
        stairs = create_item('cave')
        stairs.img_names = ['floors', 'dirt2']
        place_object(stairs, [x, y], session.player_obj.envs['cave'][-1])

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """
    
    def __init__(self, envs, name, size, soundtrack, lvl_num, walls, floors, roofs, blocked=True, hidden=True, img_names=['', '']):
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
        
        # Global mechanisms
        self.envs = envs

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
        X_range  = [0, self.size * session.pyg.screen_width]
        Y_range  = [0, self.size * session.pyg.screen_height]
        number    = 0
        for X in range(X_range[0], X_range[1]+1, session.pyg.tile_width):
            row = [] 
            for Y in range(Y_range[0], Y_range[1]+1, session.pyg.tile_height):
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
                        rand_X      = random.randint(-session.pyg.tile_width, session.pyg.tile_width),
                        rand_Y      = random.randint(-session.pyg.tile_height, session.pyg.tile_height),
                        
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
                        rand_X      = random.randint(-session.pyg.tile_width, session.pyg.tile_width),
                        rand_Y      = random.randint(-session.pyg.tile_height, session.pyg.tile_height),
                        
                        biome       = None,
                        blocked     = blocked,
                        hidden      = hidden,
                        unbreakable = False,
                        placed      = False)
                
                row.append(tile)
            self.map.append(row)
        
        # Other
        self.entities           = []
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
                env      = session.player_obj.ent.env,
                x1       = min_x,
                y1       = min_y,
                width    = int(max_x - min_x),
                height   = int(max_y - min_y),
                biome    = 'city',
                hidden   = False,
                objects  = True,
                floor    = ['floors', 'wood'],
                walls    = obj.img_names,
                roof     = session.player_obj.ent.env.roofs,
                boundary = boundary)

    def combine_rooms(self):
        """ Removes walls of intersecting rooms, then recombines them into a single room. """
    
        # Sort through each room
        cache = []
        rooms_copy = copy.deepcopy(self.rooms)
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
        
        rooms_copy = copy.deepcopy(self.rooms)
        counter = 0
        for i in range(len(rooms_copy)):
            if self.rooms[i-counter].delete: self.rooms.remove(self.rooms[i-counter])
            counter += 1

    def create_tunnel(self, x, y):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        
        self.map[x][y].img_names = self.floors

    def __getstate__(self):
        state = self.__dict__.copy()
        if "weather" in state:
            del state["weather"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.weather = Weather(
            light_set = self.weather_backup['light_set'],
            clouds    = self.weather_backup['clouds'])

class Room:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, name, env, x1, y1, width, height, hidden, floor, walls, roof, objects, biome, plan=None, boundary=None):
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
        self.hidden   = hidden
        self.delete   = False
        self.objects  = objects
        self.plan     = plan
        self.boundary = boundary
        
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
                    tile.img_names = self.env.walls
                    tile.blocked   = True
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
                            
                            # Remove items and entities
                            tile.item = None
                            if tile.entity:
                                self.env.entities.remove(tile.entity)
                                tile.entity = None
                        
                        else:
                            
                            # Place door
                            tile.blocked = False
                            place_object(create_item('door'), [tile_x, tile_y], self.env)           
                    
                    # Place floor
                    if self.plan[y][x] == '.':
                        tile.blocked   = False
                    
                    # Place furniture
                    elif self.plan[y][x] == '=': place_object(create_item('red bed'),         [tile_x, tile_y], self.env)                    
                    elif self.plan[y][x] == 'b': place_object(create_item('red chair left'),  [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == 'T': place_object(create_item('table'),           [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == 'd': place_object(create_item('red chair right'), [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == '[': place_object(create_item('shelf left'),      [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == ']': place_object(create_item('shelf right'),     [tile_x, tile_y], self.env)
                    
                    # Place items
                    elif self.plan[y][x] == 'g': place_object(create_item('jug of grapes'),   [tile_x, tile_y], self.env)
                    elif self.plan[y][x] == 'c': place_object(create_item('jug of cement'),   [tile_x, tile_y], self.env)
                    
                # Place things outside
                else:
                    
                    # Place items
                    if self.plan[y][x] == 'L':   place_object(create_item('lights'),          [tile_x, tile_y], self.env)

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
            if not (0 <= x < len(session.player_obj.ent.env.map) and 0 <= y < len(session.player_obj.ent.env.map[0])):
                continue
            
            tile = session.player_obj.ent.env.map[x][y]
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
                    floors.append(session.player_obj.ent.env.map[x][y])
        
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
            if self.roof and (session.player_obj.ent.tile not in self.tiles_list):
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
            placed      : bool; notifies custom placement via Catalog """
        
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
        if self.biome in session.img.biomes['sea']:     image = session.img.static(image, offset=20, rate=100)
        
        # Return result for rendering
        return image, (X, Y)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __eq__(self, other):
        return self.X == other.Y and self.Y == other.Y

    def __hash__(self):
        return hash((self.X, self.Y))

class Weather:

    def __init__(self, env, light_set=None, clouds=True):
        
        # Global mechanisms
        self.env = env

        # Dark blue background
        self.overlay = pygame.Surface((session.pyg.screen_width * 10, session.pyg.screen_height * 10), pygame.SRCALPHA)
        
        self.last_hour = time.localtime().tm_hour + 1
        self.last_min  = time.localtime().tm_min + 1

        self.lamp_list = []
        
        self.light_set = light_set
        self.cloudy = clouds
        self.clouds = []

    def run(self):
        
        # Set day
        if (time.localtime().tm_hour + 1) != self.last_hour:
            self.last_hour = time.localtime().tm_hour + 1
            session.player_obj.ent.env.env_date = ((session.player_obj.ent.env.env_date+1) % 8) + 1
        
        # Set time of day
        if int(time.localtime().tm_min / 10) != self.last_min:
            self.last_min = int(time.localtime().tm_min / 10)
            session.player_obj.ent.env.env_time = (session.player_obj.ent.env.env_time + 1) % 8
        
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
            self.overlay.set_alpha(self.light_set)

    def set_day_and_time(self, day=None, time=None, increment=False):
        
        # Set a specific day and time
        if not increment:
            if day is not None:  session.player_obj.ent.env.env_date = (day % 8) + 1
            if time is not None: session.player_obj.ent.env.env_time = time % 8
        
        # Move forwards in time by one step
        else: session.player_obj.ent.env.env_time = (session.player_obj.ent.env.env_time + 1) % 8

    def update_brightness(self):
        if session.player_obj.ent.env.env_time == 0:   alpha = 170 # 🌖
        elif session.player_obj.ent.env.env_time == 1: alpha = 85  # 🌗
        elif session.player_obj.ent.env.env_time == 2: alpha = 34  # 🌘
        elif session.player_obj.ent.env.env_time == 3: alpha = 0   # 🌑
        elif session.player_obj.ent.env.env_time == 4: alpha = 34  # 🌒
        elif session.player_obj.ent.env.env_time == 5: alpha = 85  # 🌓
        elif session.player_obj.ent.env.env_time == 6: alpha = 170 # 🌔
        elif session.player_obj.ent.env.env_time == 7: alpha = 255 # 🌕
        self.overlay.set_alpha(alpha)

    def create_cloud(self):
        
        # Set direction of travel
        env       = session.player_obj.ent.env
        x_range   = [0, (env.size * session.pyg.screen_width) // session.pyg.tile_width]
        y_range   = [0, (env.size * session.pyg.screen_height) // session.pyg.tile_height]
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
        camera = self.env.camera
        data = []
        
        # Draw visible tiles
        for y in range(int(camera.Y/32), int(camera.bottom/session.pyg.tile_height + 1)):
            for x in range(int(camera.X/32), int(camera.right/session.pyg.tile_width + 1)):
                try:    tile = session.player_obj.ent.env.map[x][y]
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
                                        X = x * session.pyg.tile_width - self.env.camera.X
                                        Y = y * session.pyg.tile_height - self.env.camera.Y
                                        
                                        data.append(image, (X, Y))

        return data

    def update_lamps(self):
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
                width  = session.pyg.tile_width * size
                height = session.pyg.tile_height * size
                alpha  = 255//size
                left   = X - size*session.pyg.tile_width//2
                top    = Y - size*session.pyg.tile_height//2
                for i in range(size+1):
                    transparent_rect = pygame.Rect(
                        left   + (i+1) * 16,
                        top    + (i+1) * 16,
                        width  - i * 32,
                        height - i * 32)
                    self.overlay.fill((0, 0, 0, 255-alpha*i), transparent_rect)
            
        return [self.overlay, (0, 0)]

    def render(self):
        """ Creates a black overlay and cuts out regions for lighting.
            Light is shown for any of the following conditions.
                1. The object has self.lamp as an effect and is not owned by an entity.
                2. The object has self.lamp as an effect and is equipped by an entity. """
        
        # Set background color
        self.overlay.fill((0, 0, 0))
        
        # Check for lights
        data = self.update_lamps()
        
        # Check for clouds
        if self.cloudy: data.extend(self.update_clouds())

        return data

########################################################################################################################################################
# Tools
def voronoi_biomes(env, biomes):
    """ Partitions environment map into random regions. Not yet generalized for arbitrary applications.
    
        Parameters
        ----------
        biomes : list of dictionaries of objects
                 [<wall/floor name>, [<item name 1>, ...]], {...}] """
    
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
                region_center = [seeds_with_ids[i][1][0] * session.pyg.tile_width, seeds_with_ids[i][1][1] * session.pyg.tile_height]
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

########################################################################################################################################################