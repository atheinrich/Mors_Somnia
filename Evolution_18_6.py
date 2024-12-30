#######################################################################################################################################################
##
## DYSOLUTION
##
#######################################################################################################################################################

#######################################################################################################################################################
# Imports
## Game mechanics
import pygame
from pygame.locals import *
import random
import textwrap

## File saving
import pickle
import os
import shutil
import copy

## Debugging
import time
import sys
import inspect

# Aesthetics
from PIL import Image, ImageFilter

#######################################################################################################################################################
#######################################################################################################################################################
# Global values
## Other
step_counter            = [False, 0, False, 0]
file_set                = ['', '', '']
super_dig               = False
idle_animation_counter  = [0]
key_cache = K_DOWN
category_order = ["apparel", "weapons", "hair"]
hair_list, skin_list, handedness_list = ['null', 'hair'], ['player'], ['left', 'right']
hair_index, skin_index, handedness_index = 0, 0, 0
debug = True
movement_speed_toggle, movement_speed_cache, toggle_list = 0, 1, ['Default', 'Fast']
last_press_time, cooldown_time = 0, 0.5

## Quests
current_tasks = {'main': ['Finish the game.'],
                 'side': ['Try the beta.']}
quest_menu_index = 0

#######################################################################################################################################################
# Startup
def __STARTUP__():
    pass

## Initialization
def main():
    """ Initializes the essentials and opens the main menu. """
    
    global pyg, mech, img, aud, player_obj
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # Initialize pygame (parameters, screen, clock, etc.)
    pyg  = Pygame()
    
    # Initialize general mechanics (?)
    mech = Mechanics()
    
    # Import images (sorted dictionary and cache)
    img         = Images()
    img.flipped = Images(flipped=True)
    
    # Initialize and load pygame audio
    aud  = Audio()
    
    # Create player
    player_obj = Player()
    player_obj.create_player()

    # Generate main menu
    player_obj.envs['garden'] = build_garden()
    
    # Open the main menu
    main_menu()

def build_garden():
    """ Generates environment for main menu. """
    
    # Initialize environment
    player_obj.envs['garden'] = Environment(
        name       = 'garden',
        floor      = 0,
        size       = 1,
        soundtrack = [aud.home[0]],
        entities   = [],
        player_coordinates = None,
        camera     = None)
    
    # Construct rooms
    main_room = Rectangle(0, 0, 19, 14)
    player_obj.envs['garden'].center = main_room.center()
    player_obj.envs['garden'].create_room(
        rect = main_room,
        hidden = False,
        unbreakable = False,
        image_name_1 = 'floors',
        image_name_2 = 'dark blue') #?
    
    # Update player
    place_player(env=player_obj.envs['garden'], loc=player_obj.envs['garden'].center)
    player_obj.envs['garden'].camera = Camera(player_obj.ent)
    player_obj.envs['garden'].camera.fixed = True
    
    return player_obj.envs['garden']

def main_menu():
    """ Manages the menu. Handles player input. Only active when the main menu is open. """
    
    global load_saves, game_title, last_press_time, cooldown_time
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # -------------------------------------- INIT --------------------------------------
    # Play menu music
    aud.control(new_track=aud.menu[0])

    # Initialize title
    title_font = pygame.font.SysFont('segoeuisymbol', 40, bold=True)
    game_title = title_font.render("EVOLUTION", True, pyg.green)
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
        background_image = pygame.image.load("Data/File_0/garden.png").convert()
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
        pyg.clock.tick(30)
        event = pygame.event.get()
        
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
                    elif event[0].key in pyg.key_0:
                        play_game()
                    
                    elif event[0].key in pyg.key_RETURN:
                        
                        # >>NEW GAME<<
                        if choice == 0:
                            pyg.startup_toggle2 = True  # when false, prevents returning to character creation menu after initialization
                            character_creation()
                            if not pyg.startup_toggle2:
                                new_game(True)
                                play_game()
                        
                        # >>LOAD<<
                        if choice == 1:
                            load_account()
                            play_game()
                        
                        # >>SAVE<<
                        if choice == 2:
                            save_account()
                            play_game()

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
                                              'Unused:                                   7',
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
                        else:
                            if player_obj.envs['home']:
                                place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].player_coordinates)

            # -------------------------------------- RENDER --------------------------------------
            pyg.gui_toggle, pyg.msg_toggle = False, False
            render_all()
            
            if menu_toggle:
                y = 300
                for menu_choice_surface in menu_choices_surfaces:
                    pyg.screen.blit(menu_choice_surface, (80, y))
                    y += 24
                pyg.screen.blit(game_title, game_title_pos)
                pyg.screen.blit(cursor_img, cursor_img_pos)
                pygame.display.flip()

## Gameplay and utility
def new_game(new):
    """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
        Called when starting a new game or loading a previous game.

        new:  creates player as Object with Fighter stats, calls make_home(), then loads initial inventory
        else: calls load_objects_from_file() to load player, inventory, and current floor """
    
    global questlog
    if debug: print(f"{debug_call()[0]:<30}{new}")

    # Clear prior data
    new_game_trigger = True
    #friend_quest(init=True)
    player_obj.envs['garden'] = build_garden()

    # Generate new player
    player_obj.create_player()
    questlog = Questlog()
    
    # Generate map
    player_obj.envs['home'] = build_home()
    place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].center)

    pyg.update_gui()
    message('Welcome!', pyg.red)
    
    # Create items
    clothes = create_objects('clothes', [0, 0])
    hair = create_objects('hair', [0, 0])
    shovel  = create_objects('shovel',  [0, 0])
    player_obj.ent.inventory[clothes.role].append(clothes)
    player_obj.ent.inventory[hair.role].append(hair)
    player_obj.ent.inventory[shovel.role].append(shovel)
    clothes.toggle_equip()
    sort_inventory()

def inventory_menu(header):
    """ Calls a menu with each item of the inventory as an option, then returns an item if it is chosen. """
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
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

def debug_call():
    """ Just a print statement for debugging. Shows which function is called alongside variable details. """
    optional_data = time.strftime("%M:%S", time.localtime())
    return [inspect.currentframe().f_back.f_code.co_name, optional_data]

def load_game(): # ! (files)

    # -------------------------------------- LOAD --------------------------------------
    load_objects_from_file(load_saves[0])
    load_objects_from_file(load_saves[4], inventory)
    if player_obj.ent.env in player_obj.envs['dungeons']:
        load_floor(load_saves[3], aud.home[0], load_objects_file='Data/data_dungeon_obj.pkl')
    else:
        load_floor(load_saves[1], aud.home[0], load_objects_file=load_saves[2], home=True)
        #load_floor('screenshot_hidden.pkl', aud.home[0], home=True, load_objects_file='screenshot_objects.pkl')

    player_obj.ent.env.camera.update()
        
    pyg.update_gui() # places health and dungeon level on the pyg.screen
    message('Welcome!', pyg.red)
    
    sort_inventory()

def file_menu(header): # ! (files)
    """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen. """
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    options = [f"File 1 {file_set[0]}",
               f"File 2 {file_set[1]}",
               f"File 3 {file_set[2]}"]
               
    set_file_backgrounds = ["Data/File_1/screenshot.png",
                            "Data/File_2/screenshot.png",
                            "Data/File_3/screenshot.png"]
                  
    index = new_menu(header, options, backgrounds=set_file_backgrounds)
    if type(index) != int: main_menu()
    else:                  index += 1
    
    return index

## Classes
class Pygame:
    """ Pygame stuff. Does not need to be saved, but update_gui should be run after loading a new file. """

    def __init__(self):
        
        # Graphics parameters
        self.screen_width      = 640 # 20 tiles
        self.screen_height     = 480 # 15 tiles
        self.tile_width        = 32
        self.tile_height       = 32
        self.map_width         = 640 * 2
        self.map_height        = 480 * 2
        self.tile_map_width    = int(self.map_width/self.tile_width)
        self.tile_map_height   = int(self.map_height/self.tile_height)

        # Graphics overlays
        self.msg_toggle        = True # Boolean; shows or hides messages
        self.msg               = []   # list of font objects; messages to be rendered
        self.gui_toggle        = True # Boolean; shows or hides GUI
        self.gui               = None # font object; stats to be rendered
        self.gui_env           = None # string; uses pre-defined text

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
        self.key_UP            = [K_UP,    K_w]             # movement (up)
        self.key_DOWN          = [K_DOWN,  K_s]             # movement (down)
        self.key_LEFT          = [K_LEFT,  K_a]             # movement (left)
        self.key_RIGHT         = [K_RIGHT, K_d]             # movement (right)
        self.key_RETURN        = [K_RETURN]                 # activate
        self.key_SLASH         = [K_SLASH]                  # messages
        
        # Other
        self.startup_toggle = True
        self.startup_toggle2 = True
        
        # Pygame initialization
        pygame.init()
        pygame.display.set_caption("Evolution") # Sets game title
        self.screen            = pygame.display.set_mode((self.screen_width, self.screen_height),)
        self.font              = pygame.font.SysFont('segoeuisymbol', 16, bold=True)
        self.clock             = pygame.time.Clock()
        pygame.key.set_repeat(250, 150)

    def update_gui(self):
        if self.gui_env in ['home', 'dungeons']:
            self.gui = self.font.render('HP: '            + str(player_obj.ent.hp) + '/' + str(player_obj.ent.max_hp) +  ' '*60 + 
                                        'Environment: ' + str(player_obj.ent.env.name),
                                        True, pyg.yellow)
        else:
            self.gui = self.font.render('', True, pyg.white)

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

    def next_level(self):
        """ Advances player to the next level. """
        if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
        
        message('You take a moment to rest, and recover your strength.', pyg.violet)
        player_obj.ent.heal(int(player_obj.ent.max_hp / 2))  #heal the player by 50%

        # Generate dungeon
        time.sleep(0.5)
        message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', pyg.red)
        build_dungeon_level()
        
        # Change music and dungeon level
        aud.control(new_track=aud.dungeons[player_obj.envs['dungeons'][-1].floor])
        
        # Place player and update screen
        place_player(env=player_obj.envs['dungeons'][-1], loc=player_obj.envs['dungeons'][-1].center)

    def get_impact_image(self):
        if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
        
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
            dict  : dict; mutable dictionary of names and pygame images
            cache : dict; unmutable dictionary of names and pygame images """

        # Create entity dictionary
        ent_matrix = self.load('Data/tileset_ent.png', flipped)
        entity_names = ['white', 'black', 'cyborg',
                        'friend', 'eye', 'eyes', 'troll', 'triangle', 'purple',
                        'tentacles', 'round1', 'aura', 'round2', 'grass',
                        'skeleton', 'round3', 'lizard']
        self.ent = {key: None for key in entity_names}
        index = 0
        entity_options = ['front', 'back', 'left', 'right']
        for entity_name in self.ent:
            self.ent[entity_name] = {option: image for (option, image) in zip(entity_options, ent_matrix[index])}
            if flipped:
                cache = self.ent[entity_name]['right']
                self.ent[entity_name]['right'] = self.ent[entity_name]['left']
                self.ent[entity_name]['left'] = cache
            index += 1
        
        # Create equipment dictionary
        equip_matrix = self.load('Data/tileset_equip.png', flipped)
        equip_names = ['iron armor', 'green clothes', 'iron shield', 'medium hair',
                       'dagger', 'blood dagger', 'shovel', 'super shovel', 'sword', 'blood sword']
        self.equip = {key: None for key in equip_names}
        index = 0
        equip_options = ['dropped', 'front', 'back', 'left', 'right']
        for _ in equip_names:
            self.equip[equip_names[index]] = {option: image for (option, image) in zip(equip_options, equip_matrix[index])}
            if flipped:
                cache = self.equip[equip_names[index]]['right']
                self.equip[equip_names[index]]['right'] = self.equip[equip_names[index]]['left']
                self.equip[equip_names[index]]['left'] = cache
            index += 1
        
        # Create other dictionary
        other_matrix = self.load('Data/tileset_other.png', flipped)
        other_names = ['decor', 'drugs', 'potions', 'scrolls', 'stairs', 'floors', 'walls']
        decor_options = ['tree', 'bones', 'boxes', 'fire']
        drugs_options = ['needle', 'skin', 'teeth', 'bowl1', 'plant', 'scroll', 'bubbles']

        potions_options = ['red', 'blue', 'gray', 'purple']
        scrolls_options = ['closed', 'open']
        stairs_options = ['door']
        floors_options = ['dark green', 'dark blue', 'dark red', 'green', 'red', 'blue', 'wood', 'water',
                         'sand1', 'sand2', 'grass1', 'grass2', 'bubbles1', 'bubbles2', 'bubbles3',
                         'dirt1', 'dirt2']
        walls_options = ['dark green', 'dark red', 'dark blue', 'gray', 'red', 'green', 'gold']
        other_options = [decor_options, drugs_options, potions_options, scrolls_options, stairs_options, floors_options, walls_options]
        self.other = {}
        index = 0
        for _ in other_names:
            self.other[other_names[index]] = {option: image for (option, image) in zip(other_options[index], other_matrix[index])}
            index += 1
        
        self.dict = self.ent | self.equip | self.other
        
        #self.ent_cache   = copy.deepcopy(self.ent)
        #self.equip_cache = copy.deepcopy(self.equip)
        #self.other_cache = copy.deepcopy(self.other)

    def load(self, filename, flipped=False):
        
        # Import tileset
        tileset = pygame.image.load(filename).convert_alpha()
    
        # Break tileset into rows and columns
        num_rows     = tileset.get_height() // pyg.tile_height
        num_columns  = tileset.get_width() // pyg.tile_width
        tile_matrix  = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
        for row in range(num_rows):
            for col in range(num_columns):
                
                # Find location of image in tileset
                x     = col * pyg.tile_width
                y     = row * pyg.tile_height
                if flipped:
                    image = pygame.transform.flip(tileset.subsurface(x, y, pyg.tile_width, pyg.tile_height).convert_alpha() , True, False)
                else:       image = tileset.subsurface(x, y, pyg.tile_width, pyg.tile_height).convert_alpha()                
                
                # Update tile matrices
                tile_matrix[row][col] = image
        
        return tile_matrix

    def combine(self, ent):
        main = [self.ent[ent.name]['front'],
                self.ent[ent.name]['back'],
                self.ent[ent.name]['left'],
                self.ent[ent.name]['right']]

    def flip(self, obj):
        
        if type(obj) == list:
            obj = [pygame.transform.flip(objs, True, False) for objs in obj]
        elif type(obj) == dict:
            obj = {key: pygame.transform.flip(value, True, False) for (key, value) in obj.items()}
        else:
            print("------flip error")

class Audio:
    """ Manages audio. One save for each file. """

    def __init__(self):
        
        # Initialize music player
        pygame.mixer.init()
        
        self.menu = []
        self.home = []
        self.dungeons = [None]

        self.menu.append(pygame.mixer.Sound("Data/music_menu.mp3"))
        self.home.append(pygame.mixer.Sound("Data/music_home.mp3"))
        self.dungeons.append(pygame.mixer.Sound("Data/music_dungeon_1.mp3"))
        self.dungeons.append(pygame.mixer.Sound("Data/music_dungeon_2.mp3"))

        # Start music
        self.current_track = self.menu[0]
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

class Player: # ! (files)
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
        self.img        = None

    def create_player(self):
        
        self.ent = Entity(
            name       = 'Alex',
            role       = 'player',
            image_name_1 = 'white',
            image_name_2 = 'front',
            images     = None,
            image      = None,
            handedness = 'left',

            exp        = 0,
            rank       = 1,
            hp         = 100,
            max_hp     = 100,
            attack     = 100,
            defense    = 100,
            effects    = [],

            env        = None,
            tile       = None,
            x          = 10 * pyg.tile_width,
            y          = 10 * pyg.tile_width,
            reach      = None,  

            inventory  = {'weapon': [],   'armor': [],   'potion':        [],   'scroll':            [], 'other': []},
            equipment  = {'head':   None, 'body':  None, 'dominant hand': None, 'non-dominant hand': None},
            death      = None,
            follow     = False,
            aggressive = False,
            questline  = None)
        
        dagger  = create_objects('dagger',  [0, 0])
        hair    = create_objects('hair',    [0, 0])
        self.ent.inventory[dagger.role].append(dagger)
        self.ent.inventory[hair.role].append(hair)
        dagger.toggle_equip()

#######################################################################################################################################################
# Player actions
def new_menu(header, options, options_categories=None, position='top left', backgrounds=None):
    """ IMPORTANT. Creates cursor, background, and menu options, then returns index of choice.

        header             : string; top line of text
        options            : list of strings; menu choices
        options_categories : list of strings; categorization; same length as options
        position           : chooses layout preset """

    global game_title

    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
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
    header_position    = {'top left': [5,        10],       'center': [int((pyg.screen_width - game_title.get_width())/2), 85]}
    cursor_position    = {'top left': [50+tab_x, 38+tab_y], 'center': [50, 300]}
    options_positions  = {'top left': [80+tab_x, 34],       'center': [80, 300]}
    category_positions = {'top left': [5,        34],       'center': [80, 300]}

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
    while True:
        pygame.time.Clock().tick(30)
        
        # Render menu background
        if backgrounds:
            pyg.screen.fill(pyg.black)
            pyg.screen.blit(backgrounds[choice], (0, 0))
        else:
            pyg.screen.fill(pyg.black)
        
        # Render header and cursor
        pyg.screen.blit(header, header_position[position])
        pyg.screen.blit(cursor_img, cursor_position_mutable)
        
        # Render categories and options
        for i in range(len(options_render)):
            
            # Render category text if it is not present 
            if options_categories:
                if options_categories[i] != options_categories_cache:
                    options_categories_cache = options_categories[i]
                    text = pyg.font.render(f'{options_categories_cache.upper()}:', True, pyg.gray)
                    options_positions_mutable[1] += tab_y
                    pyg.screen.blit(text, (category_positions_mutable[0], options_positions_mutable[1]))
                
            # Render option text
            pyg.screen.blit(options_render[i], options_positions_mutable)
            options_positions_mutable[1] += 24
        options_positions_mutable = options_positions[position].copy()
        category_positions_mutable = category_positions[position].copy()
        pygame.display.flip()
        
        # Called when the user inputs a command
        for event in pygame.event.get():
            if event.type == KEYDOWN:

                # >>RESUME<<
                if event.key in pyg.key_0:
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
                    return choice

# ! (animation)
def character_creation():
    """ Manages the character creation menu. Handles player input. Only active when menu is open.
        Called when starting a new game.
    
        HAIR:       sets hair by altering hair_index, which is used in new_game to add hair as an Object hidden in the inventory
        HANDEDNESS: mirrors player/equipment tiles, which are saved in img.dict and img.cache
        ACCEPT:     runs new_game() to generate player, home, and default items, then runs play_game() """
    
    global load_saves, hair_index, skin_index, handedness_index
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # -------------------------------------- INIT --------------------------------------
    # Initialize cursor
    cursor_img = pygame.Surface((16, 16)).convert()
    cursor_img.set_colorkey(cursor_img.get_at((0,0)))
    pygame.draw.polygon(cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
    cursor_img_pos = [50, 304]
    
    # Set character background
    background_image = pygame.image.load("Data/room.png")
    
    # Initialize menu options
    menu_choices = ["HAIR", "HANDEDNESS", "", "ACCEPT", "BACK"]   
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
    while True:
        pyg.clock.tick(30)
        
        # Prevent escape from going back to character creation
        if not pyg.startup_toggle2:
            return
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # >>MAIN MENU<<
                if event.key in pyg.key_0:
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
                    
                    # >>HANDEDNESS<<
                    if choice == 1:
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
                    if choice == 3:
                        pyg.startup_toggle2 = False
                        return
                    
                    # >>MAIN MENU<<
                    if choice == 4:
                        return
        
        # -------------------------------------- RENDER --------------------------------------
        # Implement timed rotation of character
        if time.time()-last_press_time > cooldown_time:
            last_press_time = float(time.time()) 
            player_obj.ent.image_name_2 = orientations[orientations.index(player_obj.ent.image_name_2) - 1]

        # Set menu background
        pyg.screen.fill(pyg.black)
        
        # Renders menu to update cursor location
        y = 300
        for menu_choice in menu_choices:
            pyg.screen.blit(menu_choice, (80, y))
            y += 24
        pyg.screen.blit(cursor_img, cursor_img_pos)
        pyg.screen.blit(background_image, (400, 200))
        player_obj.ent.draw(pyg.screen, loc=(464, 264))
        pygame.display.flip()

# ! (other)
def play_game():
    """ IMPORTANT. Processes user input and triggers monster movement. """
    
    global player_action, msg_toggle, stairs, last_press_time
    global gui_toggle, questlog
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    player_move = False
    pygame.key.set_repeat(250, 150)
    
    # Show gui
    pyg.gui_toggle, pyg.msg_toggle = True, True

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
            if not player_obj.ent.death:
                if event[0].type == KEYDOWN:
                    active_effects()
                    print(f"\n({player_obj.ent.x}, {player_obj.ent.y}), ({int(player_obj.ent.x/pyg.tile_width)}, {int(player_obj.ent.y/pyg.tile_height)})")
                    
                    # >>MAIN MENU<<
                    if event[0].key in pyg.key_0:
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
                            if player_obj.ent.tile.item.name == 'stairs':
                                
                                # ! (saving)
                                # Save house
                                #if player_obj.ent.env == player_obj.ent.home:  
                                #    save_floor(load_saves[1])
                                #    save_objects_to_file(load_saves[2], data_source=data_objects_1)
                                mech.next_level()
                            else:
                                player_obj.ent.tile.item.pick_up()
                                player_obj.ent.tile.item = None

                    # >>HOME<<
                    if event[0].key == K_RSHIFT:
                        if player_obj.ent.tile.item:
                            if player_obj.ent.tile.item.name == 'stairs':
                                if player_obj.ent.env.name != 'home':
                                    go_home()

                    # >>VIEW STATS<<
                    if event[0].key in pyg.key_1:
                        level_up_exp = mech.level_up_base + player_obj.ent.rank * mech.level_up_factor
                        new_menu(header  =  'Character Information',
                                 options = ['Rank:                                ' + str(player_obj.ent.rank),
                                            'Experience:                       ' + str(player_obj.ent.exp),
                                            'Experience to level up:    ' + str(level_up_exp),
                                            'Maximum HP:                    ' + str(player_obj.ent.max_hp),
                                            'Attack:                             ' + str(player_obj.ent.attack),
                                            'Defense:                           ' + str(player_obj.ent.defense)])
                    
                    # >>CHECK INVENTORY<<
                    elif event[0].key in pyg.key_2:
                        chosen_item = inventory_menu("INVENTORY:         USE ITEM")
                        if chosen_item is not None:
                            chosen_item.use()
                            pyg.update_gui()
                    
                    # >>DROP ITEM<<
                    elif event[0].key in pyg.key_3:
                        if player_obj.ent.tile.item:
                            message("There's already something here", color=pyg.red)
                        else:
                            chosen_item = inventory_menu("INVENTORY:         DROP ITEM")
                            if chosen_item is not None:
                                chosen_item.drop()
                                pygame.event.clear()
                    
                    # >>VIEW QUESTLOG<<
                    elif event[0].key in pyg.key_4:
                        try:
                            questlog.questlog_menu()
                        except:
                            questlog = Questlog()
                            questlog.questlog_menu()
                    
                    # >>MOVEMENT SPEED<<
                    elif event[0].key in pyg.key_5 and (time.time()-last_press_time > cooldown_time):
                        movement_speed(adjust=True)
                        last_press_time = float(time.time())
                    
                    # >>SCREENSHOT<<
                    elif event[0].key in pyg.key_6:
                        screenshot(cache=True, big=True)
                    
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
            
            else:
                # >>MAIN MENU<<
                if event[0].type == KEYDOWN:
                    if event[0].key in pyg.key_0:
                        return
                        
                # >>TOGGLE MESSAGES<<
                elif event[0].key in pyg.key_SLASH:
                    if pyg.msg_toggle:
                        pyg.msg_toggle = False
                    else:
                        if pyg.gui_toggle:
                            pyg.gui_toggle = False
                            pyg.msg_toggle = False,
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

#######################################################################################################################################################
# Play game
def __PLAY_GAME__():
    pass

def go_home():
    """ Advances player to home. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    message('You take a moment to rest, and recover your strength.', pyg.violet)
    player_obj.ent.heal(int(player_obj.ent.max_hp / 2)) # Heals the player by 50%
    time.sleep(0.5)
    message('You gather you belongings and head home.', pyg.red)
    
    place_player(env=player_obj.ent.env, loc=player_obj.ent.env.center)

def floor_effects(floor_effect):
    if floor_effect == "fire":
        player_obj.ent.take_damage(10)
    pass

#######################################################################################################################################################
# Environment management
def __ENVIRONMENT_MANAGEMENT__():
    pass

def place_objects(room, env):
    """ Decides the chance of each monster or item appearing, then generates and places them. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # Set spawn chance for [chance, floor]
    max_monsters                    = from_dungeon_level([[2, 1], [3, 4], [5, 10]])
    monster_chances                 = {} # Chance of spawning monster by monster type
    monster_chances['orc']          = 80 # Sets spawn chance for orcs
    monster_chances['troll']        = from_dungeon_level([[15, 2], [30, 5], [60, 10]])
    monster_chances['goblin']       = from_dungeon_level([[1, 2], [5, 5], [10, 10]])
 
    max_items                       = from_dungeon_level([[1, 1], [2, 4]]) # Maximum per room
    item_chances                    = {} # Chance of spawning item by item type
    item_chances['healing']         = 35 # Sets spawn chance for potions
    item_chances['transformation']  = 5 # Sets spawn chance for potions

    item_chances['lightning']       = from_dungeon_level([[25, 4]])
    item_chances['fireball']        = from_dungeon_level([[25, 6]])
    item_chances['confuse']         = from_dungeon_level([[10, 2]])

    item_chances['shovel']          = 20
    item_chances['super shovel']    = 10
    item_chances['sword']           = from_dungeon_level([[10, 5]])
    item_chances['blood dagger']    = from_dungeon_level([[5, 4]])
    item_chances['blood sword']     = from_dungeon_level([[2, 1]])
    item_chances['shield']          = from_dungeon_level([[15, 8]])

    num_monsters = random.choice([0, 1, max_monsters])
    num_items    = random.randint(0, max_items)
    
    for i in range(num_monsters): # Places monsters
        x = random.randint(room.x1+1, room.x2-1)
        y = random.randint(room.y1+1, room.y2-1)
        if not is_blocked(env, [x, y]):
            choice = random_choice(monster_chances)
            ent = create_enemy(choice, [x, y])
            ent.env = env
            ent.tile = env.map[x][y]
            env.map[x][y].entity = ent
            env.entities.append(ent)

    for i in range(num_items): # Places items
        x = random.randint(room.x1+1, room.x2-1)
        y = random.randint(room.y1+1, room.y2-1)
        if not is_blocked(env, [x, y]):
            
            choice = random_choice(item_chances)
            
            if choice == 'healing':          item = create_objects('healing potion',           [x, y])
            elif choice == 'transformation': item = create_objects('transformation potion',    [x, y])
            elif choice == 'lightning':      item = create_objects('scroll of lightning bolt', [x, y])
            elif choice == 'fireball':       item = create_objects('scroll of fireball',       [x, y])
            elif choice == 'confuse':        item = create_objects('scroll of confusion',      [x, y])
            elif choice == 'blood dagger':   item = create_objects('blood dagger',             [x, y])
            elif choice == 'sword':          item = create_objects('sword',                    [x, y])
            elif choice == 'blood sword':    item = create_objects('blood sword',              [x, y])
            elif choice == 'shield':         item = create_objects('shield',                   [x, y])
            elif choice == 'shovel':         item = create_objects('shovel',                   [x, y])
            elif choice == 'super shovel':   item = create_objects('super shovel',             [x, y])
            
            env.map[x][y].item = item

def create_enemy(selection, location):
    """ Creates and returns an object.
    
        Parameters
        ----------
        selection : string; name of object
        location  : list of int; coordinates of item location """

    # ----------------------- DUNGEONS -----------------------
    # Orc
    if selection == 'orc':
        ent = Entity(
            name       = 'orc',
            role       = 'enemy',
            image_name_1 = 'white',
            image_name_2 = 'front',
            images     = None,
            image      = None,
            handedness = 'left',

            exp        = 35,
            rank       = 1,
            hp         = 20,
            max_hp     = 20,
            attack     = 4,
            defense    = 0,
            effects    = [],

            env        = None,
            tile       = None,
            x          = 10 * pyg.tile_width,
            y          = 10 * pyg.tile_width,
            reach      = None,

            inventory  = {'weapon': [],   'armor':  [],   'potion':    [],   'scroll':     [],   'other': []},
            equipment  = {'head':   None, 'body':   None, 'non-dominant hand': None, 'dominant hand': None, 'legs':  None, 'feet': None},
            death      = death,
            follow     = True,
            aggressive = True,
            questline  = None)
    
    elif selection == 'troll':
        ent = Entity(
            name       = 'troll',
            role       = 'enemy',
            image_name_1 = 'white',
            image_name_2 = 'front',
            images     = None,
            image      = None,
            handedness = 'left',

            exp        = 100,
            rank       = 1,
            hp         = 30,
            max_hp     = 30,
            attack     = 8,
            defense    = 2,
            effects    = [],

            env        = None,
            tile       = None,
            x          = 10 * pyg.tile_width,
            y          = 10 * pyg.tile_width,
            reach      = None,

            inventory  = {'weapon': [],   'armor':  [],   'potion':    [],   'scroll':     [],   'other': []},
            equipment  = {'head':   None, 'body':   None, 'non-dominant hand': None, 'dominant hand': None, 'legs':  None, 'feet': None},
            death      = death,
            follow     = True,
            aggressive = True,
            questline  = None)

    elif selection == 'goblin':
        ent = Entity(
            name       = 'goblin',
            role       = 'enemy',
            image_name_1 = 'white',
            image_name_2 = 'front',
            images     = None,
            image      = None,
            handedness = 'left',

            exp        = 500,
            rank       = 1,
            hp         = 50,
            max_hp     = 50,
            attack     = 15,
            defense    = 5,
            effects    = [],

            env        = None,
            tile       = None,
            x          = 10 * pyg.tile_width,
            y          = 10 * pyg.tile_width,
            reach      = None,

            inventory  = {'weapon': [],   'armor':  [],   'potion':    [],   'scroll':     [],   'other': []},
            equipment  = {'head':   None, 'body':   None, 'non-dominant hand': None, 'dominant hand': None, 'legs':  None, 'feet': None},
            death      = death,
            follow     = True,
            aggressive = True,
            questline  = None)
    
    return ent

#######################################################################################################################################################
# Item effects
def cast_heal():
    """ Heals the player. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    if player_obj.ent.fighter.hp == player_obj.ent.fighter.max_hp:
        message('You are already at full health.', pyg.red)
        return 'cancelled'
    message('Your wounds start to feel better!', pyg.violet)
    player_obj.ent.fighter.heal(mech.heal_amount)

def cast_lightning():
    """ Finds the closest enemy within a maximum range and attacks it. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    monster = closest_monster(mech.lightning_range)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', pyg.red)
        return 'cancelled'
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(mech.lightning_damage) + ' hit points.', pyg.light_blue)
    monster.fighter.take_damage(mech.lightning_damage)

def cast_fireball():
    """ Asks the player for a target tile to throw a fireball at. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    message('Left-click a target tile for the fireball, or right-click to cancel.', pyg.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(int(mech.fireball_radius/pyg.tile_width)) + ' tiles!', pyg.orange)
    for ent in player_obj.ent.env.entities: # Damages every fighter in range, including the player
        if ent.distance(x, y) <= mech.fireball_radius and ent.fighter:
            message('The ' + ent.name + ' gets burned for ' + str(mech.fireball_damage) + ' hit points.', pyg.orange)
            ent.fighter.take_damage(mech.fireball_damage)

def cast_confuse():
    """ Asks the player for a target to confuse, then replaces the monster's AI with a "confused" one. After some turns, it restores the old AI. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    message('Left-click an enemy to confuse it, or right-click to cancel.', pyg.light_cyan)
    monster = target_monster(mech.confuse_range)
    if monster is None: return 'cancelled'
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', pyg.light_green)

#######################################################################################################################################################
# Utilities
def __UTILITIES__():
    pass

def render_all(size='screen', visible=False):
    """ Draws tiles and stuff. Constantly runs. """
    
    pyg.screen.fill(pyg.black)
    
    # View entire map
    if size == 'full':
        y_range_1, y_range_2 = 0, len(player_obj.ent.env.map[0])
        x_range_1, x_range_2 = 0, len(player_obj.ent.env.map)
    
    # View screen
    else:
        if not player_obj.ent.env.camera: Camera(player_obj.ent)
            
        y_range_1, y_range_2 = player_obj.ent.env.camera.tile_map_y, player_obj.ent.env.camera.y_range
        x_range_1, x_range_2 = player_obj.ent.env.camera.tile_map_x, player_obj.ent.env.camera.x_range
    
    # Draw visible tiles
    for y in range(y_range_1, y_range_2):
        for x in range(x_range_1, x_range_2):
            tile = player_obj.ent.env.map[x][y]
            
            # Lowest tier (floor and walls)
            if visible or not tile.hidden:
                
                # Sets wall image
                tile.draw(pyg.screen)

                # Second tier (decor and items)
                if tile.item:
                    tile.item.draw(pyg.screen)
                
                # Third tier (entity)
                if tile.entity:
                    tile.entity.draw(pyg.screen)
    
    if size == 'screen':
        if mech.impact:
            pyg.screen.blit(mech.impact_image, mech.impact_image_pos)
        
        # Print messages
        if pyg.msg_toggle: 
           y = 10
           for message in pyg.msg:
               pyg.screen.blit(message, (5, y))
               y += 24
        if pyg.gui_toggle:
            pyg.screen.blit(pyg.gui, (10, 456))
        pygame.display.flip()

def message(new_msg, color):
    """ Initializes messages to be projected with render_all. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # Split the message among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, mech.message_width)
    
    # Update message list
    for line in new_msg_lines:
        
        # Delete older messages
        if len(pyg.msg) == mech.message_height:
            del pyg.msg[0]
        
        # Create message object
        pyg.msg.append(pyg.font.render(line, True, color))

def active_effects():
    """ Applies effects from items and equipment. Runs constantly. """
    global friendly, teleport, dig, super_dig
    
    #if 'transformation potion' in inventory_cache:
    #    player_obj.ent.image = img.dict['monsters'][0]
    #    friendly = True
    #else:
    #    #player.image = images[2]
    #    friendly = False
    
    if step_counter[0]:
        dig = True
    else:
        dig = False
    
    try:
        if get_equipped_in_slot('dominant hand').name == 'super shovel':
            super_dig = True
        else:
            super_dig = False
    except:
        super_dig = False
    
    #if 'scroll of lightning bolt' in inventory_cache:
    #    teleport = True
    #else:
    #    teleport = False

def death(ent):
    if ent.name == 'player':
        message('You died!', pyg.red)
        player_obj.ent.image       = img.dict['decor']['bones']
        player_obj.ent.tile.entity = None
        player_obj.ent.tile.item   = player_obj.ent
    
    else:
        message('The ' + ent.name + ' is dead! You gain ' + str(ent.exp) + ' experience points.', pyg.orange)
        ent.image       = img.dict['decor']['bones']
        ent.tile.entity = None
        ent.blocks      = False
        ent.fighter     = None
        ent.category    = 'other'
        ent.name        = 'remains of ' + ent.name

        ent.item = Item(image_name_1='decor', image_name_2='bones')
        ent.item.owner = ent
        if not ent.tile.item:
            ent.tile.item = ent
        pygame.event.get()

def closest_monster(max_range):
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for ent in player_obj.ent.env.entities:
        if ent.fighter and ent != player_obj.ent and not ent.tile.hidden:
            #calculate distance between this object and the player
            dist = player_obj.ent.distance_to(ent)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = ent
                closest_dist
    return closest_enemy

def target_tile(max_range=None):
    """ Returns the position of a tile left-clicked in player's field of view, or (None,None) if right-clicked. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    while True:         
        pygame.time.Clock().tick(30)
        for event in pygame.event.get(): # Processes user input
        
            if event.type == QUIT: # Quit
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN: # Cancels action for escape
                if event.key in pyg.key_0:
                    pyg.msg_toggle = False 
                    return (None, None)
                    
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3: # Cancels action for right-click
                    pyg.msg_toggle = False 
                    return (None, None)
                    
                if event.button == 1: # Accepts the target if clicked in the field of view
                    mouse_x, mouse_y = event.pos
                    mouse_x += player_obj.ent.env.camera.x
                    mouse_y += player_obj.ent.env.camera.y
                    x = int(mouse_x /pyg.tile_width)
                    y = int(mouse_y /pyg.tile_height)
                    if (not player_obj.ent.env.map[x][y].hidden and
                        (max_range is None or player_obj.ent.distance(mouse_x, mouse_y) <= max_range)):
                        return (mouse_x, mouse_y)
        render_all()

def check_tile(x, y):
    """ Reveals newly explored regions. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    tile = player_obj.ent.env.map[x][y]
    old_x = x
    old_y = y
    for x in range(old_x - 1, old_x + 2):
        for y in range(old_y - 1, old_y + 2):
            player_obj.ent.env.map[x][y].hidden = False
    if tile.room and tile.room.hidden:
        tile.room.hidden = False
        for x in range(tile.room.x1 , tile.room.x2 + 1):
            for y in range(tile.room.y1, tile.room.y2 + 1):
                player_obj.ent.env.map[x][y].hidden = False       

def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    level_up_exp = mech.level_up_base + player_obj.ent.rank * mech.level_up_factor
    if player_obj.ent.exp >= level_up_exp: # Levels up
        player_obj.ent.rank += 1
        player_obj.ent.exp -= level_up_exp
        message('Your battle skills grow stronger! You reached level ' + str(player_obj.ent.rank) + '!', pyg.yellow)
        choice = None
        while choice == None: # Keeps asking until a choice is made
            choice = new_menu(header = 'Level up! Choose a stat to raise:',
                              options = ['Constitution (+20 HP, from ' + str(player.max_hp) + ')',
                                         'Strength (+1 attack, from ' + str(player.power) + ')',
                                         'Agility (+1 defense, from ' + str(player.defense) + ')'], 
                              position="center")

        if choice == 0: # Boosts health
            player_obj.ent.max_hp += 20
            player_obj.ent.hp += 20
        elif choice == 1: # Boosts power
            player_obj.ent.power += 1
        elif choice == 2: # Boosts defense
            player_obj.ent.defense += 1
        pyg.update_gui()

def from_dungeon_level(table):
    """ Returns a value that depends on the dungeon level. Runs in groups.
        The table specifies what value occurs after each level with 0 as the default. """
    
    for (value, level) in reversed(table):
        if player_obj.ent.env.floor >= level:
            return value
    return 0

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
        message('A mysterious breeze seeps through the cracks.', pyg.white)
        pygame.event.clear()
        return True
    
    return False

def get_equipped_in_slot(slot):
    """ Returns the equipment in a slot, or None if it's empty. """
    
    for eq in player_obj.ent.inventory.values():
        if eq.slot == slot and eq.equipped:
            return eq
    return None

def entity_flash(entity):
    """ Death animation. """
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    mech.impact = True
    mech.impact_image_pos[0] = entity.x-player_obj.ent.env.camera.x
    mech.impact_image_pos[1] = entity.y-player_obj.ent.env.camera.y
    render_all()
    mech.impact = False
    
    #wait_time = 0
    #while wait_time < 5:
    #    pygame.time.Clock().tick(30)
    #    wait_time += 1    
    
    flash = 3
    flash_time = 2
    if entity.hp <=0:
       flash_time = 4
    entity_old_image = entity.image
    while flash_time > 1:
        pygame.time.Clock().tick(30)
        if flash:
           entity.image = mech.blank_surface
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

def random_choice_index(chances):
    """ Chooses an option from a list of possible values, then returns its index. """
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
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
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    chances = chances_dict.values()
    strings = list(chances_dict.keys())
    return strings[random_choice_index(chances)]

def sort_inventory():    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    inventory_cache = {'weapon': [], 'armor': [], 'potion': [], 'scroll': [], 'other': []}
    other_cache     = {'weapon': [], 'armor': [], 'potion': [], 'scroll': [], 'other': []}

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

#######################################################################################################################################################
# Classes
def __CLASSES__():
    pass

class Entity:
    """ Player, enemies, and NPCs. Manages stats, inventory, and basic mechanics. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name           : string
            role           : string in ['player', 'enemy', 'NPC']
            images         : dict of pygame images; {'front', 'back', 'left', 'right'}
            image          : pygame image; current image in images
            image_name_1   : string
            image_name_2   : string
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
            aggressive     : bool; toggles attack functions
            questline      : """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Set images
        self.images = img.dict[self.image_name_1]
        self.image  = img.dict[self.image_name_1][self.image_name_2]

    def ai(self):
        """ Preset movements. """
        
        if self.role == 'enemy':
            self.miss_rate = 100
            
            if not self.tile.hidden:
                distance = self.distance_to(player_obj.ent)
                if distance < 128:
                    if player_obj.ent.env.floor != 0:
                        if distance >= 64: # moves towards player if far away
                            self.move_towards(player_obj.ent.x, player_obj.ent.y)
                        
                        elif player_obj.ent.hp > 0:
                            if random.randint(1, self.miss_rate) == 1:
                                self.attack_target(player_obj.ent)
                        
                    else:
                        if distance >= 100:
                            self.move_towards(player_obj.ent.x, player_obj.ent.y)

    def move(self, dx, dy):
        """ Moves the player by the given amount if the destination is not blocked. """
        
        # Determine direction
        if dy > 0:   direction = 'front'
        elif dy < 0: direction = 'back'
        elif dx < 0: direction = 'left'
        elif dx > 0: direction = 'right'
        
        # Change orientation before moving
        if self.image_name_2 != direction:
            self.image_name_2 = direction
        else:
            
            # Move player
            if self.role == 'player':
                
                # Find new position
                x = int((self.x + dx)/pyg.tile_width)
                y = int((self.y + dy)/pyg.tile_height)
                
                # Remove (map[x][y].entity and dungeon_lvl != 0) for default
                #if ((player_obj.ent.env.map[x][y].entity == player_obj.ent) and (player_obj.ent.dungeon_lvl == 0)) or not is_blocked(env, [x, y]):
                if not is_blocked(self.env, [x, y]):
                    
                    # Move player and update map
                    self.x += dx
                    self.y += dy
                    self.tile.entity = None # removes player from previous position; invisible barrier otherwise
                    self.env.map[x][y].entity = self
                    self.tile = self.env.map[x][y]
                    self.env.player_coordinates = [x, y]
                    print('-----')
                    print(self.env.player_coordinates)
                    check_tile(x, y)
                    
                    # Trigger floor effects
                    try: floor_effects(self.env.map[x][y].floor_effect)
                    except: pass
                
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
                                self.env.map[x][y].image_name_1 = 'floors'
                                self.env.map[x][y].image_name_2 = 'dark green' # sets new image under the player when digging
                                self.env.map[x][y].entity      = self
                                self.tile                      = self.env.map[x][y]
                                self.env.player_coordinates    = [x, y]
                                check_tile(x, y)
                            else:
                                message('The shovel strikes the wall but does not break it.', pyg.white)
                            
                            # Update durability
                            if self.equipment['dominant hand'].durability <= 100:
                                self.equipment['dominant hand'].durability -= 1
                            if self.equipment['dominant hand'].durability <= 0:
                                self.equipment['dominant hand'].drop()
                                self.tile.item = None # removes item from world
                
                self.env.camera.update() # ! omit this if you want to modulate when the camera focuses on the player
            
            # Move NPC or enemy
            else:
                x = int((self.x + dx)/pyg.tile_width)
                y = int((self.y + dy)/pyg.tile_height)
                if not is_blocked(self.env, [x, y]):
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
        dx       = int(round(dx / distance)) * pyg.tile_width # Restricts to map grid
        dy       = int(round(dy / distance)) * pyg.tile_height
        self.move(dx, dy)

    def distance_to(self, other):
        """ Returns the distance to another object. """
        
        dx = other.x - self.x
        dy = other.y - self.y
        return (dx ** 2 + dy ** 2)**(1/2)

    def distance(self, x, y):
        """ Returns the distance to some coordinates. """
        
        return ((x - self.x) ** 2 + (y - self.y) ** 2)**(1/2)

    def attack_target(self, target):
        """ Calculates and applies attack damage. """
        
        if self.name != target.name:
            damage = self.attack - target.defense
            if damage > 0:
                message(self.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', pyg.red)
                target.take_damage(damage)
            else:
                message(self.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!', pyg.red)

    def take_damage(self, damage):
        """ Applies damage if possible. """
        
        if damage > 0:
            
            # Apply damage
            self.hp -= damage
            
            # ?
            entity_flash(self)
            
            # Check for death
            if self.hp <= 0:
                self.hp = 0
                if self.death is not None:
                    self.death(self)
                    
                # Gain experience
                if self != player_obj.ent:
                    player_obj.ent.exp += self.exp
                    check_level_up()
                
            pyg.update_gui()
    
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
            x = self.x-player_obj.ent.env.camera.x
            y = self.y-player_obj.ent.env.camera.y
        
        # Draw skin
        self.image = self.images[self.image_name_2]
        surface.blit(self.image, (x, y))

        # Absolutely stupid; applies armor before hair, and hair before weapons
        for item in self.equipment.values():
            if item is not None:
                if item.role == 'armor':
                    if self.handedness == 'left':
                        surface.blit(img.dict[item.image_name_1][self.image_name_2], (x, y))
                    else:
                        surface.blit(img.flipped.dict[item.image_name_1][self.image_name_2], (x, y))
                else:
                    pass
        for item in self.equipment.values():
            if item is not None:
                if item.role == 'hair':
                    if self.handedness == 'left':
                        surface.blit(img.dict[item.image_name_1][self.image_name_2], (x, y))
                    else:
                        surface.blit(img.flipped.dict[item.image_name_1][self.image_name_2], (x, y))
                else:
                    pass
        for item in self.equipment.values():
            if item is not None:
                if item.role == 'weapon':
                    if self.handedness == 'left':
                        surface.blit(img.dict[item.image_name_1][self.image_name_2], (x, y))
                    else:
                        surface.blit(img.flipped.dict[item.image_name_1][self.image_name_2], (x, y))
                else:
                    pass

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        state.pop('images', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.images = img.dict[self.image_name_1]

class Item:
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name          : string
            role          : string in ['weapon', 'armor', 'potion', 'scroll', 'other']
            slot          : string in ['non-dominant hand', 'dominant hand', 'body', 'head']
            image_name_1  : string
            image_name_2  : string
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

        # Set images
        self.images = img.dict[self.image_name_1]
        self.image  = img.dict[self.image_name_1][self.image_name_2]

    def flip(self):
        
        pygame.transform.flip(self.image, True, False)
        for image in self.images.values():
            pygame.transform.flip(image, True, False)

    def draw(self, surface):
        """ Draws the object at its position. """
        self.images = img.dict[self.image_name_1]
        self.image  = img.dict[self.image_name_1][self.image_name_2]
        surface.blit(self.image, (self.x-player_obj.ent.env.camera.x, self.y-player_obj.ent.env.camera.y))

    def pick_up(self):
        """ Adds an item to the player's inventory and removes it from the map. """
        
        if len(player_obj.ent.inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.name + '.', pyg.red)
        else:
            player_obj.ent.inventory[self.role].append(self)
            sort_inventory()
            message('You picked up a ' + self.name + '!', pyg.green)

    def drop(self):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at
            the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home. """
        
        # Dequip before dropping
        if self in player_obj.ent.equipment.values():
            self.toggle_equip()
        
        # ?
        #if player_obj.ent.dungeon_lvl == 0:
        #    data_objects_1.append(self.owner)
        
        player_obj.ent.inventory[self.role].remove(self)
        player_obj.ent.tile.item = self
        message('You dropped a ' + self.name + '.', pyg.yellow)   

    def use(self):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        # Equipment
        if self.equippable:
            self.toggle_equip()
        
        # Items
        else:
            if self.effect: player_obj.ent.effects.append(self.effect)
            else: message('The ' + self.owner.name + ' cannot be used.')

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
            message('Equipped ' + self.name + ' on ' + self.slot + '.', pyg.light_green)

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
            message('Dequipped ' + self.name + ' from ' + self.slot + '.', pyg.light_yellow)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        state.pop('images', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.images = img.dict[self.image_name_1]

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name       : string
            floor      : int or string
            size       : string in ['small', 'medium', 'large']
            soundtrack : list of pygame audio files
            entities   : list of Entity objects
            camera     : Camera object """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Generate map
        self.map  = [[Tile(
            name        = 'wall',
            image_name_1 = 'walls',
            image_name_2 = 'dark green',
            images      = None,
            image       = None,
            room        = None,
            entity      = None,
            item        = None,
            
            x           = x,
            y           = y,

            blocked     = True,
            hidden      = True,
            unbreakable = False)
            for y in range(0, pyg.map_height * self.size, pyg.tile_height)]
            for x in range(0, pyg.map_width  * self.size, pyg.tile_width)]

    def create_room(self, rect, hidden, unbreakable, image_name_1, image_name_2):
        """ Creates tiles for a room's floor and walls.
            Takes Rectangle object as an argument with parameters for width (x2 - x1) and height (y2 - y1). """
        
        self.player_coordinates = rect.center()
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                tile              = self.map[x][y]
                tile.room         = rect
                tile.blocked      = False
                tile.hidden       = hidden
                tile.image_name_1 = image_name_1
                tile.image_name_2 = image_name_2
                tile.image        = img.dict[image_name_1][image_name_2]
                
                if unbreakable:
                    if (x == rect.x1 + 1) or (x == rect.x2 - 1) or (y == rect.y1 + 1) or (y == rect.y2 - 1):
                        tile.unbreakable = True                
                    else:
                        tile.hidden = False

    def create_h_tunnel(self, x1, x2, y):
        """ Creates horizontal tunnel. min() and max() are used if x1 is greater than x2. """
        if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
        
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].image_name_1 = 'floors'
            self.map[x][y].image_name_2 = 'dark green'

    def create_v_tunnel(self, y1, y2, x):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
        
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].image_name_1 = 'floors'
            self.map[x][y].image_name_2 = 'dark green'
    
    def create_tunnel(self, x, y):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
        
        print(self.map[x][y].image_name_2)
        self.map[x][y].image_name_1 = 'floors'
        self.map[x][y].image_name_2 = 'dark green'
        print(self.map[x][y].image_name_2)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('soundtrack', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name        : str; identifier for image
            images      : list of pygame images; typically only one image
            room        : Rectangle object
            entity      : Entity object; entity that occupies the tile
            item        : Item object; entity that occupies the tile
            image_name_1 : 
            image_name_2 : 
            
            x           : int; location of the tile
            y           : int; location of the tile

            blocked     : bool; prevents items and entities from occupying the tile 
            hidden      : bool; prevents player from seeing the tile
            unbreakable : bool; prevents player from changing the tile """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def draw(self, surface):
        self.images = [img.dict[self.image_name_1][self.image_name_2]]
        self.image  = img.dict[self.image_name_1][self.image_name_2]    
        
        surface.blit(self.image, (self.x-player_obj.ent.env.camera.x, self.y-player_obj.ent.env.camera.y))

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        state.pop('images', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.images = [img.dict[self.image_name_1]]

class Rectangle:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, x, y, w, h):
        """ Defines a rectangle and its size. """
        
        self.x1       = x
        self.y1       = y
        self.x2       = x + w
        self.y2       = y + h
        self.hidden   = True
        self.name     = 'rectangle'

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
        self.width           = pyg.screen_width
        self.height          = pyg.screen_height + pyg.tile_height
        self.x               = self.target.x - int(self.width / 2)
        self.y               = self.target.y - int(self.height / 2)
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

    def fix_position(self):
        """ ? """
        if self.x < 0:
           self.x          = 0
           self.center_x   = self.x + int(self.width / 2)
           self.right      = self.x + self.width
           self.tile_map_x = int(self.x / pyg.tile_width)
           self.x_range    = self.tile_map_x + self.tile_map_width
        elif self.right > pyg.map_width * player_obj.ent.env.size:
           self.right      = pyg.map_width
           self.x          = self.right - self.width
           self.center_x   = self.x + int(self.width / 2)
           self.tile_map_x = int(self.x / pyg.tile_width)
           self.x_range    = self.tile_map_x + self.tile_map_width
        if self.y < 0:
           self.y          = 0
           self.center_y   = self.y + int(self.height / 2)
           self.bottom     = self.y + self.height
           self.tile_map_y = int(self.y / pyg.tile_height)
           self.y_range    = self.tile_map_y + self.tile_map_height
        elif self.bottom > pyg.map_height * player_obj.ent.env.size:
           self.bottom     = pyg.map_height
           self.y          = self.bottom - self.height
           self.center_y   = self.y + int(self.height / 2)
           self.tile_map_y = int(self.y / pyg.tile_height)
           self.y_range    = self.tile_map_y + self.tile_map_height

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

def friend_quest(init=False, NPC_name=None):
    """ Manages friend quest, including initialization and dialogue. """
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")

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
            message("☑ You say hello to your new friend.", pyg.white)
            questlog.update_questlog(name="Making a friend")
        
        if int(friend_level) <= 3:
            message(friend_messages[f'level {int(friend_level)}'][random.randint(0, len(friend_messages[f'level {int(friend_level)}']))], pyg.white)
        else:
            if random.randint(0,10) != 1:
                message(friend_messages[f'level {int(friend_level)}'][random.randint(0, len(friend_messages[f'level {int(friend_level)}']))], pyg.white)
            else:
            
                # Start quest
                message("Woah! What's that?", pyg.white)
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
    message('Quest added!', pyg.green)
    mysterious_note = Quest(name='Mysterious note',
                         content=['My pyg.green friend dropped this. It has a strange encryption.',
                                  'ξνμλ λξ ξλι ξγθιβξ ξ θθ,', 'Ηκρσ σρσ λβνξθι νθ,', 'Ψπθ αβνιθ πθμ.',
                                  '☐ Keep an eye out for more mysterious notes.'],
                         category='Main')

#######################################################################################################################################################
# Uncategorized

#######################################################################################################################################################
# WIP
def __WIP__():
    pass

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
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # Select file number
    file_num = new_menu(
        header      = "Save",
        options     = [f"File 1 {file_set[0]}",
                       f"File 2 {file_set[1]}",
                       f"File 3 {file_set[2]}"],
        backgrounds = ["Data/File_1/screenshot.png",
                       "Data/File_2/screenshot.png",
                       "Data/File_3/screenshot.png"])
    if type(file_num) != int: main_menu()
    else:                     file_num += 1
    
    # Update Player object
    player_obj.file_num = file_num
    
    # Save everything
    with open(f"Data/File_{file_num}/ent.pkl", 'wb') as file:
        pickle.dump(player_obj.ent, file)
    with open(f"Data/File_{file_num}/envs.pkl", 'wb') as file:
        pickle.dump(player_obj.envs, file)
    print(player_obj.envs['garden'].player_coordinates)
    print(player_obj.envs['home'].player_coordinates)
    screenshot(size='screen', visible=False, folder=f"Data/File_{file_num}", filename="screenshot.png", blur=True)

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
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    # Select file number
    file_num = new_menu(
        header      = "Load",
        options     = [f"File 1 {file_set[0]}",
                       f"File 2 {file_set[1]}",
                       f"File 3 {file_set[2]}"],
        backgrounds = ["Data/File_1/screenshot.png",
                       "Data/File_2/screenshot.png",
                       "Data/File_3/screenshot.png"])
    if type(file_num) != int: main_menu()
    else:                     file_num += 1
    
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

#######################################################################################################################################################
# World creation and management
##effect:
#- gain an unlimited capacity for health, but your maximum health is low; healing is essentially impossible to rely on1

def build_home():
    """ Generates player's home. """
        
    # Initialize environment
    player_obj.envs['home'] = Environment(
        name       = 'home',
        floor      = 0,
        size       = 5,
        soundtrack = [aud.home[0]],
        entities   = [],
        player_coordinates = None,
        camera     = None)

    # Construct rooms
    main_room       = Rectangle(10, 10, mech.room_max_size, mech.room_max_size)
    secret_room     = Rectangle(30, 30, mech.room_min_size*2, mech.room_min_size*2)
    player_obj.envs['home'].center = main_room.center()
    player_obj.envs['home'].create_room(
        rect = main_room,
        hidden = False,
        unbreakable = False,
        image_name_1 = 'floors',
        image_name_2 = 'dark green')
    player_obj.envs['home'].create_room(
        rect = secret_room,
        hidden = False,
        unbreakable = True,
        image_name_1 = 'floors',
        image_name_2 = 'dark green')

    # Place items in home
    for i in range(5): 

        # Healing potion
        x, y                    = 13, 11
        item                    = create_objects('healing potion', [x, y])
        item.tile               = player_obj.envs['home'].map[x][y]
        player_obj.envs['home'].map[x][y].item = item
        
        # Lightning scroll
        x, y                    = 14, 11
        item                    = create_objects('scroll of lightning bolt', [x, y])
        item.tile               = player_obj.envs['home'].map[x][y]
        player_obj.envs['home'].map[x][y].item = item

        # Fireball scroll
        x, y                    = 15, 11
        item                    = create_objects('scroll of fireball', [x, y])
        item.tile               = player_obj.envs['home'].map[x][y]
        player_obj.envs['home'].map[x][y].item = item

        # Blood sword
        x, y                    = 33, 33
        item                    = create_objects('blood sword', [x, y])
        item.tile               = player_obj.envs['home'].map[x][y]
        player_obj.envs['home'].map[x][y].item = item

        # Shield
        x, y                    = 34, 34
        item                    = create_objects('shield', [x, y])
        item.tile               = player_obj.envs['home'].map[x][y]
        player_obj.envs['home'].map[x][y].item = item

        # Bug fix
        x, y                    = 0, 0
        item                    = create_objects('scroll of fireball', [x, y])
        item.tile               = player_obj.envs['home'].map[x][y]
        player_obj.envs['home'].map[x][y].item = item
    
    # Generate stairs
    x, y                    = 18, 15
    item                    = create_objects('stairs', [x, y])
    item.tile               = player_obj.envs['home'].map[x][y]
    player_obj.envs['home'].map[x][y].item = item
    
    # Generate friend
    x, y = 18, 18
    ent = Entity(
        name       = 'friend',
        role       = 'enemy',
        image_name_1 = 'friend',
        image_name_2 = 'front',
        images     = None,
        image      = None,
        handedness = 'left',

        exp        = 0,
        rank       = 100,
        hp         = 100,
        max_hp     = 100,
        attack     = 0,
        defense    = 100,
        effects    = [],

        env        = player_obj.envs['home'],
        tile       = player_obj.envs['home'].map[x][y],
        x          = x * pyg.tile_width,
        y          = y * pyg.tile_width,
        reach      = None,

        inventory  = {},
        equipment  = {},
        death      = death,
        follow     = False,
        aggressive = False,
        questline  = None)
    ent.env = player_obj.envs['home']
    player_obj.envs['home'].map[x][y].entity = ent
    player_obj.envs['home'].entities.append(ent)
    
    return player_obj.envs['home']

def create_objects(selection, location):
    """ Creates and returns an object.
    
        Parameters
        ----------
        selection : string; name of object
        location  : list of int; coordinates of item location """

    # ----------------------- WEAPONS -----------------------
    # Shovel
    if selection == 'shovel':
        item = Item(
            name          = 'shovel',
            role          = 'weapon',
            slot          = 'dominant hand',
            image_name_1  = 'shovel',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 100,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = None)
    
    # Super shovel
    elif selection == 'super shovel':
        item = Item(
            name          = 'super shovel',
            role          = 'weapon',
            slot          = 'dominant hand',
            image_name_1  = 'super shovel',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 100,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 10,
            defense_bonus = 0,
            effect        = None)
    
    # Dagger
    elif selection == 'dagger':
        item = Item(
            name          = 'dagger',
            role          = 'weapon',
            slot          = 'dominant hand',
            image_name_1  = 'dagger',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 2,
            defense_bonus = 0,
            effect        = None)

    # Sword
    elif selection == 'sword':
        item = Item(
            name          = 'sword',
            role          = 'weapon',
            slot          = 'dominant hand',
            image_name_1  = 'sword',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 5,
            defense_bonus = 0,
            effect        = None)
    
    # Blood dagger
    elif selection == 'blood dagger':
        item = Item(
            name          = 'blood dagger',
            role          = 'weapon',
            slot          = 'dominant hand',
            image_name_1  = 'blood dagger',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 10,
            defense_bonus = 0,
            effect        = None)
    
    # Blood sword
    elif selection == 'blood sword':
        item = Item(
            name          = 'blood sword',
            role          = 'weapon',
            slot          = 'dominant hand',
            image_name_1  = 'blood sword',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 15,
            defense_bonus = 0,
            effect        = None)

    # ----------------------- ARMOR -----------------------
    # Clothes
    elif selection == 'clothes':
        item = Item(
            name          = 'green clothes',
            role          = 'armor',
            slot          = 'body',
            image_name_1  = 'green clothes',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 1,
            effect        = None)
    
    # Wig
    elif selection == 'hair':
        item = Item(
            name          = 'medium hair',
            role          = 'armor',
            slot          = 'head',
            image_name_1  = 'medium hair',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = None)
    
    # Shield
    elif selection == 'shield':
        item = Item(
            name          = 'iron shield',
            role          = 'armor',
            slot          = 'non-dominant hand',
            image_name_1  = 'iron shield',
            image_name_2  = 'dropped',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 10,
            effect        = None)

    # ----------------------- POTIONS -----------------------
    # Healing potion
    elif selection == 'healing potion':
        item = Item(
            name          = 'healing potion',
            role          = 'potion',
            slot          = None,
            image_name_1  = 'potions',
            image_name_2  = 'red',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = cast_heal)
    
    # Transformation potion
    elif selection == 'transformation potion':
        item = Item(
            name          = 'transformation potion',
            role          = 'potion',
            slot          = None,
            image_name_1  = 'potions',
            image_name_2  = 'purple',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = None)
    
    # ----------------------- SCROLLS -----------------------
    # Scroll of lightning bolt
    elif selection == 'scroll of lightning bolt':
        item = Item(
            name          = 'scroll of lightning bolt',
            role          = 'scroll',
            slot          = None,
            image_name_1  = 'scrolls',
            image_name_2  = 'closed',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = cast_lightning)
    
    # Scroll of fireball
    elif selection == 'scroll of fireball':
        item = Item(
            name          = 'scroll of fireball',
            role          = 'scroll',
            slot          = None,
            image_name_1  = 'scrolls',
            image_name_2  = 'closed',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = cast_fireball)

    # Scroll of confusion
        item = Item(
            name          = 'scroll of confusion',
            role          = 'scroll',
            slot          = None,
            image_name_1  = 'scrolls',
            image_name_2  = 'closed',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = cast_confuse)
    
    # ----------------------- OTHER -----------------------
    # Stairs
    elif selection == 'stairs':
        item = Item(
            name          = 'stairs',
            role          = 'other',
            slot          = None,
            image_name_1  = 'stairs',
            image_name_2  = 'door',
            images        = None,
            image         = None,

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            
            tile          = None,
            x             = location[0] * pyg.tile_width,
            y             = location[1] * pyg.tile_height,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = None)
    
    return item

def build_dungeon_level():
    """ Generates a dungeon level. """
    
    # Initialize environment
    dungeon_env = Environment(
        name       = 'dungeon',
        floor      = 1 + len(player_obj.envs['dungeons']),
        size       = 5,
        soundtrack = [aud.dungeons[len(player_obj.envs['dungeons'])]],
        entities   = [],
        player_coordinates = None,
        camera     = None)
    player_obj.envs['dungeons'].append(dungeon_env)
    
    # Construct rooms
    rooms, room_counter = [], 0
    num_rooms           = int(mech.max_rooms * player_obj.envs['dungeons'][-1].floor)
    new_map_height      = int(pyg.map_height * player_obj.envs['dungeons'][-1].floor)
    new_map_width       = int(pyg.map_width  * player_obj.envs['dungeons'][-1].floor)
 
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(mech.room_min_size, mech.room_max_size)
        height   = random.randint(mech.room_min_size, mech.room_max_size)
        x        = random.randint(0,             pyg.tile_map_width  - width - 1)
        y        = random.randint(0,             pyg.tile_map_height - height - 1)
        new_room = Rectangle(x, y, width, height)

        failed = False
        if random.choice([0, 1, 2, 3]) != 0: # include more values to make more hallways (?)
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

        # Set floor image
        if random.choice(range(player_obj.envs['dungeons'][-1].floor)) >= player_obj.envs['dungeons'][-1].floor*(3/4):
            player_obj.envs['dungeons'][-1].create_room(
                rect = new_room,
                hidden = False,
                unbreakable = False,
                image_name_1 = 'floors',
                image_name_2 = 'dark green')
        else:
            player_obj.envs['dungeons'][-1].create_room(
                rect = new_room,
                hidden = False,
                unbreakable = False,
                image_name_1 = 'floors',
                image_name_2 = 'green') #?

        # Customize room
        if not failed:
            x, y = new_room.center()[0], new_room.center()[1]
            
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
                (prev_x, prev_y) = rooms[room_counter-1].center()
                if random.randint(0, 1) == 0:
                    player_obj.envs['dungeons'][-1].create_h_tunnel(prev_x, x, prev_y)
                    player_obj.envs['dungeons'][-1].create_v_tunnel(prev_y, y, x)
                else:
                    player_obj.envs['dungeons'][-1].create_v_tunnel(prev_y, y, prev_x)
                    player_obj.envs['dungeons'][-1].create_h_tunnel(prev_x, x, y)
                
            # Place objects
            place_objects(new_room, player_obj.envs['dungeons'][-1])
            
            # Prepare for next room
            rooms.append(new_room)
            room_counter += 1

    # Generate stairs
    stairs = create_objects('stairs' , [prev_x, prev_y])
    player_obj.envs['dungeons'][-1].map[prev_x][prev_y].item = stairs

def place_player(env, loc):
    """ Sets player in a new position.

        Parameters
        ----------
        env : Environment object; new environment of player
        loc : list of integers; new location of player """
    
    # Remove from current location
    if player_obj.ent.env:
        player_obj.ent.env.entities.remove(player_obj.ent)
        player_obj.ent.tile = None

    # Set current environment and tile
    player_obj.ent.env             = env
    player_obj.ent.tile            = player_obj.ent.env.map[loc[0]][loc[1]]
    player_obj.ent.x               = loc[0] * pyg.tile_width
    player_obj.ent.y               = loc[1] * pyg.tile_height

    # Notify environmnet of player position
    env.map[loc[0]][loc[1]].entity = player_obj.ent
    env.entities.append(player_obj.ent)

    pyg.gui_env = env.name

    check_tile(loc[0], loc[1])
    
    if not env.camera: env.camera = Camera(player_obj.ent)
    env.camera.update()
    
    time.sleep(0.5)
    pyg.update_gui()

def movement_speed(adjust=False, move=False):
    global movement_speed_toggle
    
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")
    
    if adjust:
        if movement_speed_toggle == len(toggle_list)-1: 
            movement_speed_toggle = 0
        else:
            movement_speed_toggle += 1
        
        if toggle_list[movement_speed_toggle] == 'Default':
            pygame.key.set_repeat(250, 150)
            message(f"Movement speed: Default", pyg.blue)
        elif toggle_list[movement_speed_toggle] == 'Slow':
            pygame.key.set_repeat(0, 0)
            message(f"Movement speed: Fixed", pyg.white)
        else:
            pygame.key.set_repeat(175, 150)
            message(f"Movement speed: Fast", pyg.red)

def screenshot(size='screen', visible=False, folder="Data", filename="cache.png", blur=False):
    """ Takes a screenshot.
        cache:  saves a regular screenshot under Data/Cache/screenshot.png
        save:   moves regular cached screenshot to Data/File_#/screenshot.png 
        blur:   adds a blur effect """
    
    global gui_toggle, msg_toggle, screenshot_time_counter
    if debug: print(f"{debug_call()[0]:<30}{debug_call()[1]}")

    # Turn off gui
    pyg.gui_toggle, pyg.msg_toggle = False, False
    
    # Select screen size
    if size == 'full':
        camera_cache = [player_obj.ent.env.camera.x, player_obj.ent.env.camera.y]
        pyg.screen = pygame.display.set_mode((len(player_obj.ent.env.map[0])*16, len(player_obj.ent.env.map)*16),)
        player_obj.ent.env.camera.x = 0
        player_obj.ent.env.camera.y = 0
        player_obj.ent.env.camera.update()
    render_all(size=size, visible=visible)
    
    # Save image
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)
    pygame.image.save(pyg.screen, path)
    
    # Add effects
    if blur:
        image_before = Image.open(folder + '/' + filename)
        image_after  = image_before.filter(ImageFilter.BLUR)
        image_after.save(folder + '/' + filename)
    
    # Reset everthing to normal
    if size == 'full':
        pyg.screen = pygame.display.set_mode((pyg.screen_width, pyg.screen_height),)
        player_obj.ent.env.camera.x = camera_cache[0]
        player_obj.ent.env.camera.y = camera_cache[1]
        player_obj.ent.env.camera.update()
    render_all()
    pyg.gui_toggle, pyg.msg_toggle = True, True

#####
# Templates
def play_game_min():

    # Wait for command
    while True:
        pyg.clock.tick(30)
        event = pygame.event.get()
        if event:
            if event[0].type == KEYDOWN:
                
                if menu_index == 0:
                    
                    # >>MOVE/ATTACK<<
                    if event[0].key in pyg.key_UP:
                        if player_obj.ent.image == img.dict['player'][1]:
                            player_obj.ent.move(0, -pyg.tile_height)
                    elif event[0].key in pyg.key_DOWN:
                        if player_obj.ent.image == img.dict['player'][0]:
                            player_obj.ent.move(0, pyg.tile_height)
                    elif event[0].key in pyg.key_LEFT:
                        if player_obj.ent.image == img.dict['player'][2]:
                            player_obj.ent.move(-pyg.tile_width, 0)
                    elif event[0].key in pyg.key_RIGHT:
                        if player_obj.ent.image == img.dict['player'][3]:
                            player_obj.ent.move(pyg.tile_width, 0)

                    # >>MENU<<
                    elif event[0].key in pyg.key_SLASH and (time.time()-last_press_time > cooldown_time):
                        last_press_time = float(time.time())
                        menu_index = 1
                
            render_all()


#######################################################################################################################################################
# Global scripts
if __name__ == "__main__":
    main()

#######################################################################################################################################################