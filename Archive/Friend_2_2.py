########################################################################
## Alex Heinrich
## Evolution
########################################################################


########################################################################
## Initialization
# Imports
import pygame, random, time, sys, math, random, textwrap, pickle
from pygame.locals import *

# Window and scene parameters
SCREEN_WIDTH=640
SCREEN_HEIGHT=480

TILE_WIDTH = 32
TILE_HEIGHT = 32

MAP_WIDTH = 640 * 2
MAP_HEIGHT = 480 * 2

TILE_MAP_WIDTH = int(MAP_WIDTH/TILE_WIDTH)
TILE_MAP_HEIGHT = int(MAP_HEIGHT/TILE_HEIGHT)

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 4
MAX_ROOMS = 30

# Player parameters
HEAL_AMOUNT = 4
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5 * TILE_WIDTH
CONFUSE_RANGE = 8 * TILE_WIDTH
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3 * TILE_WIDTH
FIREBALL_DAMAGE = 12

LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

TORCH_RADIUS = 10

# Sizes and coordinates relevant for the GUI
MSG_X = 5
MSG_WIDTH = int(SCREEN_WIDTH / 10)
MSG_HEIGHT = 3

# Colors
BLACK = pygame.color.THECOLORS["black"]
WHITE = pygame.color.THECOLORS["white"]
RED = pygame.color.THECOLORS["red"]
GREEN = pygame.color.THECOLORS["green"]
BLUE = pygame.color.THECOLORS["blue"]
YELLOW = pygame.color.THECOLORS["yellow"]
ORANGE = pygame.color.THECOLORS["orange"]
VIOLET = pygame.color.THECOLORS["violet"]
LIGHT_CYAN = pygame.color.THECOLORS["lightcyan"]
LIGHT_GREEN = pygame.color.THECOLORS["lightgreen"]
LIGHT_BLUE = pygame.color.THECOLORS["lightblue"]
LIGHT_YELLOW = pygame.color.THECOLORS["lightyellow"]

# Other
message_log_toggle = False
dungeon_level_cache = 0
home_objects, home_object_positions = [], []
new_game_trigger = True


#######################################################################
## Functions and classes
# Main scripts
def main_menu():
    """ Initializes the startup menu. """
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont('Arial', 45, bold=True)
    game_title = title_font.render("Evolution", True, GREEN) # Sets game title
    game_title_pos = (int((SCREEN_WIDTH - game_title.get_width())/2), 150)
    cursor_img = pygame.Surface((16, 16)).convert()
    cursor_img.set_colorkey(cursor_img.get_at((0,0)))
    pygame.draw.polygon(cursor_img, RED, [(0, 0), (16, 8), (0, 16)], 0)
    cursor_img_pos = [195, 254]
    menu_choices = ["NEW GAME", "CONTINUE", "CONTROLS", "QUIT"]   
    for i in range(len(menu_choices)):
        menu_choices[i] = font.render(menu_choices[i], True, WHITE)
    choice = 0
    choices_length = len(menu_choices)-1
    while True:
        clock.tick(30)
        for event in pygame.event.get(): # Processes user input
            if event.type == QUIT: # Quit
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN: # Key pressed
                if event.key == K_ESCAPE: # Quit
                    pygame.quit()
                    sys.exit()
                if event.key == K_UP: # Up
                    cursor_img_pos[1] -= 24
                    choice -= 1
                    if choice < 0:
                        choice = choices_length
                        cursor_img_pos[1] = 326
                elif event.key == K_DOWN: # Down
                    cursor_img_pos[1] += 24
                    choice += 1
                    if choice > choices_length:
                        choice = 0
                        cursor_img_pos[1] = 254
                if event.key == K_RETURN: # Enter
                    if choice == 0:  # >> NEW GAME <<
                        new_game()
                        play_game()
                    if choice == 1:  # >> CONTINUE <<
                        load_game()
                        play_game()
                    if choice == 2: # >> CONTROLS <<
                        menu('Controls', ['Move:                                       arrow keys',
                                          'Descend stairs or grab item:    enter',
                                          'Ascend stairs to home:            shift',
                                          'Check stats:                             1',
                                          'Use item in inventory:              2',
                                          'Drop item from inventory:        3',
                                          'Toggle messages:                    ?'], True)
                    elif choice == 3:  # >> QUIT <<
                        return
        screen.fill(BLACK)
        y = 250
        for menu_choice in menu_choices:
            screen.blit(menu_choice,(230,y))
            y += 24
        screen.blit(game_title, game_title_pos)
        screen.blit(cursor_img, cursor_img_pos)                
        pygame.display.flip()

def new_game():
    """ Sets player stats, initial inventory, map, and rooms. """
    global player, camera, game_state, player_action, active_entities
    global gui, game_msgs, game_msgs_data, message_log, inventory,  dungeon_level 

    # The Figher class sets stats, damage, and health. In this case, the Object class initializes the player and sets its movement.
    fighter_component = Fighter(hp=100, defense=100, power=100, exp=0, death_function=player_death)
    player = Object(TILE_WIDTH*10, TILE_HEIGHT*7, images[2], "player", blocks=True, fighter=fighter_component)
    player.level = 1

    # Generates the map and sets the player in a room
    dungeon_level = 0
    make_home()
    camera = Camera(player)
    
    game_state = 'playing' # As opposed to 'dead'
    player_action = 'didnt-take-turn' 
    inventory = []
    active_entities = []
    
    update_gui() # Places health and dungeon level on the screen
    game_msgs, game_msgs_data = [], [] # Holds game messages and their colors
    message_log = True
    message('Welcome!', RED)
    
    # Sets initial inventory
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    obj = Object(0, 0, images[10], 'dagger', equipment=equipment_component)
    inventory.append(obj)
    equipment_component.equip()

def make_home():
    """ Initializes and generates the player's home, its rooms, and its contents. """
    global level_map, objects, stairs, new_game_trigger
    objects = [player]
    rooms = []
    num_rooms = 0 # Counts number of generated rooms
    
    level_map = [[ Tile(True, x, y) # Initializes tiles at each point in the map.
              for y in range(0, MAP_HEIGHT, TILE_HEIGHT) ]
                for x in range(0, MAP_WIDTH, TILE_WIDTH) ]
 
    w = ROOM_MAX_SIZE # random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE) # Sets a random width and height for a single room
    h = ROOM_MAX_SIZE # random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    x = 10 #random.randint(0, TILE_MAP_WIDTH - w - 1) # Set a random position within the map
    y = 10 #random.randint(0, TILE_MAP_HEIGHT - h - 1)
    new_room = Rectangle(x, y, w, h) # Places the room at the random location.

    create_room(new_room) # Sets parameters for the room's floor
    (new_x, new_y) = new_room.center() # Holds coordinates for the room's center
    if num_rooms == 0: # Places player in the first room
        player.x = new_x * TILE_WIDTH
        player.y = new_y * TILE_HEIGHT
        new_x, new_y = new_x + 3, new_y # Sets the position for the stairs
        level_map[new_x][new_y].entity = player
        player.tile = level_map[new_x][new_y]
        check_tile(new_x, new_y)
        place_objects(new_room, home=True, fresh_start=new_game_trigger) # Adds content to the room
        if new_game_trigger:
            new_game_trigger = False
    else: # Makes tunnel to connect to the previous room
        (prev_x, prev_y) = rooms[num_rooms-1].center() # Coordinates of previous room's center
        if random.randint(0, 1) == 0:
            create_h_tunnel(prev_x, new_x, prev_y)
            create_v_tunnel(prev_y, new_y, new_x)
        else:
            create_v_tunnel(prev_y, new_y, prev_x)
            create_h_tunnel(prev_x, new_x, new_y)
        place_objects(new_room, True) # Adds content to the room
    rooms.append(new_room) # Adds new room to the room list
    num_rooms += 1

    # Creates stairs at the center of the last room
    stairs = Object(new_x * TILE_WIDTH, new_y * TILE_HEIGHT, images[9], 'stairs')
    level_map[new_x][new_y].item = stairs
    objects.append(stairs)
    stairs.send_to_back()

def make_map():
    """ Initializes and generates the map, its rooms, and its contents. """
    global level_map, objects, stairs
    objects = [player]
    rooms = []
    num_rooms = 0 # Counts number of generated rooms
    
    level_map = [[ Tile(True, x, y) # Initializes tiles at each point in the map.
              for y in range(0, MAP_HEIGHT, TILE_HEIGHT) ]
                for x in range(0, MAP_WIDTH, TILE_WIDTH) ]
 
    for r in range(MAX_ROOMS): # Creates a random set of rooms and places them in the map
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE) # Sets a random width and height for a single room
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = random.randint(0, TILE_MAP_WIDTH - w - 1) # Set a random position within the map
        y = random.randint(0, TILE_MAP_HEIGHT - h - 1)
        new_room = Rectangle(x, y, w, h) # Places the room at the random location.
 
        failed = False # Checks for room intersections. Include more values to make more hallways.
        if random.choice([0, 1, 2, 3]) != 0:
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

        if not failed: # Completes room
            create_room(new_room) # Sets parameters for the room's floor
            (new_x, new_y) = new_room.center() # Coordinates of the room's center
            if num_rooms == 0: # Places player in the first room
                player.x = new_x * TILE_WIDTH
                player.y = new_y * TILE_HEIGHT
                level_map[new_x][new_y].entity = player
                player.tile = level_map[new_x][new_y]
                check_tile(new_x, new_y)
            else: # Makes tunnel to connect to the previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center() # Coordinates of previous room's center
                if random.randint(0, 1) == 0:
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
                place_objects(new_room) # Adds content to the room
            rooms.append(new_room) # Adds new room to the room list
            num_rooms += 1

    # Creates stairs at the center of the last room
    stairs = Object(new_x * TILE_WIDTH, new_y * TILE_HEIGHT, images[9], 'stairs')
    level_map[new_x][new_y].item = stairs
    objects.append(stairs)
    stairs.send_to_back()

def create_room(room):
    """ Sets parameters for a room's floor. """
    global level_map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            tile = level_map[x][y]
            tile.blocked = False
            tile.block_sight = False
            tile.room = room

def place_objects(room, home=False, fresh_start=True):
    """ Decides the chance of each monster or item appearing, then generates and places them. """
    global home_objects, home_objects2
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]]) # Maximum per room. [value, level]
    monster_chances = {} # Chance of spawning monster by monster type
    monster_chances['orc'] = 80 # Sets spawn chance for orcs
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
 
    max_items = from_dungeon_level([[1, 1], [2, 4]]) # Maximum per room
    item_chances = {} # Chance of spawning item by item type
    item_chances['heal'] = 35 # Sets spawn chance for potions
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] =  from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   from_dungeon_level([[10, 2]])
    item_chances['sword'] =     from_dungeon_level([[5, 4]])
    item_chances['shield'] =    from_dungeon_level([[15, 8]])

    if home: # Places items in home
        if fresh_start:
            for i in range(3): # Places default items
                x = room.x1+3+i # Sets location
                y = room.y1+1
                if not is_blocked(x, y):
                    item_component = Item(use_function=cast_heal)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[6],
                                   'healing potion', item=item_component)
                    home_objects.append(item)
                    home_object_positions.append([x, y])
                    objects.append(item)
                    level_map[x][y].item = item
            x = random.randint(room.x1+1, room.x2-1) # Sets random location
            y = random.randint(room.y1+1, room.y2-1)
            if not is_blocked(x, y):
                fighter_component = Fighter(hp=20, defense=0, power=0, exp=0, death_function=monster_death)
                ai_component = BasicMonster()               
                monster = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[3], 'orc', blocks=True, fighter=fighter_component, ai=ai_component)
                home_objects.append(item)
                home_object_positions.append([x, y])
                objects.append(monster)
                level_map[x][y].entity = monster # Places monster?
                monster.tile = level_map[x][y]
        else: # Places last known items
            for i in range(len(home_objects)):
                if home_objects != 0:
                    item = home_objects[i]
                    x, y = home_object_positions[i][0], home_object_positions[i][1]
                    objects.append(item)
                    #menu(f'{x}, {y}', 'test')
                    level_map[x][y].item = item

    else: # Places items and monsters in dungeon
        num_monsters = random.choice([0, 0, 0, 0, 1, max_monsters])
        num_items = random.randint(0, max_items) # Sets number of items?
        
        for i in range(num_monsters): # Places monsters
            x = random.randint(room.x1+1, room.x2-1) # Sets random location
            y = random.randint(room.y1+1, room.y2-1)
            if not is_blocked(x, y):
                choice = random_choice(monster_chances) # Sets random monster
                if choice == 'orc': # Creates an orc
                    fighter_component = Fighter(hp=20, defense=0, power=4, exp=35, death_function=monster_death)
                    ai_component = BasicMonster()               
                    monster = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[3], 'orc', blocks=True,
                        fighter=fighter_component, ai=ai_component)
                elif choice == 'troll':
                    fighter_component = Fighter(hp=30, defense=2, power=8, exp=100, death_function=monster_death)
                    ai_component = BasicMonster()               
                    monster = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[4], 'troll', blocks=True,
                        fighter=fighter_component, ai=ai_component)
                objects.append(monster)
                level_map[x][y].entity = monster # Places monster?
                monster.tile = level_map[x][y]

        for i in range(num_items): # Places items
            x = random.randint(room.x1+1, room.x2-1) # Sets random location
            y = random.randint(room.y1+1, room.y2-1)
            if not is_blocked(x, y):
                choice = random_choice(item_chances) # Sets random item
                if choice == 'heal': # Creates a potion
                    item_component = Item(use_function=cast_heal)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[6],
                                   'healing potion', item=item_component)
                elif choice == 'lightning': # Creates a lightning scroll
                    item_component = Item(use_function=cast_lightning)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5],
                                   'scroll of lightning bolt', item=item_component)
                elif choice == 'fireball': # Creates a fireball scroll
                    item_component = Item(use_function=cast_fireball)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5],
                                   'scroll of fireball', item=item_component)
                elif choice == 'confuse': # Creates a confusion scroll
                    item_component = Item(use_function=cast_confuse)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5],
                                   'scroll of confusion', item=item_component)
                elif choice == 'sword': # Creates a sword
                     equipment_component = Equipment(slot='right hand', power_bonus=3)
                     item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[7],
                                    'sword', equipment=equipment_component)
                elif choice == 'shield': # Creates a shield
                     equipment_component = Equipment(slot='left hand', defense_bonus=1)
                     item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[8],
                                    'shield', equipment=equipment_component)
                objects.append(item)
                level_map[x][y].item = item
                item.send_to_back()

def play_game():
    """ Processes user input and triggers monster movement. """
    global player_action, message_log, message_log_toggle
    clock = pygame.time.Clock() # Keeps track of time
    player_move = False
    pygame.key.set_repeat(400, 100) # Sets delay and interval for held keys
    while True:
        clock.tick(30)
        #for event in pygame.event.get(): # Processes user input
        event = pygame.event.get()
        if event:
            if event[0].type == QUIT: # Save and quit
                save_game()
                pygame.quit()
                sys.exit()
            if game_state == 'playing':
                if event[0].type == KEYDOWN:
                    if event[0].key == K_ESCAPE: # Save (esc)
                        save_game()
                        return
                    message_log = False

                    if event[0].key == K_UP: # Move or attack
                        player_move_or_attack(0, -TILE_HEIGHT)
                    elif event[0].key == K_DOWN:
                        player_move_or_attack(0, TILE_HEIGHT)
                    if event[0].key == K_LEFT:
                        player_move_or_attack(-TILE_WIDTH, 0)
                    elif event[0].key == K_RIGHT:
                        player_move_or_attack(TILE_WIDTH, 0)

                    if event[0].key == K_RETURN: # Pick up item or descend stairs (enter)
                        if player.tile.item and player.tile.item.item: 
                            player.tile.item.item.pick_up()
                            player.tile.item = None # Hides icon
                        elif stairs.x == player.x and stairs.y == player.y:
                            next_level()
                    if event[0].key == K_RSHIFT and dungeon_level != 0: # Ascend stairs to home
                        if stairs.x == player.x and stairs.y == player.y:
                            go_home()

                    if event[0].key == K_1 or event[0].key == K_KP1: # View player information (1)
                        level_up_exp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                        menu('Character Information', ['Level:                                ' + str(player.level),
                                                       'Experience:                       ' + str(player.fighter.exp),
                                                       'Experience to level up:    ' + str(level_up_exp),
                                                       'Maximum HP:                    ' + str(player.fighter.max_hp),
                                                       'Attack:                             ' + str(player.fighter.power),
                                                       'Defense:                           ' + str(player.fighter.defense)], True)
                            
                    if event[0].key == K_2 or event[0].key == K_KP2: # Check inventory and use item (2)
                        chosen_item = inventory_menu("Inventory: Use Item")
                        if chosen_item is not None:
                            chosen_item.use()
                            update_gui()
                            
                    if event[0].key == K_3 or event[0].key == K_KP3: # Drop item (3)
                        if player.tile.item:
                            message("There's already something here")
                        else:
                            chosen_item = inventory_menu('Inventory: Drop Item')
                            if chosen_item is not None:
                                chosen_item.drop()
                    
                    if event[0].key == K_SLASH: # Toggles messages
                        if message_log_toggle:
                            message_log, message_log_toggle = False, False
                        else:
                            message_log, message_log_toggle = True, True

            if event[0].type == MOUSEBUTTONDOWN: # Cursor-controlled actions?
                if event[0].button == 1:
                    player_move = True
                    message_log = False
                elif event[0].button == 3:
                    mouse_x, mouse_y = event[0].pos
                    get_names_under_mouse(mouse_x, mouse_y)
            if event[0].type == MOUSEBUTTONUP:
                if event[0].button == 1:
                    player_move = False

        if player_move and game_state == 'playing': # Cursor-controlled movement
            pos = pygame.mouse.get_pos()
            x = int((pos[0] + camera.x)/TILE_WIDTH)
            y = int((pos[1] + camera.y)/TILE_HEIGHT)
            tile = level_map[x][y]
            if tile != player.tile:
                dx = tile.x - player.x
                dy = tile.y - player.y
                distance = math.sqrt(dx ** 2 + dy ** 2) # Distance from player to target
                dx = int(round(dx / distance)) * TILE_WIDTH # Restrict motion to grid
                dy = int(round(dy / distance)) * TILE_HEIGHT
                player_move_or_attack(dx, dy) # Triggers the chosen action

    #if game_state == 'playing' and player_action != 'didnt-take-turn': # Tab forward and unhash to allow turn-based game
        for entity in active_entities:
            if entity.ai:
                entity.ai.take_turn()
        player_action = 'didnt-take-turn'
        render_all()

def player_move_or_attack(dx, dy):
    """ Moves the player by the given amount. """
    global player_action
    target = None
    x = int((player.x + dx)/TILE_WIDTH)
    y = int((player.y + dy)/TILE_HEIGHT)
    if not is_blocked(x, y): # Moves player
       player.x += dx
       player.y += dy
       player.tile.entity = None
       level_map[x][y].entity = player
       player.tile = level_map[x][y]
       check_tile(x, y)
       camera.update()
    elif level_map[x][y].entity: # Attacks target
       target = level_map[x][y].entity
       #if target.fighter:
       player.fighter.attack(target)
    player_action = 'took-turn'

def inventory_menu(header):
    """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen. """
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            if item.equipment and item.equipment.is_equipped: # Shows additional information in case it's equipped
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
    index = menu(header, options)
    if index is None or len(inventory) == 0:
       return None
    return inventory[index].item

def menu(header, options, no_letters=False):
    """ Populates menu? """
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    screen.fill(BLACK)
    header = font.render(header, True, YELLOW)
    screen.blit(header,(0,0))
    y = header.get_height()+5
    letter_index = ord('a')
    for option_text in options:
        if no_letters:
            text = font.render(option_text, True, WHITE)
        else:
            text = font.render('(' + chr(letter_index) + ') ' + option_text, True, WHITE)
        screen.blit(text,(0,y))
        y += text.get_height()
        letter_index += 1
    
    pygame.display.flip()
    while True:
        pygame.time.Clock().tick(30)
        for event in pygame.event.get(): # Processes user input
            if event.type == QUIT: # Quit
                save_game()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # Save and quit
                    save_game() 
                    pygame.quit()
                    sys.exit()
                else: # Converts ASCII code to an index, then returns option if applicable
                    if event.unicode != '':
                        index = ord(event.unicode) - ord('a')
                        if index >= 0 and index < len(options): 
                            return index
                        else:
                            return None

def update_gui():
    """ Updates health and dungeon level. """
    global gui
    gui = font.render('HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp) +  ' '*60 + ' Dungeon level ' + str(dungeon_level), True, YELLOW)
    #gui= font.render('Dungeon level ' + str(dungeon_level) +  ' '*5 + 'HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp), True, YELLOW)

def next_level():
    """ Advances player to the next level. """
    global dungeon_level
    message('You take a moment to rest, and recover your strength.', VIOLET)
    player.fighter.heal(int(player.fighter.max_hp / 2))  #heal the player by 50%
    if dungeon_level_cache == 0:
        dungeon_level += 1
    else:
        dungeon_level = dungeon_level_cache + 1
    time.sleep(0.5)
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', RED)
    make_map()  #create a fresh new level!
    camera.update()
    time.sleep(0.5)
    update_gui()

def go_home():
    """ Advances player to home. """
    global dungeon_level, dungeon_level_cache
    message('You take a moment to rest, and recover your strength.', VIOLET)
    player.fighter.heal(int(player.fighter.max_hp / 2)) # Heals the player by 50%
    time.sleep(0.5)
    message('You gather you belongings and head home.', RED)
    if dungeon_level != 0:
        dungeon_level_cache = dungeon_level
        dungeon_level = 0
    make_home()
    camera.update()
    time.sleep(0.5)
    update_gui()     

def check_tile(x, y):
    """ Reveals newly explored regions. """
    tile = level_map[x][y]
    if not tile.explored:
       tile.explored = True 
       old_x = x
       old_y = y
       for x in range(old_x - 1, old_x + 2):
           for y in range(old_y - 1, old_y + 2):
               level_map[x][y].visible = True
       if tile.room and not  tile.room.explored:
          room = tile.room
          room.explored = True
          for x in range(room.x1 , room.x2 + 1):
              for y in range(room.y1 , room.y2 + 1):
                  level_map[x][y].visible = True       

def render_all():
    """ Draws tiles and stuff. """
    global active_entities
    active_entities = []
    screen.fill(BLACK)
    for y in range(camera.tile_map_y, camera.y_range): # Draws visible tiles
        for x in range(camera.tile_map_x, camera.x_range):
            tile = level_map[x][y]
            if tile.visible:
               if tile.block_sight:
                   screen.blit(images[0], (tile.x-camera.x, tile.y-camera.y))
               else:
                   screen.blit(images[1], (tile.x-camera.x, tile.y-camera.y))
                   if tile.item:
                      tile.item.draw(screen)
                   if tile.entity:
                      tile.entity.draw(screen)
                      active_entities.append(tile.entity)
    if impact:
       screen.blit(impact_image, impact_image_pos)
    screen.blit(gui, (10,456))                  
    if message_log: # Prints messages
       y = 10
       for msg in game_msgs:
           screen.blit(msg, (5,y))
           y += 24
    pygame.display.flip()
    
def player_death(player):
    """ Ends the game upon death and transforms the player into a corpse. """
    global game_state
    message('You died!', RED)
    game_state = 'dead'
    player.image = images[10]
    player.image_index = 10
    player.tile.entity = None
    player.tile.item = player

def monster_death(monster):
    """ Transforms a monster into a corpse. """
    message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.exp) + ' experience points.', ORANGE)
    monster.image = images[10]
    monster.image_index = 10
    monster.tile.entity = None
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    try:
        monster.send_to_back()
    except:
        print()
    monster.item = Item()
    monster.item.owner = monster
    if not monster.tile.item:
        monster.tile.item = monster
    pygame.event.get()
   
def target_tile(max_range=None):
    """ Returns the position of a tile left-clicked in player's field of view, or (None,None) if right-clicked. """
    global message_log
    while True:         
        pygame.time.Clock().tick(30)
        for event in pygame.event.get(): # Processes user input
            if event.type == QUIT: # Quit
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN: # Cancels action for escape
                if event.key == K_ESCAPE:
                    message_log = False 
                    return (None, None)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3: # Cancels action for right-click
                    message_log = False 
                    return (None, None)
                if event.button == 1: # Accepts the target if clicked in the field of view
                    mouse_x, mouse_y = event.pos
                    mouse_x += camera.x
                    mouse_y += camera.y
                    x = int(mouse_x /TILE_WIDTH)
                    y = int(mouse_y /TILE_HEIGHT)
                    if (level_map[x][y].visible and
                        (max_range is None or player.distance(mouse_x, mouse_y) <= max_range)):
                        return (mouse_x, mouse_y)
        render_all()

def target_monster(max_range=None):
    """ Returns the first clicked monster inside the field of view up to a range, or None if right-clicked. """
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None
        x = int(x / TILE_WIDTH)
        y = int(y / TILE_HEIGHT)
        tile = level_map[x][y]
        for obj in active_entities:
            if obj.x == tile.x and obj.y == tile.y and obj.fighter and obj != player:
                return obj
    
def cast_heal():
    """ Heals the player. """
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', RED)
        return 'cancelled'
    message('Your wounds start to feel better!', VIOLET)
    player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
    """ Finds the closest enemy within a maximum range and attacks it. """
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', RED)
        return 'cancelled'
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(LIGHTNING_DAMAGE) + ' hit points.', LIGHT_BLUE)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_fireball():
    """ Asks the player for a target tile to throw a fireball at. """
    message('Left-click a target tile for the fireball, or right-click to cancel.', LIGHT_CYAN)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(int(FIREBALL_RADIUS/TILE_WIDTH)) + ' tiles!', ORANGE)
    for obj in active_entities: # Damages every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', ORANGE)
            obj.fighter.take_damage(FIREBALL_DAMAGE)

def cast_confuse():
    """ Asks the player for a target to confuse, then replaces the monster's AI with a "confused" one. After some turns, it restores the old AI. """
    message('Left-click an enemy to confuse it, or right-click to cancel.', LIGHT_CYAN)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', LIGHT_GREEN)

def msgbox(text):
    menu(text, []) # menu("<message>")

def message(new_msg, color = WHITE):
    """  """
    global game_msgs, message_log, game_msgs_data
    if not message_log:
       game_msgs = []
       game_msgs_data = []
    message_log = True
    
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH) # Splits the message among multiple lines
    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
            del game_msgs_data[0]
        msg = font.render(line, True, color) # Adds the new message
        game_msgs.append(msg)
        game_msgs_data.append((line,color))
    render_all()
    wait_time = 0
    while wait_time < 10:
        pygame.time.Clock().tick(30)
        wait_time += 1

def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    level_up_exp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.exp >= level_up_exp: # Levels up
        player.level += 1
        player.fighter.exp -= level_up_exp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', YELLOW)
        choice = None
        while choice == None: # Keeps asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:',
                ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'])
        if choice == 0: # Boosts health
            player.fighter.max_hp += 20
            player.fighter.hp += 20
        elif choice == 1: # Boosts power
            player.fighter.power += 1
        elif choice == 2: # Boosts defense
            player.fighter.defense += 1
        update_gui()

# Utilities and stuff
def random_choice_index(chances):
    """ Chooses an option from a list of possible values, then returns its index. """
    dice = random.randint(1, sum(chances))
    running_sum = 0
    choice = 0
    # Checks if the random choice corresponds to one of the possible values
    for w in chances:
        running_sum += w
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    """ Chooses one option from dictionary of chances, then returning its key. """
    chances = chances_dict.values()
    strings = list(chances_dict.keys())
    return strings[random_choice_index(chances)]

def from_dungeon_level(table):
    """ Returns a value that depends on the dungeon level. The table specifies what value occurs after each level with 0 as the default. """
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def create_h_tunnel(x1, x2, y):
    """ Creates horizontal tunnel. min() and max() are used if x1 is greater than x2. """
    global level_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        level_map[x][y].blocked = False
        level_map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
    global level_map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        level_map[x][y].blocked = False
        level_map[x][y].block_sight = False

def is_blocked(x, y):
    if level_map[x][y].blocked: # Checks for barriers
        return True
    if level_map[x][y].entity: # Checks for monsters
        return True
    return False

def closest_monster(max_range):
    """ Finds the closest enemy up to a maximum range. """
    closest_enemy = None
    closest_dist = max_range + 1  # Starts with maximum range
    for obj in active_entities:
        if obj.fighter and obj != player and obj.tile.visible:
            dist = player.distance_to(obj)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = obj
                closest_dist
    return closest_enemy

def get_names_under_mouse(mouse_x, mouse_y):
    """ Creates a list with the names of all objects at the mouse's coordinates and in the field of view, then returns a string with the names of all objects under the mouse. """
    x = int((mouse_x + camera.x)/TILE_WIDTH)
    y = int((mouse_y + camera.y)/TILE_HEIGHT)    
    tile = level_map[x][y]
    if tile.visible:
        if not(tile.item or tile.entity):
            message("There is nothing there.")
        else:
            names = []
            if tile.item:
                names.append(tile.item.name)
            if tile.entity:
                names.append(tile.entity.name)
            if tile.item and tile.entity:
                names = ' and '.join(names)
                message("There is "+names+" there.")
            else:
                message("There is "+names[0]+" there.")
    else:
       message("You can't see that spot.")

def get_equipped_in_slot(slot):
    """ Returns the equipment in a slot, or None if it's empty. """
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj):
    """ Returns a list of equipped items. """
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []

def entity_flash(entity):
    """ ? """
    global impact
    impact = True
    impact_image_pos[0] = entity.x-camera.x
    impact_image_pos[1] = entity.y-camera.y
    render_all()
    impact = False
    wait_time = 0
    while wait_time < 5:
        pygame.time.Clock().tick(30)
        wait_time += 1    
    flash = 3
    flash_time = 2
    if entity.fighter.hp <=0:
       flash_time = 4
    entity_old_image = entity.image
    while flash_time > 1:
        pygame.time.Clock().tick(30)
        if flash:
           entity.image = blank_surface
        render_all()
        if not flash:
           flash = 6
        flash -= 1
        if flash < 1:
           flash = False
           flash_time -= 1
           entity.image = entity_old_image 
           if flash_time < 1:
              flash_time = 0
              flash = False
              entity.image = entity_old_image

def get_impact_image():
    """ ? """
    color = (230,230,230)
    impact_image = pygame.Surface((TILE_WIDTH, TILE_WIDTH)).convert()
    impact_image.set_colorkey(impact_image.get_at((0,0)))
    image = pygame.Surface((int(TILE_WIDTH/2), int(TILE_HEIGHT/3))).convert()
    top = 0
    left = 0
    bottom = image.get_width()-1
    right = image.get_height()-1
    center_x = int(image.get_width()/2)-1
    center_y = int(image.get_height()/2)-1
    pygame.draw.line(image, color, (top,left), (bottom,right), 2)
    #pygame.draw.line(image, color, (bottom,left), (top,right), 2)
    #pygame.draw.line(image, color, (center_x,top), (center_x,bottom), 2)
    #pygame.draw.line(image, color, (left,center_y),(right,center_y), 2)
    x = int((impact_image.get_width()-image.get_width())/2)
    y = int((impact_image.get_height()-image.get_height())/2)
    impact_image.blit(image, (x,y))
    return impact_image

# Classes
class Object:
    """ Defines a generic object, such as the player, a monster, an item, or stairs. """
    def __init__(self, x, y, image, name, blocks=False, fighter=None, ai=None, item=None, equipment=None):
        """ Defines object and object parameters. """
        self.x = x
        self.y = y
        self.image = image
        self.image_index = images.index(image)
        self.name = name
        self.blocks = blocks
        self.tile = None
        self.fighter = fighter
        if self.fighter: # Lets the fighter component know who owns it
            self.fighter.owner = self
        self.ai = ai
        if self.ai: # Lets the AI component know who owns it
            self.ai.owner = self
        self.item = item
        if self.item: # Lets the Item component know who owns it
            self.item.owner = self
        self.equipment = equipment
        if self.equipment: # Lets the Equipment component know who owns it
            self.equipment.owner = self
            # There must be an Item component for the Equipment component to work properly
            self.item = Item()
            self.item.owner = self

    def move(self, dx, dy):
        """ Moves the player by the given amount if the destination is not blocked. """
        x = int((self.x + dx)/TILE_WIDTH)
        y = int((self.y + dy)/TILE_HEIGHT)
        if not is_blocked(x, y):
           self.x += dx
           self.y += dy
           self.tile.entity = None
           level_map[x][y].entity = self
           self.tile = level_map[x][y]

    def move_towards(self, target_x, target_y):
        """ Moves object towards target. """
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance)) * TILE_WIDTH # Restricts to map grid
        dy = int(round(dy / distance)) * TILE_HEIGHT
        self.move(dx, dy)
 
    def distance_to(self, other):
        """ Returns the distance to another object. """
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
      
    def distance(self, x, y):
        """ Returns the distance to some coordinates. """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)      
      
    def send_to_back(self):
        """ Lets this object be drawn first, so all others appear above it if they're on the same tile. """
        global objects
        objects.remove(self)
        objects.insert(0, self)
       
    def draw(self, surface):
        """ Draws the object at its position. """
        surface.blit(self.image, (self.x-camera.x, self.y-camera.y))

class Fighter:
    """ Defines combat-related properties and methods (monster, player, NPC). """
    def __init__(self, hp, defense, power, exp, death_function=None):
        """ Defines fighter and fighter parameters. """
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.exp = exp
        self.death_function = death_function
 
    def attack(self, target):
        """ Formulates attack damage. """
        damage = self.power - target.fighter.defense
        if damage > 0: # Damages the target
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        """ Applies damage if possible. """
        if damage > 0:
            self.hp -= damage
            entity_flash(self.owner)
            if self.owner == player:
               update_gui()
            if self.hp <= 0: # Checks for death and calls death function if present
                self.hp = 0
                update_gui()
                function = self.death_function
                if function is not None:
                    function(self.owner)
                if self.owner != player: #Gives experience to the player
                    player.fighter.exp += self.exp
                    check_level_up()
                    
    def heal(self, amount):
        """ Heals player by the given amount without going over the maximum. """
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class Item:
    """ Defines an item that can be picked up and used. """
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        """ Adds an item to the player's inventory and removes it from the map. """
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', RED)
        else:
            inventory.append(self.owner)
            if self.owner in home_objects:
                index = home_objects.index(self.owner)
                home_objects[index] = 0 # Removes item from home
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', GREEN)
            equipment = self.owner.equipment # Automatically equips item if possible
            if equipment and get_equipped_in_slot(equipment.slot) is None:
               equipment.equip()

    def drop(self):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at the player's coordinates and removes it from their inventory. """
        if self.owner.equipment:
            self.owner.equipment.dequip()
        if dungeon_level == 0: # Saves dropped items at home
            home_objects.append(self.owner)
            home_object_positions.append([int(player.x/TILE_WIDTH), int(player.y/TILE_HEIGHT)])
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        player.tile.item = self.owner
        message('You dropped a ' + self.owner.name + '.', YELLOW)   
 
    def use(self):
        """ Equips of unequips an item if the object has the Equipment component. """
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner) # Destroys item after use

class Equipment:
    """ Defines an object that can be equipped and yield bonuses. Automatically adds the Item component. """
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        """ Defines equipment and equipment parameters. """
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False

    def toggle_equip(self):
        """ Toggles the equip/unequip status. """
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        """ Unequips object if the slot is already being used. """
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        player.fighter.power +=  self.power_bonus
        player.fighter.defense +=  self.defense_bonus
        player.fighter.max_hp +=  self.max_hp_bonus
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', LIGHT_GREEN)
 
    def dequip(self):
        """ Unequips an object and shows a message about it. """
        if not self.is_equipped: return
        self.is_equipped = False
        player.fighter.power -=  self.power_bonus
        player.fighter.defense -=  self.defense_bonus
        player.fighter.max_hp -=  self.max_hp_bonus
        if player.fighter.hp > player.fighter.max_hp:
           player.fighter.hp = player.fighter.max_hp 
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', LIGHT_YELLOW)

class BasicMonster:
    """ Defines the AI for a basic monster. """
    def take_turn(self):
        """ Lets a basic monster takes its turn. """
        monster = self.owner
        if monster.tile.visible:
            distance = monster.distance_to(player)
            if distance < 128:
                if dungeon_level != 0:
                    if distance >= 64: # Moves towards player if far away
                        monster.move_towards(player.x, player.y)
                    elif player.fighter.hp > 0: # Attacks player
                        if dungeon_level != 0:
                            monster.fighter.attack(player)
                else:
                    if distance >= 100:
                        monster.move_towards(player.x, player.y)

class ConfusedMonster:
    """ Defines the AI for a temporarily confused monster, which reverts to previous AI after a while. """
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self):
        """ Moves in a random direction and decreases the number of turns confusedm or restores the previous AI. """
        if self.num_turns > 0:
            dx = random.randint(-1, 1) * TILE_WIDTH
            dy = random.randint(-1, 1) * TILE_HEIGHT
            self.owner.move(dx, dy)
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', RED)

class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    def __init__(self, blocked, x, y, block_sight = None):
        self.blocked = blocked
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.x = x
        self.y = y
        self.visible = False
        self.explored = False
        self.room = None
        self.entity = None
        self.item = None

class Rectangle :
    """ Defines rectangles on the map. Used to characterize a room. """
    def __init__(self, x, y, w, h):
        """ Defines a rectangle and its size. """
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.explored = False

    def center(self):
        """ Finds the center of the rectangle. """
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)
 
    def intersect(self, other):
        """ Returns true if this rectangle intersects with another one. """
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)        

class Camera :
    """ Defines a camera to follow the player. """
    def __init__(self, target):
        """ Defines a camera and its parameters. """
        self.target = target
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT + TILE_HEIGHT
        self.x = self.target.x - int(self.width / 2)
        self.y = self.target.y - int(self.height / 2)
        self.center_x = self.x + int(self.width / 2)
        self.center_y = self.y + int(self.height / 2)
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        self.tile_map_x = int(self.x / TILE_WIDTH)
        self.tile_map_y = int(self.y / TILE_HEIGHT)
        self.tile_map_width = int(self.width / TILE_WIDTH)
        self.tile_map_height = int(self.height / TILE_HEIGHT)
        self.x_range = self.tile_map_x + self.tile_map_width
        self.y_range = self.tile_map_y + self.tile_map_height
        self.fix_position()
        
    def update(self):
        """ ? """
        if self.target.x != self.center_x:
           x_move = self.target.x - self.center_x
           self.x += x_move
           self.center_x += x_move
           self.right += x_move
           self.tile_map_x = int(self.x / TILE_WIDTH)
           self.x_range = self.tile_map_x + self.tile_map_width
        #if self.y > 0 and  self.target.y < self.center_y \
        #or self.bottom < MAP_HEIGHT and  self.target.y > self.center_y:
        if self.target.y != self.center_y:   
           y_move = self.target.y - self.center_y
           self.y += y_move
           self.center_y += y_move
           self.bottom += y_move
           self.tile_map_y = int(self.y / TILE_HEIGHT)
           self.y_range = self.tile_map_y + self.tile_map_height
        self.fix_position()

    def fix_position(self):
        """ ? """
        if self.x < 0:
           self.x = 0
           self.center_x = self.x + int(self.width / 2)
           self.right = self.x + self.width
           self.tile_map_x = int(self.x / TILE_WIDTH)
           self.x_range = self.tile_map_x + self.tile_map_width
        elif self.right > MAP_WIDTH:
           self.right = MAP_WIDTH
           self.x = self.right - self.width
           self.center_x = self.x + int(self.width / 2)
           self.tile_map_x = int(self.x / TILE_WIDTH)
           self.x_range = self.tile_map_x + self.tile_map_width
        if self.y < 0:
           self.y = 0
           self.center_y = self.y + int(self.height / 2)
           self.bottom = self.y + self.height
           self.tile_map_y = int(self.y / TILE_HEIGHT)
           self.y_range = self.tile_map_y + self.tile_map_height
        elif self.bottom > MAP_HEIGHT:
           self.bottom = MAP_HEIGHT
           self.y = self.bottom - self.height
           self.center_y = self.y + int(self.height / 2)
           self.tile_map_y = int(self.y / TILE_HEIGHT)
           self.y_range = self.tile_map_y + self.tile_map_height

# Startup
def save_game():
    """ Writes game data. """
    for obj in objects:
        obj.image = None
    game_data = {}
    game_data['map'] = level_map
    game_data['objects'] = objects
    game_data['player'] = player
    game_data['stairs'] = stairs
    game_data['inventory'] = inventory
    game_data['game_msgs_data'] = game_msgs_data
    game_data['game_state'] = game_state
    game_data['player_action'] = player_action
    game_data['message_log'] = message_log
    game_data['dungeon_level'] = dungeon_level
    with open('Evolution.dat', 'wb') as file:
         file_saver=pickle.Pickler(file)
         file_saver.dump(game_data)

def load_game():
    """ Reads game data. """
    global level_map, objects, player, stairs, camera, inventory, dungeon_level
    global game_msgs, game_msgs_data, game_state, player_action, message_log
    with open('Evolution.dat', 'rb') as file:
         file_loader=pickle.Unpickler(file)
         game_data=file_loader.load()
    level_map = game_data['map']
    objects = game_data['objects']
    player = game_data['player']
    stairs = game_data['stairs']
    inventory = game_data['inventory']
    game_msgs_data = game_data['game_msgs_data']     
    game_state = game_data['game_state']
    player_action = game_data['player_action']
    message_log = game_data['message_log']
    dungeon_level = game_data['dungeon_level']
    
    camera = Camera(player)
    update_gui()
    for obj in objects:
        obj.image = images[obj.image_index]
    game_msgs = []       
    for line,color in game_msgs_data:
        msg = font.render(line, True, color)
        game_msgs.append(msg)

def main():
    """ Starts the game. """
    global screen, font, images, gui, blank_surface, impact_image, impact_image_pos, impact
    pygame.init()
    
    screen = pygame.display.set_mode((640, 480),)
    pygame.display.set_caption("Evolution") # Sets game title
    font = pygame.font.SysFont('Arial', 20, bold=True)

    rogue_tiles = pygame.image.load('rogue_tiles.png').convert() # Processes images
    tile_width = int(rogue_tiles.get_width()/11)
    tile_height = rogue_tiles.get_height()
    blank_surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT)).convert()
    blank_surface.set_colorkey(blank_surface.get_at((0,0)))
    impact_image = get_impact_image()
    impact_image_pos = [0,0]
    impact = False
    images = []
    for i in range(11):
        image = rogue_tiles.subsurface(tile_width*i, 0, tile_width, tile_height).convert()
        if i not in (0, 1, 9):
           image.set_colorkey(image.get_at((0,0)))
        images.append(image)
        
    main_menu() # Opens the main menu


########################################################################
## Global scripts
if __name__ == "__main__":
    main()


########################################################################
## Old stuff
# Functions
def set_speed(score, old_background):
    ''' Changes speed as score increases, then calls set_background before returning
    both results to global script. '''
    speed = score/10 + 5
    background = set_background(speed, score, old_background)
    return speed, background

def set_background(speed, score, old_background):
    ''' Changes background color as score increases, then returns the value to set_speed. '''
    if old_background[0] >= 230: # trigger for color 2
        if old_background[1] >= 230: # trigger for color 3
            if old_background[2] >= 230: # trigger for color reset
                background = (0,0,0) # reset color (x,y,z)
            else: background = (old_background[0], old_background[1], old_background[2] + score/300) # increase z
        else: background = (old_background[0], old_background[1] + score/200, old_background[2]) # increase y
    else: background = (old_background[0] + score/100, old_background[1], old_background[2]) # increase x  
    return background

def draw_meteors(met_list, met_dim, screen, color):
    ''' Draws each meteor in met_list when called by global script. '''
    for met in met_list:
        pygame.draw.rect(screen, color, (met[0], met[1], met_dim, met_dim))
    
def drop_meteors(met_list, met_dim, width):
    ''' Adds a new meteor to the game screen at a random interval. '''
    if random.randint(0, 6) == 1: # sets the chance of spawning a meteor
        met_overlap = random.randint(0, width)
        for meteor in met_list:
                 if met_overlap == meteor[0]:
                      drop_meteors(met_list, met_dim, width) # prevents meteors from overlapping                                       
        met_pos = [met_overlap, 0] # sets meteor position
        met_list.append(met_pos) # adds meteor to list

def update_meteor_positions(met_list, height, score, speed):
    ''' Adjusts the y-position of each meteor in met_list. When a meteor reaches the end of the
    screen, this function deletes it from the list. '''
    met_list_copy = met_list[:] # creates a copy of met_list
    for i in range(len(met_list_copy)):
        met_list_copy[i][-1] += speed
        if met_list_copy[i][-1] >= height:
            del met_list[i]
            score += 1
    return score

def collision_effect():
    ''' Called by detect_collision() for decreasing the player's size.
    When it reaches zero, the game ends. '''
    global player_dim # imports player size
    player_dim -= 25
    if player_dim == 0:
        return True

def detect_collision(met_pos, player_pos, player_dim):
    ''' Called by collision_check() for comparing each meteor position to that of the player.
    Note: met_pos=[x1,y1]; player_pos=[x2,y2]; player_dim=num; met_dim=num. '''
    if (player_pos[0]-player_dim/2) <= met_pos[0] <= (player_pos[0]+player_dim) and (player_pos[1]-player_dim/2) <= met_pos[1] <= (player_pos[1]+player_dim/2):
        return collision_effect()
    else:
        return False

def collision_check(met_list, player_pos, player_dim):
    ''' Called by the global script to send meteor positions to detect_collision(). '''
    for met_pos in met_list:
        if detect_collision(met_pos, player_pos, player_dim) == True:
            return True
    return False

def escape():
    ''' Closes pygame abruptly. '''
    pygame.quit()

# Global scripts
player_color = (255,0,0)                          # rgb color of player
met_color = (244,208,63)                          # rgb color of meteors
background = (0,0,156)                            # initialize background colot (r,g,b)

player_dim = 50                                   # player size in pixels
player_pos = [width/2, height-2*player_dim]       # initial location of player

met_dim = 20                                      # meteor size in pixels
met_list = []                                     # initialize list of meteor positions

screen = pygame.display.set_mode((width, height))    # initialize game screen
game_over = False                                 # initialize game_over
score = 0                                         # initialize score
clock = pygame.time.Clock()                          # initialize clock

my_font = pygame.font.SysFont("monospace", 35)       # initialize system font

while not game_over:                              # play until game_over=True; update player_pos
    for event in pygame.event.get():                 # loop through events in queue
        if event.type == pygame.KEYDOWN:             # checks for key press
            x = player_pos[0]                     # assign current x position
            y = player_pos[1]                     # assign curren y position
            if event.key == pygame.K_LEFT or event.key == ord('a'):           # checks if left arrow;
                x -= player_dim                   # if True, moves player left
                if x < 0:                         # sets boundary
                   x = 0                   
            elif event.key == pygame.K_RIGHT or event.key == ord('d'):        # checks if right arrow;
                x += player_dim                   # moves player right
                if x > width - player_dim:        # sets boundary
                   x = width - player_dim                       
            elif event.key == pygame.K_UP or event.key == ord('w'):           # moves player up
                if y < player_dim:                # sets boundary
                   y = player_dim 
                y -= player_dim
            elif event.key == pygame.K_DOWN or event.key == ord('s'):         # moves player down
                if y > height - 2*player_dim:     # sets boundary
                   y = height - 2*player_dim 
                y += player_dim
            elif event.key == pygame.K_ESCAPE:       # exit game
                escape()
            player_pos = [x, y]                   # reset player position

    screen.fill(background)                       # refresh screen bg color
    drop_meteors(met_list, met_dim, width)        # self-explanatory; read prompt
    speed, background = set_speed(score, background) # sets speed and background color
    score = update_meteor_positions(met_list, height, score, speed)
                                                  # read prompt
    text = "Score: " + str(score)                 # create score text
    label = my_font.render(text, 1, met_color)    # render text into label
    screen.blit(label, (width-250, height-40))    # blit label to screen at
                                                  # given position
    draw_meteors(met_list, met_dim, screen, met_color) # draw meteors
    pygame.draw.rect(screen, player_color, (player_pos[0], player_pos[1], player_dim, player_dim)) # draw player

    if collision_check(met_list, player_pos, player_dim): # check for collisions
        game_over = True                       
    
    clock.tick(45)                                 # set frame rate
    pygame.display.update()                           # update screen characters

print('GAME OVER\nFinal score:', score)            # final score
label = my_font.render("GAME OVER", 12, met_color) # render text into label
screen.blit(label, (40, height-40))                # blit label to screen
pygame.display.update()
pygame.time.delay(1200)                               # delays exit of window

pygame.display.quit()
pygame.quit()                                         # leave pygame


########################################################################