#####################################################################################################
##
## EVOLUTION
##
#####################################################################################################

#####################################################################################################
# Descriptions

## Game description (SPOILERS)
### The player is stuck in a dungeon they assume is underground.
### There is one customizable safe floor to call home.
### They are free to explore and scavenge for items and materials.
### They can seek serenity, strength, or evolution.
#### SERENITY: The home is a haven of collection and creativity.
##### It may be expanded and populated by friendly creatures.
#### STRENGTH: Low floors yield high stats and strong items.
##### There is no end to the depths.
#### EVOLUTION: Special events may alter the player.
##### The effects may be beneficial, damaging, or superficial.
### ENDGAME: There is a locked room somewhere in the dungeon.
### It is only unlocked by sacrificing the player's life.
##### SERENITY: Without preparation, their life is over.
##### STRENGTH: Sufficient equipment may revive the player.
##### EVOLUTION: The player may construct a clone to sacrifice.


#####################################################################################################
# Initialization

## Imports
import pygame, random, time, sys, math, random, textwrap, pickle
from pygame.locals import *

## Set pygame parameters
SCREEN_WIDTH      = 640
SCREEN_HEIGHT     = 480

TILE_WIDTH        = 32
TILE_HEIGHT       = 32

MAP_WIDTH         = 640 * 2
MAP_HEIGHT        = 480 * 2

TILE_MAP_WIDTH    = int(MAP_WIDTH/TILE_WIDTH)
TILE_MAP_HEIGHT   = int(MAP_HEIGHT/TILE_HEIGHT)

ROOM_MAX_SIZE     = 10
ROOM_MIN_SIZE     = 4
MAX_ROOMS         = 30

## Set player parameters
HEAL_AMOUNT       = 4
LIGHTNING_DAMAGE  = 20
LIGHTNING_RANGE   = 5 * TILE_WIDTH
CONFUSE_RANGE     = 8 * TILE_WIDTH
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS   = 3 * TILE_WIDTH
FIREBALL_DAMAGE   = 12

LEVEL_UP_BASE     = 200
LEVEL_UP_FACTOR   = 150

TORCH_RADIUS      = 10

## Set GUI
MSG_X             = 5
MSG_WIDTH         = int(SCREEN_WIDTH / 10)
MSG_HEIGHT        = 3

## Set color names
BLACK             = pygame.color.THECOLORS["black"]
WHITE             = pygame.color.THECOLORS["white"]
RED               = pygame.color.THECOLORS["red"]
GREEN             = pygame.color.THECOLORS["green"]
BLUE              = pygame.color.THECOLORS["blue"]
YELLOW            = pygame.color.THECOLORS["yellow"]
ORANGE            = pygame.color.THECOLORS["orange"]
VIOLET            = pygame.color.THECOLORS["violet"]
LIGHT_CYAN        = pygame.color.THECOLORS["lightcyan"]
LIGHT_GREEN       = pygame.color.THECOLORS["lightgreen"]
LIGHT_BLUE        = pygame.color.THECOLORS["lightblue"]
LIGHT_YELLOW      = pygame.color.THECOLORS["lightyellow"]

## Other
message_log_toggle = False
home_map = []
inventory_cache = []
dungeon_level = 0
home_objects = []
step_counter = [False, 0, False, 0]

#####################################################################################################
# User interaction

def main_menu():
    """ Manages the menu. Handles player input. Only active when menu is open. """
    
    # Initialize time
    clock = pygame.time.Clock()
    
    # Initialize title
    title_font = pygame.font.SysFont('Arial', 45, bold=True)
    game_title = title_font.render("Evolution", True, GREEN) # Sets game title
    game_title_pos = (int((SCREEN_WIDTH - game_title.get_width())/2), 150)
    
    # Initialize cursor
    cursor_img = pygame.Surface((16, 16)).convert()
    cursor_img.set_colorkey(cursor_img.get_at((0,0)))
    pygame.draw.polygon(cursor_img, RED, [(0, 0), (16, 8), (0, 16)], 0)
    cursor_img_pos = [195, 254]
    
    # Initialize menu options
    menu_choices = ["NEW GAME", "CONTINUE", "SAVE", "CONTROLS", "QUIT"]   
    for i in range(len(menu_choices)):
        menu_choices[i] = font.render(menu_choices[i], True, WHITE)
    choice, choices_length = 0, len(menu_choices)-1
    
    # Allow player to select menu option
    while True:
        clock.tick(30)
        
        # Called for user input
        for event in pygame.event.get():

            if event.type == KEYDOWN:
            
                if event.key == K_ESCAPE: # resume
                    play_game()
                    
                elif event.key == K_UP: # Up
                    cursor_img_pos[1] -= 24
                    choice -= 1
                    if choice < 0:
                        choice = choices_length
                        cursor_img_pos[1] = 350 # change this if you add or remove menu choices
                        
                elif event.key == K_DOWN: # Down
                    cursor_img_pos[1] += 24
                    choice += 1
                    if choice > choices_length:
                        choice = 0
                        cursor_img_pos[1] = 254
                        
                elif event.key == K_RETURN:
                    if choice == 0:  # >> NEW GAME <<
                        new_game(True)
                        play_game()
                        
                    if choice == 1:  # >> CONTINUE <<
                        new_game(False, filename="player_data.pkl")
                        play_game()
                    
                    if choice == 2:  # >> SAVE <<
                        player.dungeon_level = dungeon_level
                        player.save("player_data.pkl")
                        if dungeon_level == 0:
                            layout_data = {}
                            for row_index, row in enumerate(level_map):
                                for col_index, tile in enumerate(row):
                                    layout_data[(row_index, col_index)] = {
                                        'blocked': tile.blocked,
                                        'x': tile.x,
                                        'y': tile.y,
                                        'block_sight': tile.block_sight,
                                        'visible': tile.visible,
                                        'explored': tile.explored
                                        }
                            with open("home_data.pkl", 'wb') as file:
                                pickle.dump(layout_data, file)
                        
                    if choice == 3:  # >> CONTROLS <<
                        menu('Controls', ['Move:                                       arrow keys',
                                          'Descend stairs or grab item:    enter',
                                          'Ascend stairs to home:            shift',
                                          'Check stats:                             1',
                                          'Use item in inventory:              2',
                                          'Drop item from inventory:        3',
                                          'Toggle messages:                    ?'], True)
                    
                    elif choice == 4:  # >> QUIT <<
                        pygame.quit()
                        sys.exit()

        # Set menu background
        screen.fill(BLACK)
        
        # Renders menu to update cursor location
        y = 250
        for menu_choice in menu_choices:
            screen.blit(menu_choice,(230,y))
            y += 24
        screen.blit(game_title, game_title_pos)
        screen.blit(cursor_img, cursor_img_pos)                
        pygame.display.flip()

def play_game():
    """ Processes user input and triggers monster movement. """
    
    global player_action, message_log, message_log_toggle
    
    clock = pygame.time.Clock() # Keeps track of time
    player_move = False
    pygame.key.set_repeat(400, 100) # Sets key delay and interval for held keys
    
    while True:
        clock.tick(30)
        active_effects()
        event = pygame.event.get()
        if event:
            
            # Save and quit
            if event[0].type == QUIT:
                save_game()
                pygame.quit()
                sys.exit()
            
            # Keep playing
            if game_state == 'playing':
                if event[0].type == KEYDOWN:
                    if event[0].key == K_ESCAPE:
                        return
                    message_log = False
                    
                    # Move or attack
                    if event[0].key == K_UP:
                        player_move_or_attack(0, -TILE_HEIGHT)
                    elif event[0].key == K_DOWN:
                        player_move_or_attack(0, TILE_HEIGHT)
                    if event[0].key == K_LEFT:
                        player_move_or_attack(-TILE_WIDTH, 0)
                    elif event[0].key == K_RIGHT:
                        player_move_or_attack(TILE_WIDTH, 0)

                    # Pick up item or climb stairs
                    if event[0].key == K_RETURN:
                        if player.tile.item and player.tile.item.item: 
                            player.tile.item.item.pick_up()
                            player.tile.item = None # Hides icon
                        elif stairs.x == player.x and stairs.y == player.y:
                            next_level()
                    if event[0].key == K_RSHIFT and dungeon_level != 0: # Ascend stairs to home
                        if stairs.x == player.x and stairs.y == player.y:
                            go_home()

                    # View player information (1)
                    if event[0].key == K_1 or event[0].key == K_KP1:
                        level_up_exp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                        menu('Character Information', ['Level:                                ' + str(player.level),
                                                       'Experience:                       ' + str(player.fighter.exp),
                                                       'Experience to level up:    ' + str(level_up_exp),
                                                       'Maximum HP:                    ' + str(player.fighter.max_hp),
                                                       'Attack:                             ' + str(player.fighter.power),
                                                       'Defense:                           ' + str(player.fighter.defense)], True)
                            
                    # Check inventory and use item (2)
                    if event[0].key == K_2 or event[0].key == K_KP2:
                        chosen_item = inventory_menu("Inventory: Use Item")
                        if chosen_item is not None:
                            chosen_item.use()
                            update_gui()
                    
                    # Drop item (3)
                    if event[0].key == K_3 or event[0].key == K_KP3:
                        if player.tile.item:
                            message("There's already something here")
                        else:
                            chosen_item = inventory_menu('Inventory: Drop Item')
                            if chosen_item is not None:
                                chosen_item.drop()
                    
                    # Toggles messages
                    if event[0].key == K_SLASH:
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

def menu(header, options, no_letters=False):
    """ Generic menu """
    
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
                    return
                else: # Converts ASCII code to an index, then returns option if applicable
                    if event.unicode != '':
                        index = ord(event.unicode) - ord('a')
                        if index >= 0 and index < len(options): 
                            return index
                        else:
                            return None


#####################################################################################################
# Core

def main():
    """ Starts the game. Only called at starup. """
    
    global screen, font, images, gui, blank_surface, impact_image, impact_image_pos, impact
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480),)
    pygame.display.set_caption("Evolution") # Sets game title
    font = pygame.font.SysFont('Arial', 20, bold=True)

    # Initialize images
    rogue_tiles = pygame.image.load('rogue_tiles.png').convert() # Processes images
    tile_width = int(rogue_tiles.get_width()/11)
    tile_height = rogue_tiles.get_height()
    images = []
    for i in range(11):
        image = rogue_tiles.subsurface(tile_width*i, 0, tile_width, tile_height).convert()
        if i not in (0, 1, 9):
           image.set_colorkey(image.get_at((0,0)))
        images.append(image)
    
    # Used in combat
    blank_surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT)).convert()
    blank_surface.set_colorkey(blank_surface.get_at((0,0)))
    impact_image = get_impact_image()
    impact_image_pos = [0,0]
    impact = False
        
    main_menu() # Opens the main menu

def new_game(new, filename=None):
    """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms. """
    
    global player, camera, game_state, player_action, active_entities, level_map
    global gui, game_msgs, game_msgs_data, message_log, inventory,  dungeon_level
    global dungeon_level_cache, home_objects, home_object_positions, new_game_trigger, save_objects, active_effects_cache, friendly, teleport, inventory_cache, dig
    
    if new:
        # Clear prior data
        dungeon_level, dungeon_level_cache = 0, 0
        home_objects, home_object_positions = [], []
        new_game_trigger = True
        save_objects = []
        active_effects_cache = []
        inventory_cache = []
        friendly, teleport, dig = False, False, False

        # Generate new player
        fighter_component = Fighter(hp=100, defense=100, power=100, exp=0, death_function=player_death)
        player = Object(TILE_WIDTH*10, TILE_HEIGHT*7, images[2], "player", blocks=True, fighter=fighter_component, image_num=2, hp=100, defense=100, power=100, tile=True, level=1, dungeon_level=0)

        # Generate map and sets the player in a room
        make_home()
        
        inventory = []
        active_entities = []
    
    else:       
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        fighter_component = Fighter(hp=data['hp'], defense=data['defense'], power=data['power'], exp=0, death_function=player_death)
        player = Object(data['x'], data['y'], images[data['image_index']], "player", blocks=True, fighter=fighter_component, image_num=data['image_index'], hp=data['hp'], defense=data['defense'], power=data['power'], level=data['level'], dungeon_level=data['dungeon_level'])
        dungeon_level = player.dungeon_level
        
        # Generate map and sets the player in a room
        load_home()
    
    camera = Camera(player)
    camera.update()
    
    game_state = 'playing' # as opposed to 'dead'
    player_action = 'didnt-take-turn' 
    
    update_gui() # places health and dungeon level on the screen
    game_msgs, game_msgs_data = [], [] # holds game messages and their colors
    message_log = True
    message('Welcome!', RED)
    
    if new:
        # Sets initial inventory
        slot_set, power_bonus_set = 'right hand', 2
        equipment_component = Equipment(slot=slot_set, power_bonus=power_bonus_set)
        equipment_list = [slot_set, power_bonus_set]
        dagger = Object(0, 0, images[10], 'dagger', equipment=equipment_component, equipment_list=[slot_set, power_bonus_set])
        
        slot_set, power_bonus_set = 'right hand', 0
        equipment_component = Equipment(slot=slot_set, power_bonus=power_bonus_set, timer=True)
        equipment_list = [slot_set, power_bonus_set]
        shovel = Object(0, 0, images[10], 'shovel', equipment=equipment_component, equipment_list=[slot_set, power_bonus_set])

        inventory.append(dagger)
        inventory.append(shovel)
        inventory_cache.append('dagger')
        inventory_cache.append('shovel')
        step_counter[3] = shovel
        equipment_component.equip()

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

def update_gui():
    """ Updates health and dungeon level. """
    global gui
    gui = font.render('HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp) +  ' '*60 + ' Dungeon level ' + str(dungeon_level), True, YELLOW)


#####################################################################################################
# Environment creation

def create_room(room):
    """ Creates tiles for a room's floor and walls.
        Takes Rectangle object as an argument with parameters for width (x2 - x1) and height (y2 - y1). """
    
    global level_map
    
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            tile = level_map[x][y]
            tile.blocked = False # False for path, True for barrier
            tile.block_sight = False # False for floor, True for wall
            tile.room = room

def create_h_tunnel(x1, x2, y):
    """ Creates horizontal tunnel. min() and max() are used if x1 is greater than x2. """
    
    global level_map
    
    for x in range(min(x1, x2), max(x1, x2) + 1):
        level_map[x][y].blocked = False
        level_map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
    
    global level_map
    
    for y in range(min(y1, y2), max(y1, y2) + 1):
        level_map[x][y].blocked = False
        level_map[x][y].block_sight = False

def load_home():
    global level_map, dungeon_level
    
    objects = [player]
    
    # Loads floor plan
    with open("home_data.pkl", 'rb') as file:
        layout_data = pickle.load(file)
    level_map = []
    for row_index in range(max(layout_data.keys(), key=lambda x: x[0])[0] + 1):
        row = []
        for col_index in range(max(layout_data.keys(), key=lambda x: x[1])[1] + 1):
            tile_data = layout_data.get((row_index, col_index))
            if tile_data is not None:
                row.append(Tile(
                    tile_data['blocked'],
                    tile_data['x'],
                    tile_data['y'],
                    tile_data['block_sight'],
                    tile_data['visible'],
                    explored=False
                    ))
            else:
                row.append(None)
        level_map.append(row)
    
    # Place player
    #player.x = 480
    #player.y = 480
    level_map[int(player.x/32)][int(player.y/32)].entity = player
    player.tile = level_map[int(player.x/32)][int(player.y/32)]
    check_tile(int(player.x/32), int(player.y/32))
    place_objects(home=True, fresh_start=False) # Adds content to the room

    # Creates stairs at the center of the last room
    stairs = Object(18 * TILE_WIDTH, 15 * TILE_HEIGHT, images[9], 'stairs', image_num=9, appended='objects')
    level_map[18][15].item = stairs
    objects.append(stairs)
    stairs.send_to_back()

def make_home():
    """ Initializes and generates the player's home, its rooms, and its contents. """
    
    global level_map, objects, stairs, new_game_trigger
    
    objects = [player] # holds objects in home
    
    # Defines the map. [[x for x in range(2)] for y in range(3)] yields [[0,1], [0,1], [0,1]], for example.
    level_map = [[ Tile(True, x, y, visible=False) # initialize walls at each point in the map
              for y in range(0, MAP_HEIGHT*5, TILE_HEIGHT) ]
                for x in range(0, MAP_WIDTH*5, TILE_WIDTH) ]
 
    w = ROOM_MAX_SIZE # random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE) # Sets a random width and height for a single room
    h = ROOM_MAX_SIZE # random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    
    x = 10 #random.randint(0, TILE_MAP_WIDTH - w - 1) # Set a random position within the map
    y = 10 #random.randint(0, TILE_MAP_HEIGHT - h - 1)
    new_room = Rectangle(x, y, w, h) # Places the room at the random location.
    create_room(new_room) # Sets parameters for the room's floor
    (new_x, new_y) = new_room.center() # Holds coordinates for the room's center
    
    # Place player
    player.x = new_x * TILE_WIDTH
    player.y = new_y * TILE_HEIGHT
    level_map[new_x][new_y].entity = player
    player.tile = level_map[new_x][new_y]
    check_tile(new_x, new_y)
    new_x, new_y = new_x + 3, new_y # Sets the position for the stairs
    place_objects(new_room, home=True, fresh_start=new_game_trigger) # Adds content to the room
    if new_game_trigger:
        new_game_trigger = False

    # Creates stairs at the center of the last room
    stairs = Object(new_x * TILE_WIDTH, new_y * TILE_HEIGHT, images[9], 'stairs', image_num=9, appended='objects')
    level_map[new_x][new_y].item = stairs
    objects.append(stairs)
    stairs.send_to_back()


def place_objects(room=None, home=False, fresh_start=True):
    """ Decides the chance of each monster or item appearing, then generates and places them. """
    
    global home_objects
    
    if not room: # Lazy bug fix
        room = Rectangle(1,1,2,2)
    
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]]) # Maximum per room. [value, level]
    monster_chances = {} # Chance of spawning monster by monster type
    monster_chances['orc'] = 80 # Sets spawn chance for orcs
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
 
    max_items = from_dungeon_level([[1, 1], [2, 4]]) # Maximum per room
    item_chances = {} # Chance of spawning item by item type
    item_chances['heal'] = 35 # Sets spawn chance for potions
    item_chances['shovel'] = 35
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] =  from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   from_dungeon_level([[10, 2]])
    item_chances['sword'] =     from_dungeon_level([[5, 4]])
    item_chances['shield'] =    from_dungeon_level([[15, 8]])

    if home: # Places items in home
        if fresh_start:
            for i in range(4): # Places default items
                x = room.x1+3+i # Sets location
                y = room.y1+1
                if i == 0:
                    item_component = Item(use_function=cast_heal)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[6], 'healing potion', item=item_component, image_num=6, appended='objects')
                elif i == 1:
                    item_component = Item(use_function=cast_lightning)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5], 'scroll of lightning bolt', item=item_component, image_num=5, appended='objects')
                elif i == 2:
                    item_component = Item(use_function=cast_fireball)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5], 'scroll of fireball', item=item_component, image_num=5, appended='objects')
                elif i == 3:
                    item_component = Item()
                    item = Object(0, 0, images[0], 'scroll of fireball', item=item_component, image_num=0, appended='objects')
                home_objects.append(item)
                home_object_positions.append([x, y])
                objects.append(item)
                level_map[x][y].item = item
        
        else: # Places last known items
            for i in range(len(home_objects)):
                if home_objects[i] != 0:
                    item = home_objects[i]
                    x, y = home_object_positions[i][0], home_object_positions[i][1]
                    objects.append(item)
                    #menu(f'{x}, {y}', 'test')
                    level_map[x][y].item = item
        
        # Generates Otzz
        x = random.randint(11, 19) # Sets random location
        y = random.randint(11, 19)
        hp_set, defense_set, power_set, exp_set = 20, 0, 0, 0
        fighter_component = Fighter(hp=hp_set, defense=defense_set, power=power_set, exp=exp_set, death_function=monster_death)
        ai_component = BasicMonster()             
        monster = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[3], 'orc', blocks=True, fighter=fighter_component, ai=ai_component, image_num=3, appended='objects')
        home_objects.append(item)
        home_object_positions.append([x, y])
        objects.append(monster)
        level_map[x][y].entity = monster # Places monster?
        monster.tile = level_map[x][y]

    else: # Places items and monsters in dungeon
        num_monsters = random.choice([0, 0, 0, 0, 1, max_monsters])
        num_items = random.randint(0, max_items) # Sets number of items?
        
        for i in range(num_monsters): # Places monsters
            x = random.randint(room.x1+1, room.x2-1) # Sets random location
            y = random.randint(room.y1+1, room.y2-1)
            if not is_blocked(x, y):
                choice = random_choice(monster_chances) # Sets random monster
                if choice == 'orc': # Creates an orc
                    hp_set, defense_set, power_set, exp_set = 20, 0, 4, 35
                    fighter_component = Fighter(hp=hp_set, defense=defense_set, power=power_set, exp=exp_set, death_function=monster_death)
                    ai_component = BasicMonster()               
                    monster = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[3], 'orc', blocks=True, fighter=fighter_component, ai=ai_component, image_num=3)
                elif choice == 'troll':
                    hp_set, defense_set, power_set, exp_set = 30, 2, 8, 100
                    fighter_component = Fighter(hp=hp_set, defense=defense_set, power=power_set, exp=exp_set, death_function=monster_death)
                    ai_component = BasicMonster()               
                    monster = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[4], 'troll', blocks=True, fighter=fighter_component, ai=ai_component, image_num=4, appended='objects')
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
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[6], 'healing potion', item=item_component, image_num=6, appended='objects')
                elif choice == 'lightning': # Creates a lightning scroll
                    item_component = Item(use_function=cast_lightning)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5], 'scroll of lightning bolt', item=item_component, image_num=5, appended='objects')
                elif choice == 'fireball': # Creates a fireball scroll
                    item_component = Item(use_function=cast_fireball)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5], 'scroll of fireball', item=item_component, image_num=5, appended='objects')
                elif choice == 'confuse': # Creates a confusion scroll
                    item_component = Item(use_function=cast_confuse)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[5], 'scroll of confusion', item=item_component, image_num=5, appended='objects')
                elif choice == 'sword': # Creates a sword
                    equipment_component = Equipment(slot='right hand', power_bonus=3)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[7], 'sword', equipment=equipment_component, image_num=7, appended='objects')
                elif choice == 'shield': # Creates a shield
                    equipment_component = Equipment(slot='left hand', defense_bonus=1)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[8], 'shield', equipment=equipment_component, image_num=8, appended='objects')
                elif choice == 'shovel':
                    equipment_component = Equipment(slot='right hand', power_bonus=0, timer=True)
                    item = Object(x*TILE_WIDTH, y*TILE_HEIGHT, images[10], 'shovel', equipment=equipment_component, equipment_list=['right hand', 0])                
                objects.append(item)
                level_map[x][y].item = item
                item.send_to_back()


#####################################################################################################
# Gameplay

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
    #load_home()
    camera.update()
    time.sleep(0.5)
    update_gui()

def active_effects():
    global friendly, teleport, dig
    if 'healing potion' in inventory_cache:
        player.image = images[3]
        friendly = True
    else:
        player.image = images[2]
        friendly = False
    if step_counter[0]:
        dig = True
    else:
        dig = False
    if 'scroll of lightning bolt' in inventory_cache:
        teleport = True
    else:
        teleport = False

def player_move_or_attack(dx, dy):
    """ Moves the player by the given amount. """
    
    global player_action, dig, step_counter
    
    target = None

    # Find new position
    x = int((player.x + dx)/TILE_WIDTH)
    y = int((player.y + dy)/TILE_HEIGHT)
    
    # Move player if path is clear
    # Remove (level_map[x][y].entity and dungeon_level != 0) for default
    if (level_map[x][y].entity == player and dungeon_level == 0) or not is_blocked(x, y):
        player.x += dx
        player.y += dy
        player.tile.entity = None # remove player from previous position; invisible barrier otherwise
        level_map[x][y].entity = player
        player.tile = level_map[x][y]
        check_tile(x, y)
        camera.update()
    
    # Attack target
    elif level_map[x][y].entity and dungeon_level != 0: 
        target = level_map[x][y].entity
        player.fighter.attack(target)
    
    # Dig tunnel
    else:
        if dig == True: # True if shovel equipped
            
            # Move player
            if player.x >= 64 and player.y >= 64:
                player.x += dx
                player.y += dy
                player.tile.entity = None
                level_map[x][y].blocked = False
                level_map[x][y].block_sight = False
                level_map[x][y].entity = player
                player.tile = level_map[x][y]
                check_tile(x, y) # Reveals tile
                camera.update()
                
                if step_counter[1] >= 10:
                    inventory[inventory.index(step_counter[3])].item.drop()
                    player.tile.item = None # Hides icon
                    step_counter = [False, 0, False, 0]
                else:
                    step_counter[1] += 1
            
        #if (teleport == True) and (is_blocked(player.x+dx,player.y+dy) == True):
            #if (dx < 0) or (dy < 0):
            #    neg = -1
            #else:
            #    neg = 1
            #for i in range(1000):
            #    #print(f'old position: {player.x} and {player.y}')
            #    #print(f'new position: {player.x+dx*(i+1)} and {player.y+dy*(i+1)}')
            #    if dx == 0:
            #        #print(int(player.y/TILE_HEIGHT)+i)
            #        if is_blocked(int(player.x/TILE_WIDTH),int(player.y/TILE_HEIGHT)+i) == False:
            #            player.y = player.y+TILE_HEIGHT*i*neg
            #            player.tile.entity = None
            #            level_map[x][y].entity = player
            #            player.tile = level_map[x][y]
            #            check_tile(x, y)
            #            camera.update()
            #            break
            #    if dy == 0:
            #        if is_blocked(int(player.x/TILE_WIDTH)+TILE_WIDTH*i,int(player.y/TILE_HEIGHT)) == False:
            #            player.x = player.x+TILE_WIDTH*i
            #            player.tile.entity = None
            #            level_map[x][y].entity = player
            #            player.tile = level_map[x][y]
            #            check_tile(x, y)
            #            camera.update()
            #            break
    player_action = 'took-turn'

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


#####################################################################################################
# Utility

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
       if tile.room and not tile.room.explored:
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
    
    # Draw visible tiles
    for y in range(camera.tile_map_y, camera.y_range):
        for x in range(camera.tile_map_x, camera.x_range):
            tile = level_map[x][y]
            if tile.visible:
                
                # Generates wall; sets wall image
                if tile.block_sight:
                    screen.blit(images[0], (tile.x-camera.x, tile.y-camera.y))
                
                # Generates floor and entities; sets floor image
                else:
                    screen.blit(images[1], (tile.x-camera.x, tile.y-camera.y))
                    if tile.item:
                        tile.item.draw(screen)
                    if tile.entity:
                        tile.entity.draw(screen)
                        active_entities.append(tile.entity)

    # ?
    if impact:
       screen.blit(impact_image, impact_image_pos)
    screen.blit(gui, (10,456))

    # Print messages
    if message_log: 
       y = 10
       for msg in game_msgs:
           screen.blit(msg, (5,y))
           y += 24
    pygame.display.flip()

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

def from_dungeon_level(table):
    """ Returns a value that depends on the dungeon level. The table specifies what value occurs after each level with 0 as the default. """
    
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def is_blocked(x, y):
    try:
        if level_map[x][y].blocked: # Checks for barriers
            return True
        if level_map[x][y].entity: # Checks for monsters
            return True
    except:
        return True
    return False

def get_equipped_in_slot(slot):
    """ Returns the equipment in a slot, or None if it's empty. """
    
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def entity_flash(entity):
    """ Death animation. """
    
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


#####################################################################################################
# Dungeons

def make_map():
    """ Initializes and generates the map, its rooms, and its contents. """
    global level_map, objects, stairs
    objects = [player]
    rooms = []
    num_rooms = 0 # Counts number of generated rooms
    
    level_map = [[ Tile(True, x, y) # Initializes tiles at each point in the map.
              for y in range(0, MAP_HEIGHT, TILE_HEIGHT) ]
                for x in range(0, MAP_WIDTH, TILE_WIDTH) ]
 
    # Creates random set of rooms and places them in the map
    for r in range(MAX_ROOMS):
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
    stairs = Object(new_x * TILE_WIDTH, new_y * TILE_HEIGHT, images[9], 'stairs', image_num=9, appended='objects')
    level_map[new_x][new_y].item = stairs
    objects.append(stairs)
    stairs.send_to_back()

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

#####################################################################################################
# Classes

class Object:
    """ Defines a generic object, such as the player, a monster, an item, or stairs. """
    
    def __init__(self, x, y, image, name, blocks=False, fighter=None, hp=None, power=None, defense=None, ai=None, item=None, equipment=None, image_num=False, item_list=False, equipment_list=False, appended=False, tile=None, level=None, dungeon_level=None):
        """ Defines object and object parameters, such as name, image and image size, stats, and equipment.
            Initializes player, monster, stairs, and items. 
            player = Object(TILE_WIDTH*10, TILE_HEIGHT*7, images[2], "player", blocks=True, fighter=fighter_component, image_num=2, fighter_list=[hp_set, defense_set, power_set, exp_set, 'player_death'])
            player.level = 1 """
        
        global level_map

        # Assign object parameters
        self.x           = x                              # tile width (integer)
        self.y           = y                              # tile height (integer)
        
        self.image       = image                      # tile image (integer, pulled from rogue_tiles.png)
        self.image_index = images.index(image)  # currently only used for player/monster death (integer)
        
        self.name        = name                        # name (string)
        
        self.blocks      = blocks                    # unknown
        self.tile        = None                        # initialized tile location (?)
        
        self.fighter     = fighter                  # true for player or monster
        self.level       = level
        self.hp          = hp
        self.defense     = defense
        self.power       = power

        self.ai          = ai                            # true for monsters
        self.item        = item                        # true for usable items
        self.equipment   = equipment              # true for wearable items
        self.dungeon_level = dungeon_level

        # Lets player and monsters fight
        if self.fighter:
            self.fighter.owner = self
        
        # Lets monsters control themselves
        if self.ai:
            self.ai.owner = self
        
        # Lets items be usable
        if self.item:
            self.item.owner = self
            
        # Lets items be wearable
        if self.equipment: # Lets the Equipment component know who owns it
            self.equipment.owner = self
            self.item            = Item()
            self.item.owner      = self
        
    def save(self, filename):
        data = {
            'x':           self.x,
            'y':           self.y,
            'image_index': self.image_index,
            'name':        self.name,
            'blocks':      self.blocks,
            'ai':          self.ai,
            'item':        self.item,
            'equipment':   self.equipment,
            'hp':          self.hp,
            'defense':     self.defense,
            'power':       self.power,
            'level':       self.level,
            'dungeon_level': self.dungeon_level
        }
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
            
    def move(self, dx, dy):
        """ Moves the player by the given amount if the destination is not blocked. """
        x = int((self.x + dx)/TILE_WIDTH)
        y = int((self.y + dy)/TILE_HEIGHT)
        if not is_blocked(x, y):
            self.x                 += dx
            self.y                 += dy
            self.tile.entity       = None
            level_map[x][y].entity = self
            self.tile              = level_map[x][y]

    def move_towards(self, target_x, target_y):
        """ Moves object towards target. """
        dx       = target_x - self.x
        dy       = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx       = int(round(dx / distance)) * TILE_WIDTH # Restricts to map grid
        dy       = int(round(dy / distance)) * TILE_HEIGHT
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
        try:
            objects.remove(self)
        except:
            print("Not in objects.")
        objects.insert(0, self)
       
    def draw(self, surface):
        """ Draws the object at its position. """
        surface.blit(self.image, (self.x-camera.x, self.y-camera.y))

class Fighter:
    """ Defines combat-related properties and methods (monster, player, NPC).
        Used by fighter_component, attack(), cast_lightning(), cast_fireball(), player_move_or_attack(), take_turn(), next_level(), go_home(), and cast_heal().
        Can call player_death() and monster_death(). 
        fighter_component = Fighter(hp=100, defense=100, power=100, exp=0, death_function=player_death) """
    
    def __init__(self, hp, defense, power, exp, death_function=None):
        """ Defines fighter stats. """
        
        self.max_hp         = hp                # initial health (integer)
        self.hp             = hp                # current health (integer)
        self.defense        = defense           # defense stat (integer)
        self.power          = power             # attack stat (integer)
        self.exp            = exp               # experience gained (integer, zero for player)
        self.death_function = death_function    # player death or monster death

    def save(self, filename):
        data = {
            'max_hp':         self.max_hp,
            'hp':             self.hp,
            'defense':        self.defense,
            'power':          self.power,
            'exp':            self.exp,
            'death_function': self.death_function
        }
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
    
    def attack(self, target):
        """ Calculates and applies attack damage.
            Used by player_move_or_attack() and take_turn() for monsters. """
        
        if self.owner.name != target.name:                  # prevents self-inflicted damage
            damage = self.power - target.fighter.defense    # accounts for defense stats
            if damage > 0:                                  # damages the target
                message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                target.fighter.take_damage(damage)
            else:
                message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        """ Applies damage if possible.
            Used by attack(), cast_lightning(), and cast_fireball().
            Calls player_death() or monster_death() if applicable. """
        
        if damage > 0:
            self.hp -= damage
            entity_flash(self.owner)
            if self.owner == player:
               update_gui()
            if self.hp <= 0:                    # checks for death
                self.hp = 0
                update_gui()
                function = self.death_function  # kills player or monster
                if function is not None:
                    function(self.owner)
                if self.owner != player:        # gives experience to the player
                    player.fighter.exp += self.exp
                    check_level_up()
    
    def heal(self, amount):
        """ Heals player by the given amount without going over the maximum.
            Used when leveling up, going home, or using a health item. """
        
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class Item:
    """ Defines an item that can be picked up and used. """
    
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        """ Adds an item to the player's inventory and removes it from the map. """
        
        global inventory_cache
        
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', RED)
        else:
            inventory.append(self.owner)
            inventory_cache.append(self.owner.name)
            if self.owner in home_objects:
                index = home_objects.index(self.owner)
                home_objects.pop(index) # Removes item from home
                home_object_positions.pop(index)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', GREEN)
            equipment = self.owner.equipment # Automatically equips item if possible
            if equipment and get_equipped_in_slot(equipment.slot) is None:
               equipment.equip()

    def drop(self):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home. """
        
        if self.owner.equipment:
            self.owner.equipment.dequip()
        if dungeon_level == 0: # Saves dropped items at home
            home_objects.append(self.owner)
            home_object_positions.append([int(player.x/TILE_WIDTH), int(player.y/TILE_HEIGHT)])
        objects.append(self.owner)
        inventory.remove(self.owner)
        inventory_cache.remove(self.owner.name)
        self.owner.x = player.x
        self.owner.y = player.y
        player.tile.item = self.owner
        message('You dropped a ' + self.owner.name + '.', YELLOW)   

    def use(self):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        global step_counter
        
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
    
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0, timer=False):
        """ Defines equipment and equipment parameters. """
        
        self.power_bonus   = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus  = max_hp_bonus
        self.slot          = slot
        self.is_equipped   = False
        self.timer = timer

    def toggle_equip(self):
        """ Toggles the equip/unequip status. """
        
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        """ Unequips object if the slot is already being used. """
        
        global step_counter
        
        old_equipment          = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped       = True
        player.fighter.power   += self.power_bonus
        player.fighter.defense += self.defense_bonus
        player.fighter.max_hp  += self.max_hp_bonus
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', LIGHT_GREEN)
        
        if self.timer:
            step_counter[0] = True
            step_counter[1] += 1
            step_counter[3] = self.owner

    def dequip(self):
        """ Unequips an object and shows a message about it. """
        
        if not self.is_equipped: return
        self.is_equipped = False
        player.fighter.power   -= self.power_bonus
        player.fighter.defense -= self.defense_bonus
        player.fighter.max_hp  -= self.max_hp_bonus
        if player.fighter.hp > player.fighter.max_hp:
           player.fighter.hp = player.fighter.max_hp 
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', LIGHT_YELLOW)

        if self.timer:
            step_counter[0] = False

class BasicMonster:
    """ Defines the AI for a basic monster. """
    
    def take_turn(self):
        """ Lets a basic monster takes its turn. """
        
        monster = self.owner
        if monster.tile.visible:
            distance = monster.distance_to(player)
            if distance < 128:
                if (dungeon_level != 0) and (friendly == False):
                    if distance >= 64: # Moves towards player if far away
                        monster.move_towards(player.x, player.y)
                    elif player.fighter.hp > 0: # Attacks player
                        monster.fighter.attack(player)
                else:
                    if distance >= 100:
                        monster.move_towards(player.x, player.y)

class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. 
        Used in make_home() and make_map(). """
    
    def __init__(self, blocked, x, y, block_sight = None, visible=False, explored=False):
        self.blocked = blocked
        if block_sight is None: block_sight = blocked # blocked makes walls, None makes floor
        self.block_sight = block_sight
        self.x           = x
        self.y           = y
        self.visible     = visible # True makes everything visible
        self.explored    = explored # True makes everything hidden
        self.room        = None
        self.entity      = None
        self.item        = None

class Rectangle:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, x, y, w, h):
        """ Defines a rectangle and its size. """
        
        self.x1       = x
        self.y1       = y
        self.x2       = x + w
        self.y2       = y + h
        self.explored = False # False for visible, True for hidden

    def center(self):
        """ Finds the center of the rectangle. """
        
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)
 
    def intersect(self, other):
        """ Returns true if this rectangle intersects with another one. """
        
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)        

class Camera:
    """ Defines a camera to follow the player. """
    
    def __init__(self, target):
        """ Defines a camera and its parameters. """
        
        self.target          = target
        self.width           = SCREEN_WIDTH
        self.height          = SCREEN_HEIGHT + TILE_HEIGHT
        self.x               = self.target.x - int(self.width / 2)
        self.y               = self.target.y - int(self.height / 2)
        self.center_x        = self.x + int(self.width / 2)
        self.center_y        = self.y + int(self.height / 2)
        self.right           = self.x + self.width
        self.bottom          = self.y + self.height
        self.tile_map_x      = int(self.x / TILE_WIDTH)
        self.tile_map_y      = int(self.y / TILE_HEIGHT)
        self.tile_map_width  = int(self.width / TILE_WIDTH)
        self.tile_map_height = int(self.height / TILE_HEIGHT)
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        self.fix_position()
        
    def update(self):
        """ ? """
        
        if self.target.x != self.center_x:
            x_move          = self.target.x - self.center_x
            self.x          += x_move
            self.center_x   += x_move
            self.right      += x_move
            self.tile_map_x = int(self.x / TILE_WIDTH)
            self.x_range    = self.tile_map_x + self.tile_map_width
        #if self.y > 0 and  self.target.y < self.center_y \
        #or self.bottom < MAP_HEIGHT and  self.target.y > self.center_y:
        if self.target.y != self.center_y:   
            y_move          = self.target.y - self.center_y
            self.y          += y_move
            self.center_y   += y_move
            self.bottom     += y_move
            self.tile_map_y = int(self.y / TILE_HEIGHT)
            self.y_range    = self.tile_map_y + self.tile_map_height
        self.fix_position()

    def fix_position(self):
        """ ? """
        if dungeon_level != 0:
            if self.x < 0:
               self.x          = 0
               self.center_x   = self.x + int(self.width / 2)
               self.right      = self.x + self.width
               self.tile_map_x = int(self.x / TILE_WIDTH)
               self.x_range    = self.tile_map_x + self.tile_map_width
            elif self.right > MAP_WIDTH:
               self.right      = MAP_WIDTH
               self.x          = self.right - self.width
               self.center_x   = self.x + int(self.width / 2)
               self.tile_map_x = int(self.x / TILE_WIDTH)
               self.x_range    = self.tile_map_x + self.tile_map_width
            if self.y < 0:
               self.y          = 0
               self.center_y   = self.y + int(self.height / 2)
               self.bottom     = self.y + self.height
               self.tile_map_y = int(self.y / TILE_HEIGHT)
               self.y_range    = self.tile_map_y + self.tile_map_height
            elif self.bottom > MAP_HEIGHT:
               self.bottom     = MAP_HEIGHT
               self.y          = self.bottom - self.height
               self.center_y   = self.y + int(self.height / 2)
               self.tile_map_y = int(self.y / TILE_HEIGHT)
               self.y_range    = self.tile_map_y + self.tile_map_height


#####################################################################################################
# Global scripts

if __name__ == "__main__":
    main()


#####################################################################################################