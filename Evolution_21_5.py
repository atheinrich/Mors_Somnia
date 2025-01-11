#######################################################################################################################################################
##
## MORS SOMNIA
##
#######################################################################################################################################################

#######################################################################################################################################################
# Imports
## Game mechanics
import pygame
from pygame.locals import *
import random
import textwrap
import time

## File saving
import pickle
import os
import copy

## Debugging
import sys
import inspect

# Aesthetics
from PIL import Image, ImageFilter

#######################################################################################################################################################
# Global values
super_dig = False
movement_speed_toggle, toggle_list = 0, ['Default', 'Fast', 'Slow']
last_press_time, cooldown_time = 0, 0.5

#######################################################################################################################################################
# Core
## Initialization
def debug_call(func):
    """ Just a print statement for debugging. Shows which function is called alongside variable details. """

    def wrapped_function(*args, **kwargs):
        print(f"{func.__name__:<30}{time.strftime('%M:%S', time.localtime())}")
        return func(*args, **kwargs)
    return wrapped_function

def main():
    """ Initializes the essentials and opens the main menu. """
    
    global pyg, mech, img, aud, player_obj, dev
    
    # Initialize pygame (parameters, display, clock, etc.)
    pyg  = Pygame()
    dev  = DevTools()
    
    # Initialize general mechanics (?)
    mech = Mechanics()
    
    # Import images (sorted dictionary and cache)
    img         = Images()
    img.flipped = Images(flipped=True)
    pygame.display.set_icon(img.dict['decor']['skeleton'])

    # Initialize and load pygame audio
    aud  = Audio()
    
    # Create player
    player_obj = Player()
    player_obj.create_player()

    # Generate main menu
    player_obj.envs['garden'] = build_garden()
    place_player(player_obj.envs['garden'], player_obj.envs['garden'].center)
    
    # Open the main menu
    main_menu()

@debug_call
def main_menu():
    """ Manages the menu. Handles player input. Only active when the main menu is open. """
    
    global game_title, last_press_time, cooldown_time
    pygame.key.set_repeat(0, 0)
    
    # -------------------------------------- INIT --------------------------------------
    # Play menu music
    aud.control(new_track=aud.dict['menu'][0])

    # Initialize title
    title_font = pygame.font.SysFont('segoeuisymbol', 40, bold=True)
    game_title = title_font.render("MORS SOMNIA", True, pyg.green)
    game_title_pos = (int((pyg.screen_width - game_title.get_width())/2), 85)
    
    # Initialize cursor
    cursor_img = pygame.Surface((16, 16)).convert()
    cursor_img.set_colorkey(cursor_img.get_at((0, 0)))
    pygame.draw.polygon(cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
    cursor_img_pos = [50, 304]
    
    # Initialize menu options
    menu_choices = ["NEW GAME", "LOAD", "SAVE", "CONTROLS", "QUIT"]
    menu_choices_surfaces = []
    for i in range(len(menu_choices)):
        if i == 0:                       color = pyg.green
        elif i == len(menu_choices) - 1: color = pyg.red
        else:                            color = pyg.gray
        menu_choices_surfaces.append(pyg.font.render(menu_choices[i], True, color))
    choice, choices_length = 0, len(menu_choices) - 1
    
    # Allows access to garden
    menu_toggle = True

    # -------------------------------------- STARTUP --------------------------------------
    # Fade in at startup
    if pyg.startup_toggle:
        
        # Startup background
        background_image = pygame.image.load("Data/garden.png").convert()
        background_image = pygame.transform.scale(background_image, (pyg.screen_width, pyg.screen_height))

        # Fade details
        alpha = 0
        fade_speed = 10
        fade_surface = pygame.Surface((pyg.screen_width, pyg.screen_height))
        fade_surface.fill(pyg.black)
        
        # Apply fade
        while alpha < 255:
            pyg.clock.tick(30)
            fade_surface.set_alpha(255 - alpha)
            
            # Set menu background to the custom image
            pyg.screen.blit(background_image, (0, 0))

            # Draw the menu elements during the fade
            pyg.screen.blit(game_title, game_title_pos)

            # Apply the fade effect
            pyg.screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
            
            # Increase alpha for the next frame
            alpha += fade_speed
            
        pyg.startup_toggle = False

    # -------------------------------------- ACTIONS --------------------------------------
    # Wait for command
    while True:
        pyg.clock.tick(25)
        event = pygame.event.get()
        
        # Automate the Garden
        if menu_toggle and (player_obj.ent.env.name == 'garden'):
            player_obj.ent.role = 'NPC'
            player_obj.ent.ai()
            render_all(gui=False)
            if menu_toggle:
                y = 300
                for menu_choice_surface in menu_choices_surfaces:
                    pyg.display.blit(menu_choice_surface, (80, y))
                    y += 24
                
                # Customize main icon (Garden floor)
                ## Regular text
                if pyg.startup_toggle2: pyg.display.blit(game_title, game_title_pos)
                pyg.display.blit(cursor_img, cursor_img_pos)
            pygame.display.flip()
        else:
            player_obj.ent.role = 'player'
        
        if event:
            if event[0].type == KEYDOWN:
                
                # ---------------------------- GARDEN -----------------------------
                if not menu_toggle:
                    
                    # >>MOVE/ATTACK<<
                    if event[0].key in pyg.key_UP:
                        player_obj.ent.move(0, -pyg.tile_height)
                    elif event[0].key in pyg.key_DOWN:
                        player_obj.ent.move(0, pyg.tile_height)
                    elif event[0].key in pyg.key_LEFT:
                        player_obj.ent.move(-pyg.tile_width, 0)
                    elif event[0].key in pyg.key_RIGHT:
                        player_obj.ent.move(pyg.tile_width, 0)
                    
                    # >>MENU<<
                    elif event[0].key in pyg.key_SLASH and (time.time()-last_press_time > cooldown_time):
                        last_press_time = float(time.time())
                        pygame.key.set_repeat(0, 0)
                        menu_toggle = True
                
                # ---------------------------- MENU -----------------------------
                if menu_toggle:
                
                    # >>SELECT MENU ITEM<<
                    if event[0].key in pyg.key_UP:
                        cursor_img_pos[1] -= 24
                        choice -= 1
                        if choice < 0:
                            choice = choices_length
                            cursor_img_pos[1] = 304 + (len(menu_choices) - 1) * 24
                    elif event[0].key in pyg.key_DOWN:
                        cursor_img_pos[1] += 24
                        choice += 1
                        if choice > choices_length:
                            choice = 0
                            cursor_img_pos[1] = 304
                    
                    # >>RESUME<<
                    elif (event[0].key in pyg.key_0) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                        pyg.last_press_time = float(time.time())
                        if not pyg.startup_toggle2:
                            play_game()
                    
                    elif event[0].key in pyg.key_RETURN:
                        
                        # >>NEW GAME<<
                        if choice == 0:
                            pyg.startup_toggle2 = True  # when false, prevents returning to character creation menu after initialization
                            character_creation()
                            if not pyg.startup_toggle2:
                                new_game()
                                play_game()
                        
                        # >>LOAD<<
                        if choice == 1:
                            load_account()
                            if not pyg.startup_toggle2:
                                print(True)
                                play_game()
                        
                        # >>SAVE<<
                        if choice == 2:
                            save_account()

                        # >>CONTROLS<<
                        if choice == 3:
                            new_menu(header='Controls', 
                                     options=['Move:                                       Arrow keys or WASD',
                                              'Descend stairs or grab item:    Enter',
                                              'Ascend stairs to home:            Shift',
                                              'Check stats:                             1',
                                              'Use item in inventory:              2',
                                              'Drop item from inventory:        3',
                                              'Open questlog:                        4',
                                              'Toggle movement speed:         5',
                                              'Take screenshot:                      6',
                                              'Construct items:                         7',
                                              'Unused:                                   8',
                                              'Unused:                                   9',
                                              'Toggle messages:                     /'])
                        
                        # >>QUIT<<
                        elif choice == 4:
                            pygame.quit()
                            sys.exit()
                    
                    # >>GARDEN<<
                    elif event[0].key in pyg.key_SLASH and (time.time()-last_press_time > cooldown_time):
                        last_press_time = float(time.time())
                        menu_toggle = False
                        if player_obj.ent.env.name != 'garden':
                            place_player(env=player_obj.envs['garden'], loc=player_obj.envs['garden'].player_coordinates)
                        elif not pyg.startup_toggle2:
                            place_player(env=player_obj.ent.last_env, loc=player_obj.ent.last_env.player_coordinates)

                # -------------------------------------- RENDER --------------------------------------
                render_all(gui=False)
                if menu_toggle:
                    y = 300
                    for menu_choice_surface in menu_choices_surfaces:
                        pyg.display.blit(menu_choice_surface, (80, y))
                        y += 24
                    
                    # Customize main icon (Garden floor)
                    ## Regular text
                    if pyg.startup_toggle2: pyg.display.blit(game_title, game_title_pos)
                    pyg.display.blit(cursor_img, cursor_img_pos)
                pygame.display.flip()
        pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
        pygame.display.update()

def new_menu(header, options, options_categories=None, position='top left', backgrounds=None):
    """ IMPORTANT. Creates cursor, background, and menu options, then returns index of choice.

        header             : string; top line of text
        options            : list of strings; menu choices
        options_categories : list of strings; categorization; same length as options
        position           : chooses layout preset """

    global game_title
    
    # -------------------------------------- INIT --------------------------------------
    # Initialize temporary data containers
    choice                   = 0              # holds index of option pointed at by cursor
    choices_length           = len(options)-1 # number of choices
    options_categories_cache = ''             # holds current category
    options_render = options.copy()
    
    # Alter layout if categories are present
    if options_categories: 
        tab_x, tab_y         = 70, 10
        options_categories_cache_2 = options_categories[0]
    else:
        tab_x, tab_y         = 0, 0

    # Set initial position of each text type
    header_position    = {'top left': [5,        10],       'center': [int((pyg.screen_width - game_title.get_width())/2), 85],
                          'bottom left': [5, 10], 'bottom right': [60 ,70]}
    cursor_position    = {'top left': [50+tab_x, 38+tab_y], 'center': [50, 300],
                          'bottom left': [50+tab_x, 65-tab_y], 'bottom right': [60 ,70]}
    options_positions  = {'top left': [80+tab_x, 34],       'center': [80, 300],
                          'bottom left': [5, 10], 'bottom right': [60 ,70]}
    category_positions = {'top left': [5,        34],       'center': [80, 300],
                          'bottom left': [5, 10], 'bottom right': [60 ,70]}

    # Set mutable copies of text positions
    cursor_position_mutable    = cursor_position[position].copy()
    options_positions_mutable  = options_positions[position].copy()
    category_positions_mutable = category_positions[position].copy()

    # Initialize cursor
    cursor_img = pygame.Surface((16, 16)).convert()
    cursor_img.set_colorkey(cursor_img.get_at((0,0)))
    pygame.draw.polygon(cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
    
    # Initialize menu options
    header = pyg.font.render(header, True, pyg.yellow)
    for i in range(len(options)):
        color = pyg.gray
        options_render[i] = pyg.font.render(options[i], True, color)
    
    # Initialize backgrounds
    if backgrounds:
        for i in range(len(backgrounds)):
            backgrounds[i] = pygame.image.load(backgrounds[i]).convert()

    # -------------------------------------- MENU --------------------------------------
    # Allow player to select menu option
    running = True
    while running: # while True
        pygame.time.Clock().tick(30)
        
        # Render menu background
        if backgrounds:
            pyg.display.fill(pyg.black)
            pyg.display.blit(backgrounds[choice], (0, 0))
        else:
            pyg.display.fill(pyg.black)
        
        # Render header and cursor
        pyg.display.blit(header, header_position[position])
        pyg.display.blit(cursor_img, cursor_position_mutable)
        
        # Render categories and options
        for i in range(len(options_render)):
            
            # Render category text if it is not present 
            if options_categories:
                if options_categories[i] != options_categories_cache:
                    options_categories_cache = options_categories[i]
                    text = pyg.font.render(f'{options_categories_cache.upper()}:', True, pyg.gray)
                    options_positions_mutable[1] += tab_y
                    pyg.display.blit(text, (category_positions_mutable[0], options_positions_mutable[1]))
                
            # Render option text
            pyg.display.blit(options_render[i], options_positions_mutable)
            options_positions_mutable[1] += 24
        options_positions_mutable = options_positions[position].copy()
        category_positions_mutable = category_positions[position].copy()
        pygame.display.flip()
        
        # Called when the user inputs a command
        for event in pygame.event.get():
            if event.type == KEYDOWN:

                # >>RESUME<<
                if (event.key in pyg.key_0) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                    pyg.last_press_time = float(time.time())
                    running = False
                    return None
                
                # >>SELECT MENU ITEM<<
                if event.key in pyg.key_UP:
                
                    # Move cursor up
                    cursor_position_mutable[1]     -= 24
                    choice                         -= 1
                    
                    # Move to lowest option
                    if choice < 0:
                        choice                     = choices_length
                        cursor_position_mutable[1] = cursor_position[position][1] + (len(options)-1) * 24
                        if options_categories:
                            cursor_position_mutable[1] += tab_y * (len(set(options_categories)) - 1)
                            options_categories_cache_2 = options_categories[choice]
                    
                    # Move cursor again if there are categories
                    elif options_categories:
                        if options_categories[choice] != options_categories_cache_2:
                            options_categories_cache_2 = options_categories[choice]
                            cursor_position_mutable[1] -= tab_y
                
                elif event.key in pyg.key_DOWN:
                
                    # Move cursor down
                    cursor_position_mutable[1]     += 24
                    choice                         += 1
                    
                    # Move to highest option
                    if choice > choices_length:
                        choice                     = 0
                        cursor_position_mutable[1] = cursor_position[position][1]
                        if options_categories:
                            options_categories_cache_2 = options_categories[choice]
                    
                    # Move cursor again if there are categories
                    elif options_categories:
                        if options_categories[choice] != options_categories_cache_2:
                            options_categories_cache_2 = options_categories[choice]
                            cursor_position_mutable[1] += tab_y
                            
                elif event.key in pyg.key_RETURN:
                    running = False
                    return choice
        pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
        pygame.display.update()

def inventory_menu(header):
    """ Calls a menu with each item of the inventory as an option, then returns an item if it is chosen. """
    
    # Initialize cache files
    options            = [] # list of strings; sent to menu
    options_categories = [] # list of strings; sent to menu
    item_cache         = [] # list of Item objects
    
    # Extract names and roles
    for role in player_obj.ent.inventory.values():
        for item in role:
            if not item.hidden:
                text = item.name
                if item.equipped:
                    text = text + ' (on ' + item.slot + ')'
                options.append(text)
                options_categories.append(item.role)
                item_cache.append(item)
    if not options:
        options = ['Inventory is empty.']

    # Generate menu and return selected option
    index = new_menu(header, options, options_categories=options_categories, position="top left")
    if index is not None: return item_cache[index]

## Gameplay
def character_creation():
    """ Manages the character creation menu. Handles player input. Only active when menu is open.
        Called when starting a new game.
    
        HAIR:       sets hair by altering hair_index, which is used in new_game to add hair as an Object hidden in the inventory
        HANDEDNESS: mirrors player/equipment tiles, which are saved in img.dict and img.cache
        ACCEPT:     runs new_game() to generate player, home, and default items, then runs play_game() """
        
    # -------------------------------------- INIT --------------------------------------
    # Reset character
    player_obj.create_player()
    place_player(player_obj.envs['garden'], player_obj.envs['garden'].center)
    player_obj.ent.env.camera = Camera(player_obj.ent)
    player_obj.ent.env.camera.fixed = True
    
    # Initialize cursor
    cursor_img = pygame.Surface((16, 16)).convert()
    cursor_img.set_colorkey(cursor_img.get_at((0,0)))
    pygame.draw.polygon(cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
    cursor_img_pos = [50, 304]
    
    # Set character background
    background_image = pygame.image.load("Data/room.png")
    
    # Initialize menu options
    menu_choices = ["HAIR", "SKIN", "HANDEDNESS", "", "ACCEPT", "BACK"]   
    for i in range(len(menu_choices)):
        if   i == len(menu_choices)-2:  color = pyg.green
        elif i == len(menu_choices)-1:  color = pyg.red
        else:                           color = pyg.gray
        menu_choices[i] = pyg.font.render(menu_choices[i], True, color)
    choice, choices_length = 0, len(menu_choices)-1
    
    # Begins with default settings (ideally)
    orientations = ['front', 'right', 'back', 'left']
    last_press_time = 0
    cooldown_time = 1

    # -------------------------------------- INPUT --------------------------------------
    running = True
    while running: # while True
        pyg.clock.tick(30)
        
        # Prevent escape from going back to character creation
        if not pyg.startup_toggle2:
            running = False
            return
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # >>MAIN MENU<<
                if (event.key in pyg.key_0) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                    pyg.last_press_time = float(time.time())
                    running = False
                    return
                
                # >>SELECT MENU ITEM<<
                elif event.key in pyg.key_UP:   # Up
                    cursor_img_pos[1]     -= 24
                    choice                -= 1
                    if choice < 0:
                        choice            = choices_length
                        cursor_img_pos[1] = 304 + (len(menu_choices)-1) * 24
                    elif choice == (choices_length - 2):
                        choice = choices_length - 3
                        cursor_img_pos[1] = 304 + (len(menu_choices)-4) * 24
                elif event.key in pyg.key_DOWN: # Down
                    cursor_img_pos[1]     += 24
                    choice                += 1
                    if choice > choices_length:
                        choice            = 0
                        cursor_img_pos[1] = 304
                    elif choice == (choices_length - 2):
                        choice = choices_length - 1
                        cursor_img_pos[1] = 304 + (len(menu_choices)-2) * 24
                elif event.key in pyg.key_RETURN:
                
                    # >>HAIR<<
                    if choice == 0:
                        player_obj.ent.inventory['armor'][0].toggle_equip()
                        if player_obj.ent.inventory['armor'][0].equipped: player_obj.cache = 'medium hair'
                        else:                                             player_obj.cache = None
                    
                    # >>SKIN<<
                    if choice == 1:
                        if player_obj.ent.img_names[0] == 'white':   player_obj.ent.img_names[0] = 'black'
                        elif player_obj.ent.img_names[0] == 'black': player_obj.ent.img_names[0] = 'white'
                    
                    # >>HANDEDNESS<<
                    if choice == 2:
                        if player_obj.ent.handedness == 'left':
                            player_obj.ent.handedness = 'right'
                            player_obj.ent.images = img.dict['white']
                            player_obj.ent.inventory['weapon'][0].images = img.dict['dagger']
                            player_obj.ent.inventory['armor'][0].images = img.dict['medium hair']
                        elif player_obj.ent.handedness == 'right':
                            player_obj.ent.handedness = 'left'
                            player_obj.ent.images = img.flipped.dict['white']
                            player_obj.ent.inventory['weapon'][0].images = img.flipped.dict['dagger']
                            player_obj.ent.inventory['armor'][0].images = img.flipped.dict['medium hair']
                    
                    # >>ACCEPT<<
                    if choice == 4:
                        pyg.startup_toggle2 = False
                        running = False
                        return
                    
                    # >>MAIN MENU<<
                    if choice == 5:
                        running = False
                        return
        
        # -------------------------------------- RENDER --------------------------------------
        # Implement timed rotation of character
        if time.time()-last_press_time > cooldown_time:
            last_press_time = float(time.time()) 
            player_obj.ent.img_names[1] = orientations[orientations.index(player_obj.ent.img_names[1]) - 1]

        # Set menu background
        pyg.display.fill(pyg.black)
        
        # Renders menu to update cursor location
        y = 300
        for menu_choice in menu_choices:
            pyg.display.blit(menu_choice, (80, y))
            y += 24
        pyg.display.blit(cursor_img, cursor_img_pos)
        pyg.display.blit(background_image, (400, 200))
        player_obj.ent.draw(pyg.display, loc=(464, 264))
        pygame.display.flip()
        pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
        pygame.display.update()

def new_game():
    """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
        Called when starting a new game or loading a previous game.

        new:  creates player as Object with Fighter stats, calls make_home(), then loads initial inventory
        else: calls load_objects_from_file() to load player, inventory, and current floor """
    
    global questlog

    # Clear prior data
    new_game_trigger = True
    #friend_quest(init=True)
    player_obj.envs['garden'] = build_garden()

    # Prepare player
    player_obj.ent.role         = 'player'
    player_obj.ent.img_names[1] = 'front'
    questlog = Questlog()
    
    player_obj.envs['home'] = build_home()
    place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].center)

    
    # Create items
    clothes = create_item('green clothes')
    hair = create_item('medium hair')
    shovel  = create_item('super shovel')
    player_obj.ent.inventory[clothes.role].append(clothes)
    player_obj.ent.inventory[hair.role].append(hair)
    player_obj.ent.inventory[shovel.role].append(shovel)
    clothes.toggle_equip()
    sort_inventory()
    
    # Prepare gui
    pyg.msg = []
    pyg.update_gui('Press / to hide messages.', pyg.red)
    pyg.msg_toggle = True

@debug_call
def play_game():
    """ IMPORTANT. Processes user input and triggers monster movement. """
    
    global player_action, msg_toggle, stairs, last_press_time
    
    player_move = False
    movement_speed(toggle=False)
    player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
    
    # Start loop
    while True:
        pyg.clock.tick(30)
        event = pygame.event.get()
        if event:

            # Save and quit
            if event[0].type == QUIT:
                save_game()
                pygame.quit()
                sys.exit()
            
            # Keep playing
            if not player_obj.ent.dead:
                if event[0].type == KEYDOWN:
                    active_effects()
                    print(f"\n({player_obj.ent.x}, {player_obj.ent.y}), ({int(player_obj.ent.x/pyg.tile_width)}, {int(player_obj.ent.y/pyg.tile_height)})")
                    
                    # >>MAIN MENU<<
                    if (event[0].key in pyg.key_0) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                        pyg.last_press_time = float(time.time())
                        pygame.key.set_repeat(0, 0)
                        player_obj.ent.env.camera.zoom_in(custom=1)
                        return
                    
                    # ! (this is just ugly)
                    if toggle_list[movement_speed_toggle] == 'Fast':

                        # >>MOVE/ATTACK<<
                        if event[0].key in pyg.key_UP:
                            player_obj.ent.move(0, -pyg.tile_height)
                        elif event[0].key in pyg.key_DOWN:
                            player_obj.ent.move(0, pyg.tile_height)
                        elif event[0].key in pyg.key_LEFT:
                            player_obj.ent.move(-pyg.tile_width, 0)
                        elif event[0].key in pyg.key_RIGHT:
                            player_obj.ent.move(pyg.tile_width, 0)
                    else:
                        # >>MOVE/ATTACK<<
                        if event[0].key in pyg.key_UP:
                            player_obj.ent.move(0, -pyg.tile_height)
                        elif event[0].key in pyg.key_DOWN:
                            player_obj.ent.move(0, pyg.tile_height)
                        elif event[0].key in pyg.key_LEFT:
                            player_obj.ent.move(-pyg.tile_width, 0)
                        elif event[0].key in pyg.key_RIGHT:
                            player_obj.ent.move(pyg.tile_width, 0)

                    # >>PICKUP/STAIRS<<
                    if event[0].key in pyg.key_RETURN:
                        
                        # Check if an item is under the player
                        if player_obj.ent.tile.item:
                            if player_obj.ent.tile.item.name in ['door', 'portal']:
                                mech.next_level()
                            else:
                                player_obj.ent.tile.item.pick_up()
                                player_obj.ent.tile.item = None

                    # >>HOME<<
                    if event[0].key == K_RSHIFT:
                        if player_obj.ent.tile.item:
                            if player_obj.ent.tile.item.name in ['door', 'portal']:
                                if player_obj.ent.env.name != 'home':
                                    place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].player_coordinates)

                    # >>VIEW STATS<<
                    if event[0].key in pyg.key_1:
                        player_obj.ent.env.camera.zoom_in(custom=1)
                        
                        level_up_exp = mech.level_up_base + player_obj.ent.rank * mech.level_up_factor
                        new_menu(header  =  'Character Information',
                                 options = ['Rank:                                ' + str(player_obj.ent.rank),
                                            'Experience:                       ' + str(player_obj.ent.exp),
                                            'Experience to level up:    ' + str(level_up_exp),
                                            'Maximum HP:                    ' + str(player_obj.ent.max_hp),
                                            'Attack:                             ' + str(player_obj.ent.attack),
                                            'Defense:                           ' + str(player_obj.ent.defense)])
                    
                        player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
                    
                    # >>CHECK INVENTORY<<
                    elif event[0].key in pyg.key_2:
                        pygame.key.set_repeat(250, 150)
                        player_obj.ent.env.camera.zoom_in(custom=1)
                        
                        chosen_item = inventory_menu("INVENTORY:         USE ITEM")
                        if chosen_item is not None:
                            chosen_item.use()
                            pyg.update_gui()
                        
                        movement_speed(toggle=False)
                        player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
                    
                    # >>DROP ITEM<<
                    elif event[0].key in pyg.key_3:
                        pygame.key.set_repeat(250, 150)
                        player_obj.ent.env.camera.zoom_in(custom=1)
                        
                        if player_obj.ent.tile.item:
                            pyg.update_gui("There's already something here", color=pyg.red)
                        else:
                            chosen_item = inventory_menu("INVENTORY:         DROP ITEM")
                            if chosen_item is not None:
                                chosen_item.drop()
                                pygame.event.clear()
                        
                        movement_speed(toggle=False)
                        player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
                    
                    # >>VIEW QUESTLOG<<
                    elif event[0].key in pyg.key_4:
                        pygame.key.set_repeat(250, 150)
                        player_obj.ent.env.camera.zoom_in(custom=1)
                        
                        try:
                            questlog.questlog_menu()
                        except:
                            questlog = Questlog()
                            questlog.questlog_menu()
                        
                        movement_speed(toggle=False)
                        player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
                    
                    # >>MOVEMENT SPEED<<
                    elif event[0].key in pyg.key_5 and (time.time()-last_press_time > cooldown_time):
                        movement_speed()
                        last_press_time = float(time.time())
                    
                    # >>SCREENSHOT<<
                    elif event[0].key in pyg.key_6:
                        screenshot(size='display', visible='False')
                    
                    # >>DEV TOOLS<<
                    elif event[0].key in pyg.key_7:
                        pygame.key.set_repeat(250, 150)
                        if pyg.zoom != 1:
                            player_obj.ent.env.camera.zoom_in(custom=1)
                            pyg.zoom_cache = pyg.zoom
                        
                        dev.select_item()
                        
                        movement_speed(toggle=False)

                    # >>DEV TOOLS<<
                    elif event[0].key in pyg.key_8:
                        dev.export_env()
                    
                    # >>DEV TOOLS<<
                    elif event[0].key in pyg.key_9:
                        dev.import_env()
                    
                    # >>TOGGLE MESSAGES<<
                    elif event[0].key in pyg.key_SLASH:
                    
                        # Hide messages
                        if pyg.msg_toggle:
                            pyg.msg_toggle = False
                        
                        else:
                            # Hide messages and GUI
                            if pyg.gui_toggle:
                                pyg.gui_toggle = False
                                pyg.msg_toggle = False
                            
                            # View messages and GUI
                            else:
                                pyg.gui_toggle = True
                                pyg.msg_toggle = True
            
                    # >>ZOOM<<
                    elif event[0].key in pyg.key_PLUS:
                        player_obj.ent.env.camera.zoom_in()
                    elif event[0].key in pyg.key_MINUS:
                        player_obj.ent.env.camera.zoom_out()
            
            else:
                # >>MAIN MENU<<
                if event[0].type == KEYDOWN:
                    if (event[0].key in pyg.key_0) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                        pyg.last_press_time = float(time.time())
                        pygame.key.set_repeat(0, 0)
                        player_obj.ent.env.camera.zoom_in(custom=1)
                        return
                        
                # >>TOGGLE MESSAGES<<
                elif event[0].key in pyg.key_SLASH:
                    if pyg.msg_toggle:
                        pyg.msg_toggle = False
                    else:
                        if pyg.gui_toggle:
                            pyg.gui_toggle = False
                            pyg.msg_toggle = False
                        else:
                            pyg.msg_toggle = True
                            pyg.gui_toggle = True
            
            # ! (unknown)
            if event[0].type == MOUSEBUTTONDOWN: # Cursor-controlled actions?
                if event[0].button == 1:
                    player_move = True
                    pyg.msg_toggle = False
                elif event[0].button == 3:
                    mouse_x, mouse_y = event[0].pos
                    get_names_under_mouse(mouse_x, mouse_y)
            
            # ! (unknown)
            if event[0].type == MOUSEBUTTONUP:
                if event[0].button == 1:
                    player_move = False

        # ! (unknown)
        if player_move:
            pos = pygame.mouse.get_pos()
            x = int((pos[0] + player_obj.ent.env.camera.x)/pyg.tile_width)
            y = int((pos[1] + player_obj.ent.env.camera.y)/pyg.tile_height)
            tile = player_obj.ent.env.map[x][y]
            if tile != player_obj.ent.tile:
                dx = tile.x - player_obj.ent.x
                dy = tile.y - player_obj.ent.y
                distance = (dx ** 2 + dy ** 2)**(1/2) # Distance from player to target
                dx = int(round(dx / distance)) * pyg.tile_width # Restrict motion to grid
                dy = int(round(dy / distance)) * pyg.tile_height
                player_obj.ent.move(dx, dy) # Triggers the chosen action

    #if game_state == 'playing' and player_action != 'didnt-take-turn': # Tab forward and unhash to allow turn-based game
        for entity in player_obj.ent.env.entities:
            entity.ai()
        render_all()
        pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
        pygame.display.update()

def render_all(size='display', visible=False, gui=True):
    """ Draws tiles and stuff. Constantly runs. """
    
    pyg.display.fill(pyg.black)
    
    # View entire map
    if size == 'full':
        y_range_1, y_range_2 = 0, len(player_obj.ent.env.map[0])
        x_range_1, x_range_2 = 0, len(player_obj.ent.env.map)
    
    # View display
    else:
        if not player_obj.ent.env.camera:
            player_obj.ent.env.camera = Camera(player_obj.ent)

        # Calculate visible ranges dynamically based on zoom level and tile size
        camera = player_obj.ent.env.camera

        y_range_1 = max(0, camera.tile_map_y)
        y_range_2 = min(len(player_obj.ent.env.map[0]) - 1, camera.tile_map_y + camera.tile_map_height + 2)

        x_range_1 = max(0, camera.tile_map_x)
        x_range_2 = min(len(player_obj.ent.env.map) - 1, camera.tile_map_x + camera.tile_map_width + 2)
    
    # Draw visible tiles
    for y in range(len(player_obj.ent.env.map[0])):
        for x in range(len(player_obj.ent.env.map)):
            tile = player_obj.ent.env.map[x][y]
            
            if visible or not tile.hidden:
                
                # Lowest tier (floor and walls)
                tile.draw(pyg.display)

                # Second tier (decor and items)
                if tile.item:
                    tile.item.draw(pyg.display)
                
                # Third tier (entity)
                if tile.entity:
                    tile.entity.draw(pyg.display)
    
    if size == 'display':
        if mech.impact:
            pyg.display.blit(mech.impact_image, mech.impact_image_pos)
        
        # Print messages
        if gui:
            if pyg.msg_toggle: 
                y = 10
                for message in pyg.msg:
                    pyg.display.blit(message, (10, y))
                    y += 16
            if pyg.gui_toggle:
                pyg.display.blit(pyg.gui, (10, 453))
        pygame.display.flip()

#######################################################################################################################################################
# Classes
## Utility
class Pygame:
    """ Pygame stuff. Does not need to be saved, but pyg.update_gui should be run after loading a new file. """

    def __init__(self):
        
        # Colors
        self.black             = pygame.color.THECOLORS['black']
        self.gray              = pygame.color.THECOLORS['gray90']
        self.white             = pygame.color.THECOLORS['white']
        self.red               = pygame.color.THECOLORS['orangered3']
        self.green             = pygame.color.THECOLORS['palegreen4']
        self.blue              = pygame.color.THECOLORS['blue']
        self.yellow            = pygame.color.THECOLORS['yellow']
        self.orange            = pygame.color.THECOLORS['orange']
        self.violet            = pygame.color.THECOLORS['violet']
        self.light_cyan        = pygame.color.THECOLORS['lightcyan']
        self.light_green       = pygame.color.THECOLORS['lightgreen']
        self.light_blue        = pygame.color.THECOLORS['lightblue']
        self.light_yellow      = pygame.color.THECOLORS['lightyellow']
        
        # Controls
        self.key_0             = [K_0,     K_KP0, K_ESCAPE] # back
        self.key_1             = [K_1,     K_KP1]           # stats
        self.key_2             = [K_2,     K_KP2]           # inventory (equip)
        self.key_3             = [K_3,     K_KP3]           # inventory (drop)
        self.key_4             = [K_4,     K_KP4]           # quests
        self.key_5             = [K_5,     K_KP5]           # movement speed
        self.key_6             = [K_6,     K_KP6]           # screenshot
        self.key_7             = [K_7,     K_KP7]           # screenshot
        self.key_8             = [K_8,     K_KP8]           # screenshot
        self.key_9             = [K_9,     K_KP9]           # screenshot
        self.key_UP            = [K_UP,    K_w]             # movement (up)
        self.key_DOWN          = [K_DOWN,  K_s]             # movement (down)
        self.key_LEFT          = [K_LEFT,  K_a]             # movement (left)
        self.key_RIGHT         = [K_RIGHT, K_d]             # movement (right)
        self.key_RETURN        = [K_RETURN]                 # activate
        self.key_SLASH         = [K_SLASH]                  # messages
        self.key_PLUS          = [K_PLUS,  K_KP_PLUS] 
        self.key_MINUS         = [K_MINUS, K_KP_MINUS]
        
        # Graphics parameters
        self.screen_width      = 640 # 20 tiles
        self.screen_height     = 480 # 15 tiles
        self.tile_width        = 32
        self.tile_height       = 32
        self.map_width         = 640 * 2
        self.map_height        = 480 * 2
        self.tile_map_width    = int(self.map_width/self.tile_width)
        self.tile_map_height   = int(self.map_height/self.tile_height)
        self.zoom              = 1
        self.zoom_cache        = 1

        # Graphics overlays
        self.msg_toggle        = True # Boolean; shows or hides messages
        self.msg               = []   # list of font objects; messages to be rendered
        self.gui_toggle        = True # Boolean; shows or hides GUI
        self.gui               = None # font object; stats to be rendered

        # Other
        self.startup_toggle = True
        self.startup_toggle2 = True
        self.cooldown_time = 0.5
        self.last_press_time = 0
        
        # Pygame initialization
        pygame.init()
        pygame.key.set_repeat(250, 150)
        pygame.display.set_caption("Mors Somnia") # Sets game title
        self.screen            = pygame.display.set_mode((self.screen_width, self.screen_height),)
        self.font              = pygame.font.SysFont('segoeuisymbol', 16, bold=True)
        self.clock             = pygame.time.Clock()
        self.display = pygame.Surface((int(self.screen_width / self.zoom), int(self.screen_height / self.zoom)))

    def update_gui(self, new_msg=None, color=None):
        
        # Update pyg.update_gui list
        if new_msg:
            for line in textwrap.wrap(new_msg, mech.message_width):
                
                # Delete older messages
                if len(self.msg) == mech.message_height:
                    del self.msg[0]
                
                # Create pyg.update_gui object
                self.msg.append(self.font.render(line, True, color))
        
        # Updage lower gui
        else:
            self.gui = self.font.render('HP: '            + str(player_obj.ent.hp) + '/' + str(player_obj.ent.max_hp) +  ' '*60 + 
                                        'Environment: ' + str(player_obj.ent.env.name),
                                        True, pyg.yellow)

class Images:
    """ Loads images from png file and sorts them in a global dictionary. One save for each file.

        The tileset (tileset.png) is organized in rows, with each row being a category identified below
        by the categories list. This function breaks the tileset into individual tiles and adds each tile
        to its respective category in a global dictionary for later use.
        
        img.dict:        mutable dictionary sorted by category
        img.cache:  less mutable than img.dict """
    
    def __init__(self, flipped=False):
        """ Parameters
            ----------
            dict         : dict; mutable dictionary of all names and pygame images
            
            ent          : dict; mutable dictionary of entity names and pygame images
            equip        : dict; mutable dictionary of equipment names and pygame images
            other        : dict; mutable dictionary of all names and pygame images

            ent_names    : list of strings; name for each entity image
            equip_names  : list of strings; name for each equipment image
            other_names  : list of strings; name for each other image
            
            ent_count    : int; number of entity images
            equip_count  : int; number of equipment images
            other_count  : int; number of other images
            
            biomes       : dict; set of biome names and associated region_id list 

            Alternates
            ----------
            flipped.<>   : flipped version of the parameters """

        # Create entity dictionary
        self.load_entities(flipped)
        
        # Create equipment dictionary
        self.load_equipment(flipped)
        
        # Create other dictionary
        self.load_other(flipped)
        
        # Create combined dictionary
        self.dict = self.ent | self.equip | self.other
        
        # Assign tiles to biomes
        self.biomes()

    def import_tiles(self, filename, flipped=False, effects=None):
        
        if not effects:
            tileset = pygame.image.load(filename).convert_alpha()
        else:
            kernel = ImageFilter.Kernel((3, 3), [1, -3, 1, -1, 3, 2, 3, 5, 5], 9, 1)
            tileset = Image.open(filename)
            tileset = tileset.filter(kernel)
            mode = tileset.mode
            size = tileset.size
            data = tileset.tobytes()
            tileset = pygame.image.fromstring(data, size, mode)
    
        # Break tileset into rows and columns
        num_rows     = tileset.get_height() // pyg.tile_height
        num_columns  = tileset.get_width() // pyg.tile_width
        tile_matrix  = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
        for row in range(num_rows):
            for col in range(num_columns):
                
                # Find location of image in tileset
                x = col * pyg.tile_width
                y = row * pyg.tile_height
                if flipped:
                    image = pygame.transform.flip(tileset.subsurface(x, y, pyg.tile_width, pyg.tile_height).convert_alpha() , True, False)
                else:
                    image = tileset.subsurface(x, y, pyg.tile_width, pyg.tile_height).convert_alpha()
                
                # Update tile matrices
                tile_matrix[row][col] = image
        
        return tile_matrix

    def load_entities(self, flipped):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Import tiles
        ent_matrix = self.import_tiles('Data/tileset_ent.png', flipped)
        
        # Define tile names and options
        self.ent_names = [
            'white',     'black',  'cyborg',
            'friend',    'eye',    'eyes',   'troll',  'triangle', 'purple',
            'tentacles', 'round1', 'round2', 'grass',  'round3',   'lizard',
            'red',       'rock',   'frog',   'radish']
        entity_options = [
            'front', 'back', 'left', 'right']

        # Create image dictionary
        self.ent = {key: None for key in self.ent_names}
        index = 0
        for entity_name in self.ent:
            self.ent[entity_name] = {option: image for (option, image) in zip(entity_options, ent_matrix[index])}
            if flipped:
                cache = self.ent[entity_name]['right']
                self.ent[entity_name]['right'] = self.ent[entity_name]['left']
                self.ent[entity_name]['left'] = cache
            index += 1
        self.ent_count = len(self.ent_names)

    def load_equipment(self, flipped):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """

        # Import tiles
        equip_matrix = self.import_tiles('Data/tileset_equip.png', flipped)
        
        # Define tile names and options
        self.equip_names = [
            'iron armor', 'green clothes', 'iron shield', 'medium hair',
            'dagger',     'blood dagger',  'shovel',      'super shovel',
            'sword',      'blood sword']
        equip_options = [
            'dropped', 'front', 'back', 'left', 'right']
        
        # Create image dictionary
        self.equip = {key: None for key in self.equip_names}
        index = 0
        for _ in self.equip_names:
            self.equip[self.equip_names[index]] = {option: image for (option, image) in zip(equip_options, equip_matrix[index])}
            if flipped:
                cache = self.equip[self.equip_names[index]]['right']
                self.equip[self.equip_names[index]]['right'] = self.equip[self.equip_names[index]]['left']
                self.equip[self.equip_names[index]]['left'] = cache
            index += 1
        self.equip_count = len(self.equip_names)

    def load_other(self, flipped):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Import tiles
        other_matrix = self.import_tiles('Data/tileset_other.png', flipped)
        
        # Define tile names and options
        self.other_names = [
            'decor', 'drugs', 'potions', 'scrolls',
            'stairs', 'floors', 'walls', 'roofs', None]
        decor_options = [
            'tree', 'bones', 'boxes', 'fire', 'leafy', 'bubble', 'skeleton']
        drugs_options = [
            'needle', 'skin', 'teeth', 'bowl', 'plant', 'bubbles']
        potions_options = [
            'red', 'blue', 'gray', 'purple']
        scrolls_options = [
            'closed', 'open']
        stairs_options = [
            'door', 'portal']
        floors_options = [
            'dark green', 'dark blue', 'dark red', 'green',  'red',    'blue',
            'wood',       'water',     'sand1',    'sand2',  'grass1', 'grass2',
            'bubbles1',   'bubbles2',  'bubbles3', 'dirt1',  'dirt2',
            'path',       'grass3',    'grass4']
        walls_options = [
            'dark green', 'dark red', 'dark blue', 'gray', 'red', 'green', 'gold']
        roofs_options = [
            'tiled', 'slats']
        null_options  = [
            None]
        other_options = [decor_options, drugs_options, potions_options, scrolls_options, stairs_options, floors_options, walls_options, roofs_options, null_options]
        
        # Create image dictionary
        self.other = {}
        index = 0
        for _ in self.other_names:
            self.other[self.other_names[index]] = {option: image for (option, image) in zip(other_options[index], other_matrix[index])}
            index += 1
        self.other_count = sum([len(options_list) for options_list in other_options])

    def biomes(self):
        """ Manages biome types. """
        
        self.biomes = {
            'any':     ['forest', 'desert', 'dungeon', 'water'],
            'wet':     ['forest', 'water'],
            
            'land':    ['forest', 'desert', 'dungeon'],
            'forest':  ['forest'],
            'desert':  ['desert'],
            'dungeon': ['dungeon'],
            
            'sea':     ['water'],
            'water':   ['water']}

    def flip(self, obj):
        
        if type(obj) == list:
            obj = [pygame.transform.flip(objs, True, False) for objs in obj]
        elif type(obj) == dict:
            obj = {key: pygame.transform.flip(value, True, False) for (key, value) in obj.items()}
        else:
            print("------flip error")

    def static(self, img_names, offset, rate):
        """Shift the tile by an offset. """
        
        image = self.dict[img_names[0]][img_names[1]]
        if random.randint(1, rate) == 1:
            x_offset, y_offset = random.randint(0, offset), random.randint(0, offset)
            x_offset %= image.get_width() # keeps offset within bounds
            y_offset %= image.get_height()
            
            shifted = pygame.Surface((image.get_width(), image.get_height()))
            shifted.blit(image, (x_offset, y_offset)) # draws shifted
            shifted.blit(image, (x_offset - image.get_width(), y_offset)) # wraps horizontally
            shifted.blit(image, (x_offset, y_offset - image.get_height())) # wraps vertically
            shifted.blit(image, (x_offset - image.get_width(), y_offset - image.get_height())) # wraps corners
            return shifted
        else: return image

    def halved(self, img_names, flipped=False):
        
        if flipped: image = self.flipped.dict[img_names[0]][img_names[1]]
        else:       image = self.dict[img_names[0]][img_names[1]]
        
        # Create a new surface with the same dimensions as the original image
        half = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)

        # Fill the surface with transparency to start
        half.fill((0, 0, 0, 0))

        # Blit the bottom half of the original image onto the new surface, shifted downward
        #half.blit(image, (0, 16), (0, image.get_height() // 2, image.get_width(), image.get_height() // 2))
        half.blit(image, (0, 0),  (0,                       0, image.get_width(), image.get_height() // 2))
        return half

class Audio:
    """ Manages audio. One save for each file. """

    def __init__(self):
        
        # Initialize music player
        pygame.mixer.init()
        
        self.dict = {}

        self.dict['menu'] = [pygame.mixer.Sound("Data/music_menu.mp3")]
        self.dict['home'] = [pygame.mixer.Sound("Data/music_home.mp3")]
        self.dict['dungeons'] = [pygame.mixer.Sound("Data/music_dungeon_1.mp3")]
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_1.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_1.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_1.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_1.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_2.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_2.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_2.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_2.mp3"))
        self.dict['dungeons'].append(pygame.mixer.Sound("Data/music_dungeon_2.mp3"))

        # Start music
        self.current_track = self.dict['menu'][0]
        self.current_track.play()

        self.shuffle = False

    def control(self, new_track=None):
        
        if self.shuffle:
            pass
        elif (new_track is not None) and (new_track is not self.current_track):
            #for i in range(len(track_list)):
            #    if (track_list[i] == current_track):
            #        current_track.stop()
            pygame.mixer.fadeout(4000)
            new_track.play(fade_ms=4000)
            self.current_track = new_track

class Player:
    """ Manages player file. One save for each file. """

    def __init__(self, env=None):
        """ Holds everything regarding the player.
            Parameters
            ----------
            envs     : dict of list of Environment objects
            dungeons : list of Environment objects; dungeon levels """
        
        self.ent      = None
        self.envs     = {'home': [], 'dungeons': []}
        self.dungeons = []
        self.img      = None
        self.file_num = 0

    def create_player(self, skin='white', hair='medium hair'):
        
        if self.ent:
            if self.ent.tile:
                self.ent.tile.entity = None
                self.ent.env.entities.remove(self.ent)
                self.ent.env = None
        
        self.ent = Entity(
            name       = 'Alex',
            role       = 'player',
            img_names = [skin, 'front'],

            exp        = 0,
            rank       = 1,
            hp         = 100,
            max_hp     = 100,
            attack     = 50,
            defense    = 100,
            
            x          = 0,
            y          = 0,
            habitat    = 'any',

            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0)
        
        if hair:
            hair = create_item(hair)
            self.ent.inventory[hair.role].append(hair)
            hair.toggle_equip()
        dagger = create_item('dagger')
        self.ent.inventory[dagger.role].append(dagger)
        dagger.toggle_equip()

class DevTools:
    
    def __init__(self):
        
        # Data for select_item and locked_item
        self.cursor_img_pos = [pyg.screen_width-pyg.tile_width, 32]
        self.dic_index = 0
        self.dic_categories = ['floors', 'walls', 'roofs', 'stairs', 'decor', 'drugs', 'potions', 'scrolls']
        self.dic_indices = [[0, 0] for _ in self.dic_categories] # offset, choice
        self.locked = False
        self.img_names = [None, None]

    def select_item(self):   

        # Initialize cursor
        cursor_img = pygame.Surface((32, 32)).convert()
        cursor_img.set_colorkey(cursor_img.get_at((0,0)))
        pygame.draw.polygon(cursor_img, pyg.white, [(0, 0), (31, 0), (31, 31), (0, 31)], 1)
        cursor_img_pos = self.cursor_img_pos
        
        # Initialize tile selection
        dic = img.other[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        img_x, img_y = None, None
        offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
        
        running = True
        while running: # while True
            pyg.clock.tick(30)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                
                    # >>PLAY GAME<<
                    if (event.key in pyg.key_0) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                        pyg.last_press_time = float(time.time())
                        running = False
                        return
                    
                    elif event.key in pyg.key_7:
                        if not self.locked:
                            cursor_img = pygame.Surface((32, 32)).convert()
                            cursor_img.set_colorkey(cursor_img.get_at((0,0)))
                            self.locked = True
                            pygame.draw.polygon(cursor_img, pyg.white, [(0, 0), (30, 0), (30, 30), (0, 30)], 2)
                        else:
                            cursor_img = pygame.Surface((32, 32)).convert()
                            cursor_img.set_colorkey(cursor_img.get_at((0,0)))
                            self.locked = False
                            pygame.draw.polygon(cursor_img, pyg.white, [(0, 0), (31, 0), (31, 31), (0, 31)], 1)
                    
                    # >>NAVIGATE DICTIONARY<<
                    elif event.key in pyg.key_UP:
                        
                        # Selection
                        if not self.locked:
                            choice -= 1
                            if cursor_img_pos[1] == 32: offset -= 1
                            else: cursor_img_pos[1] -= pyg.tile_height
                        else: player_obj.ent.move(0, -pyg.tile_height)
                    
                    elif event.key in pyg.key_DOWN:
                        if not self.locked:
                            choice += 1
                            if cursor_img_pos[1] >= (min(len(dic), 12) * 32): offset += 1
                            else: cursor_img_pos[1] += pyg.tile_height
                        else: player_obj.ent.move(0, pyg.tile_height)
                    
                    # >>CHANGE DICTIONARY<<
                    elif (event.key in pyg.key_LEFT) or (event.key in pyg.key_RIGHT):
                    
                        if event.key in pyg.key_LEFT:
                            if not self.locked: self.dic_index -= 1
                            else: player_obj.ent.move(-pyg.tile_height, 0)
                                
                        elif event.key in pyg.key_RIGHT:
                            if not self.locked: self.dic_index += 1
                            else: player_obj.ent.move(pyg.tile_width, 0)

                        dic = img.other[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                        offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                        choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
                        choice = cursor_img_pos[1]//32 + offset - 1
                        
                        # Move cursor to the highest spot in the dictionary
                        if cursor_img_pos[1] > 32*len(dic):
                            cursor_img_pos[1] = 32*len(dic)
                            choice = len(dic) - offset - 1
                    
                    # >>SELECT AND PLACE<<
                    elif event.key in pyg.key_RETURN:
                        self.place_item(dic, choice)

                # Save for later reference
                self.cursor_img_pos = cursor_img_pos
                self.dic_indices[self.dic_index%len(self.dic_indices)][0] = offset
                self.dic_indices[self.dic_index%len(self.dic_indices)][1] = choice
                render_all(gui=False)
            
            # Renders menu to update cursor location
            y = 32
            counter = 0
            for i in range(len(list(dic))):
                
                # Stop at the 12th image, starting with respect to the offset 
                if counter <= 12:
                    pyg.display.blit(dic[list(dic.keys())[(i+offset)%len(dic)]], (pyg.screen_width-pyg.tile_width, y))
                    y += pyg.tile_height
                    counter += 1
                else: break
            pyg.display.blit(cursor_img, cursor_img_pos)
            pygame.display.flip()
            pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
            pygame.display.update()

    def place_item(self, dic, choice):

        # Note location and image names
        self.img_x, self.img_y = int(player_obj.ent.x/pyg.tile_width), int(player_obj.ent.y/pyg.tile_height)
        self.img_names[0] = self.dic_categories[self.dic_index%len(self.dic_categories)]
        self.img_names[1] = list(dic.keys())[(choice)%len(dic)]
        
        # Set location for drop
        if player_obj.ent.direction == 'front':   self.img_y += 1
        elif player_obj.ent.direction == 'back':  self.img_y -= 1
        elif player_obj.ent.direction == 'right': self.img_x += 1
        elif player_obj.ent.direction == 'left':  self.img_x -= 1
        
        # Place tile
        if self.img_names[0] in ['floors', 'walls', 'roofs']:
            place_object(
                obj = player_obj.ent.env.map[self.img_x][self.img_y],
                loc = [self.img_x, self.img_y],
                env = player_obj.ent.env,
                names = self.img_names.copy())
        
        # Place entity
        elif self.img_names[0] in img.ent_names:
            item = create_entity(
                names = self.img_names.copy())
            place_object(
                obj = item,
                loc = [self.img_x, self.img_y],
                env = player_obj.ent.env,
                names = self.img_names.copy())
        
        # Place item
        else:
            item = create_item(
                names = self.img_names)
            place_object(
                obj = item,
                loc = [self.img_x, self.img_y],
                env = player_obj.ent.env,
                names = self.img_names.copy())
        
        self.img_x, self.img_y = None, None

    def export_env(self):
        with open(f"Data/File_{player_obj.file_num}/env.pkl", 'wb') as file:
            pickle.dump(player_obj.ent.env, file)

    def import_env(self):
        try:
            with open(f"Data/File_{player_obj.file_num}/env.pkl", "rb") as file:
                env = pickle.load(file)
            env.camera = Camera(player_obj.ent)
            env.camera.update()
            place_player(env, env.player_coordinates)
        except: print("No file found!")

## Gameplay    
class Mechanics:
    """ Game parameters. Does not need to be saved. """
    
    def __init__(self):
        
        self.room_max_size     = 10
        self.room_min_size     = 4
        self.max_rooms         = 3

        # Combat
        self.heal_amount       = 4
        self.lightning_damage  = 20
        self.lightning_range   = 5 * pyg.tile_width
        self.confuse_range     = 8 * pyg.tile_width
        self.confuse_num_turns = 10
        self.fireball_radius   = 3 * pyg.tile_width
        self.fireball_damage   = 12
        
        self.blank_surface = pygame.Surface((pyg.tile_width, pyg.tile_height)).convert()
        self.blank_surface.set_colorkey(self.blank_surface.get_at((0,0)))
        self.impact_image = self.get_impact_image()
        self.impact_image_pos = [0,0]
        self.impact = False

        self.level_up_base     = 200
        self.level_up_factor   = 150

        self.torch_radius      = 10

        ## GUI
        self.message_width     = int(pyg.screen_width / 6)
        self.message_height    = 3

    @debug_call
    def next_level(self):
        """ Advances player to the next level. """
        
        pyg.update_gui('You take a moment to rest, and recover your strength.', pyg.violet)
        player_obj.ent.heal(int(player_obj.ent.max_hp / 2))  #heal the player by 50%

        # Generate dungeon
        time.sleep(0.5)
        pyg.update_gui('After a rare moment of peace, you descend deeper into the heart of the dungeon...', pyg.red)
        build_dungeon_level()
        
        # Change music and dungeon level
        aud.control(new_track=aud.dict['dungeons'][player_obj.envs['dungeons'][-1].lvl_num])
        
        # Place player and update display
        place_player(env=player_obj.envs['dungeons'][-1], loc=player_obj.envs['dungeons'][-1].center)

    def get_impact_image(self):
        color = (230,230,230)
        self.impact_image = pygame.Surface((pyg.tile_width, pyg.tile_width)).convert()
        self.impact_image.set_colorkey(self.impact_image.get_at((0,0)))
        image = pygame.Surface((int(pyg.tile_width/2), int(pyg.tile_height/3))).convert()
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
        x = int((self.impact_image.get_width()-image.get_width())/2)
        y = int((self.impact_image.get_height()-image.get_height())/2)
        self.impact_image.blit(image, (x,y))
        return self.impact_image

class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name        : str; identifier for image
            images      : list of pygame images; typically only one image
            room        : Room object
            entity      : Entity object; entity that occupies the tile
            item        : Item object; entity that occupies the tile
            img_names   : list of strings
            
            x           : int; location of the tile
            y           : int; location of the tile

            blocked     : bool; prevents items and entities from occupying the tile 
            hidden      : bool; prevents player from seeing the tile
            unbreakable : bool; prevents player from changing the tile """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def draw(self, surface):
        #image = img.static(img_names=self.img_names, offset=100, rate=100)
        surface.blit(img.dict[self.img_names[0]][self.img_names[1]], (self.x-player_obj.ent.env.camera.x, self.y-player_obj.ent.env.camera.y))

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        state.pop('images', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

class Item:
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name          : string
            role          : string in ['weapon', 'armor', 'potion', 'scroll', 'other']
            slot          : string in ['non-dominant hand', 'dominant hand', 'body', 'head']
            img_names[0]  : string
            img_names[1]  : string
            images        : dict of pygame images
                            equipment:     {'dropped', 'front', 'back', 'left', 'right']
                            non-equipment: varies
            image         : pygame image
            
            durability    : int; item breaks at 0
            equippable    : Boolean; lets item be equipped by entity
            equipped      : Boolean; notes if the item is equipped
            hidden        : Boolean; hides from inventory menu
            
            hp_bonus      : int
            attack_bonus  : int
            defense_bonus : int
            effects       : """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Other
        self.tile   = None
        self.x      = None
        self.y      = None
    
    def flip(self):
        
        pygame.transform.flip(self.image, True, False)
        for image in self.images.values():
            pygame.transform.flip(image, True, False)

    def draw(self, surface):
        """ Draws the object at its position. """
        surface.blit(img.dict[self.img_names[0]][self.img_names[1]], (self.x-player_obj.ent.env.camera.x, self.y-player_obj.ent.env.camera.y))

    def pick_up(self):
        """ Adds an item to the player's inventory and removes it from the map. """
        
        if len(player_obj.ent.inventory) >= 26:
            pyg.update_gui('Your inventory is full, cannot pick up ' + self.name + '.', pyg.red)
        else:
            player_obj.ent.inventory[self.role].append(self)
            sort_inventory()
            pyg.update_gui('You picked up a ' + self.name + '!', pyg.green)

    def drop(self):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at
            the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home. """
        
        # Dequip before dropping
        if self in player_obj.ent.equipment.values():
            self.toggle_equip()
        
        self.x = player_obj.ent.x
        self.y = player_obj.ent.y
        player_obj.ent.inventory[self.role].remove(self)
        player_obj.ent.tile.item = self
        pyg.update_gui('You dropped a ' + self.name + '.', pyg.yellow)   

    def use(self):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        # Equipment
        if self.equippable:
            self.toggle_equip()
        
        # Items
        else:
            if self.effect: player_obj.ent.effects.append(self.effect)
            else: pyg.update_gui('The ' + self.name + ' cannot be used.')

    def toggle_equip(self):
        """ Toggles the equip/unequip status. """
        
        if self.equipped: self.dequip()
        else:             self.equip()

    def equip(self):
        """ Unequips object if the slot is already being used. """
        
        # Check if anything is already equipped
        if player_obj.ent.equipment[self.slot] is not None:
            player_obj.ent.equipment[self.slot].dequip()
        
        # Apply stat adjustments
        player_obj.ent.equipment[self.slot] = self
        player_obj.ent.max_hp  += self.hp_bonus
        player_obj.ent.attack  += self.attack_bonus
        player_obj.ent.defense += self.defense_bonus
        player_obj.ent.effects.append(self.effect)
        
        self.equipped = True

        # ?
        if not self.hidden:
            pyg.update_gui('Equipped ' + self.name + ' on ' + self.slot + '.', pyg.light_green)

    def dequip(self):
        """ Unequips an object and shows a message about it. """
        
        # Update player
        player_obj.ent.equipment[self.slot] = None
        player_obj.ent.attack  -= self.attack_bonus
        player_obj.ent.defense -= self.defense_bonus
        player_obj.ent.max_hp  -= self.hp_bonus
        if player_obj.ent.hp > player_obj.ent.max_hp:
            player_obj.ent.hp = player_obj.ent.max_hp 
        player_obj.ent.effects.remove(self.effect)

        self.equipped = False

        if not self.hidden:
            pyg.update_gui('Dequipped ' + self.name + ' from ' + self.slot + '.', pyg.light_yellow)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        state.pop('images', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

class Entity:
    """ Player, enemies, and NPCs. Manages stats, inventory, and basic mechanics. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name           : string
            role           : string in ['player', 'enemy', 'NPC']
            images         : dict of pygame images; {'front', 'back', 'left', 'right'}
            image          : pygame image; current image in images
            img_names      : list of strings
            handedness     : string in ['left', 'right']

            exp            : int; experience accumulated by player or given from enemy
            rank           : int; entity level
            hp             : int; current health
            max_hp         : int; maximum health
            attack         : int; attack power
            defense        : int; defense power
            effects        : 

            env            : Environment object; current environment
            tile           : Tile object; current tile in current environment
            x              : int; horizontal position
            y              : int; vertical position
            x0             : int; initial horizontal position
            y0             : int; initial vertical position
            reach          : int or None; number of tiles the entity can move from its initial position

            inventory      : list of Item objects
            equipment      : list of Item objects
            death          : 
            follow         : bool or Entity object; sets entity as follower
            aggression     : int; toggles attack functions
            questline      : """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Images
        self.direction   = self.img_names[1]
        self.handedness  = 'left'

        # Location
        self.env        = None
        self.tile       = None
        self.x          = 0
        self.y          = 0
        self.x0         = 0
        self.y0         = 0

        # Movement
        self.ai_cooldown   = 0.25
        self.ai_last_press = 0
        self.reach         = 1000

        # Mechanics
        self.effects    = []
        self.inventory  = {'weapon': [], 'armor': [], 'potion': [], 'scroll': [], 'drug': [], 'other': []}
        self.equipment  = {'head': None, 'body': None, 'dominant hand': None, 'non-dominant hand': None}
        self.dead       = False
        self.questline  = None

    def ai(self):
        """ Preset movements. """
        
        if time.time()-self.ai_last_press > self.ai_cooldown:
            self.ai_last_press = float(time.time())
            distance = self.distance_to(player_obj.ent)
            
            # Follow or idle
            if self.follow:
                if distance < 320:
                    if not random.randint(0, self.lethargy//2):
                        self.move_towards(player_obj.ent.x, player_obj.ent.y)
                else:     self.idle()
            
            # Attack or move
            if (self.aggression) and (player_obj.ent.hp > 0):
                if distance < 64:
                    if random.randint(0, self.miss_rate) == 0:
                        self.attack_target(player_obj.ent)
                elif distance < self.aggression*32:
                    if not random.randint(0, self.lethargy//2):
                        self.move_towards(player_obj.ent.x, player_obj.ent.y)
            
            # Idle
            if not self.follow and not self.aggression:
                if self.role == 'NPC': self.idle()

    def idle(self):
        """ Randomly walks around """
        
        # Choose direction
        if random.randint(0, 1):
            dx = random.randint(-1, 1) * pyg.tile_width
            dy = 0
        else:
            dx = 0
            dy = random.randint(-1, 1) * pyg.tile_width
        
        # Move
        if self.distance_new([self.x+dx, self.y+dy], [self.x0, self.y0]) <= self.reach:
            if (dx < 0) and (self.img_names[1] == 'left'):    chance = 5
            elif (dx > 0) and (self.img_names[1] == 'right'): chance = 5
            elif (dy < 0) and (self.img_names[1] == 'back'):  chance = 5
            elif (dy > 0) and (self.img_names[1] == 'front'): chance = 5
            else:                                             chance = 1
            if not random.randint(0, self.lethargy//chance):
                self.move(dx, dy)

    def move(self, dx, dy):
        """ Moves the player by the given amount if the destination is not blocked. """
        
        # Determine direction
        if dy > 0:   self.direction = 'front'
        elif dy < 0: self.direction = 'back'
        elif dx < 0: self.direction = 'left'
        elif dx > 0: self.direction = 'right'
        
        # Change orientation before moving
        if self.img_names[1] != self.direction:
            if self.img_names[1]:
                self.img_names[1] = self.direction
        else:
            
            # Move player
            if self.role == 'player':
                
                # Find new position
                x = int((self.x + dx)/pyg.tile_width)
                y = int((self.y + dy)/pyg.tile_height)
                if not is_blocked(self.env, [x, y]):
                    
                    # Move player and update map
                    self.x                      += dx
                    self.y                      += dy
                    self.tile.entity            = None
                    self.env.map[x][y].entity   = self
                    self.tile                   = self.env.map[x][y]
                    self.env.player_coordinates = [x, y]
                    check_tile(x, y)
                    
                    # Trigger floor effects
                    if self.env.map[x][y].item:
                        floor_effects(self.env.map[x][y].item.effect)
                
                # Attack target
                elif self.env.map[x][y].entity: 
                    if self.env.name != 'home':
                        target = self.env.map[x][y].entity
                        self.attack_target(target)
                
                # Dig tunnel
                elif self.equipment['dominant hand'] is not None:
                    if self.equipment['dominant hand'].name in ['shovel', 'super shovel']:
                        # Move player and reveal tiles
                        if self.x >= 64 and self.y >= 64:
                            if super_dig or not self.env.map[x][y].unbreakable:
                                self.env.create_tunnel(x, y)
                                self.x                         += dx
                                self.y                         += dy
                                self.tile.entity               = None
                                self.env.map[x][y].blocked     = False
                                self.env.map[x][y].unbreakable = False
                                self.env.map[x][y].img_names   = self.env.floors
                                self.env.map[x][y].entity      = self
                                self.tile                      = self.env.map[x][y]
                                self.env.player_coordinates    = [x, y]
                                check_tile(x, y)
                            else:
                                pyg.update_gui('The shovel strikes the wall but does not break it.', pyg.white)
                            
                            # Update durability
                            if self.equipment['dominant hand'].durability <= 100:
                                self.equipment['dominant hand'].durability -= 1
                            if self.equipment['dominant hand'].durability <= 0:
                                self.equipment['dominant hand'].drop()
                                self.tile.item = None # removes item from world
                
                self.env.camera.update() # omit this if you want to modulate when the camera focuses on the player
            
            # Move NPC or enemy
            else:
                x = int((self.x + dx)/pyg.tile_width)
                y = int((self.y + dy)/pyg.tile_height)
                if not is_blocked(self.env, [x, y]):
                    
                    # Keep the entity in its native habitat
                    if self.env.map[x][y].biome in img.biomes[self.habitat]:
                        self.x                 += dx
                        self.y                 += dy
                        self.tile.entity       = None
                        player_obj.ent.env.map[x][y].entity = self
                        self.tile              = player_obj.ent.env.map[x][y]

    def move_towards(self, target_x, target_y):
        """ Moves object towards target. """
        
        dx       = target_x - self.x
        dy       = target_y - self.y
        distance = (dx ** 2 + dy ** 2)**(1/2)
        if distance:
            if dx and not dy:
                dx = round(dx/distance) * pyg.tile_width
                dy = 0
            elif dy and not dx:
                dx = 0
                dy = round(dx/distance) * pyg.tile_width
            elif dx and dy:
                if random.randint(0, 1):
                    dx = round(dx/distance) * pyg.tile_width
                    dy = 0
                else:
                    dx = 0
                    dy = round(dy/distance) * pyg.tile_width
            self.move(dx, dy)

    def distance_to(self, other):
        """ Returns the distance to another object. """
        
        if type(other) in [tuple, list]:
            dx = other[0] - self.x
            dy = other[1] - self.y
        else:
            dx = other.x - self.x
            dy = other.y - self.y
        return (dx ** 2 + dy ** 2)**(1/2)

    def distance(self, x, y):
        """ Returns the distance to some coordinates. """
        
        return ((x - self.x) ** 2 + (y - self.y) ** 2)**(1/2)

    def distance_new(self, loc_1, loc_2):
        return ((loc_2[0] - loc_1[0]) ** 2 + (loc_2[1] - loc_1[1]) ** 2)**(1/2)

    def attack_target(self, target):
        """ Calculates and applies attack damage. """
        
        if self.name != target.name:
            damage = self.attack - target.defense
            if damage > 0:
                pyg.update_gui(self.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', pyg.red)
                target.take_damage(damage)
            else:
                pyg.update_gui(self.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!', pyg.red)

    def take_damage(self, damage):
        """ Applies damage if possible. """
        
        if damage > 0:
            
            # Apply damage
            self.hp -= damage
            
            # Damage animation
            entity_flash(self)
            
            # Check for death
            if self.hp <= 0:
                self.hp = 0
                self.death()
                
                # Gain experience
                if self != player_obj.ent:
                    player_obj.ent.exp += self.exp
                    check_level_up()
                else:
                    pyg.update_gui()

    def death(self):
        if self.role == 'player':
            pyg.update_gui('You died!', pyg.red)
            player_obj.ent.image       = img.dict['decor']['bones']
            player_obj.ent.tile.entity = None
            player_obj.ent.tile.item   = player_obj.ent
        
        else:
            pyg.update_gui('The ' + self.name + ' is dead! You gain ' + str(self.exp) + ' experience points.', pyg.orange)
            self.img_names   = ['decor', 'bones']
            self.role        = 'corpse'
            self.name        = 'remains of ' + self.name
            self.tile.entity = None
            self.env.entities.remove(self)
            
            if not self.tile.item:
                item = create_item('bones')
                item.name = f"the corpse of {self.name}"
                place_object(item, [self.x//pyg.tile_width, self.y//pyg.tile_height], self.env)

            pygame.event.get()

    def heal(self, amount):
        """ Heals player by the given amount without going over the maximum. """
        
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def flip(self):
        
        pygame.transform.flip(self.image, True, False)
        for image in self.images.values():
            pygame.transform.flip(image, True, False)

    def draw(self, surface, loc=None):
        """ Draws the object at its position. """
        
        # Used without reference to an environment
        if loc:
            x = loc[0]
            y = loc[1]
        else:
            x = self.x-self.env.camera.x
            y = self.y-self.env.camera.y
        
        # Swimming
        if self.tile.biome in img.biomes['sea']: swimming = True
        else: swimming = False
        
        # Draw skin
        if self.handedness == 'left': 
            if swimming: surface.blit(img.halved([self.img_names[0], self.img_names[1]]), (x, y))
            else:        surface.blit(img.dict[self.img_names[0]][self.img_names[1]],     (x, y))
        
        # Draw flipped skin
        else:
            if swimming: surface.blit(img.halved([self.img_names[0], self.img_names[1]], flipped=True), (x, y))
            else:        surface.blit(img.flipped.dict[self.img_names[0]][self.img_names[1]],           (x, y))
            
        # Blit armor
        for item in self.equipment.values():
            if item is not None:
                if item.role == 'armor':
                    if self.handedness == 'left':
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]]), (x, y))
                        else:        surface.blit(img.dict[item.img_names[0]][self.img_names[1]],     (x, y))
                    else:
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (x, y))
                        else:        surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (x, y))
                else: pass
        
        # Blit hair
        for item in self.equipment.values():
            if item is not None:
                if item.role == 'hair':
                    if self.handedness == 'left':
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]]), (x, y))
                        else:        surface.blit(img.dict[item.img_names[0]][self.img_names[1]],     (x, y))
                    else:
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (x, y))
                        else:        surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (x, y))
                else: pass
        
        # Blit weapons
        for item in self.equipment.values():
            if item is not None:
                if item.role == 'weapon':
                    if self.handedness == 'left':
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]]), (x, y))
                        else:        surface.blit(img.dict[item.img_names[0]][self.img_names[1]],     (x, y))
                    else:
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (x, y))
                        else:        surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (x, y))
                else: pass

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        state.pop('images', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.images = img.dict[self.img_names[0]]

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """
    
    def __init__(self, name, size, soundtrack, lvl_num, walls, floors, roofs, blocked=True, hidden=True, img_names=['', '']):
        """ Parameters
            ----------
            name       : string
            floor      : int or string
            size       : string in ['small', 'medium', 'large']
            soundtrack : list of pygame audio files
            entities   : list of Entity objects
            camera     : Camera object """
        
        # Identity
        self.name       = name
        self.lvl_num    = lvl_num
        self.size       = size
        self.soundtrack = soundtrack
        
        # Images and rooms
        self.walls = walls
        self.floors = floors
        self.roofs = roofs
        self.rooms = []
        
        # Generate map tiles
        self.map = []
        x_range = [0, pyg.map_width * self.size]
        y_range = [0, pyg.map_height * self.size]
        for x in range(x_range[0], x_range[1]+1, pyg.tile_width):
            row = [] 
            for y in range(y_range[0], y_range[1]+1, pyg.tile_height):
                
                # Handle bulk
                if (x in x_range) or (y in y_range):
                    tile = Tile(
                        room=None,
                        entity=None,
                        item=None,
                        img_names=img_names,
                        walls=walls,
                        roofs=roofs,
                        x=x,
                        y=y,
                        biome=None,
                        blocked=True,
                        hidden=hidden,
                        unbreakable=True)
                else:
                    tile = Tile(
                        room=None,
                        entity=None,
                        item=None,
                        img_names=img_names,
                        walls=walls,
                        roofs=roofs,
                        x=x,
                        y=y,
                        biome=None,
                        blocked=blocked,
                        hidden=hidden,
                        unbreakable=False)
                row.append(tile)
            self.map.append(row)
        
        # Other
        self.entities           = []
        self.player_coordinates = (0, 0)
        self.camera = None
        self.center = (int(len(self.map)/2), int(len(self.map[0])/2))

    def create_h_tunnel(self, x1, x2, y):
        """ Creates horizontal tunnel. min() and max() are used if x1 is greater than x2. """
        
        offset = 0
        for x in range(min(x1-offset, x2+offset), max(x1-offset, x2+offset) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].img_names = self.floors

    def create_v_tunnel(self, y1, y2, x):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        
        offset = 0
        for y in range(min(y1-offset, y2+offset), max(y1-offset, y2+offset) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].img_names = self.floors
    
    def combine_rooms(self):
    
        # Sort through each room
        cache = []
        backup = copy.deepcopy(self.rooms)
        for i in range(len(backup)):
            for j in range(len(backup)):
                if backup[i] != backup[j]:
                    
                    # Prevent double counting
                    if {backup[i], backup[j]} not in cache:
                        cache.append({backup[i], backup[j]})
                        
                        # Find region of overlap
                        intersections_1 = self.rooms[i].intersect(self.rooms[j])
                        intersections_2 = self.rooms[j].intersect(self.rooms[i])
                        
                        if intersections_1 and intersections_2:
                            
                            # Convert internal walls into floors
                            for tile in intersections_1:
                                if tile not in backup[j].walls_list:
                                    tile.img_names = tile.room.floor
                                    tile.blocked = False
                                    tile.item = None
                            for tile in intersections_2:
                                if tile not in backup[i].walls_list:
                                    tile.img_names = tile.room.floor
                                    tile.blocked = False
                                    tile.item = None

                            # Combine into one room
                            for tile in self.rooms[i].tiles_list:
                                tile.room = self.rooms[j]
                            self.rooms[j].tiles_list += self.rooms[i].tiles_list

    def create_tunnel(self, x, y):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        
        self.map[x][y].img_names = self.floors

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

class Room:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, name, env, x1, y1, width, height, hidden, floor, walls, roof):
        """ Defines a rectangle and its size. """
        
        self.name = name
        
        # Location
        self.x1       = x1
        self.y1       = y1
        self.x2       = x1 + width
        self.y2       = y1 + height
        self.endpoints = [self.x1, self.y1, self.x2, self.y2]
        env.player_coordinates = self.center()
        
        # Image names and environment
        self.floor    = floor
        self.walls    = walls
        self.roof     = roof
        self.env      = env
        env.rooms.append(self)

        # Tiles
        self.tiles_list = []
        self.tile_dict = {}
        self.walls_list = []
        self.corners_list = []
        
        # Properties
        self.hidden   = hidden

        # Assign tiles to room
        for x in range(self.x1, self.x2 + 1):
            self.tile_dict[x] = {}
            for y in range(self.y1, self.y2 + 1):
                
                # Apply properties to bulk
                env.map[x][y].room         = self
                env.map[x][y].hidden       = self.hidden
                
                env.map[x][y].img_names    = self.floor
                env.map[x][y].blocked      = False
                
                env.map[x][y].item         = None
                if env.map[x][y].entity:
                    env.entities.remove(env.map[x][y].entity)
                    env.map[x][y].entity   = None
                
                self.tiles_list.append(env.map[x][y])
                self.tile_dict[x][y] = env.map[x][y]
                
                # Handle walls
                if (x == self.x1) or (x == self.x2) or (y == self.y1) or (y == self.y2):
                    env.map[x][y].img_names    = env.walls
                    env.map[x][y].blocked      = True
                    self.walls_list.append(env.map[x][y])
                
                    # Handle corners
                    if (x == self.x1) and (y == self.y1):
                        self.corners_list.append(env.map[x][y])
                    elif (x == self.x1) and (y == self.y2):
                        self.corners_list.append(env.map[x][y])
                    elif (x == self.x2) and (y == self.y1):
                        self.corners_list.append(env.map[x][y])
                    elif (x == self.x2) and (y == self.y2):
                        self.corners_list.append(env.map[x][y])

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
                if (wall_1.x >= other.x1*32) and (wall_1.x <= other.x2*32):
                    if (wall_1.y >= other.y1*32) and (wall_1.y <= other.y2*32):
                        
                        # Filter out corners
                        if wall_1 not in other.walls_list:
                            intersecting_wall.append(wall_1)

        return intersecting_wall

class Camera:
    """ Defines a camera to follow the player. """
    
    def __init__(self, target):
        """ Defines a camera and its parameters. 
            Parameters
            ----------
            target          : Entity object; focus of camera
            width           : int; translational offset in number of pixels
            height          : int; translational offset in number of pixels
            x               : 
            y               : 
            center_x        : unused
            center_y        : unused
            right           : unused
            bottom          : unused
            tile_map_x      : 
            tile_map_y      : 
            tile_map_width  : 
            tile_map_height : 
            x_range         : 
            y_range         : 
            fix_position    : """
        
        self.target          = target
        self.width           = int(pyg.screen_width / pyg.zoom)
        self.height          = int((pyg.screen_height + pyg.tile_height) / pyg.zoom)
        self.x               = (self.target.x * pyg.zoom) - int(self.width / 2)
        self.y               = (self.target.y * pyg.zoom) - int(self.height / 2)
        self.center_x        = self.x + int(self.width / 2)
        self.center_y        = self.y + int(self.height / 2)
        self.right           = self.x + self.width
        self.bottom          = self.y + self.height
        self.tile_map_x      = int(self.x / pyg.tile_width)
        self.tile_map_y      = int(self.y / pyg.tile_height)
        self.tile_map_width  = int(self.width / pyg.tile_width)
        self.tile_map_height = int(self.height / pyg.tile_height)
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        
        self.fixed           = False
        self.fix_position()

    @debug_call
    def update(self):
        """ ? """
        
        if not self.fixed:
            x_move          = self.target.x - self.center_x
            self.x          += x_move
            self.center_x   += x_move
            self.right      += x_move
            self.tile_map_x = int(self.x / pyg.tile_width)
            self.x_range    = self.tile_map_x + self.tile_map_width

            y_move          = self.target.y - self.center_y
            self.y          += y_move
            self.center_y   += y_move
            self.bottom     += y_move
            self.tile_map_y = int(self.y / pyg.tile_height)
            self.y_range    = self.tile_map_y + self.tile_map_height
            self.fix_position()
    
    @debug_call
    def fix_position(self):
        """ ? """
        if self.x < 0:
            self.x          = 0
            self.center_x   = self.x + int(self.width / 2)
            self.right      = self.x + self.width
            self.tile_map_x = int(self.x / (pyg.tile_width / pyg.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        elif self.right > (len(player_obj.ent.env.map)-1)*pyg.tile_width:
            self.right      = (len(player_obj.ent.env.map))*pyg.tile_width
            self.x          = self.right - self.width
            self.center_x   = self.x + int(self.width / 2)
            self.tile_map_x = int(self.x / (pyg.tile_width / pyg.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        if self.y < 0:
            self.y          = 0
            self.center_y   = self.y + int(self.height / 2)
            self.bottom     = (self.y + self.height) / pyg.zoom
            self.tile_map_y = int(self.y / (pyg.tile_height / pyg.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height
        elif self.bottom > (len(player_obj.ent.env.map[0]))*pyg.tile_height:
            self.bottom      = (len(player_obj.ent.env.map[0]))*pyg.tile_height
            self.y          = self.bottom - self.height
            self.center_y   = self.y + int(self.height / 2)
            self.tile_map_y = int(self.y / (pyg.tile_height / pyg.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height

    def zoom_in(self, factor=0.1, custom=None):
        """ Zoom in by reducing the camera's width and height. """
        
        if not self.fixed:
            if custom:
                pyg.zoom = custom
            else:
                pyg.zoom += factor
                pyg.zoom_cache = pyg.zoom
            pyg.update_gui()
            self.width = int(pyg.screen_width / pyg.zoom)
            self.height = int(pyg.screen_height / pyg.zoom)
            pyg.display = pygame.Surface((self.width, self.height))
            self._recalculate_bounds()

    def zoom_out(self, factor=0.1, custom=None):
        """ Zoom out by increasing the camera's width and height. """
        
        if not self.fixed:
            if round(pyg.zoom, 2) > factor:  # Ensure zoom level stays positive
                if custom:
                    pyg.zoom = custom
                else:
                    pyg.zoom -= factor
                    pyg.zoom_cache = pyg.zoom
                pyg.update_gui()
                self.width = int(pyg.screen_width / pyg.zoom)
                self.height = int(pyg.screen_height / pyg.zoom)
                pyg.display = pygame.Surface((self.width, self.height))
                self._recalculate_bounds()

    @debug_call
    def _recalculate_bounds(self):
        """ Recalculate dependent properties after zooming. """
        self.x               = self.target.x - int(self.width / 2)
        self.y               = self.target.y - int(self.height / 2)
        self.center_x        = self.x + int(self.width / 2)
        self.center_y        = self.y + int(self.height / 2)
        self.right           = self.x + self.width
        self.bottom          = self.y + self.height
        self.tile_map_width  = int(self.width / pyg.tile_width)
        self.tile_map_height = int(self.height / pyg.tile_height)
        self.tile_map_x      = int(self.x / pyg.tile_width)
        self.tile_map_y      = int(self.y / pyg.tile_height)
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        self.fix_position()

#######################################################################################################################################################
# Creation
## Environments
@debug_call
def build_garden():
    """ Generates environment for main menu. """

    # Initialize environment
    player_obj.envs['garden'] = Environment(
        name = 'garden',
        lvl_num = 0,
        size = 1,
        soundtrack = ['home'],
        img_names = ['floors', 'dark green'],
        floors = ['floors', 'dark green'],
        walls = ['walls', 'gray'],
        roofs = ['roofs', 'tiled'])
    
    # Construct rooms
    main_room = Room(
        name = 'garden',
        env = player_obj.envs['garden'],
        x1 = 0,
        y1 = 0,
        width = 19,
        height = 14,
        hidden = False,
        floor = player_obj.envs['garden'].floors,
        walls = player_obj.envs['garden'].walls,
        roof = [None, None])
    player_obj.envs['garden'].center = main_room.center()
    
    # Update player
    place_player(env=player_obj.envs['garden'], loc=player_obj.envs['garden'].center)
    player_obj.envs['garden'].camera = Camera(player_obj.ent)
    player_obj.envs['garden'].camera.fixed = True
    
    return player_obj.envs['garden']

def garden_objects():
    pass

@debug_call
def build_home():
    """ Generates player's home. """

    # Initialize environment
    player_obj.envs['home'] = Environment(
        name = 'home',
        lvl_num = 0,
        size = 5,
        soundtrack = ['home'],
        img_names = ['walls', 'gray'],
        floors = ['floors', 'green'],
        walls = ['walls', 'gray'],
        roofs = ['roofs', 'tiled'])

    # Construct rooms
    main_room = Room(
        name = 'home room 1',
        env = player_obj.envs['home'],
        x1 = 1,
        y1 = 10,
        width = mech.room_max_size,
        height = mech.room_max_size,
        hidden = False,
        floor = player_obj.envs['home'].floors,
        walls = player_obj.envs['home'].walls,
        roof = [None, None])
    hallway = Room(
        name = 'home room 1',
        env = player_obj.envs['home'],
        x1 = 0,
        y1 = 14,
        width = 10,
        height = 2,
        hidden = False,
        floor = player_obj.envs['home'].floors,
        walls = player_obj.envs['home'].walls,
        roof = [None, None])
    player_obj.envs['home'].combine_rooms()
    
    secret_room = Room(
        name = 'secret room',
        env = player_obj.envs['home'],
        x1 = 30,
        y1 = 30,
        width = mech.room_min_size*2,
        height = mech.room_min_size*2,
        hidden = True,
        floor = player_obj.envs['home'].floors,
        walls = player_obj.envs['home'].walls,
        roof = [None, None])
    player_obj.envs['home'].center = main_room.center()

    # Place items in home
    for i in range(5): 

        # Healing potion
        x, y                    = 4, 11
        item                    = create_item('healing potion')
        place_object(item, [x, y], player_obj.envs['home'])
        
        # Lightning scroll
        x, y                    = 5, 11
        item                    = create_item('scroll of lightning bolt')
        place_object(item, [x, y], player_obj.envs['home'])

        # Fireball scroll
        x, y                    = 6, 11
        item                    = create_item('scroll of fireball')
        place_object(item, [x, y], player_obj.envs['home'])

        # Blood sword
        x, y                    = 24, 33
        item                    = create_item('blood sword')
        place_object(item, [x, y], player_obj.envs['home'])

        # Shield
        x, y                    = 29, 34
        item                    = create_item('iron shield')
        place_object(item, [x, y], player_obj.envs['home'])

        # Bug fix
        x, y                    = 0, 0
        item                    = create_item('scroll of fireball')
        place_object(item, [x, y], player_obj.envs['home'])
    
    # Generate stairs
    x, y                    = 9, 15
    item                    = create_item('portal')
    place_object(item, [x, y], player_obj.envs['home'])
    
    # Generate friend
    x, y = 9, 18
    ent = create_entity('friend')
    place_object(ent, [x, y], player_obj.envs['home'])
    
    # Generate door
    x, y                    = 0, 15
    item                    = create_item('door', effect='overworld')
    place_object(item, [x, y], player_obj.envs['home'])
    player_obj.envs['home'].map[x][y].blocked = False
    player_obj.envs['home'].map[x][y].unbreakable = False
    
    return player_obj.envs['home']

def home_objects():
    pass

@debug_call
def build_dungeon_level():
    """ Generates a dungeon level. """

    # Initialize environment
    dungeon_env = Environment(
        name = 'dungeon',
        lvl_num = 1 + len(player_obj.envs['dungeons']),
        size = 5,
        soundtrack = ['dungeons'],
        img_names = ['walls', 'gray'],
        floors = ['floors', 'green'],
        walls = ['walls', 'gray'],
        roofs = ['roofs', 'tiled'])
    player_obj.envs['dungeons'].append(dungeon_env)
    
    # Construct rooms
    rooms, room_counter = [], 0
    num_rooms           = int(mech.max_rooms * player_obj.envs['dungeons'][-1].lvl_num) + 1
    new_map_height      = int(pyg.map_height * player_obj.envs['dungeons'][-1].lvl_num)
    new_map_width       = int(pyg.map_width  * player_obj.envs['dungeons'][-1].lvl_num)
    
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(mech.room_min_size, mech.room_max_size)
        height   = random.randint(mech.room_min_size, mech.room_max_size)
        x        = random.randint(0,             pyg.tile_map_width  - width - 1)
        y        = random.randint(0,             pyg.tile_map_height - height - 1)
        new_room = Room(
            name = 'dungeon room',
            env = dungeon_env,
            x1 = x,
            y1 = y,
            width = width,
            height = height,
            hidden = True,
            floor = player_obj.envs['dungeons'][-1].floors,
            walls = player_obj.envs['dungeons'][-1].walls,
            roof = player_obj.envs['dungeons'][-1].roofs)
        
        failed = False
        if random.choice([0, 1, 2, 3]) != 0: # include more values to make more hallways (?)
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

        # Set floor image
        if random.choice(range(player_obj.envs['dungeons'][-1].lvl_num)) >= player_obj.envs['dungeons'][-1].lvl_num*(3/4):
            new_room.img_names = ['floors', 'green']
        else:
            new_room.img_names = ['floors', 'red']
        
        # Customize room
        if not failed:
            x, y = new_room.center()[0], new_room.center()[1]
    player_obj.envs['dungeons'][-1].combine_rooms()
    
    for i in range(num_rooms):
        (x, y) = player_obj.envs['dungeons'][-1].rooms[i].center()
    
        # Place player in first room
        if room_counter == 0:
            player_obj.ent.x    = x * pyg.tile_width
            player_obj.ent.y    = y * pyg.tile_height
            player_obj.envs['dungeons'][-1].entity = player_obj.ent
            player_obj.ent.tile = player_obj.envs['dungeons'][-1].map[x][y]
            check_tile(x, y)
            player_obj.envs['dungeons'][-1].center = new_room.center()
        
        # Construct hallways
        else:
            
            (prev_x, prev_y) = player_obj.envs['dungeons'][-1].rooms[i-1].center()
            if random.randint(0, 1) == 0:
                player_obj.envs['dungeons'][-1].create_h_tunnel(prev_x, x, prev_y)
                player_obj.envs['dungeons'][-1].create_v_tunnel(prev_y, y, x)
            else:
                player_obj.envs['dungeons'][-1].create_v_tunnel(prev_y, y, prev_x)
                player_obj.envs['dungeons'][-1].create_h_tunnel(prev_x, x, y)
            
        # Place objects
        dungeon_objects(new_room, player_obj.envs['dungeons'][-1])
        
        # Prepare for next room
        room_counter += 1
    
    # Generate stairs
    stairs = create_item('door')
    place_object(stairs, [prev_x, prev_y], player_obj.envs['dungeons'][-1])

def dungeon_objects(room, env):
    """ Decides the chance of each monster or item appearing, then generates and places them. """
    
    # Set spawn chance for [chance, floor]
    max_monsters                    = from_dungeon_level([[2, 1], [3, 4], [5, 10]])
    monster_chances                 = {} # Chance of spawning monster by monster type
    monster_chances['eye']          = 80 # Sets spawn chance for orcs
    monster_chances['tentacles']    = from_dungeon_level([[15, 2], [30, 5], [60, 10]])
    monster_chances['round1']       = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
    monster_chances['round2']       = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
    monster_chances['round3']       = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
    monster_chances['lizard']       = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
    monster_chances['red']          = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
    monster_chances['white']        = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
 
    max_items                       = from_dungeon_level([[1, 1], [2, 4]]) # Maximum per room
    item_chances                    = {} # Chance of spawning item by item type
    item_chances['healing']         = 35 # Sets spawn chance for potions
    item_chances['transformation']  = 5 # Sets spawn chance for potions
    item_chances['bones']           = 5 # Sets spawn chance for potions
    item_chances['skin']            = 5 # Sets spawn chance for potions

    item_chances['lightning']       = from_dungeon_level([[25, 4]])
    item_chances['fireball']        = from_dungeon_level([[25, 6]])
    item_chances['confuse']         = from_dungeon_level([[10, 2]])

    item_chances['shovel']          = 20
    item_chances['super shovel']    = 10
    item_chances['sword']           = from_dungeon_level([[10, 5]])
    item_chances['blood dagger']    = from_dungeon_level([[5, 4]])
    item_chances['blood sword']     = from_dungeon_level([[2, 1]])
    item_chances['iron shield']          = from_dungeon_level([[15, 8]])

    num_monsters = random.choice([0, 1, max_monsters * 100])
    num_items    = random.randint(0, max_items * 100)
    
    for i in range(num_monsters): # Places monsters
        x = random.randint(0, 199)
        y = random.randint(0, 149)
        if not is_blocked(env, [x, y]):
            choice = random_choice(monster_chances)
            
            ent = create_entity(choice)
            place_object(ent, [x, y], env)

    for i in range(num_items): # Places items
        x = random.randint(0, 199)
        y = random.randint(0, 149)
        if not is_blocked(env, [x, y]):
            choice = random_choice(item_chances)
            
            if choice == 'healing': item = create_item('healing potion')
            elif choice == 'transformation': item = create_item('transformation potion')
            elif choice == 'bones': item = create_item('bones')
            elif choice == 'skin': item = create_item('skin')
            elif choice == 'lightning': item = create_item('scroll of lightning bolt')
            elif choice == 'fireball': item = create_item('scroll of fireball')
            elif choice == 'confuse': item = create_item('scroll of confusion')
            elif choice == 'shovel': item = create_item('shovel')
            elif choice == 'super shovel': item = create_item('super shovel')
            elif choice == 'sword': item = create_item('sword')
            elif choice == 'blood dagger': item = create_item('blood dagger')
            elif choice == 'blood sword': item = create_item('blood sword')
            elif choice == 'iron shield': item = create_item('iron shield')
            else: print(choice)
            
            place_object(item, [x, y], env)

@debug_call
def build_overworld():
    """ Generates the overworld environment. """

    # Initialize environment
    overworld_env = Environment(
        name = 'overworld',
        lvl_num = 0,
        size = 5,
        soundtrack = ['home'],
        img_names = ['floors', 'grass3'],
        floors = ['floors', 'grass3'],
        walls = ['walls', 'gray'],
        roofs = ['roofs', 'tiled'],
        blocked = False,
        hidden = False)
    player_obj.envs['overworld'] = overworld_env
    
    # Generate biomes
    biomes = [
        ['forest', 'grass3'],
        ['forest', 'grass3'],
        ['forest', 'grass3'],
        ['forest', 'grass3'],
        ['desert', 'sand1'],
        ['desert', 'sand1'],
        ['desert', 'sand1'],
        ['desert', 'sand1'],
        ['water',  'water'],
        ['water',  'water']]
    voronoi_biomes(overworld_env, biomes)
    
    # Generate objects and entities
    objects = [
        ['forest', 'tree',   10],
        ['forest', 'leafy',  10],
        ['desert', 'plant',  10000]]
    entities = [
        ['forest', 'radish', 50],
        ['wet',    'frog',   500],
        ['forest', 'grass',  1000]]
    place_objects(overworld_env, objects, entities)
    
    # Construct rooms
    num_rooms             = 20
    rooms                 = []
    room_counter, counter = 0, 0
    center                = player_obj.envs['overworld'].center
    (x_1, y_1)            = center
    x_2                   = lambda width:  len(player_obj.envs['overworld'].map)    - width - 1
    y_2                   = lambda height: len(player_obj.envs['overworld'].map[0]) - height - 1
    while room_counter < num_rooms:
        
        # Generate location
        width    = random.randint(mech.room_min_size, mech.room_max_size)
        height   = random.randint(mech.room_min_size, mech.room_max_size)
        x        = random.randint(x_1, x_2(width))
        y        = random.randint(y_1, y_2(height))
        
        # Check for solid ground
        failed = False
        for u in range(width):
            for v in range(height):
                if overworld_env.map[x+u][y+v].biome in img.biomes['sea']: failed = True
        if not failed:
            
            # Construct room
            new_room = Room(
                name = 'overworld room',
                env = overworld_env,
                x1 = x,
                y1 = y,
                width = width,
                height = height,
                hidden = False,
                floor = ['floors', 'dark green'],
                walls = player_obj.envs['overworld'].walls,
                roof = player_obj.envs['overworld'].roofs)
            add_doors(new_room)
            
            room_counter += 1
            x, y = new_room.center()[0], new_room.center()[1]
        
        else:
            counter += 1
        if counter > num_rooms:
            counter = 0
            (x_1, y_1) = (0, 0)
    
    player_obj.envs['overworld'].combine_rooms()
    
    (x, y) = player_obj.envs['overworld'].rooms[0].center()

    # Place player in first room
    player_obj.ent.x    = x * pyg.tile_width
    player_obj.ent.y    = y * pyg.tile_height
    player_obj.envs['overworld'].entity = player_obj.ent
    player_obj.ent.tile = player_obj.envs['overworld'].map[x][y]
    check_tile(x, y)
    player_obj.envs['overworld'].center = new_room.center()
    place_object(create_entity('lizard'), [player_obj.ent.x//32+1, player_obj.ent.y//32+1], overworld_env)

    # Generate stairs
    stairs = create_item('door')
    place_object(stairs, [x, y], player_obj.envs['overworld'])

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
            tile = env.map[x][y]
            min_distance = float('inf')
            biome = None
            
            for i in range(len(seeds_with_ids)):
                region_center = [seeds_with_ids[i][1][0]*pyg.tile_width, seeds_with_ids[i][1][1]*pyg.tile_height]
                weight = seeds_with_ids[i][2]
                distance = (abs(region_center[0] - tile.x) + abs(region_center[1] - tile.y)) / weight
                if distance < min_distance:
                    min_distance = distance
                    biome  = biomes[i][0]
                    floor_name   = biomes[i][1]
                    region_num   = i
            
            tile.biome = biome
            tile.img_names = ['floors', floor_name]

## Objects
def create_item(names, effect=None):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names : string or list of strings; name of object """

    item = None
    item_dict = {
    
    # Decor (decor_options)

        'tree': Item(
            name          = 'tree',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'tree'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = True,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
        'bones': Item(
            name          = 'bones',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'bones'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
            
        'boxes': Item(
            name          = 'boxes',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'boxes'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'fire': Item(
            name          = 'fire',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'fire'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'leafy': Item(
            name          = 'leafy tree',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'leafy'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = True,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'bubble': Item(
            name          = 'bubble',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'bubble'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'skeleton': Item(
            name          = 'skeleton',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'skeleton'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

    # Drugs (drugs_options)

        'needle': Item(
            name          = 'needle',
            role          = 'drug',
            slot          = None,
            img_names     = ['drugs', 'needle'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'skin': Item(
            name          = 'skin',
            role          = 'drug',
            slot          = None,
            img_names   = ['drugs', 'skin'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'teeth': Item(
            name          = 'teeth',
            role          = 'drug',
            slot          = None,
            img_names     = ['drugs', 'teeth'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'bowl': Item(
            name          = 'bowl',
            role          = 'drug',
            slot          = None,
            img_names     = ['drugs', 'bowl'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'plant': Item(
            name          = 'plant',
            role          = 'drug',
            slot          = None,
            img_names   = ['drugs', 'plant'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'bubbles': Item(
            name          = 'bubbles',
            role          = 'drug',
            slot          = None,
            img_names     = ['drugs', 'bubbles'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

    # Potions and scrolls (potions_options, scrolls_options)
    
        'healing potion': Item(
            name          = 'healing potion',
            role          = 'potion',
            slot          = None,
            img_names     = ['potions', 'red'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'transformation potion': Item(
            name          = 'transformation potion',
            role          = 'potion',
            slot          = None,
            img_names     = ['potions', 'purple'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'blue potion': Item(
            name          = 'transformation potion',
            role          = 'potion',
            slot          = None,
            img_names     = ['potions', 'blue'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'gray potion': Item(
            name          = 'transformation potion',
            role          = 'potion',
            slot          = None,
            img_names     = ['potions', 'gray'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of lightning bolt': Item(
            name          = 'scroll of lightning bolt',
            role          = 'scroll',
            slot          = None,
            img_names     = ['scrolls', 'closed'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of fireball': Item(
            name          = 'scroll of fireball',
            role          = 'scroll',
            slot          = None,
            img_names     = ['scrolls', 'closed'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of confusion': Item(
            name          = 'scroll of confusion',
            role          = 'scroll',
            slot          = None,
            img_names     = ['scrolls', 'closed'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of death': Item(
            name          = 'scroll of death',
            role          = 'scroll',
            slot          = None,
            img_names     = ['scrolls', 'open'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

    # Structures (stairs_options, floors_options)
        'door': Item(
            name          = 'door',
            role          = 'other',
            slot          = None,
            img_names     = ['stairs', 'door'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
            
        'portal': Item(
            name          = 'portal',
            role          = 'other',
            slot          = None,
            img_names     = ['stairs', 'portal'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
            
        'path': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['path', 'door'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    # Weapons (equip_names)
    
        'shovel': Item(
            name          = 'shovel',
            role          = 'weapon',
            slot          = 'dominant hand',
            img_names     = ['shovel', 'dropped'],

            durability    = 100,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'super shovel': Item(
            name          = 'super shovel',
            role          = 'weapon',
            slot          = 'dominant hand',
            img_names     = ['super shovel', 'dropped'],

            durability    = 1000,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 10,
            defense_bonus = 0,
            effect        = effect),

        'dagger': Item(
            name          = 'dagger',
            role          = 'weapon',
            slot          = 'dominant hand',
            img_names     = ['dagger', 'dropped'],
            
            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 2,
            defense_bonus = 0,
            effect        = effect),

        'sword': Item(
            name          = 'sword',
            role          = 'weapon',
            slot          = 'dominant hand',
            img_names     = ['sword', 'dropped'],
            
            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 5,
            defense_bonus = 0,
            effect        = effect),

        'blood dagger': Item(
            name          = 'blood dagger',
            role          = 'weapon',
            slot          = 'dominant hand',
            img_names     = ['blood dagger', 'dropped'],
            
            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 10,
            defense_bonus = 0,
            effect        = effect),

        'blood sword': Item(
            name          = 'blood sword',
            role          = 'weapon',
            slot          = 'dominant hand',
            img_names     = ['blood sword', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 15,
            defense_bonus = 0,
            effect        = effect),

    # Armor (equip_names)

        'green clothes': Item(
            name          = 'green clothes',
            role          = 'armor',
            slot          = 'body',
            img_names     = ['green clothes', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 1,
            effect        = effect),

        'medium hair': Item(
            name          = 'medium hair',
            role          = 'armor',
            slot          = 'head',
            img_names     = ['medium hair', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'bald': Item(
            name          = 'bald',
            role          = 'armor',
            slot          = 'head',
            img_names     = ['medium hair', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
        
        'iron shield': Item(
            name          = 'iron shield',
            role          = 'armor',
            slot          = 'non-dominant hand',
            img_names     = ['iron shield', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 10,
            effect        = effect)}

    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if val.img_names == names:
                item = val
    else:
        item = item_dict[names]
    
    if not item: raise Exception(names)
    else:        return item

def create_entity(names):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names : string; name of object
        location  : list of int; coordinates of item location """

    item = None
    item_dict = {
            
        'white': Entity(
            name       = 'white NPC',
            role       = 'NPC',
            img_names = ['white', 'front'],
            habitat    = 'any',
            
            exp        = 0,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0),
        
        'black': Entity(
            name       = 'black NPC',
            role       = 'NPC',
            img_names = ['black', 'front'],
            habitat    = 'any',
            
            exp        = 0,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0),
        
        'cyborg': Entity(
            name       = 'cyborg NPC',
            role       = 'NPC',
            img_names = ['cyborg', 'front'],
            habitat    = 'any',
            
            exp        = 0,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0),
        
        'friend': Entity(
            name       = 'friend',
            role       = 'NPC',
            img_names = ['friend', 'front'],
            habitat    = 'land',

            exp        = 0,
            rank       = 100,
            hp         = 100,
            max_hp     = 100,
            attack     = 0,
            defense    = 100,
            
            reach      = 640,

            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0),
    
        'eye': Entity(
            name       = 'eye',
            role       = 'enemy',
            img_names  = ['eye', 'front'],
            habitat    = 'land',
            
            exp        = 35,
            rank       = 1,
            hp         = 20,
            max_hp     = 20,
            attack     = 4,
            defense    = 0,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
        
        'eyes': Entity(
            name       = 'eyes',
            role       = 'enemy',
            img_names  = ['eyes', 'front'],
            habitat    = 'land',
            
            exp        = 35,
            rank       = 1,
            hp         = 20,
            max_hp     = 20,
            attack     = 4,
            defense    = 0,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
    
        'troll': Entity(
            name       = 'troll',
            role       = 'enemy',
            img_names = ['troll', 'front'],
            habitat    = 'land',

            exp        = 100,
            rank       = 1,
            hp         = 30,
            max_hp     = 30,
            attack     = 8,
            defense    = 2,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),

        'triangle': Entity(
            name       = 'triangle',
            role       = 'enemy',
            img_names = ['triangle', 'front'],
            habitat    = 'land',

            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
    
        'purple': Entity(
            name       = 'purple',
            role       = 'enemy',
            img_names = ['purple', 'front'],
            habitat    = 'land',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
    
        'tentacles': Entity(
            name       = 'tentacles',
            role       = 'enemy',
            img_names  = ['tentacles', 'front'],
            habitat    = 'any',

            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
    
        'round1': Entity(
            name       = 'round1',
            role       = 'enemy',
            img_names = ['round1', 'front'],
            habitat    = 'land',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
    
        'round2': Entity(
            name       = 'round2',
            role       = 'enemy',
            img_names = ['round2', 'front'],
            habitat    = 'land',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
        
        'grass': Entity(
            name       = 'grass',
            role       = 'enemy',
            img_names = ['grass', 'front'],
            habitat    = 'forest',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 40,
            aggression = 20),

        'round3': Entity(
            name       = 'round3',
            role       = 'enemy',
            img_names = ['round3', 'front'],
            habitat    = 'any',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
        
        'lizard': Entity(
            name       = 'lizard',
            role       = 'enemy',
            img_names = ['lizard', 'front'],
            habitat    = 'desert',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
        
        'red': Entity(
            name       = 'red',
            role       = 'enemy',
            img_names = ['red', 'front'],
            habitat    = 'land',
            
            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10),
        
        'rock': Entity(
            name       = 'rock',
            role       = 'enemy',
            img_names = ['rock', 'front'],
            habitat    = 'land',
            
            exp        = 500,
            rank       = 1,
            hp         = 10,
            max_hp     = 10,
            attack     = 0,
            defense    = 500,
            
            follow     = False,
            lethargy   = 50,
            miss_rate  = 10,
            aggression = 0),
        
        'frog': Entity(
            name       = 'frog',
            role       = 'enemy',
            img_names = ['frog', 'front'],
            habitat    = 'any',
            
            exp        = 15,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            
            follow     = False,
            lethargy   = 10,
            miss_rate  = 10,
            aggression = 10),
        
        'radish': Entity(
            name       = 'radish',
            role       = 'enemy',
            img_names = ['radish', 'front'],
            habitat    = 'forest',
            
            exp        = 0,
            rank       = 1,
            hp         = 25,
            max_hp     = 25,
            attack     = 0,
            defense    = 25,
            
            follow     = True,
            lethargy   = 6,
            miss_rate  = 6,
            aggression = 0)}
    
    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if (val.img_names[0] == names[0]) and (val.img_names[1] == names[1]):
                item = val
    else:
        item = item_dict[names]
    
    if not item: raise Exception(names)
    else:        return item

def place_object(obj, loc, env, names=None):
    """ Places a single object in the given location. """
    
    if type(obj) == Tile:
        env.map[loc[0]][loc[1]].img_names = names
    
    elif type(obj) == Item:
        obj.x  = loc[0] * pyg.tile_width
        obj.x0 = loc[0] * pyg.tile_width
        obj.y  = loc[1] * pyg.tile_height
        obj.y0 = loc[1] * pyg.tile_height
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].item = obj
        if obj.blocked:
            env.map[loc[0]][loc[1]].blocked = True

    elif type(obj) == Entity:
        obj.x  = loc[0] * pyg.tile_width
        obj.x0 = loc[0] * pyg.tile_width
        obj.y  = loc[1] * pyg.tile_height
        obj.y0 = loc[1] * pyg.tile_height
        obj.env = env
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].entity = obj
        env.entities.append(obj)

def place_objects(env, objects, entities):
    """ Places entities and items according to probability and biome. """
    
    # Sort through each tile
    for y in range(len(env.map[0])):
        for x in range(len(env.map)):
            tile = env.map[x][y]

            # Randomly select an object
            selection = random.choice(objects)
            
            # Check that the object matches the biome
            if tile.biome in img.biomes[selection[0]]:
                if not random.randint(0, selection[2]):
                    
                    # Place object
                    item = create_item(selection[1])
                    place_object(item, [x, y], env)

            # Check that the space is not already occupied
            if not is_blocked(env, [x, y]):
                
                # Randomly select an entity
                selection = random.choice(entities)
                
                # Check that the entity matches the biome
                if tile.biome in img.biomes[selection[0]]:
                    if not random.randint(0, selection[2]):
                        
                        # Place entity
                        entity = create_entity(selection[1])
                        entity.biome = tile.biome
                        place_object(entity, [x, y], env)

def add_doors(room):
    tiles = list(set(room.walls_list) - set(room.corners_list))
    if not random.randint(0, 10):
        selected_tile = random.choice(tiles)
        loc = [selected_tile.x // 32, selected_tile.y // 32]
        place_object(create_item('door'), loc, room.env)
        room.env.map[loc[0]][loc[1]].blocked = False
        
        selected_tile = random.choice(tiles)
        loc = [selected_tile.x // 32, selected_tile.y // 32]
        place_object(create_item('door'), loc, room.env)
        room.env.map[loc[0]][loc[1]].blocked = False
    else:
        selected_tile = random.choice(tiles)
        loc = [selected_tile.x // 32, selected_tile.y // 32]
        place_object(create_item('door'), loc, room.env)
        room.env.map[loc[0]][loc[1]].blocked = False

@debug_call
def place_player(env, loc):
    """ Sets player in a new position.

        Parameters
        ----------
        env : Environment object; new environment of player
        loc : list of integers; new location of player """
        
    # Remove from current location
    if player_obj.ent.env:
        player_obj.ent.env.player_coordinates = (player_obj.ent.x//32, player_obj.ent.y//32)
        player_obj.ent.last_env = player_obj.ent.env
        player_obj.ent.env.entities.remove(player_obj.ent)
        player_obj.ent.tile.entity = None
        player_obj.ent.tile = None

    # Set current environment and tile
    player_obj.ent.env             = env
    player_obj.ent.tile            = player_obj.ent.env.map[loc[0]][loc[1]]
    player_obj.ent.x               = loc[0] * pyg.tile_width
    player_obj.ent.x0              = loc[0] * pyg.tile_width
    player_obj.ent.y               = loc[1] * pyg.tile_height
    player_obj.ent.y0              = loc[1] * pyg.tile_height

    # Notify environmnet of player position
    player_obj.ent.env.entities.append(player_obj.ent)
    player_obj.ent.tile.entity = player_obj.ent

    check_tile(loc[0], loc[1])
    
    if not env.camera: env.camera = Camera(player_obj.ent)
    env.camera.update()
    
    time.sleep(0.5)
    pyg.update_gui()
    
    aud.control(new_track=aud.dict[env.soundtrack[0]][0])

#######################################################################################################################################################
# Mechanics
## Common
@debug_call
def entity_flash(ent):
    """ Death animation. """
    
    mech.impact = True
    mech.impact_image_pos[0] = ent.x-player_obj.ent.env.camera.x
    mech.impact_image_pos[1] = ent.y-player_obj.ent.env.camera.y
    render_all()
    mech.impact = False
    
    #wait_time = 0
    #while wait_time < 5:
    #    pygame.time.Clock().tick(30)
    #    wait_time += 1    
    flash = 3
    flash_time = 2
    if ent.hp <=0:
       flash_time = 4
    old_img_names = ent.img_names.copy()
    while flash_time > 1:
        pygame.time.Clock().tick(30)
        if flash:
            ent.img_names = [None, None]
        render_all()
        flash -= 1

        if flash < 1:
            flash = False
            flash_time -= 1
            ent.img_names = old_img_names
            if flash_time < 1:
                flash_time = 0
                flash = False
                ent.img_names = old_img_names

def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    
    level_up_exp = mech.level_up_base + player_obj.ent.rank * mech.level_up_factor
    if player_obj.ent.exp >= level_up_exp: # Levels up
        player_obj.ent.rank += 1
        player_obj.ent.exp -= level_up_exp
        pyg.update_gui('Your battle skills grow stronger! You reached level ' + str(player_obj.ent.rank) + '!', pyg.yellow)
        choice = None
        while choice == None: # Keeps asking until a choice is made
            choice = new_menu(header = 'Level up! Choose a stat to raise:',
                              options = ['Constitution (+20 HP, from ' + str(player_obj.ent.max_hp) + ')',
                                         'Strength (+1 attack, from ' + str(player_obj.ent.attack) + ')',
                                         'Agility (+1 defense, from ' + str(player_obj.ent.defense) + ')'], 
                              position='center')

        if choice == 0: # Boosts health
            player_obj.ent.max_hp += 20
            player_obj.ent.hp += 20
        elif choice == 1: # Boosts attack
            player_obj.ent.attack += 1
        elif choice == 2: # Boosts defense
            player_obj.ent.defense += 1
        pyg.update_gui()

def check_tile(x, y):
    """ Reveals newly explored regions with respect to the player's position. """
    
    # Define some shorthand
    tile = player_obj.ent.env.map[x][y]
    
    # Reveal a square around the player
    for u in range(x - 1, x + 2):
        for v in range(y - 1, y + 2):
            player_obj.ent.env.map[u][v].hidden = False
    
    # Reveal a hidden room
    if tile.room:
        if tile.room.hidden:
            tile.room.hidden = False
            for room_tile in tile.room.tiles_list:
                room_tile.hidden = False

## Effects
def cast_heal():
    """ Heals the player. """
    
    if player_obj.ent.fighter.hp == player_obj.ent.fighter.max_hp:
        pyg.update_gui('You are already at full health.', pyg.red)
        return 'cancelled'
    pyg.update_gui('Your wounds start to feel better!', pyg.violet)
    player_obj.ent.fighter.heal(mech.heal_amount)

def cast_lightning():
    """ Finds the closest enemy within a maximum range and attacks it. """
    
    monster = closest_monster(mech.lightning_range)
    if monster is None:  #no enemy found within maximum range
        pyg.update_gui('No enemy is close enough to strike.', pyg.red)
        return 'cancelled'
    pyg.update_gui('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(mech.lightning_damage) + ' hit points.', pyg.light_blue)
    monster.fighter.take_damage(mech.lightning_damage)

def cast_fireball():
    """ Asks the player for a target tile to throw a fireball at. """
    
    pyg.update_gui('Left-click a target tile for the fireball, or right-click to cancel.', pyg.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    pyg.update_gui('The fireball explodes, burning everything within ' + str(int(mech.fireball_radius/pyg.tile_width)) + ' tiles!', pyg.orange)
    for ent in player_obj.ent.env.entities: # Damages every fighter in range, including the player
        if ent.distance(x, y) <= mech.fireball_radius and ent.fighter:
            pyg.update_gui('The ' + ent.name + ' gets burned for ' + str(mech.fireball_damage) + ' hit points.', pyg.orange)
            ent.fighter.take_damage(mech.fireball_damage)

def cast_confuse():
    """ Asks the player for a target to confuse, then replaces the monster's AI with a "confused" one. After some turns, it restores the old AI. """
    
    pyg.update_gui('Left-click an enemy to confuse it, or right-click to cancel.', pyg.light_cyan)
    monster = target_monster(mech.confuse_range)
    if monster is None: return 'cancelled'
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    pyg.update_gui('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', pyg.light_green)

def floor_effects(floor_effect):
    if floor_effect:
        if floor_effect == 'damage':
            player_obj.ent.take_damage(10)
        elif floor_effect == 'overworld':
            build_overworld()
            place_player(env=player_obj.envs['overworld'], loc=player_obj.envs['overworld'].center)

def active_effects():
    """ Applies effects from items and equipment. Runs constantly. """
    global friendly, teleport, dig, super_dig
    
    #if 'transformation potion' in inventory_cache:
    #    player_obj.ent.image = img.dict['monsters'][0]
    #    friendly = True
    #else:
    #    #player.image = images[2]
    #    friendly = False
    
    try:
        if get_equipped_in_slot('dominant hand').name == 'super shovel':
            super_dig = True
        else:
            super_dig = False
    except:
        super_dig = False

#######################################################################################################################################################
# Quests
class Quest:
    """ Holds quest information. """

    def __init__(self, name='', notes=[], tasks=[], category='main'):
        """ name     : string; title of quest
            content  : list of strings; notes and checklists
            category : string in ['main', 'side']; organizes quest priority
            finished : Boolean; notes if the quest has been completed """

        self.name     = name
        self.notes    = notes
        self.tasks    = tasks
        self.category = category
        self.finished = False
        
        self.content  = notes + tasks
        self.categories    = ['Notes' for i in range(len(notes))]
        self.categories    += ['Tasks' for i in range(len(tasks))]

class Questlog:
    """ Manages quest menu and modifies Quest objects. """
    
    def __init__(self):
        """ Only runs once when a new game is started.

            quests          : list of Quest objects
            quest_names     : list of strings
            categories      : list of strings; 'main' or 'side'
            main_quests     : list of Quest objects
            side_quests     : list of Quest objects
            selected_quest  : Quest object
            
            menu_index      : int; toggles questlog pages
            categories      : 
            achievements    : """
        
        # Initialize parameters
        self.menu_index = 0
        
        # Create default quests
        gathering_supplies  = Quest(name='Gathering supplies',
                                    notes=['My bag is nearly empty.',
                                           'It would be good to have some items on hand.'],
                                    tasks=['☐ Collect 3 potions.',
                                           '☐ Find a spare shovel.'],
                                    category='Main')

        finding_a_future    = Quest(name='Finding a future',
                                    notes=['I should make my way into town.'],
                                    tasks=['☐ Wander east.'],
                                    category='Main')

        making_a_friend     = Quest(name='Making a friend',
                                    notes=['I wonder who this is. Maybe I should say hello.'],
                                    tasks=['☐ Say hello to the creature.',
                                           '☐ Get to know them.'],
                                    category='Side')

        furnishing_a_home   = Quest(name='Furnishing a home',
                                    notes=['My house is empty. Maybe I can spruce it up.'],
                                    tasks=['☐ Use the shovel to build new rooms.',
                                           '☐ Drop items to be saved for later use.',
                                           '☐ Look for anything interesting.'],
                                    category='Side')

        self.quests = [gathering_supplies, finding_a_future, making_a_friend, furnishing_a_home]
        self.update_questlog()

    def back_to_menu(self):
        """ Toggle menus. """
        
        if self.menu_index == 0: self.menu_index += 1
        else:                    self.menu_index = 0
    
    def update_questlog(self):
        """ Updates data containers used in menu. """
        
        self.main_quests = []
        self.side_quests = []
        self.quest_names = []
        self.categories  = []
        
        for quest in self.quests:
            
            if quest.category == 'Main': self.main_quests.append(quest)
            else:                        self.side_quests.append(quest)
            
            self.quest_names.append(quest.name)
            self.categories.append(quest.category)

    def questlog_menu(self):
        """ Manages menu for quest titles and details. """
        
        # Show lsit of quests
        if self.menu_index == 0:
        
            # List of quests
            quest_index = new_menu(header='Questlog',
                                   options=self.quest_names,
                                   options_categories=self.categories)
            
            # Description of selected quest
            if type(quest_index) == int:
                self.selected_quest = self.quests[quest_index]
                self.update_questlog()
                selected_index = new_menu(header=self.selected_quest.name,
                                          options=self.selected_quest.content,
                                          options_categories=self.selected_quest.categories)
                
                # Go back to list of quests
                if type(selected_index) != int:
                    self.back_to_menu()
        
        # Show description of selected quest
        else:
            
            # Description of selected quest
            selected_index = new_menu(header=self.selected_quest.name,
                                      options=self.selected_quest.content,
                                      options_categories=self.selected_quest.categories)
            
            # Go back to list of quests
            if type(selected_index) == int:
                questlog.back_to_menu()

@debug_call
def friend_quest(init=False, NPC_name=None):
    """ Manages friend quest, including initialization and dialogue. """
    
    global friend_messages, friend_level, NPC_names

    # Initialize dialogue
    if init:
        
        # Set NPC names
        NPC_names = ['friend']
        
        # Initialize friend dialogue
        friend_messages, friend_level = {}, 1
        
        # Friend: level 1
        cache_list = []
        for i in range(34):
            if i < 30:
                cache_list.append("Who is this, anyways?")
                cache_list.append("")
                cache_list.append("")
            else:
                cache_list.append("Your new friend seems bored.")
                cache_list.append("Your new friend gazes deeply into the distance.")
                cache_list.append("Your new friend looks nervous.")
                cache_list.append("You give your new friend a playful nudge.")
        friend_messages['level 1'] = cache_list
        
        # Friend: level 2
        cache_list = []
        for i in range(34):
            if i < 30:
                cache_list.append("Your friend looks happy to see you.")
                cache_list.append("")
                cache_list.append("")
            else:
                cache_list.append("Why are you here?")
                cache_list.append("Your friend seems friendlier now.")
                cache_list.append("Who is this, anyways?")
                cache_list.append("You give your friend a playful nudge.")
        friend_messages['level 2'] = cache_list

        # Friend: level 3
        cache_list = []
        for i in range(34):
            if i < 30:
                cache_list.append("Your friend seems excited.")
                cache_list.append("")
                cache_list.append("")
            else:
                cache_list.append("Your friend feels calmer in your presence.")
                cache_list.append("Your friend fidgets but seems content.")
                cache_list.append("Who is this, anyways?")
                cache_list.append("You give your friend a playful nudge.")
        friend_messages['level 3'] = cache_list
    
    elif NPC_name == 'friend':
        
        # Increase friendship
        friend_level += 0.1
        if friend_level == 1.1:
            pyg.update_gui("☑ You say hello to your new friend.", pyg.white)
            questlog.update_questlog(name="Making a friend")
        
        if int(friend_level) <= 3:
            pyg.update_gui(friend_messages[f'level {int(friend_level)}'][random.randint(0, len(friend_messages[f'level {int(friend_level)}']))], pyg.white)
        else:
            if random.randint(0,10) != 1:
                pyg.update_gui(friend_messages[f'level {int(friend_level)}'][random.randint(0, len(friend_messages[f'level {int(friend_level)}']))], pyg.white)
            else:
            
                # Start quest
                pyg.update_gui("Woah! What's that?", pyg.white)
                x = lambda dx : int((player_obj.ent.x + dx)/pyg.tile_width)
                y = lambda dy : int((player_obj.ent.y + dy)/pyg.tile_height)

                found = False
                for i in range(3):
                    if found:
                        break
                    x_test = x(pyg.tile_width*(i-1))
                    for j in range(3):
                        y_test = y(pyg.tile_height*(j-1))
                        if not player_obj.ent.env.map[x_test][y_test].entity:
                            item_component = Item(use_function=mysterious_note)
                            item = Object(0,
                                          0,
                                          img.other['scrolls']['closed'],
                                          name="mysterious note", category='scrolls', image_num=0,
                                          item=item_component)
                            player_obj.ent.env.map[x_test][y_test].item = item
                            found = True
                            break
        pygame.event.clear()

def mysterious_note():
    global questlog

    note_text = ["ξνμλ λξ ξλι ξγθιβξ ξ θθ.", "Ηκρσ σρσ λβνξθι νθ.", "Ψπθ αβνιθ πθμ."]
    new_menu(header="mysterious note", options=note_text, position="top left")
    pyg.update_gui('Quest added!', pyg.green)
    mysterious_note = Quest(name='Mysterious note',
                         content=['My pyg.green friend dropped this. It has a strange encryption.',
                                  'ξνμλ λξ ξλι ξγθιβξ ξ θθ,', 'Ηκρσ σρσ λβνξθι νθ,', 'Ψπθ αβνιθ πθμ.',
                                  '☐ Keep an eye out for more mysterious notes.'],
                         category='Main')

#######################################################################################################################################################
# Utilities
## Gameplay
def is_blocked(env, loc):
    """ Checks for barriers and trigger dialogue. """
    
    # Check for barriers
    if env.map[loc[0]][loc[1]].blocked:
        return True
    
    # Check for monsters
    if env.map[loc[0]][loc[1]].entity: 
    
        # Triggers dialogue for friend
        #if env.map[loc[0]][loc[1]].entity.name in NPC_names:
            #friend_quest(NPC_name=env.map[loc[0]][loc[1]].entity.name)
        
        return True
    
    # Triggers message for hidden passages
    if env.map[loc[0]][loc[1]].unbreakable:
        pyg.update_gui('A mysterious breeze seeps through the cracks.', pyg.white)
        pygame.event.clear()
        return True
    
    return False

@debug_call
def sort_inventory():        
    inventory_cache = {'weapon': [], 'armor': [], 'potion': [], 'scroll': [], 'drug': [], 'other': []}
    other_cache     = {'weapon': [], 'armor': [], 'potion': [], 'scroll': [], 'drug': [], 'other': []}

    # Sort by category
    for item_list in player_obj.ent.inventory.values():
        for item in item_list:
            inventory_cache[item.role].append(item)
    
    # Sort by stats:
    sorted(inventory_cache['weapon'], key=lambda x: x.attack_bonus + x.defense_bonus + x.hp_bonus)
    sorted(inventory_cache['armor'],  key=lambda x: x.attack_bonus + x.defense_bonus + x.hp_bonus)
    sorted(inventory_cache['potion'], key=lambda x: x.name)
    sorted(inventory_cache['scroll'], key=lambda x: x.name)
    sorted(inventory_cache['other'],  key=lambda x: x.name)

    player_obj.ent.inventory = inventory_cache

def movement_speed(toggle=True):
    global movement_speed_toggle
    
    if toggle:
        if movement_speed_toggle == len(toggle_list)-1: 
            movement_speed_toggle = 0
        else:
            movement_speed_toggle += 1
    
    if toggle_list[movement_speed_toggle] == 'Fast':
        pygame.key.set_repeat(120, 120)
        if toggle: pyg.update_gui(f"Movement speed: Fast", pyg.red)
    elif toggle_list[movement_speed_toggle] == 'Slow':
        pygame.key.set_repeat(0, 0)
        if toggle: pyg.update_gui(f"Movement speed: Fixed", pyg.white)
    else:
        pygame.key.set_repeat(250, 150)
        if toggle: pyg.update_gui(f"Movement speed: Default", pyg.blue)

def from_dungeon_level(table):
    """ Returns a value that depends on the dungeon level. Runs in groups.
        The table specifies what value occurs after each level with 0 as the default. """
    
    for (value, level) in reversed(table):
        if player_obj.ent.env.lvl_num >= level:
            return value
    return 0

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

## Files
@debug_call
def save_account():    
    """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen.
        Structures
        ----------
        = player_obj
        == envs
        === garden
        === home
        === dungeons
        == ent """
        
    options = [f"File 1",
               f"File 2",
               f"File 3"]
    if player_obj.file_num: options[player_obj.file_num - 1] += ' *'
    
    # Select file number
    file_num = new_menu(
        header      = "Save",
        options     = options,
        backgrounds = ["Data/File_1/screenshot.png",
                       "Data/File_2/screenshot.png",
                       "Data/File_3/screenshot.png"])
    if type(file_num) != int: main_menu()
    else:
        file_num += 1
        
        # Update Player object
        player_obj.file_num = file_num
        
        # Save everything
        with open(f"Data/File_{file_num}/ent.pkl", 'wb') as file:
            pickle.dump(player_obj.ent, file)
        with open(f"Data/File_{file_num}/envs.pkl", 'wb') as file:
            pickle.dump(player_obj.envs, file)
        screenshot(size='display', visible=False, folder=f"Data/File_{file_num}", filename="screenshot.png", blur=True)

@debug_call
def load_account():    
    """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen.
        Structures
        ----------
        = player_obj
        == envs
        === garden
        === home
        === dungeons
        == ent """
    
    global player_obj
    
    options = [f"File 1",
               f"File 2",
               f"File 3"]
    if player_obj.file_num: options[player_obj.file_num - 1] += ' *'
    
    # Select file number
    file_num = new_menu(
        header      = "Load",
        options     = options,
        backgrounds = ["Data/File_1/screenshot.png",
                       "Data/File_2/screenshot.png",
                       "Data/File_3/screenshot.png"])
    if file_num is not None:
        
        
        if type(file_num) != int: main_menu()
        else:
            file_num += 1
            pyg.startup_toggle2 = False
        
        player_obj = Player()
        with open(f"Data/File_{file_num}/envs.pkl", "rb") as file:
            player_obj.envs = pickle.load(file)
        with open(f"Data/File_{file_num}/ent.pkl", "rb") as file:
            player_obj.ent = pickle.load(file)
        
        for env in player_obj.envs.values():
            if type(env) == list:
                for sub_env in env:
                    sub_env.camera = Camera(player_obj.ent)
            else:
                env.camera = Camera(player_obj.ent)

@debug_call
def screenshot(size='display', visible=False, folder="Data/Cache", filename="screenshot.png", blur=False):
    """ Takes a screenshot.
        cache:  saves a regular screenshot under Data/Cache/screenshot.png
        save:   moves regular cached screenshot to Data/File_#/screenshot.png 
        blur:   adds a blur effect """
    
    global gui_toggle, msg_toggle, screenshot_time_counter

    # Turn off gui
    pyg.gui_toggle, pyg.msg_toggle = False, False
    
    # Select display size
    if size == 'full':
        camera_cache = [player_obj.ent.env.camera.x, player_obj.ent.env.camera.y]
        pyg.display = pygame.display.set_mode((len(player_obj.ent.env.map[0])*16, len(player_obj.ent.env.map)*16),)
        player_obj.ent.env.camera.x = 0
        player_obj.ent.env.camera.y = 0
        player_obj.ent.env.camera.update()
    render_all(size=size, visible=visible)
    
    # Save image
    path = folder + '/' + filename
    pygame.image.save(pyg.display, path)
    
    # Add effects
    if blur:
        image_before = Image.open(folder + '/' + filename)
        image_after  = image_before.filter(ImageFilter.BLUR)
        image_after.save(folder + '/' + filename)
    
    # Reset everthing to normal
    if size == 'full':
        pyg.display = pygame.display.set_mode((pyg.screen_width, pyg.screen_height),)
        player_obj.ent.env.camera.x = camera_cache[0]
        player_obj.ent.env.camera.y = camera_cache[1]
        player_obj.ent.env.camera.update()
    render_all()
    pyg.gui_toggle, pyg.msg_toggle = True, True

#######################################################################################################################################################
# Global scripts
if __name__ == "__main__":
    main()

#######################################################################################################################################################