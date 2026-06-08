########################################################################################################################################################
# Environment design
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import copy

## Local
import session
from environments import Environment, Camera, Area, Room, Weather
from environments import place_object, place_objects, voronoi_biomes, create_text_room
from entities import create_entity, create_NPC
from items import create_item

########################################################################################################################################################
# Utility
_registry = {}
def register(id):
    def decorator(fn):
        _registry[id] = fn
        return fn
    return decorator

def _init_env(**kwargs):
    """ Creates instances to initialize basic environment. """

    # Environment instance
    area = kwargs.get('area')
    env  = Environment(
        envs          = area.envs,
        name          = kwargs.get('name'),
        lvl_num       = kwargs.get('lvl_num'),
        size          = kwargs.get('size'),
        soundtrack    = kwargs.get('soundtrack'),
        img_IDs       = kwargs.get('img_IDs'),
        floor_img_IDs = kwargs.get('floor_img_IDs'),
        wall_img_IDs  = kwargs.get('wall_img_IDs'),
        roof_img_IDs  = kwargs.get('roof_img_IDs'),
        blocked       = kwargs.get('blocked'),
        hidden        = kwargs.get('hidden'),
        area          = area)
    
    # Camera instance
    env.camera       = Camera(kwargs.get('area').envs.player_obj.ent)
    env.camera.fixed = kwargs.get('camera_fixed')
    env.camera.zoom_in(custom=1)
    
    # Weather instance
    clouds      = kwargs.get('clouds')
    env.weather = Weather(env, light_set=kwargs.get('light_set'), clouds=clouds)
    if clouds:
        for _ in range(random.randint(0, 10)):
            env.weather.create_cloud()
    
    # Biomes
    biomes = kwargs.get('biomes', None)
    if biomes is not None:
        voronoi_biomes(env, biomes)
    
    return env

room_max_size = 10
room_min_size = 4

########################################################################################################################################################
# Underworld
@register("gard")
def build_garden(area, lvl_num=0):
    """ Generates the overworld environment. """
    
    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'garden'
    size          = 1
    soundtrack    = ['menu']
    img_IDs       = ['floors', 'grass4']
    floor_img_IDs = ['floors', 'grass4']
    wall_img_IDs  = ['walls', 'gray']
    roof_img_IDs  = ['roofs', 'tiled']
    blocked       = False
    hidden        = False

    ## Camera instance
    camera_fixed  = True
    
    ## Weather instance
    light_set     = 0
    clouds        = False
    
    ## Biomes
    biomes        = [['forest', ['floors', 'grass4']]]
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
    ###############################################################
    # Construct room
    new_room = Room(
        name          = 'garden',
        env           = env,
        biome         = 'forest',

        floor_img_IDs = env.floor_img_IDs,
        wall_img_IDs  = env.wall_img_IDs,
        roof_img_IDs  = None,

        hidden        = False,
        unbreakable   = True,
        objects       = False,

        x1            = 0,
        y1            = 0,
        width         = 20,
        height        = 15)
    
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
    area.envs.player_obj.ent.tile = env.map[x][y]
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
    
    session.stats_obj.pet_moods = {
        "happiness": 5,
        "sadness":   0,
        "anger":     0,
        "boredom":   0,
        "lethargy":  0,
        "confusion": 0}

    return env

@register("womb")
def build_womb(area, lvl_num=0):
    """ Generates the overworld environment. """

    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'womb'
    size          = 1
    soundtrack    = ['menu']
    img_IDs       = ['floors', 'dark_green_floor']
    floor_img_IDs = ['floors', 'dark_green_floor']
    wall_img_IDs  = ['walls', 'gray']
    roof_img_IDs  = ['roofs', 'tiled']
    blocked       = False
    hidden        = True

    ## Camera instance
    camera_fixed  = True
    
    ## Weather instance
    light_set     = 0
    clouds        = False
    
    ## Biomes
    biomes        = [['forest', ['floors', 'grass4']]]
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
    ###############################################################
    # Construct rooms
    new_room = Room(
        name          = 'womb',
        env           = env,
        biome         = 'forest',

        floor_img_IDs = env.floor_img_IDs,
        wall_img_IDs  = env.wall_img_IDs,
        roof_img_IDs  = None,

        hidden        = True,
        objects       = False,

        x1            = 12,
        y1            = 5,
        width         = 5,
        height        = 5)
    x, y = new_room.center()[0], new_room.center()[1]
    env.center = new_room.center()
    
    return env

# Overworld
@register("home")
def build_home(area, lvl_num=0):
    """ Generates player's home. """

    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'home'
    size          = 5
    soundtrack    = ['overworld_1']
    img_IDs       = ['floors', 'gray']
    floor_img_IDs = ['floors', 'green_floor']
    wall_img_IDs  = ['walls', 'gray']
    roof_img_IDs  = ['roofs', 'tiled']
    blocked       = True
    hidden        = True

    ## Camera instance
    camera_fixed  = False
    
    ## Weather instance
    light_set     = 32
    clouds        = False
    
    ## Biomes
    biomes        = None
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
    ###############################################################
    ## Construct rooms
    center = [14, 14]
    main_room = Room(
        name          = 'home room',
        env           = env,
        biome         = 'any',

        floor_img_IDs = env.floor_img_IDs,
        wall_img_IDs  = env.wall_img_IDs,
        roof_img_IDs  = None,

        hidden        = False,
        objects       = False,

        x1            = center[0] - 4,
        y1            = center[1] - 4,
        plan          = [
            '  -----     ',
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
        name          = 'secret room',
        env           = env,
        biome         = 'any',

        floor_img_IDs = env.floor_img_IDs,
        wall_img_IDs  = env.wall_img_IDs,
        roof_img_IDs  = None,

        hidden        = True,
        objects       = False,

        x1            = center[0] + 8,
        y1            = center[1] + 7,
        width         = room_min_size * 2,
        height        = room_min_size * 2,)
    
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

@register("over")
def build_overworld(area, lvl_num=0):
    """ Generates the overworld environment. """

    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'overworld'
    size          = 10
    soundtrack    = [
        'overworld_1',
        'overworld_1',
        'overworld_1',
        'overworld_1']
    img_IDs       = ['floors', 'grass3']
    floor_img_IDs = ['floors', 'grass3']
    wall_img_IDs  = ['walls', 'gray']
    roof_img_IDs  = ['roofs', 'tiled']
    blocked       = False
    hidden        = False

    ## Camera instance
    camera_fixed  = False
    
    ## Weather instance
    light_set     = None
    clouds        = True
    
    ## Biomes
    biomes        = [
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
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
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
        width  = random.randint(room_min_size, room_max_size)
        height = random.randint(room_min_size, room_max_size)
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
                biome          = 'city',

                floor_img_IDs  = ['floors', 'dark_green_floor'],
                wall_img_IDs   = env.wall_img_IDs,
                roof_img_IDs   = env.roof_img_IDs,
                
                hidden         = False,
                objects        = False,
                unbreakable    = True,

                x1             = x,
                y1             = y,
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
        width  = random.randint(room_min_size, room_max_size)
        height = random.randint(room_min_size, room_max_size)
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
                biome         = 'city',

                floor_img_IDs = ['floors', 'dark_green_floor'],
                wall_img_IDs  = env.wall_img_IDs,
                roof_img_IDs  = env.roof_img_IDs,

                hidden        = False,
                objects       = False,
                unbreakable   = True,

                x1            = x,
                y1            = y,
                plan          = [
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
        biome         = 'any',

        floor_img_IDs = ['floors', 'red_floor'],
        wall_img_IDs  = env.wall_img_IDs,
        roof_img_IDs  = env.roof_img_IDs,
        
        hidden        = False,
        objects       = False,
        unbreakable   = True,

        x1            = 20,
        y1            = 20,
        plan          = [
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
    area.envs.player_obj.ent.tile = env.map[door_x][door_y]
    
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

@register("cave")
def build_cave(area, lvl_num):
    """ Generates a cave environment. """
    
    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'cave'
    size          = 1
    soundtrack    = ['overworld_1']
    img_IDs       = ['floors', 'dark_red']
    floor_img_IDs = ['floors', 'dirt1']
    wall_img_IDs  = ['walls', 'dark_red']
    roof_img_IDs  = None
    blocked       = True
    hidden        = True

    ## Camera instance
    camera_fixed  = False
    
    ## Weather instance
    light_set     = 16
    clouds        = False
    
    ## Biomes
    biomes        = [['dungeon', ['walls', 'dark_red']]]
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
    ###############################################################
    # Construct rooms
    num_rooms = random.randint(2, 10)
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(room_min_size, room_max_size)
        height   = random.randint(room_min_size, room_max_size)
        x        = random.randint(0, len(env.map)    - width  - 1)
        y        = random.randint(0, len(env.map[0]) - height - 1)
        
        new_room = Room(
            name          = 'cave room',
            env           = env,
            biome         = 'cave',

            floor_img_IDs = env.floor_img_IDs,
            wall_img_IDs  = env.wall_img_IDs,
            roof_img_IDs  = env.roof_img_IDs,

            hidden        = True,
            objects       = True,

            x1            = x,
            y1            = y,
            width         = width,
            height        = height)
    
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
                    env._create_h_tunnel(x_1, x_2, y_1)
                    env._create_v_tunnel(y_1, y_2, x_2)
                except: raise Exception('Error')
            else:
                env._create_v_tunnel(y_1, y_2, y_1)
                env._create_h_tunnel(x_1, x_2, y_2)
    
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
    area.envs.player_obj.ent.tile = env.map[x][y]
    
    # Generate acending stairs under player
    stairs = create_item('descend_cave')
    place_object(stairs, [x, y], env)

    # Generate stairs in the last room
    if lvl_num == 1:
        stairs = create_item('overworld_entrance')
        stairs.img_IDs = ['stairs', 'ladder_up']
    else:
        stairs = create_item('ascend_cave')
    place_object(stairs, [x, y], env)

    return env

# Dreams
@register("dung")
def build_dungeon(area, lvl_num):
    """ Generates the overworld environment. """
    
    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'dungeon'
    size          = 2 * (1 + lvl_num//3)
    soundtrack    = [f'dungeon_{lvl_num}']
    img_IDs       = ['floors', 'gray']
    floor_img_IDs = ['floors', 'dark_green_floor']
    wall_img_IDs  = ['walls', 'gray']
    roof_img_IDs  = None
    blocked       = True
    hidden        = True

    ## Camera instance
    camera_fixed  = False
    
    ## Weather instance
    light_set     = 0
    clouds        = False
    
    ## Biomes
    biomes        = [['dungeon', ['walls', 'gray']]]
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
    ###############################################################
    # Construct rooms
    num_rooms = int(3 * env.lvl_num) + 3
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(room_min_size, room_max_size)
        height   = random.randint(room_min_size, room_max_size)
        x        = random.randint(0, len(env.map)    - width  - 1)
        y        = random.randint(0, len(env.map[0]) - height - 1)
        
        floor_img_IDs = random.choice([
            ['floors', 'dark_green_floor'],
            ['floors', 'dark_green_floor'],
            ['floors', 'green_floor']])
        
        new_room = Room(
            name          = 'dungeon room',
            env           = env,
            biome         = 'any',

            floor_img_IDs = floor_img_IDs,
            wall_img_IDs  = env.wall_img_IDs,
            roof_img_IDs  = env.roof_img_IDs,

            hidden        = True,
            objects       = True,

            x1            = x,
            y1            = y,
            width         = width,
            height        = height)
    
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
                    env._create_h_tunnel(x_1, x_2, y_1)
                    env._create_v_tunnel(y_1, y_2, x_2)
                except: raise Exception('Error')
            else:
                env._create_v_tunnel(y_1, y_2, y_1)
                env._create_h_tunnel(x_1, x_2, y_2)
    
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
    area.envs.player_obj.ent.tile = env.map[x][y]

    # Generate stairs in the last room
    stairs = create_item('descend_dungeon')
    place_object(stairs, [x, y], env)
    env.stairs['descend'] = stairs

    # Generate acending stairs under player
    if lvl_num != 1:
        (x, y) = env.rooms[-1].center()
        stairs = create_item('ascend_dungeon')
        place_object(stairs, [x, y], env)
        env.stairs['ascend'] = stairs

    return env

@register("bitw")
def build_bitworld(area, lvl_num=0):
    from pygame_utilities import bw_binary

    # Reset area
    area.envs.areas['bitworld'] = Area(name='bitworld', envs=area.envs, permadeath=False)
    current_env            = session.player_obj.ent.env
    area.envs.last_env          = current_env
    area.envs.display_fx        = bw_binary

    # Copy current level
    area = area.envs.areas['bitworld']
    area.levels[current_env.name] = copy.deepcopy(current_env)

    # Remove weather
    env = area[current_env.name]
    env.weather.cloudy    = False
    env.weather.clouds    = []
    env.weather.light_set = env.weather.alpha_hours[4]
    env.camera            = Camera(session.player_obj.ent)

    # Remove player to avoid duplication
    x, y = session.player_obj.ent.get_pos()
    #session.player_obj.ent.tile = env.map[x][y]
    env.map[x][y].ent = None
    for ent in env.ents:
        if ent.ent_id == 'player':
            env.ents.remove(ent)

        # Make all entities aggressive
        else:
            ent.role       = 'enemy'
            ent.aggression = 5

    # Test quests
    session.questlogs.load_quest('kill_the_town', area)

@register("hall")
def build_hallucination(area, lvl_num=0):
    """ Generates the overworld environment. """
    
    ###############################################################
    ## Initialize environment
    if not lvl_num:
        if not area.envs.areas['hallucination'].levels:
            lvl_num = 1
        else:
            lvl_num = 1 + area.envs.areas['hallucination'][-1].lvl_num        
    
    ###############################################################
    # Initialize environment
    ## Environment instance
    name          = 'hallucination'
    size          = 3
    soundtrack    = [f'hallucination_{lvl_num}']
    img_IDs       = ['floors', 'gold']
    floor_img_IDs = ['floors', 'green_floor']
    wall_img_IDs  = ['walls', 'gold']
    roof_img_IDs  = None
    blocked       = True
    hidden        = True
    
    ## Camera instance
    camera_fixed  = False
    
    ## Weather instance
    light_set     = 32
    clouds        = False
    
    ## Biomes
    biomes        = [
        ['any', ['walls', 'gold']],
        ['any', ['walls', 'gold']],
        ['any', ['walls', 'gold']],
        ['any', ['walls', 'gold']]]
    
    env = _init_env(
        area=area, name=name, lvl_num=lvl_num, size=size,
        soundtrack=soundtrack,
        img_IDs=img_IDs, floor_img_IDs=floor_img_IDs, wall_img_IDs=wall_img_IDs, roof_img_IDs=roof_img_IDs,
        blocked=blocked, hidden=hidden,
        camera_fixed=camera_fixed,
        light_set=light_set, clouds=clouds,
        biomes=biomes)
    
    ###############################################################
    # Construct rooms
    num_rooms = int(6 * env.lvl_num) + 2
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(room_min_size*2, room_max_size*2)
        height   = random.randint(room_min_size*2, room_max_size*2)
        x        = random.randint(0, len(env.map)    - width  - 1)
        y        = random.randint(0, len(env.map[0]) - height - 1)
        
        new_room = Room(
            name          = 'hallucination backdrop',
            env           = env,
            biome         = 'any',

            floor_img_IDs = env.floor_img_IDs,
            wall_img_IDs  = env.wall_img_IDs,
            roof_img_IDs  = env.roof_img_IDs,

            hidden        = True,
            objects       = True,

            x1            = x,
            y1            = y,
            width         = width,
            height        = height)
    
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
        width  = random.randint(room_min_size, room_max_size)
        height = random.randint(room_min_size, room_max_size)
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
                name          = 'hallucination room',
                env           = env,
                biome         = 'city',

                floor_img_IDs = ['floors', 'dark_green_floor'],
                wall_img_IDs  = env.wall_img_IDs,
                roof_img_IDs  = env.roof_img_IDs,

                hidden        = False,
                objects       = False,

                x1            = x,
                y1            = y,
                plan          = create_text_room(width, height, doors=False))

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
                    env._create_h_tunnel(x_1, x_2, y_1)
                    env._create_v_tunnel(y_1, y_2, x_2)
                except: raise Exception('Error')
            else:
                env._create_v_tunnel(y_1, y_2, y_1)
                env._create_h_tunnel(x_1, x_2, y_2)
    
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
    area.envs.player_obj.ent.img_names_backup = area.envs.player_obj.ent.img_IDs
    area.envs.player_obj.ent.img_IDs = ['tentacles_ent', 'front']
    
    # Place player in first room
    (x, y) = env.rooms[0].center()
    env.player_coordinates = [x, y]
    env.center = new_room.center()
    area.envs.player_obj.ent.tile = env.map[x][y]
    
    # Generate stairs in the last room
    (x, y) = env.rooms[-2].center()
    stairs = create_item('portal')
    stairs.name = 'hallucination'
    place_object(stairs, [x, y], env)

    return env

########################################################################################################################################################