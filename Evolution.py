#######################################################################################################################################################
##
## MORS SOMNIA
##
#######################################################################################################################################################

#######################################################################################################################################################
# Plot
""" Overview
    --------
    There are many paths, but (almost) all lead to death.
    Sleep and drug use lead to roguelike dreams.
    Death is the only way to wake up from a dream or hallucination and return to the Overworld.
    Only some items and player modifications are retained upon death in a dream.
    If the player dies in the Overworld, the game ends without recovery (unless the Path 1 is followed).
    
    Path 1: With the aid of drugs, experience, and the church questline, the player can become effectively immortal through cloning.
    - This is the most difficult path to achieve and leads to the endgame.
    - The church must look favorably on the player, and the player must have sufficient experience and evolutions.
    
    Path 2: With the aid of drugs and experience, the player can defeat the church and live in harmony in the Overworld.
    - The player can still die in the Overworld, in which they do not proceed to the endgame.
    
    Path 3: With the aid of experience and the church questline (but no drugs), the player is doomed to death.
    - The church will eventually reject the player for not following their creed.
    - There is no endgame or bonus content.
    
    Path 4: With the aid of experience alone, the player will perish after the church's revolt.
    - This happens after a fixed number of days.
    - New customization options are available for runs following this path.
    
    Path 5: With the aid of the church questline alone, all life in the overworld will end.
    - This is only achieved if the church questline is completed at Rank 1.
    - Something special happens, but I don't know what yet. """

""" Environments
    ------------
    Through requisite means, the player can access their Home, the Overworld, the Dungeons, the Abyssal Gallery, and the Garden.
    
    Home            : Nothing special happens here; it is a place of refuge.
    Overworld       : The main questline occurs here.
    Dungeons        : This is mostly a placeholder for dream/drug environments that haven't been programmed yet.
    Abyssal Gallery : This is the beginning and the end; strong monsters and powerful items, etc. """

""" NPCs
    ----
    Townsfolk : Average settlers of the Overworld.
    Bloodkin  : Worshipers of the Sigil of Thanato. They rarely leave the church but can be found in dreams.
    Kyrio     : A powerful leader of the Bloodkin. He is a deviant that masquerades as a confused old man.
    Kapno     : The brother of Kyrio and the store manager of the Overworld. He is a pleasant old man that knows nothing of his brother's plot.
    Chameno   : A former leader of the Bloodkin that fled persecution to live in dreams.
    Louloud   : The player's best friend. She lives with her mother and likes to garden.
    Giatro    : The doctor of the Overworld. He is optionally converted to a Bloodkin by the player and attained as a follower.
    Erasti    : An unsuspecting member of the Townsfolk. She may be conscripted as a follower.
    Ypno      : The drug dealer of the Townsfolk. They can be found in the Overworld and in dreams.
    Thanato   : Death itself. They have no physical form but can imbue inanimate objects with deadly prowess.
    Vit       : Life itself. Idk yet. """

#######################################################################################################################################################
# Imports
## Game mechanics
import pygame
from   pygame.locals import *
import random
import time

## Utility
import pickle
import copy
import sys
import textwrap

# Aesthetics
from PIL import Image, ImageFilter, ImageOps

#######################################################################################################################################################
# Global values
super_dig = False

#######################################################################################################################################################
# Core
def debug_call(func):
    """ Just a print statement for debugging. Shows which function is called alongside variable details. """

    def wrapped_function(*args, **kwargs):
        print(f"{func.__name__:<30}{time.strftime('%M:%S', time.localtime())}")
        return func(*args, **kwargs)
    return wrapped_function

def main():
    """ Initializes the essentials and opens the main menu. """
    
    global pyg, mech, img, aud, player_obj
    global main_menu_obj, play_game_obj, new_game_obj, new_menu_obj
    global save_account_obj, load_account_obj, garden_obj
    global dev, inv, hold_obj, trade_obj
    
    # Initialize pygame (parameters, display, clock, etc.)
    pyg  = Pygame()
    pyg.game_state = 'startup'
    pyg.overlay    = None

    # Initialize general mechanics (?)
    mech = Mechanics()
    
    # Import images (sorted dictionary and cache)
    img         = Images()
    img.flipped = Images(flipped=True)
    pygame.display.set_icon(img.dict['decor']['skeleton'])

    # Initialize pygame audio and development tools
    aud = Audio()
    inv = Inventory()
    dev = DevTools()
    
    # Create player
    player_obj = Player()
    
    # Open the main menu
    main_menu_obj    = MainMenu()
    play_game_obj    = PlayGame()
    new_game_obj     = NewGame()
    garden_obj       = PlayGarden()
    new_menu_obj     = NewMenu(
        name      = 'controls',
        header    = "Controls", 
        options   = ["Move:                                       Arrow keys or WASD",
                     "Descend stairs or grab item:    Enter",
                     "Ascend stairs to home:            Shift",
                     "Check stats:                             1",
                     "Use item in inventory:              2",
                     "Drop item from inventory:        3",
                     "Open questlog:                        4",
                     "Toggle movement speed:         5",
                     "Take screenshot:                      6",
                     "Construct items:                         7",
                     "Unused:                                   8",
                     "Unused:                                   9",
                     "Toggle messages:                     /"])
    save_account_obj = NewMenu(
        name        = 'save',
        header      = "Save",
        options     = ["File 1",
                       "File 2",
                       "File 3"],
        backgrounds = ["Data/File_1/screenshot.png",
                       "Data/File_2/screenshot.png",
                       "Data/File_3/screenshot.png"])
    load_account_obj = NewMenu(
        name        = 'load',
        header      = "Load",
        options     = ["File 1",
                       "File 2",
                       "File 3"],
        backgrounds = ["Data/File_1/screenshot.png",
                       "Data/File_2/screenshot.png",
                       "Data/File_3/screenshot.png"])
    hold_obj         = Hold()
    trade_obj        = Trade()
    
    game_states()

def game_states():
    
    pyg.running    = True
    while pyg.running:
        
        ## Primary
        if pyg.game_state == 'startup':
            main_menu_obj.startup()
        
        elif pyg.game_state == 'play_game':
            play_game_obj.run()
            play_game_obj.render()
        
        elif pyg.game_state == 'new_game':
            new_game_obj.run()
            new_game_obj.render()
        
        elif pyg.game_state == 'play_garden':
            garden_obj.run()
            garden_obj.render()
        
        ## Overlays
        if pyg.overlay == 'menu':
            game_state = main_menu_obj.run()
            main_menu_obj.render()
        
        elif pyg.overlay == 'controls':
            new_menu_obj.run()
            new_menu_obj.render()
        
        elif pyg.overlay == 'load':
            load_account_obj.run()
            load_account_obj.render()
        
        elif pyg.overlay == 'save':
            save_account_obj.run()
            save_account_obj.render()
        
        elif pyg.overlay == 'inv':
            inv.run()
            inv.render()
        
        elif pyg.overlay == 'dev':
            dev.run()
            dev.render()
        
        elif pyg.overlay == 'hold':
            hold_obj.run()
            hold_obj.render()
        
        elif pyg.overlay == 'trade':
            trade_obj.run()
            trade_obj.render()
        
        img.render()
        pygame.display.flip()
        pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
        pyg.clock.tick(30)

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

def new_menu(header, options, options_categories=None, position='top left', backgrounds=None):
    """ IMPORTANT. Creates cursor, background, and menu options, then returns index of choice.

        header             : string; top line of text
        options            : list of strings; menu choices
        options_categories : list of strings; categorization; same length as options
        position           : chooses layout preset """

    
    # -------------------------------------- INIT --------------------------------------
    # Initialize temporary data containers
    choice                   = 0              # holds index of option pointed at by cursor
    choices_length           = len(options)-1 # number of choices
    options_categories_cache = ''             # holds current category
    options_render = options.copy()
    
    # Alter layout if categories are present
    if options_categories: 
        tab_X, tab_Y         = 70, 10
        options_categories_cache_2 = options_categories[0]
    else:
        tab_X, tab_Y         = 0, 0

    # Set initial position of each text type
    header_position    = {'top left':    [5, 10], 'center': [int((pyg.screen_width)/2), 85],
                          'bottom left': [5, 10],              'bottom right': [60 ,70]}
    cursor_position    = {'top left':    [50+tab_X, 38+tab_Y], 'center':       [50, 300],
                          'bottom left': [50+tab_X, 65-tab_Y], 'bottom right': [60 ,70]}
    options_positions  = {'top left':    [80+tab_X, 34],       'center':       [80, 300],
                          'bottom left': [5, 10],              'bottom right': [60 ,70]}
    category_positions = {'top left':    [5, 34],              'center':       [80, 300],
                          'bottom left': [5, 10],              'bottom right': [60 ,70]}

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
                    options_positions_mutable[1] += tab_Y
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
                if (event.key in pyg.key_BACK) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
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
                            cursor_position_mutable[1] += tab_Y * (len(set(options_categories)) - 1)
                            options_categories_cache_2 = options_categories[choice]
                    
                    # Move cursor again if there are categories
                    elif options_categories:
                        if options_categories[choice] != options_categories_cache_2:
                            options_categories_cache_2 = options_categories[choice]
                            cursor_position_mutable[1] -= tab_Y
                
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
                            cursor_position_mutable[1] += tab_Y
                            
                elif event.key in pyg.key_ENTER:
                    running = False
                    return choice

def render_all(size='display', visible=False):
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
        y_range_2 = min(len(player_obj.ent.env.map[0])-1, camera.tile_map_y + camera.tile_map_height+2)

        x_range_1 = max(0, camera.tile_map_x)
        x_range_2 = min(len(player_obj.ent.env.map)-1, camera.tile_map_x + camera.tile_map_width+2)
    
    # Draw visible tiles
    for y in range(int(camera.Y/32), int(camera.bottom/pyg.tile_height + 1)):
        for x in range(int(camera.X/32), int(camera.right/pyg.tile_width + 1)):
            try:    tile = player_obj.ent.env.map[x][y]
            except: continue
            
            if visible or not tile.hidden:
                
                # Lowest tier (floor and walls)
                tile.draw(pyg.display)

                # Second tier (decor and items)
                if tile.item:
                    tile.item.draw(pyg.display)
                
                # Third tier (entity)
                if tile.entity:
                    tile.entity.draw(pyg.display)
                
                # Fourth tier (roof)
                if tile.room:
                    if tile.room.roof:
                        if tile.img_names == tile.room.roof:
                            tile.draw(pyg.display)
    
    if (size == 'display') and (pyg.overlay != 'menu'):
        if bool(img.impact):
            for i in range(len(img.impact_images)):
                pyg.screen.blit(img.impact_images[i], img.impact_image_pos[i])
        
        # Print messages
        if pyg.msg_toggle: 
            Y = 3
            
            # Find how many messages to write
            for message in pyg.msg:
                pyg.screen.blit(message, (5, Y))
                Y += 16
        
        if pyg.gui_toggle:
            for i in range(len(pyg.gui)):
                pyg.screen.blit(list(pyg.gui.values())[i],   (5+250*i, pyg.screen_height-27))
    
    aud.shuffle()

def check_tile(x, y):
    """ Reveals newly explored regions with respect to the player's position. """
    
    # Define some shorthand
    tile = player_obj.ent.env.map[x][y]
    
    # Reveal a square around the player
    for u in range(x-1, x+2):
        for v in range(y-1, y+2):
            player_obj.ent.env.map[u][v].hidden = False
    
    # Reveal a hidden room
    if tile.room:
        if tile.room.hidden:
            tile.room.hidden = False
            for room_tile in tile.room.tiles_list:
                room_tile.hidden = False
        
        # Check if the player enters or leaves a room
        if player_obj.ent.prev_tile:
            if tile.room != player_obj.ent.prev_tile.room:
                
                # Hide the roof if the player enters a room
                if tile.room and tile.room.roof:
                    for u in range(tile.room.x1 , tile.room.x2 + 1):
                        for v in range(tile.room.y1, tile.room.y2 + 1):        
                            if player_obj.ent.env.map[u][v] not in tile.room.walls_list:
                                player_obj.ent.env.map[u][v].img_names = tile.room.floor
        
    # Reveal the roof if the player leaves the room
    if player_obj.ent.prev_tile:
        prev_tile = player_obj.ent.prev_tile
        if prev_tile.room and not tile.room:
            if prev_tile.room.roof:
                for u in range(prev_tile.room.x1, prev_tile.room.x2 + 1):
                    for v in range(prev_tile.room.y1, prev_tile.room.y2 + 1):
                        if player_obj.ent.env.map[u][v] not in prev_tile.room.walls_list:
                            player_obj.ent.env.map[u][v].img_names = prev_tile.room.roof
    
#######################################################################################################################################################
# Classes
## Utility
class Pygame:
    """ Pygame stuff. Does not need to be saved, but pyg.update_gui should be run after loading a new file. """

    def __init__(self):
        
        # Controls
        self.set_controls()
        
        # Colors
        self.set_colors()
        
        # Graphics
        self.set_graphics()
        
        # Other
        self.startup_toggle  = True
        self.cooldown_time   = 0.2
        self.last_press_time = 0
        
        # Start pygame
        pygame.init()
        pygame.key.set_repeat(250, 150)
        pygame.display.set_caption("Mors Somnia") # Sets game title
        self.screen   = pygame.display.set_mode((self.screen_width, self.screen_height),)
        self.font     = pygame.font.SysFont('segoeuisymbol', 16, bold=True) # pygame.font.Font('Data/font.ttf', 24)
        self.minifont = pygame.font.SysFont('segoeuisymbol', 14, bold=True) # pygame.font.Font('Data/font.ttf', 24)
        self.clock    = pygame.time.Clock()
        self.display  = pygame.Surface((int(self.screen_width / self.zoom), int(self.screen_height / self.zoom)))
        self.gui      = {
            'health':   self.font.render('', True, self.red),
            'stamina':  self.font.render('', True, self.green),
            'location': self.font.render('', True, self.gray)}

    def set_controls(self, controls='B'):
        
        # Extended controls
        if controls == 'A':
            
            # Movement
            self.key_UP       = [K_UP,    K_w]            # up
            self.key_DOWN     = [K_DOWN,  K_s]            # down
            self.key_LEFT     = [K_LEFT,  K_a]            # left
            self.key_RIGHT    = [K_RIGHT, K_d]            # right
            
            # Actions
            self.key_BACK     = [K_BACKSPACE, K_NUMLOCK, K_ESCAPE]  # exit/main menu
            self.key_ENTER    = [K_RETURN,    K_KP_ENTER] # action 1
            self.key_PERIOD   = [K_KP_PERIOD]             # action 2
            self.key_PLUS     = [K_PLUS,      K_KP_PLUS]  # zoom
            self.key_MINUS    = [K_MINUS,     K_KP_MINUS] # zoom
            self.key_HOLD     = [K_0, K_KP0]
            
            # Menus
            self.key_INV      = [K_4, K_KP4]              # inventory
            self.key_DEV      = [K_6, K_KP6]              # DevTools
            self.key_INFO     = [K_7, K_KP7]              # player information
            self.key_SPEED    = [K_8, K_KP8]              # movement speed
            self.key_QUEST    = [K_9, K_KP9]              # questlog
            
            # Other
            self.key_EQUIP    = [K_2, K_KP2]              # inventory (equip)
            self.key_DROP     = [K_3, K_KP3]              # inventory (drop)
            

        # Alternate controls
        elif controls == 'B':
            # Unused: 0, *
            
            # Movement
            self.key_UP       = [K_5, K_KP5,  K_UP  ]     # up
            self.key_DOWN     = [K_2, K_KP2,  K_DOWN]     # down
            self.key_LEFT     = [K_1, K_KP1,  K_LEFT]     # left
            self.key_RIGHT    = [K_3, K_KP3,  K_RIGHT]    # right

            # Actions
            self.key_BACK     = [K_BACKSPACE, K_NUMLOCK]  # exit/main menu
            self.key_ENTER    = [K_RETURN,    K_KP_ENTER] # action 1
            self.key_PERIOD   = [K_KP_PERIOD]             # action 2
            self.key_PLUS     = [K_PLUS,      K_KP_PLUS]  # zoom
            self.key_MINUS    = [K_MINUS,     K_KP_MINUS] # zoom
            self.key_HOLD     = [K_0, K_KP0]              # attack sequences
            
            # Menus
            self.key_INV      = [K_4, K_KP4]              # inventory
            self.key_DEV      = [K_6, K_KP6]              # DevTools
            self.key_INFO     = [K_7, K_KP7]              # player information
            self.key_SPEED    = [K_8, K_KP8]              # movement speed
            self.key_QUEST    = [K_9, K_KP9]              # questlog
            
            # Unused
            self.key_EQUIP    = []                       # inventory (equip)
            self.key_DROP     = []                       # inventory (drop)

    def set_colors(self):
        
        self.black             = pygame.color.THECOLORS['black']
        self.dark_gray         = pygame.color.THECOLORS['gray60']
        self.gray              = pygame.color.THECOLORS['gray90']
        self.white             = pygame.color.THECOLORS['white']
        self.red               = pygame.color.THECOLORS['orangered3']
        self.green             = pygame.color.THECOLORS['palegreen4']
        self.blue              = pygame.color.THECOLORS['blue']
        self.yellow            = pygame.color.THECOLORS['yellow']
        self.orange            = pygame.color.THECOLORS['orange']
        self.violet            = pygame.color.THECOLORS['violet']

    def set_graphics(self):
        
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
        self.message_width     = int(self.screen_width / 6)
        self.message_height    = 4 # number of lines shown

    def update_gui(self, new_msg=None, color=None):
        
        if player_obj.ent.env:
            
            # Create or delete message; update pyg.update_gui list
            if new_msg:
                for line in textwrap.wrap(new_msg, pyg.message_width):
                    
                    # Delete older messages
                    if len(self.msg) == pyg.message_height:
                        del self.msg[0]
                    
                    # Create pyg.update_gui object
                    self.msg.append(self.font.render(line, True, color))
            
            # Update top and/or bottom gui
            if not pyg.overlay:
                
                # Health
                current_health = int(player_obj.ent.hp / player_obj.ent.max_hp) * 10
                leftover_health = 10 - current_health
                health = '▆' * current_health + '▁' * leftover_health
                
                # Stamina
                current_stamina = int((player_obj.ent.stamina % 101) / 10)
                leftover_stamina = 10 - current_stamina
                stamina = '▆' * current_stamina + '▁' * leftover_stamina
                
                # Location
                env = str(player_obj.ent.env.name)
                if player_obj.ent.env.lvl_num: env = env + ' (level ' + str(player_obj.ent.env.lvl_num) + ')'
                
                self.gui = {
                    'health':   self.minifont.render(health,  True, self.red),
                    'stamina':  self.minifont.render(stamina, True, self.green),
                    'location': self.minifont.render(env,     True, self.dark_gray)}
            
            # Show last message
            else:
                if self.msg: self.msg = [self.msg[-1]]
                self.gui = {'wallet': self.minifont.render('⨋ '+str(player_obj.ent.wallet), True, self.dark_gray)}

class Images:
    """ Loads images from png file and sorts them in a global dictionary. One save for each file.

        The tileset (tileset.png) is organized in rows, with each row being a category identified below
        by the categories list. This function breaks the tileset into individual tiles and adds each tile
        to its respective category in a global dictionary for later use.
        
        img.dict:        mutable dictionary sorted by category
        img.cache:  less mutable than img.dict """
    
    # Initialization
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
        
        # Gather images for character_creation
        self.hair_options  = ['bald',  'brown hair',  'blue hair',  'short brown hair']
        self.face_options  = ['clean', 'brown beard', 'blue beard', 'white beard']
        self.chest_options = ['flat',  'bra']
        self.skin_options  = ['white', 'black', 'cyborg']
        
        self.big_img()

        self.impact_image      = self.get_impact_image()
        self.impact_images     = []
        self.impact_image_pos  = []
        self.impact            = False        
        self.blank_surface     = pygame.Surface((pyg.tile_width, pyg.tile_height)).convert()
        self.blank_surface.set_colorkey(self.blank_surface.get_at((0,0)))
        self.render_log = []

    def import_tiles(self, filename, flipped=False, effects=None):
        """ Converts an image to a pygame image, cuts it into tiles, then returns a matrix of tiles. """
        
        # Set effects and/or load image
        if not effects:
            tileset = pygame.image.load(filename).convert_alpha()
            
        else:
            tileset = Image.open(filename)
            
            # Apply posterization
            if 'posterize' in effects:
                if tileset.mode == 'RGBA':
                    img_a = tileset.getchannel('A')
                    img_rgb = tileset.convert('RGB')
                    tileset = ImageOps.posterize(img_rgb, 6)
                    tileset.putalpha(img_a)
                else:
                    try:
                        tileset = ImageOps.posterize(tileset, 6)
                    except OSError as e:
                        print("Image mode:", tileset.mode)
                        raise e
            
            # Apply custom blur kernel
            if 'kernel' in effects:
                kernel = ImageFilter.Kernel((3, 3), [1, -3, 1, -1, 3, 2, 3, 5, 5], 9, 1)
                tileset = tileset.filter(kernel)
            
            # Convert to pygame image
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
                X = col * pyg.tile_width
                Y = row * pyg.tile_height
                if flipped:
                    image = pygame.transform.flip(tileset.subsurface(X, Y, pyg.tile_width, pyg.tile_height).convert_alpha() , True, False)
                else:
                    image = tileset.subsurface(X, Y, pyg.tile_width, pyg.tile_height).convert_alpha()
                
                # Update tile matrices
                tile_matrix[row][col] = image
        
        return tile_matrix

    def load_entities(self, flipped):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Import tiles
        ent_matrix = self.import_tiles('Data/.Images/tileset_ent.png', flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        self.ent_names = [
            'white',     'black',  'cyborg',
            'friend',    'eye',    'eyes',   'troll',  'triangle', 'purple',
            'tentacles', 'round1', 'round2', 'grass',  'round3',   'lizard',
            'red',       'rock',   'frog',   'radish',
            'snake',     'star',   'plant',
            'bald']
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
        equip_matrix = self.import_tiles('Data/.Images/tileset_equip.png', flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        self.equip_names = [
            'iron armor', 'green clothes', 'iron shield', 'orange clothes', 'exotic clothes', 'yellow dress', 'chain dress',
            'bra',        'brown hair',    'blue hair',   'blue beard',     'brown beard',    'white beard',  'short brown hair', 
            'dagger',     'blood dagger',  'shovel',      'super shovel',   'sword',          'blood sword',  'clean']
        
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
        
        self.equip['flat'] = self.equip['clean']
        
        self.armor_names = ['iron armor', 'green clothes', 'orange clothes', 'exotic clothes', 'yellow dress', 'chain dress']
    
    def load_other(self, flipped):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Import tiles
        other_matrix = self.import_tiles('Data/.Images/tileset_other.png', flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        self.other_names = [
            'decor', 'drugs', 'potions', 'scrolls',
            'stairs', 'floors', 'walls', 'roofs', 'paths',
            'null']
        decor_options = [
            'tree',   'bones', 'boxes',  'fire', 'leafy',      'bubble', 'skeleton', 'shrooms',
            'red plant right', 'red plant left', 'cup shroom', 'frond',  'blades']
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
            'grass3',    'grass4']
        walls_options = [
            'dark green', 'dark red', 'dark blue', 'gray', 'red', 'green', 'gold']
        roofs_options = [
            'tiled', 'slats']
        paths_options = [
            'left right', 'up down', 'down right', 'down left', 'up right', 'up left']
        null_options  = [
            'null']
        other_options = [
            decor_options,  drugs_options, potions_options, scrolls_options, stairs_options,
            floors_options, walls_options, roofs_options,   paths_options,   null_options]
        
        # Create image dictionary
        self.other = {}
        index = 0
        for _ in self.other_names:
            self.other[self.other_names[index]] = {option: image for (option, image) in zip(other_options[index], other_matrix[index])}
            index += 1
        self.other_count = sum([len(options_list) for options_list in other_options])

    def big_img(self):
    
        # Import tiles
        self.big = self.import_tiles('Data/.Images/decor_1_m_logo.png', flipped=False, effects=['posterize'])

    def biomes(self):
        """ Manages biome types. """
        
        self.biomes = {
            
            'any':     ['forest', 'desert', 'dungeon', 'water', 'city'],
            'wet':     ['forest', 'water'],
        
            'land':    ['forest', 'desert', 'dungeon'],
            'forest':  ['forest'],
            'desert':  ['desert'],
            'dungeon': ['dungeon'],
            'city':    ['city'],
            
            'sea':     ['water'],
            'water':   ['water']}

    # Effects
    def flip(self, obj):
        
        if type(obj) == list:
            obj = [pygame.transform.flip(objs, True, False) for objs in obj]
        elif type(obj) == dict:
            obj = {key: pygame.transform.flip(value, True, False) for (key, value) in obj.items()}

    def static(self, image, offset, rate):
        """Shift the tile by an offset. """
        
        if type(image) == list: image = self.dict[img_names[0]][img_names[1]]
        
        if random.randint(1, rate) == 1:
            X_offset, Y_offset = random.randint(0, offset), random.randint(0, offset)
            X_offset %= image.get_width()
            Y_offset %= image.get_height()
            
            shifted = pygame.Surface((image.get_width(), image.get_height()))
            shifted.blit(image, (X_offset, Y_offset)) # draws shifted
            shifted.blit(image, (X_offset - image.get_width(), Y_offset)) # wraps horizontally
            shifted.blit(image, (X_offset, Y_offset - image.get_height())) # wraps vertically
            shifted.blit(image, (X_offset - image.get_width(), Y_offset - image.get_height())) # wraps corners
            return shifted
        else: return image

    def shift(self, image, offset):
        """Shift the tile by an offset. """
        
        if type(image) == list: image = self.dict[image[0]][image[1]]
        
        X_offset, Y_offset = offset[0], offset[1]
        X_offset %= image.get_width()
        Y_offset %= image.get_height()
        
        shifted = pygame.Surface((image.get_width(), image.get_height()))
        shifted.blit(image, (X_offset, Y_offset))
        shifted.blit(image, (X_offset - image.get_width(), Y_offset)) # wraps horizontally
        shifted.blit(image, (X_offset, Y_offset - image.get_height())) # wraps vertically
        shifted.blit(image, (X_offset - image.get_width(), Y_offset - image.get_height())) # wraps corners
        return shifted

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

    def scale(self, image):
        return pygame.transform.scale2x(image)

    def grayscale(self, image):
        return pygame.transform.grayscale(image)

    # Animations
    def get_impact_image(self):
        
        color = (230, 230, 230)
        self.impact_image = pygame.Surface((pyg.tile_width, pyg.tile_width)).convert()
        self.impact_image.set_colorkey(self.impact_image.get_at((0,0)))
        image = pygame.Surface((int(pyg.tile_width/2), int(pyg.tile_height/3))).convert()
        top = 0
        left = 0
        bottom = image.get_width()-1
        right = image.get_height()-1
        center_X = int(image.get_width()/2)-1
        center_Y = int(image.get_height()/2)-1
        pygame.draw.line(image, color, (top,      left),     (bottom,   right),    2)
        pygame.draw.line(image, color, (bottom,   left),     (top,      right),    2)
        X = int((self.impact_image.get_width() - image.get_width())/2)
        Y = int((self.impact_image.get_height() - image.get_height())/2)
        self.impact_image.blit(image, (X, Y))
        return self.impact_image

    def entity_flash(self, ent):
        """ Death animation. """
        
        self.impact = True
        self.impact_image_pos.append((ent.X - player_obj.ent.env.camera.X, ent.Y - player_obj.ent.env.camera.Y))
        self.impact_images.append(self.impact_image)
        render_all()
        self.impact = False
        self.impact_image_pos.remove((ent.X - player_obj.ent.env.camera.X, ent.Y - player_obj.ent.env.camera.Y))
        self.impact_images.remove(self.impact_image)
        
        flash = 3
        flash_time = 2
        if ent.hp <=0:
           flash_time = 4
        old_img_names = ent.img_names.copy()
        while flash_time > 1:
            pygame.time.Clock().tick(30)
            #if flash:
            #    ent.img_names = ['null', 'null']
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

    def vicinity_flash(self, ent, image):
        """ Death animation. """
        
        self.impact = True
        vicinity_list = ent.get_vicinity()
        for i in range(2*len(vicinity_list)):
            
            image     = image
            x         = vicinity_list[i%len(vicinity_list)].X - player_obj.ent.env.camera.X
            y         = vicinity_list[i%len(vicinity_list)].Y - player_obj.ent.env.camera.Y
            image_pos = (x, y)
            duration  = 0.5
            last_time = time.time()
            delay     = i*0.1
            
            self.render_log.append([image, image_pos, duration, last_time, delay])

    def flash_above(self, ent, image):
        """ Death animation. """
        
        self.impact = True
        for i in range(2):
            
            image     = image
            x         = ent.X - player_obj.ent.env.camera.X
            y         = ent.Y - pyg.tile_height - player_obj.ent.env.camera.Y
            image_pos = (x, y)
            duration  = 0.1
            last_time = time.time()
            delay     = i*0.2
            
            self.render_log.append([image, image_pos, duration, last_time, delay])

    def render(self):
        """ Temporarily renders images in the queue.
        
            render_log : a list of the form [image, position, duration, last_time]
            image      : pygame image file
            position   : tuple of integers in tile units
            duration   : float; number of seconds to show the image
            last_time  : float; last time the image was shown 
            delay      : float; number of seconds before showing the image """
        
        if self.render_log:
            
            # Sort through images in queue
            for i in range(len(self.render_log)):
                
                # Start from the end to avoid index issues
                j = len(self.render_log) - i - 1
                
                # Prevent over-counting
                if j >= 0:
                    
                    # Shorthand
                    image = self.render_log[j][0]
                    position = self.render_log[j][1]
                    duration = self.render_log[j][2]
                    last_time = self.render_log[j][3]
                    delay = self.render_log[j][4]
                    
                    # Count down before showing image
                    if delay > 0:
                        self.render_log[j][4] -= (time.time() - last_time)
                        self.render_log[j][3] = time.time()
                    
                    # Count down before hiding image
                    elif duration > 0:
                        self.render_log[j][2] -= (time.time() - last_time)
                        self.render_log[j][3] = time.time()
                        pyg.screen.blit(image, position)
                        
                    else:
                        self.render_log.pop(j)

class Audio:
    """ Manages audio. One save for each file. """

    def __init__(self):
        
        # Initialize music player
        pygame.mixer.init()
        
        # Define song titles
        self.dict = {
            'home':        "Data/.Music/menu.mp3",
            'menu':        "Data/.Music/menu.mp3",
            'overworld 1': "Data/.Music/overworld_1.mp3",
            'overworld 2': "Data/.Music/overworld_2.mp3",
            'overworld 3': "Data/.Music/overworld_3.wav",
            'overworld 4': "Data/.Music/overworld_4.mp3",
            'dungeon 1':   "Data/.Music/dungeon_1.wav",
            'dungeon 2':   "Data/.Music/dungeon_2.mp3",
            'dungeon 3':   "Data/.Music/dungeon_3.wav",
            'dungeon 4':   "Data/.Music/dungeon_4.mp3",
            'dungeon 5':   "Data/.Music/dungeon_5.mp3",
            'dungeon 6':   "Data/.Music/dungeon_6.mp3"}
        
        self.load_speech()
        
        # Initialize parameters
        self.current_track = None
        self.soundtrack = list(self.dict.keys())
        self.soundtrack_len = len(self.soundtrack)
        self.i = 0

        # Other
        self.last_press_time_control = 0
        self.cooldown_time_control   = 0.5
        self.last_press_time_speech = 0
        self.speech_speed   = 100
        self.paused          = False
        self.control(self.soundtrack)

    def shuffle(self):
        if not pygame.mixer.music.get_busy():
            if not self.paused: self.play_track()

    def play_track(self, song=None, fade_out_time=2000, fade_in_time=2000):
        """ Plays a track and stops and prior track if needed. """
        
        # Fade out current track
        if pygame.mixer.music.get_busy(): pygame.mixer.music.fadeout(fade_out_time)
        
        # Select next track
        if not song:
            self.i = (self.i+1) % self.soundtrack_len
            song   = self.soundtrack[self.i]

        # Play the next track with fade-in
        self.current_track = song
        pygame.mixer.music.load(self.dict[song])
        pygame.mixer.music.play(fade_ms=fade_in_time)
        
        if self.paused: pygame.mixer.music.pause()

    def control(self, soundtrack=None, new_track=None):
        """ Loads and plays soundtracks, or plays single tracks. """
        
        if time.time() - self.last_press_time_control > self.cooldown_time_control:
            self.last_press_time_control = float(time.time())
        
            # Start a playlist
            if soundtrack:
                self.soundtrack_len = len(soundtrack)
                self.i = 0
                self.play_track(soundtrack[self.i])
            
            # Play a specific song
            elif (new_track is not None) and (new_track is not self.current_track):
                pygame.mixer.fadeout(4000)
                new_track.play(fade_ms=4000)
                self.current_track = new_track
            
            # Move to the next song
            elif pygame.mixer.music.get_busy():
                song = pygame.mixer.Sound(self.dict[self.current_track])
                self.duration = song.get_length()
                current_time = pygame.mixer.music.get_pos() / 1000
                self.remaining_time = self.duration - current_time
                if self.remaining_time <= 3:
                    self.play_track(song=self.soundtrack[(i+1)//len(soundtrack)])

    def pause(self, paused):
        if paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def load_speech(self):
        
        self.sound_map = {}

        for letter in "abcdefghijklmnopqrstuvwxyz".upper():
            self.sound_map[letter] = pygame.mixer.Sound(f"Data/.Speech/{letter}.wav")
        
        self.default_sound = pygame.mixer.Sound("Data/.Speech/M.wav")

    def play_speech(self, text):
        
        if text:
        
            # Prevent repeated calls
            if time.time() - self.last_press_time_speech > self.speech_speed//100:
                self.last_press_time_speech = float(time.time())

                # Only play dialogue
                if (':' in text) and ('*' not in text):
                    
                    # Sort through each letter
                    for char in text.upper():
                        
                        # Pick some random letters to play
                        if not random.randint(0, 10):
                            
                            # Set sound
                            if char in self.sound_map:
                                self.sound_map[char].play()
                            elif self.default_sound:
                                self.default_sound.play()
                            else:
                                continue
                            
                            # Play the sound
                            pygame.time.delay(self.speech_speed)  # Wait before playing the next sound
                            pygame.event.clear()
            
                else:
                    pygame.time.delay(self.speech_speed)
                    pygame.event.clear()

class Player:
    """ Manages player file. One save for each file. """

    def __init__(self, env=None):
        """ Holds everything regarding the player.
            Parameters
            ----------
            envs     : dict of list of Environment objects
            dungeon : list of Environment objects; dungeon levels """
        
        self.ent      = None
        self.ents     = {}
        self.envs     = {'home': [], 'dungeon': [], 'garden': [], 'cave': []}
        self.file_num = 0

    @debug_call
    def create_player(self):
        
        if self.ent:
            if self.ent.tile:
                self.ent.tile.entity = None
                self.ent.env.entities.remove(self.ent)
                self.ent.env = None
        
        self.ent = Entity(
            name       = 'Alex',
            role       = 'player',
            img_names  = ['white', 'front'],

            exp        = 0,
            rank       = 1,
            hp         = 100,
            max_hp     = 100,
            attack     = 0,
            defense    = 100,
            stamina    = 100,
            
            X          = 0,
            Y          = 0,
            habitat    = 'any',

            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0,
            fear       = None,
            reach      = 1000)
        
        hair   = create_item('bald')
        face   = create_item('clean')
        chest  = create_item('flat')
        dagger = create_item('dagger')
        dagger.effect = Effect(
            name          = 'swing',
            img_names     = ['decor', 'boxes'],
            function      = mech.swing,
            sequence      = '⮜⮟⮞',
            cooldown_time = 0.1)
        self.ent.inventory[hair.role].append(hair)
        self.ent.inventory[face.role].append(face)
        self.ent.inventory[chest.role].append(chest)
        self.ent.inventory[dagger.role].append(dagger)
        hair.toggle_equip(self.ent)
        face.toggle_equip(self.ent)
        chest.toggle_equip(self.ent)
        dagger.toggle_equip(self.ent)

## States
class MainMenu:
    
    def __init__(self):
        
        # Initialize title
        self.title_font     = pygame.font.SysFont('segoeuisymbol', 40, bold=True)
        self.game_title     = self.title_font.render("MORS SOMNIA", True, pyg.gray)
        self.game_title_pos = (int((pyg.screen_width - self.game_title.get_width())/2), 85)
        
        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, pyg.gray, [(5, 3), (10, 7), (5, 11)], 0)
        self.cursor_pos = [32, 320]
        
        # Initialize menu options
        self.menu_choices = ["NEW GAME", "LOAD", "SAVE", "CONTROLS", "QUIT"]
        self.menu_choices_surfaces = []
        for i in range(len(self.menu_choices)):
            if   i == 0:                          color = pyg.gray
            elif i == len(self.menu_choices) - 1: color = pyg.gray
            else:                                 color = pyg.gray
            self.menu_choices_surfaces.append(pyg.font.render(self.menu_choices[i], True, color))
        self.choice, self.choices_length = 0, len(self.menu_choices) - 1
        
        # Allows access to garden
        self.menu_toggle = True
        
        # Other
        self.last_press_time, self.cooldown_time = 0, 0.5

    def startup(self):
        
        # Startup background
        background_image = pygame.image.load("Data/.Images/garden.png").convert()
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
            pyg.screen.blit(self.game_title, self.game_title_pos)

            # Apply the fade effect
            pyg.screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
            
            # Increase alpha for the next frame
            alpha += fade_speed
        pyg.game_state = 'play_garden'
        pyg.overlay = 'menu'
        return

    def run(self):
        
        # Restrict keystroke speed
        mech.movement_speed(toggle=False, custom=2)
        
        # Prevent saving before a game is started or loaded
        if pyg.startup_toggle:
            self.menu_choices_surfaces[2] = pyg.font.render(self.menu_choices[2], True, pyg.dark_gray)
        else:
            self.menu_choices_surfaces[2] = pyg.font.render(self.menu_choices[2], True, pyg.gray)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # Navigation
                if event.key in pyg.key_UP:       self.key_UP()
                elif event.key in pyg.key_DOWN:   self.key_DOWN()
                
                # Music
                elif event.key in pyg.key_PLUS:   self.key_PLUS()
                elif event.key in pyg.key_MINUS:  self.key_MINUS()
                elif event.key in pyg.key_DEV:    self.key_DEV()
                
                # Garden
                elif event.key in pyg.key_PERIOD: self.key_PERIOD()
        
                # Unused
                elif event.key in pyg.key_LEFT:   self.key_LEFT()
                elif event.key in pyg.key_RIGHT:  self.key_RIGHT()
                elif event.key in pyg.key_HOLD:   self.key_HOLD()
                elif event.key in pyg.key_INV:    self.key_INV()
                elif event.key in pyg.key_INFO:   self.key_INFO()
                elif event.key in pyg.key_SPEED:  self.key_SPEED()
                elif event.key in pyg.key_QUEST:  self.key_QUEST()
                elif event.key in pyg.key_EQUIP:  self.key_EQUIP()
                elif event.key in pyg.key_DROP:   self.key_DROP()
                
                # >>RESUME<<
                elif event.key in pyg.key_BACK:
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        if not pyg.startup_toggle: pyg.game_state = 'play_game'
                        else:                      pyg.game_state = 'play_garden'
                        pyg.overlay = None
                        return
                
                # Select option
                elif event.key in pyg.key_ENTER:
                    
                    # >>NEW GAME<<
                    if self.choice == 0:
                        pyg.game_state = 'new_game'
                        new_game_obj.reset()
                        pyg.overlay = None
                        return
                    
                    # >>LOAD<<
                    elif self.choice == 1:
                        pyg.overlay = 'load'
                        return
                    
                    # >>SAVE<<
                    elif self.choice == 2:
                        
                        # Prevent saving before a game is started or loaded
                        if not pyg.startup_toggle:
                            pyg.overlay = 'save'
                            return
                    
                    # >>CONTROLS<<
                    elif self.choice == 3:
                        pyg.overlay = 'controls'
                        return
                    
                    # >>QUIT<<
                    elif self.choice == 4:
                        pygame.quit()
                        sys.exit()
        
        pyg.overlay = 'menu'
        return

    def key_UP(self):
        
        # >>SELECT MENU ITEM<<
        self.cursor_pos[1] -= 24
        self.choice -= 1
        if self.choice < 0:
            self.choice = self.choices_length
            self.cursor_pos[1] = 320 + (len(self.menu_choices) - 1) * 24

    def key_DOWN(self):
        
        # >>SELECT MENU ITEM<<
        self.cursor_pos[1] += 24
        self.choice += 1
        if self.choice > self.choices_length:
            self.choice = 0
            self.cursor_pos[1] = 320
    
    def key_LEFT(self):
        pass

    def key_RIGHT(self):
        pass

    def key_PERIOD(self):

        # >>GARDEN<<
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = float(time.time())
            if player_obj.ent.env.name != 'garden':
                place_player(env=player_obj.envs['garden'], loc=player_obj.envs['garden'].player_coordinates)    # menu (key_PERIOD)
                pyg.game_state = 'play_garden'
            elif not pyg.startup_toggle:
                place_player(env=player_obj.ent.last_env, loc=player_obj.ent.last_env.player_coordinates)    # menu (key_PERIOD)
                pyg.game_state = 'play_game'

    def key_HOLD(self):
        pass

    def key_PLUS(self):
        aud.pause(paused=False)

    def key_MINUS(self):
        aud.pause(paused=True)

    def key_INFO(self):
        pass

    def key_QUEST(self):
        pass

    def key_SPEED(self):
        pass

    def key_INV(self):
        pass

    def key_DEV(self):
        aud.play_track()

    def key_EQUIP(self):
        pass

    def key_DROP(self):
        pass

    def render(self):
        
        # Blit menu options
        Y = 316
        for menu_choice_surface in self.menu_choices_surfaces:
            pyg.screen.blit(menu_choice_surface, (48, Y))
            Y += 24
        
        # Blit cursor
        pyg.screen.blit(self.cursor_img, self.cursor_pos)

        # Blit logo
        if pyg.startup_toggle:
            pyg.screen.blit(self.game_title, self.game_title_pos)
        else:
            for i in range(len(img.big)):
                for j in range(len(img.big[0])):
                    X = pyg.screen_width - pyg.tile_width * (i+2)
                    Y = pyg.screen_height - pyg.tile_height * (j+2)
                    pyg.screen.blit(img.big[len(img.big)-j-1][len(img.big[0])-i-1], (X, Y))

class NewMenu:
    
    def __init__(self, name, header, options, options_categories=None, position='top left', backgrounds=None):
        """ IMPORTANT. Creates cursor, background, and menu options, then returns index of choice.

            header             : string; top line of text
            options            : list of strings; menu choices
            options_categories : list of strings; categorization; same length as options
            position           : chooses layout preset """
        
        self.name               = name
        self.header             = header
        self.options            = options
        self.options_categories = options_categories
        self.position           = position
        self.backgrounds        = backgrounds
        
        # Initialize temporary data containers
        self.choice                   = 0                   # holds index of option pointed at by cursor
        self.choices_length           = len(self.options)-1 # number of choices
        self.options_categories_cache = ''                  # holds current category
        self.options_render           = self.options.copy()
        
        # Alter layout if categories are present
        if self.options_categories: 
            tab_X, tab_Y = 70, 10
            self.options_categories_cache_2 = self.options_categories[0]
        else:
            tab_X, tab_Y = 0, 0

        # Set initial position of each text type
        self.header_position    = {'top left':    [5, 10], 'center': [int((pyg.screen_width - main_menu_obj.game_title.get_width())/2), 85],
                              'bottom left': [5, 10],              'bottom right': [60 ,70]}
        self.cursor_position    = {'top left':    [50+tab_X, 38+tab_Y], 'center':       [50, 300],
                              'bottom left': [50+tab_X, 65-tab_Y], 'bottom right': [60 ,70]}
        self.options_positions  = {'top left':    [80+tab_X, 34],       'center':       [80, 300],
                              'bottom left': [5, 10],              'bottom right': [60 ,70]}
        self.category_positions = {'top left':    [5, 34],              'center':       [80, 300],
                              'bottom left': [5, 10],              'bottom right': [60 ,70]}

        # Set mutable copies of text positions
        self.cursor_position_mutable    = self.cursor_position[self.position].copy()
        self.options_positions_mutable  = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()

        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0,0)))
        pygame.draw.polygon(self.cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
        
        # Initialize menu options
        self.header_render = pyg.font.render(self.header, True, pyg.yellow)
        for i in range(len(self.options)):
            color = pyg.gray
            self.options_render[i] = pyg.font.render(options[i], True, color)
        
        # Initialize backgrounds
        if self.backgrounds:
            self.backgrounds_render = copy.copy(self.backgrounds)
            for i in range(len(self.backgrounds)):
                self.backgrounds_render[i] = pygame.image.load(self.backgrounds[i]).convert()

    def reset(self, name, header, options, options_categories, position, backgrounds):
        self.__init__(self.name, self.header, self.options, self.options_categories, self.position, self.backgrounds)

    def run(self):
        
        mech.movement_speed(toggle=False, custom=2)
        mech.zoom_cache = 1
        
        # Called when the user inputs a command
        for event in pygame.event.get():
            
            if event.type == KEYDOWN:
                
                # Navigation
                if event.key in pyg.key_UP:       self.key_UP()
                elif event.key in pyg.key_DOWN:   self.key_DOWN()
                
                # Unused
                elif event.key in pyg.key_LEFT:   self.key_LEFT()
                elif event.key in pyg.key_RIGHT:  self.key_RIGHT()
                elif event.key in pyg.key_HOLD:   self.key_HOLD()
                elif event.key in pyg.key_INV:    self.key_INV()
                elif event.key in pyg.key_INFO:   self.key_INFO()
                elif event.key in pyg.key_SPEED:  self.key_SPEED()
                elif event.key in pyg.key_QUEST:  self.key_QUEST()
                elif event.key in pyg.key_EQUIP:  self.key_EQUIP()
                elif event.key in pyg.key_DROP:   self.key_DROP()
                elif event.key in pyg.key_PERIOD: self.key_PERIOD()
                elif event.key in pyg.key_PLUS:   self.key_PLUS()
                elif event.key in pyg.key_MINUS:  self.key_MINUS()
                elif event.key in pyg.key_DEV:    self.key_DEV()
                
                # >>RESUME<<
                elif event.key in pyg.key_BACK:
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay = 'menu'
                        return None
                
                # Process selection or return to main menu
                elif event.key in pyg.key_ENTER:
                    
                    if self.name == 'save':
                        self.save_account()
                    elif self.name == 'load':
                        self.load_account()
                    
                    pyg.overlay = 'menu'
                    return

        pyg.overlay = copy.copy(self.name)
        return

    def key_UP(self):

        # >>SELECT MENU ITEM<<        
        # Move cursor up
        self.cursor_position_mutable[1]     -= 24
        self.choice                         -= 1
        
        # Move to lowest option
        if self.choice < 0:
            self.choice                     = self.choices_length
            self.cursor_position_mutable[1] = self.cursor_position[self.position][1] + (len(self.options)-1) * 24
            if self.options_categories:
                self.cursor_position_mutable[1] += tab_Y * (len(set(self.options_categories)) - 1)
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] -= tab_Y

    def key_DOWN(self):

        # >>SELECT MENU ITEM<<        
        # Move cursor down
        self.cursor_position_mutable[1]     += 24
        self.choice                         += 1
        
        # Move to highest option
        if self.choice > self.choices_length:
            self.choice                     = 0
            self.cursor_position_mutable[1] = self.cursor_position[self.position][1]
            if self.options_categories:
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] += tab_Y

    def key_LEFT(self):
        pass

    def key_RIGHT(self):
        pass

    def key_PERIOD(self):
        pass

    def key_HOLD(self):
        pass

    def key_PLUS(self):
        pass

    def key_MINUS(self):
        pass

    def key_INFO(self):
        pass

    def key_QUEST(self):
        pass

    def key_SPEED(self):
        pass

    def key_INV(self):
        pass

    def key_DEV(self):
        pass

    def key_EQUIP(self):
        pass

    def key_DROP(self):
        pass

    def save_account(self):    
        """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen.
            Structures
            ----------
            = player_obj
            == envs
            === garden
            === home
            === dungeon
            == ent
            == ents 
            == questlog """
        
        # Update files menu
        if player_obj.file_num: self.options[player_obj.file_num - 1] += ' *'
        
        # Save data or return to main menu
        if type(self.choice) != int:
            pyg.overlay = 'main_menu'
            return
        else:
            self.choice += 1
            
            # Update Player object
            player_obj.file_num = self.choice
            
            # Save everything
            with open(f"Data/File_{self.choice}/ent.pkl", 'wb') as file:        pickle.dump(player_obj.ent, file)
            with open(f"Data/File_{self.choice}/ents.pkl", 'wb') as file:       pickle.dump(player_obj.ents, file)
            with open(f"Data/File_{self.choice}/envs.pkl", 'wb') as file:       pickle.dump(player_obj.envs, file)
            with open(f"Data/File_{self.choice}/questlog.pkl", 'wb') as file:   pickle.dump(player_obj.questlog, file)
            with open(f"Data/File_{self.choice}/questlines.pkl", 'wb') as file: pickle.dump(player_obj.questlines, file)
            
            screenshot(
                size    = 'display',
                visible = False,
                folder  = f"Data/File_{self.choice}", filename="screenshot.png",
                blur    = True)
            
            self.reset(
                self.name,
                self.header,
                self.options,
                self.options_categories,
                self.position,
                self.backgrounds)
            load_account_obj.reset(
                load_account_obj.name,
                load_account_obj.header,
                load_account_obj.options,
                load_account_obj.options_categories,
                load_account_obj.position,
                load_account_obj.backgrounds)
            pyg.overlay = 'main_menu'

    def load_account(self):    
        """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen.
            Structures
            ----------
            = player_obj
            == envs
            === garden
            === home
            === dungeon
            == ent 
            == ents 
            == questlog """
        
        global player_obj
        
        # Update file menu
        if player_obj.file_num: self.options[player_obj.file_num - 1] += ' *'
        
        # Load data or return to main menu
        if self.choice is not None:
            
            if type(self.choice) != int:
                pyg.overlay = 'main_menu'
                return
            else:
                self.choice += 1
                pyg.startup_toggle = False
            
            # Load data onto fresh player
            player_obj = Player()
            with open(f"Data/File_{self.choice}/questlines.pkl", "rb") as file: player_obj.questlines = pickle.load(file)
            with open(f"Data/File_{self.choice}/ent.pkl", "rb") as file:        player_obj.ent        = pickle.load(file)
            with open(f"Data/File_{self.choice}/ents.pkl", "rb") as file:       player_obj.ents       = pickle.load(file)
            with open(f"Data/File_{self.choice}/envs.pkl", "rb") as file:       player_obj.envs       = pickle.load(file)
            with open(f"Data/File_{self.choice}/questlog.pkl", "rb") as file:   player_obj.questlog   = pickle.load(file)

            # Load cameras
            for env in player_obj.envs.values():
                if type(env) == list:
                    for sub_env in env: sub_env.camera = Camera(player_obj.ent)
                else:                   env.camera     = Camera(player_obj.ent)
            
            self.reset(self.name, self.header, self.options, self.options_categories, self.position, self.backgrounds)
            pyg.overlay = 'main_menu'

    def render(self):
        
        # Render menu background
        if self.backgrounds:
            pyg.screen.fill(pyg.black)
            pyg.screen.blit(self.backgrounds_render[self.choice], (0, 0))
        else:
            pyg.screen.fill(pyg.black)
        
        # Render header and cursor
        pyg.screen.blit(self.header_render, self.header_position[self.position])
        pyg.screen.blit(self.cursor_img, self.cursor_position_mutable)
        
        # Render categories and options
        for i in range(len(self.options_render)):
            
            # Render category text if it is not present 
            if self.options_categories:
                if self.options_categories[i] != self.options_categories_cache:
                    self.options_categories_cache = self.options_categories[i]
                    text = pyg.font.render(f'{self.options_categories_cache.upper()}:', True, pyg.gray)
                    self.options_positions_mutable[1] += tab_Y
                    pyg.screen.blit(text, (self.category_positions_mutable[0], self.options_positions_mutable[1]))
                
            # Render option text
            pyg.screen.blit(self.options_render[i], self.options_positions_mutable)
            self.options_positions_mutable[1] += 24
        self.options_positions_mutable = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()
        pygame.display.flip()

class NewGame:
    
    def __init__(self):
        """ Manages the character creation menu. Handles player input. Only active when menu is open.
            Called when starting a new game.
        
            HAIR:       sets hair by altering hair_index, which is used in new_game to add hair as an Object hidden in the inventory
            HANDEDNESS: mirrors player/equipment tiles, which are saved in img.dict and img.cache
            ACCEPT:     runs new_game() to generate player, home, and default items, then runs play_game() """
        
        # Reset player
        pyg.startup_toggle = True
        player_obj.create_player()
        player_obj.envs['garden'] = build_garden()
        place_player(player_obj.envs['garden'], player_obj.envs['garden'].center)    # new game
        player_obj.ent.env.camera = Camera(player_obj.ent)
        player_obj.ent.env.camera.fixed = True
        player_obj.ent.env.camera.zoom_in(custom=1)
        player_obj.questlog = Questlog()
        
        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
        
        # Set character background
        self.background_image = pygame.image.load("Data/.Images/room.png")
        
        # Initialize menu options
        self.menu_choices = ["HAIR", "FACE", "SEX", "SKIN", "HANDEDNESS", "", "ACCEPT", "BACK"]   
        for i in range(len(self.menu_choices)):
            if   i == len(self.menu_choices)-2:  color = pyg.green
            elif i == len(self.menu_choices)-1:  color = pyg.red
            else:                           color = pyg.gray
            self.menu_choices[i] = pyg.font.render(self.menu_choices[i], True, color)
        self.choice, self.choices_length = 0, len(self.menu_choices)-1
        self.cursor_pos, self.top_choice = [50, 424-len(self.menu_choices)*24], [50, 424-len(self.menu_choices)*24]
        
        # Begins with default settings (ideally)
        self.orientations = ['front', 'right', 'back', 'left']
        self.last_press_time = 0
        self.cooldown_time = 0.7

    def run(self):
        mech.movement_speed(toggle=False, custom=2)
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # >>MAIN MENU<<
                if (event.key in pyg.key_BACK) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                    pyg.last_press_time = float(time.time())
                    pyg.game_state = 'play_game'
                    pyg.overlay = 'menu'
                    return
                
                # >>SELECT MENU ITEM<<
                elif event.key in pyg.key_UP:   # Up
                    self.cursor_pos[1]     -= 24
                    self.choice            -= 1
                    
                    # Go to the top menu choice
                    if self.choice < 0:
                        self.choice         = self.choices_length
                        self.cursor_pos[1]  = self.top_choice[1] + (len(self.menu_choices)-1) * 24
                    
                    # Skip a blank line
                    elif self.choice == (self.choices_length - 2):
                        self.choice         = self.choices_length - 3
                        self.cursor_pos[1]  = self.top_choice[1] + (len(self.menu_choices)-4) * 24
                
                elif event.key in pyg.key_DOWN: # Down
                    self.cursor_pos[1]     += 24
                    self.choice            += 1
                    
                    if self.choice > self.choices_length:
                        self.choice         = 0
                        self.cursor_pos[1]  = self.top_choice[1]
                    
                    elif self.choice == (self.choices_length - 2):
                        self.choice         = self.choices_length - 1
                        self.cursor_pos[1]  = self.top_choice[1] + (len(self.menu_choices)-2) * 24
                
                # Apply option
                elif event.key in pyg.key_ENTER:
                
                    # >>HAIR and FACE<<
                    if self.choice in [0, 1, 2]:
                        
                        # Hair or face
                        if self.choice == 0:
                            role     = 'head'
                            img_dict = img.hair_options
                        elif self.choice == 1:
                            role     = 'face'
                            img_dict = img.face_options
                        elif self.choice == 2:
                            role     = 'chest'
                            img_dict = img.chest_options
                        
                        # Find next option and dequip last option
                        index = (img_dict.index(player_obj.ent.equipment[role].img_names[0]) + 1) % len(img_dict)
                        img_name = img_dict[index]
                        player_obj.ent.equipment[role].toggle_equip(player_obj.ent)
                        
                        # Equip next option if already generated
                        if img_name in [[x[i].img_names[0] for i in range(len(x))] for x in player_obj.ent.inventory.values()]:
                            player_obj.ent.inventory[img_name][0].toggle_equip(player_obj.ent)
                        
                        # Generate option before equip
                        else:
                            item = create_item(img_name)
                            player_obj.ent.inventory['armor'].append(item)
                            item.toggle_equip(player_obj.ent)
                    
                    # >>SKIN<<
                    if self.choice == 3:
                        if player_obj.ent.img_names[0] == 'white':   player_obj.ent.img_names[0] = 'black'
                        elif player_obj.ent.img_names[0] == 'black': player_obj.ent.img_names[0] = 'white'
                    
                    # >>HANDEDNESS<<
                    if self.choice == 4:
                        if player_obj.ent.handedness == 'left':
                            player_obj.ent.handedness = 'right'
                        elif player_obj.ent.handedness == 'right':
                            player_obj.ent.handedness = 'left'
                    
                    # >>ACCEPT<<
                    if self.choice == 6:
                        pyg.startup_toggle = False
                        new_game_obj.new_game()
                        pyg.game_state = 'play_game'
                        return
                    
                    # >>MAIN MENU<<
                    if self.choice == 7:
                        pyg.game_state = 'play_game'
                        pyg.overlay = 'menu'
                        return
        pyg.game_state = 'new_game'

    def reset(self):
        self.__init__()

    def new_game(self):
        """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
            Called when starting a new game or loading a previous game.

            new:  creates player as Object with Fighter stats, calls make_home(), then loads initial inventory
            else: calls load_objects_from_file() to load player, inventory, and current floor """
        
        # Clear prior data
        player_obj.envs = {}
        player_obj.ents = {}
        player_obj.questlog = None
        player_obj.envs['garden'] = build_garden()

        # Prepare player
        player_obj.ent.role         = 'player'
        player_obj.ent.img_names[1] = 'front'
        player_obj.questlog         = Questlog()
        
        player_obj.envs['home'] = build_home()
        place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].center)    # new game
        
        # Create items
        if player_obj.ent.equipment['chest'].img_names[0] == 'bra': name = 'yellow dress'
        else: name = 'green clothes'                        
        clothes = create_item(name)
        hair    = create_item('bald')
        face    = create_item('clean')
        chest   = create_item('flat')
        shovel  = create_item('super shovel')
        player_obj.ent.inventory[clothes.role].append(clothes)
        player_obj.ent.inventory[hair.role].append(hair)
        player_obj.ent.inventory[face.role].append(face)
        player_obj.ent.inventory[chest.role].append(chest)
        player_obj.ent.inventory[shovel.role].append(shovel)
        clothes.toggle_equip(player_obj.ent)
        sort_inventory()
        
        # Prepare gui
        pyg.msg = []
        pyg.update_gui('Press / to hide messages.', pyg.dark_gray)
        pyg.msg_toggle = True
    
    def render(self):
        # -------------------------------------- RENDER --------------------------------------
        # Implement timed rotation of character
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = float(time.time()) 
            player_obj.ent.img_names[1] = self.orientations[self.orientations.index(player_obj.ent.img_names[1]) - 1]

        # Set menu background
        pyg.display.fill(pyg.black)
        
        # Renders menu to update cursor location
        Y = self.top_choice[1] - 4
        for self.menu_choice in self.menu_choices:
            pyg.display.blit(self.menu_choice, (80, Y))
            Y += 24
        pyg.display.blit(self.cursor_img, self.cursor_pos)
        pyg.display.blit(self.background_image, (400, 200))
        player_obj.ent.draw(pyg.display, loc=(464, 264))

class PlayGame:

    def __init__(self):
        self.cooldown_time = 1
        self.last_press_time = 0

    def run(self):
        
        player_obj.ent.role = 'player'
        mech.movement_speed(toggle=False)
        
        if not pyg.overlay:
            for event in pygame.event.get():

                # Save and quit
                if event.type == QUIT:
                    save_account()
                    pygame.quit()
                    sys.exit()
                
                # Keep playing
                if not player_obj.ent.dead:
                    if event.type == KEYDOWN:
                        active_effects()                        
                        
                        # Movement
                        if event.key in pyg.key_UP:       self.key_UP()
                        elif event.key in pyg.key_DOWN:   self.key_DOWN()
                        elif event.key in pyg.key_LEFT:   self.key_LEFT()
                        elif event.key in pyg.key_RIGHT:  self.key_RIGHT()
                        
                        # Actions
                        elif event.key in pyg.key_ENTER:  self.key_ENTER()
                        elif event.key in pyg.key_PERIOD: self.key_PERIOD()
                        elif event.key in pyg.key_PLUS:   self.key_PLUS()
                        elif event.key in pyg.key_MINUS:  self.key_MINUS()
                        
                        # Menus
                        elif event.key in pyg.key_INFO:   self.key_INFO()
                        elif event.key in pyg.key_SPEED:  self.key_SPEED()
                        elif event.key in pyg.key_QUEST:  self.key_QUEST()
                        
                        # Other
                        elif event.key in pyg.key_EQUIP: self.key_EQUIP()
                        elif event.key in pyg.key_DROP:  self.key_DROP()
                        
                        # >>MAIN MENU<<
                        elif event.key in pyg.key_BACK:
                            if time.time()-pyg.last_press_time > pyg.cooldown_time:
                                pyg.last_press_time = float(time.time())
                                pyg.overlay = 'menu'
                                pygame.event.clear()
                                return
            
                        # >>COMBOS<<
                        elif event.key in pyg.key_HOLD:
                            pyg.overlay = 'hold'
                            pygame.event.clear()
                            return
                        
                        # >>INVENTORY<<
                        elif event.key in pyg.key_INV:
                            pyg.overlay = 'inv'
                            pygame.event.clear()
                            return
                        
                        # >>CONSTRUCTION<<
                        elif event.key in pyg.key_DEV:
                            trade_obj.ent = player_obj.ent
                            pyg.overlay = 'dev'
                            pygame.event.clear()
                            return
                
                else:
                    
                    # >>MAIN MENU<<
                    if event.type == KEYDOWN:
                        if event.key in pyg.key_BACK:
                            pyg.overlay = 'menu'
                            pygame.event.clear()
                            return
                    
                        # >>TOGGLE MESSAGES<<
                        elif event.key in pyg.key_PERIOD:
                            if pyg.msg_toggle: pyg.msg_toggle = False
                            else:
                                if pyg.gui_toggle:
                                    pyg.gui_toggle = False
                                    pyg.msg_toggle = False
                                else:
                                    pyg.msg_toggle = True
                                    pyg.gui_toggle = True
            
        for entity in player_obj.ent.env.entities:
            if not entity.dead: entity.ai()
        
        pyg.game_state = 'play_game'

    def key_UP(self):
        # >>MOVE<<
        player_obj.ent.move(0, -pyg.tile_height)

    def key_DOWN(self):
        # >>MOVE<<
        player_obj.ent.move(0, pyg.tile_height)

    def key_LEFT(self):
        # >>MOVE<<
        player_obj.ent.move(-pyg.tile_width, 0)

    def key_RIGHT(self):
        # >>MOVE<<
        player_obj.ent.move(pyg.tile_width, 0)

    def key_ENTER(self):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            print(player_obj.ent.env.player_coordinates)

            # >>PICKUP/STAIRS<<
            # Check if an item is under the player
            if player_obj.ent.tile.item:
                
                # Dungeon
                if player_obj.ent.tile.item.name == 'dungeon':     mech.enter_dungeon()
                elif player_obj.ent.tile.item.name == 'cave':      mech.enter_cave()
                elif player_obj.ent.tile.item.name == 'overworld': mech.enter_overworld()
                elif player_obj.ent.tile.item.name == 'home':      mech.enter_home()
                
                # Pick up or activate
                else: player_obj.ent.tile.item.pick_up()

    def key_PERIOD(self):
        
        # >>HOME<<
        
        if player_obj.ent.tile.item:
            if player_obj.ent.tile.item.name in ['dungeon', 'cave']:
                if time.time()-self.last_press_time > self.cooldown_time:
                    self.last_press_time = float(time.time())
                
                    # Go up by one floor
                    if player_obj.ent.env.lvl_num > 1:
                        env = player_obj.envs[player_obj.ent.env.name][player_obj.ent.env.lvl_num-2]
                        place_player(env, env.player_coordinates)    # play game (key_PERIOD)
                    
                    elif player_obj.ent.env.lvl_num == 1:
                        env = player_obj.ent.last_env
                        place_player(env, env.player_coordinates)    # play game (key_PERIOD)
        
        # >>TOGGLE MESSAGES<<
        else:
        
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

    def key_PLUS(self):
        
        # >>ZOOM<<
        player_obj.ent.env.camera.zoom_in()

    def key_MINUS(self):
        
        # >>ZOOM<<
        player_obj.ent.env.camera.zoom_out()

    def key_INFO(self):
        
        # >>VIEW STATS<<
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

    def key_QUEST(self):
        
        # >>VIEW QUESTLOG<<
        player_obj.questlog.questlog_menu()

    def key_SPEED(self):
        
        # >>MOVEMENT SPEED<<
        if time.time()-pyg.last_press_time > pyg.cooldown_time:
            pyg.last_press_time = float(time.time())
            mech.movement_speed()

    def key_EQUIP(self):
        
        # >>CHECK INVENTORY<<
        chosen_item = inventory_menu("INVENTORY:         USE ITEM")
        if chosen_item is not None:
            chosen_item.use()
            pyg.update_gui()

    def key_DROP(self):
        
        # >>DROP ITEM<<
        if player_obj.ent.tile.item:
            pyg.update_gui("There's already something here", color=pyg.dark_gray)
        else:
            chosen_item = inventory_menu("INVENTORY:         DROP ITEM")
            if chosen_item is not None:
                chosen_item.drop()
                pygame.event.clear()

    def render(self):
        pyg.message_height = 4
        if not pyg.overlay: pyg.update_gui()
        render_all()

class PlayGarden:
    
    def run(self):
        
        if pyg.overlay == 'menu': player_obj.ent.role = 'NPC'
        else:                     player_obj.ent.role = 'player'
        
        player_obj.envs['garden'].camera.zoom_in(custom=1)
        mech.movement_speed(toggle=False, custom=2)
        
        if not pyg.overlay:
            for event in pygame.event.get():

                # Save and quit
                if event.type == QUIT:
                    save_account()
                    pygame.quit()
                    sys.exit()
                
                # Keep playing
                if not player_obj.ent.dead:
                    if event.type == KEYDOWN:
                        
                        # Movement
                        if event.key in pyg.key_UP:     self.key_UP()
                        if event.key in pyg.key_DOWN:   self.key_DOWN()
                        if event.key in pyg.key_LEFT:   self.key_LEFT()
                        if event.key in pyg.key_RIGHT:  self.key_RIGHT()
                        
                        # Actions
                        if event.key in pyg.key_ENTER:  self.key_ENTER()
                        if event.key in pyg.key_PERIOD: self.key_PERIOD()
                        if event.key in pyg.key_PLUS:   self.key_PLUS()
                        if event.key in pyg.key_MINUS:  self.key_MINUS()
                        if event.key in pyg.key_HOLD:   self.key_HOLD()
                        
                        # Menus
                        if event.key in pyg.key_INFO:   self.key_INFO()
                        if event.key in pyg.key_SPEED:  self.key_SPEED()
                        if event.key in pyg.key_QUEST:  self.key_QUEST()
                        
                        # Other
                        if event.key in pyg.key_EQUIP: self.key_EQUIP()
                        if event.key in pyg.key_DROP:  self.key_DROP()
                        
                        # >>MAIN MENU<<
                        if event.key in pyg.key_BACK:
                            if time.time()-pyg.last_press_time > pyg.cooldown_time:
                                pyg.last_press_time = float(time.time())
                                pyg.overlay = 'menu'
                                pygame.event.clear()
                                return
                        
                        # >>INVENTORY<<
                        if event.key in pyg.key_INV:
                            pyg.overlay = 'inv'
                            pygame.event.clear()
                            return
                        
                        # >>CONSTRUCTION<<
                        if event.key in pyg.key_DEV:
                            pyg.overlay = 'dev'
                            pygame.event.clear()
                            return
                
                else:
                    # >>MAIN MENU<<
                    if event.type == KEYDOWN:
                        if event.key in pyg.key_BACK:
                            pyg.overlay = 'menu'
                            pygame.event.clear()
                            return
                            
                    # >>TOGGLE MESSAGES<<
                    elif event.key in pyg.key_PERIOD:
                        if pyg.msg_toggle: pyg.msg_toggle = False
                        else:
                            if pyg.gui_toggle:
                                pyg.gui_toggle = False
                                pyg.msg_toggle = False
                            else:
                                pyg.msg_toggle = True
                                pyg.gui_toggle = True
        
        for entity in player_obj.ent.env.entities: entity.ai()
        player_obj.ent.ai()
        
        pyg.game_state = 'play_garden'

    def key_UP(self):
        player_obj.ent.move(0, -pyg.tile_height)

    def key_DOWN(self):
        player_obj.ent.move(0, pyg.tile_height)

    def key_LEFT(self):
        player_obj.ent.move(-pyg.tile_width, 0)

    def key_RIGHT(self):
        player_obj.ent.move(pyg.tile_width, 0)

    def key_ENTER(self):

        # >>PICKUP/STAIRS<<            
        # Check if an item is under the player
        if player_obj.ent.tile.item:
            
            # Pick up or activate
            player_obj.ent.tile.item.pick_up()

    def key_PERIOD(self):

        # >>TOGGLE MESSAGES<<
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

    def key_HOLD(self):
        pass

    def key_PLUS(self):
        pass

    def key_MINUS(self):
        pass

    def key_INFO(self):
        pass

    def key_QUEST(self):
        player_obj.questlog.questlog_menu()

    def key_SPEED(self):

        # >>MOVEMENT SPEED<<
        if time.time()-pyg.last_press_time > pyg.cooldown_time:
            pyg.last_press_time = float(time.time())
            mech.movement_speed()

    def key_EQUIP(self):

        # >>CHECK INVENTORY<<
        chosen_item = inventory_menu("INVENTORY:         USE ITEM")
        if chosen_item is not None:
            chosen_item.use()
            pyg.update_gui()

    def key_DROP(self):
        
        # >>DROP ITEM<<
        if player_obj.ent.tile.item:
            pyg.update_gui("There's already something here", color=pyg.dark_gray)
        else:
            chosen_item = inventory_menu("INVENTORY:         DROP ITEM")
            if chosen_item is not None:
                chosen_item.drop()
                pygame.event.clear()

    def render(self):
        pyg.msg_toggle = False
        pyg.gui_toggle = False
        render_all()

class DevTools:
    
    def __init__(self):
        
        # Data for select_item and locked_item
        self.cursor_pos = [pyg.screen_width-pyg.tile_width, 32]
        self.dic_index = 0
        self.dic_categories = img.other_names[:-1]
        self.dic_indices = [[0, 0] for _ in self.dic_categories] # offset, choice
        self.locked = False
        self.img_names = ['null', 'null']
        self.img_x = 0
        self.img_y = 0

    def run(self):   
        
        mech.movement_speed(toggle=False, custom=2)
        
        # Initialize cursor
        if bool(self.locked): size, width, alpha = 30, 2, 192
        else:                 size, width, alpha = 31, 1, 128
        self.cursor_border = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)
        
        # Initialize tile selection
        self.dic = img.other[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # >>PLAY GAME<<
                if (event.key in pyg.key_BACK) or (event.key in pyg.key_HOLD):
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay = None
                        return
                
                # >>LOCK SELECTION<<
                elif event.key in pyg.key_DEV:
                    if not self.locked:
                        self.cursor_border = pygame.Surface((32, 32)).convert()
                        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))
                        self.locked = True
                        pygame.draw.polygon(self.cursor_border, pyg.white, [(0, 0), (30, 0), (30, 30), (0, 30)], 2)
                    else:
                        self.cursor_border = pygame.Surface((32, 32)).convert()
                        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))
                        self.locked = False
                        pygame.draw.polygon(self.cursor_border, pyg.white, [(0, 0), (31, 0), (31, 31), (0, 31)], 1)
                
                # >>NAVIGATE DICTIONARY<<
                elif event.key in pyg.key_UP:
                    
                    # Selection
                    if not self.locked:
                        self.choice -= 1
                        if self.cursor_pos[1] == 32: self.offset -= 1
                        else: self.cursor_pos[1] -= pyg.tile_height
                    else: player_obj.ent.move(0, -pyg.tile_height)
                
                elif event.key in pyg.key_DOWN:
                    if not self.locked:
                        self.choice += 1
                        if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
                        else: self.cursor_pos[1] += pyg.tile_height
                    else: player_obj.ent.move(0, pyg.tile_height)
                
                # >>CHANGE DICTIONARY<<
                elif (event.key in pyg.key_LEFT) or (event.key in pyg.key_RIGHT):
                
                    if event.key in pyg.key_LEFT:
                        if not self.locked: self.dic_index -= 1
                        else: player_obj.ent.move(-pyg.tile_height, 0)
                            
                    elif event.key in pyg.key_RIGHT:
                        if not self.locked: self.dic_index += 1
                        else: player_obj.ent.move(pyg.tile_width, 0)

                    self.dic = img.other[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                    self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                    self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
                    self.choice = self.cursor_pos[1]//32 + self.offset - 1
                    
                    # Move cursor to the highest spot in the dictionary
                    if self.cursor_pos[1] > 32*len(self.dic):
                        self.cursor_pos[1] = 32*len(self.dic)
                        self.choice = len(self.dic) - self.offset - 1
                
                # >>SELECT AND PLACE<<
                elif event.key in pyg.key_ENTER:
                    self.place_item()
                
                # >>INVENTORY<<
                elif event.key in pyg.key_INV:
                    pyg.overlay = 'inv'
                    pygame.event.clear()
                    return

            # Save for later reference
            self.dic_indices[self.dic_index%len(self.dic_indices)][0] = self.offset
            self.dic_indices[self.dic_index%len(self.dic_indices)][1] = self.choice
        pyg.overlay = 'dev'
        return

    def place_item(self):

        # Note location and image names
        self.img_x, self.img_y = int(player_obj.ent.X/pyg.tile_width), int(player_obj.ent.Y/pyg.tile_height)
        self.img_names[0] = self.dic_categories[self.dic_index%len(self.dic_categories)]
        self.img_names[1] = list(self.dic.keys())[(self.choice)%len(self.dic)]
        
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
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = player_obj.ent.env,
                names = self.img_names.copy())
        
        # Place item
        else:
            item = create_item(
                names = self.img_names)
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = player_obj.ent.env,
                names = self.img_names.copy())
        
        self.img_x, self.img_y = None, None
        pyg.overlay = None

    def export_env(self):
        with open(f"Data/File_{player_obj.file_num}/env.pkl", 'wb') as file:
            pickle.dump(player_obj.ent.env, file)

    def import_env(self):
        try:
            with open(f"Data/File_{player_obj.file_num}/env.pkl", "rb") as file:
                env = pickle.load(file)
            env.camera = Camera(player_obj.ent)
            env.camera.update()
            place_player(env, env.player_coordinates)    # DevTools (import)
        except: print("No file found!")

    def render(self):
        pyg.message_height = 1
        pyg.update_gui()
        render_all()
        
        pyg.screen.blit(self.cursor_fill,   self.cursor_pos)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                pyg.screen.blit(self.dic[list(self.dic.keys())[(i+self.offset)%len(self.dic)]], (pyg.screen_width-pyg.tile_width, Y))
                Y += pyg.tile_height
                counter += 1
            else: break
        pyg.screen.blit(self.cursor_border, self.cursor_pos)

class Inventory:
    
    def __init__(self):
        
        # Data for select_item and locked_item
        self.cursor_pos = [0, 32]
        self.dic_index = 0
        self.locked = False
        self.img_names = ['null', 'null']
        self.img_x = 0
        self.img_y = 0
        self.dic_indices = [[0, 0]]
        
        self.detail = True
        self.cooldown_time = 0.1
        self.last_press_time = 0

    def update_data(self):

        # Restrict movement speed
        mech.movement_speed(toggle=False, custom=2)
        
        # Initialize cursor
        if bool(self.locked): size, width, alpha = 30, 2, 192
        else:                 size, width, alpha = 31, 1, 128
        self.cursor_border = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)
        
        # Initialize tile selection
        self.inventory_dics = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        self.dic_categories = ['weapons',     'armor',     'potions',     'scrolls',     'drugs',     'other']
        for key, value in player_obj.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics[key][item.name] = img.dict[item.img_names[0]][item.img_names[1]]
        for key, value in self.inventory_dics.items():
            if not value: self.dic_categories.remove(key)
        
        # Restore last selection
        if len(self.dic_indices) != len(self.dic_categories):
            self.dic_indices = [[0, 0] for _ in self.dic_categories] # offset, choice
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
        self.dic    = self.inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]

    def run(self):   
        
        # Update dictionaries and create cursors
        self.update_data()
        
        # Handle keystrokes
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # >>PLAY GAME<<
                if (event.key in pyg.key_BACK) or (event.key in pyg.key_HOLD):
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay = None
                        return
                
                # >>LOCK SELECTION<<
                elif (event.key in pyg.key_INV) and (time.time()-self.last_press_time > self.cooldown_time):
                    self.last_press_time = float(time.time())
                    
                    if not self.locked:
                        self.cursor_border = pygame.Surface((32, 32)).convert()
                        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))
                        self.locked = True
                        pygame.draw.polygon(self.cursor_border, pyg.white, [(0, 0), (30, 0), (30, 30), (0, 30)], 2)
                    else:
                        self.cursor_border = pygame.Surface((32, 32)).convert()
                        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))
                        self.locked = False
                        pygame.draw.polygon(self.cursor_border, pyg.white, [(0, 0), (31, 0), (31, 31), (0, 31)], 1)
                
                # >>NAVIGATE DICTIONARY<<
                elif event.key in pyg.key_UP:
                    
                    # Selection
                    if not self.locked:
                        self.choice -= 1
                        if self.cursor_pos[1] == 32: self.offset -= 1
                        else: self.cursor_pos[1] -= pyg.tile_height
                    else: player_obj.ent.move(0, -pyg.tile_height)
                
                elif event.key in pyg.key_DOWN:
                    if not self.locked:
                        self.choice += 1
                        if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
                        else: self.cursor_pos[1] += pyg.tile_height
                    else: player_obj.ent.move(0, pyg.tile_height)
                
                # >>DETAILS<<
                elif event.key in pyg.key_QUEST:
                    if not self.detail: self.detail = True
                    else:               self.detail = False
                
                # >>CHANGE DICTIONARY<<
                elif (event.key in pyg.key_LEFT) or (event.key in pyg.key_RIGHT):
                
                    if event.key in pyg.key_LEFT:
                        if not self.locked: self.dic_index -= 1
                        else:               player_obj.ent.move(-pyg.tile_height, 0)
                    
                    elif event.key in pyg.key_RIGHT:
                        if not self.locked: self.dic_index += 1
                        else:               player_obj.ent.move(pyg.tile_width, 0)
                    
                    self.dic    = self.inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                    self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                    self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
                    self.choice = self.cursor_pos[1]//32 + self.offset - 1
                    
                    # Move cursor to the highest spot in the dictionary
                    if self.cursor_pos[1] > 32*len(self.dic):
                        self.cursor_pos[1] = 32*len(self.dic)
                        self.choice = len(self.dic) - self.offset - 1
                    
                # >>CONSTRUCTION<<
                elif event.key in pyg.key_DEV:
                    pyg.overlay = 'dev'
                    pygame.event.clear()
                    return
                
                # >>USE OR DROP<<
                else:
                    if event.key in pyg.key_ENTER:
                        self.activate('use')
                    elif event.key in pyg.key_PERIOD:
                        self.activate('drop')
                        self.update_data()

            # Save for later reference
            self.dic_indices[self.dic_index%len(self.dic_indices)][0] = self.offset
            self.dic_indices[self.dic_index%len(self.dic_indices)][1] = self.choice
        return

    def find_item(self, offset=None):
        
        # Retrieve inventory list
        outer_list = list(player_obj.ent.inventory.items())
        length = len(outer_list)
        filter_empty = []
        
        # Remove names without objects
        for i in range(length):
            if outer_list[i][1]: filter_empty.append(outer_list[i])
        
        # Name and list of objects for the selected category
        outer_key, inner_list = filter_empty[self.dic_index%len(filter_empty)]
        
        # Remove hidden items
        filtered_list = [item for item in inner_list if not item.hidden]
        
        # Select the item
        if filtered_list:
            
            if type(offset) == int: item = filtered_list[offset]
            else: item = filtered_list[self.choice%len(filtered_list)]
            return item

    def activate(self, action):
        
        # Use item
        item = self.find_item()
        if action == 'use':
            item.use()
            return
        elif action == 'drop':
            item.drop()
            if self.cursor_pos[1] >= 32*len(self.dic):
                self.cursor_pos[1] = 32*(len(self.dic)-1)
                self.choice = len(self.dic) - self.offset - 2
            return
        
        # Return to game
        pyg.overlay = None
        return

    def render(self):
        pyg.message_height = 1
        pyg.update_gui()
        render_all()
        
        pyg.screen.blit(self.cursor_fill,   self.cursor_pos)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                items_list = list(self.dic.keys())
                item_name  = items_list[(i+self.offset)%len(self.dic)]
                item       = self.find_item(offset=(i+self.offset)%len(self.dic))
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    
                    if item:
                        if item.equipped: detail = '(equipped)'
                        else:             detail = ''
                    else:                 detail = ''
                    
                    self.menu_choices = [item_name, detail]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, pyg.dark_gray))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.screen.blit(menu_choice_surface, (40, Y_detail))
                        Y_detail += 12
                
                # Render image
                pyg.screen.blit(self.dic[item_name], (0, Y))
                Y += pyg.tile_height
                counter += 1                
                
            else: break
        pyg.screen.blit(self.cursor_border, self.cursor_pos)

class Hold:
    
    def __init__(self):
        
        # Data for select_item and locked_item
        self.cursor_pos = [0, 32]
        self.dic_index = 0
        self.locked = False
        self.img_names = ['null', 'null']
        self.img_x = 0
        self.img_y = 0
        self.dic_indices = [[0, 0]]
        
        self.sequence_toggle = False
        self.key_sequence = []
        self.test_sequence_1 = [pyg.key_LEFT, pyg.key_RIGHT]
        self.test_sequence_2 = [pyg.key_LEFT, pyg.key_RIGHT]
        self.keys = pyg.key_LEFT + pyg.key_DOWN + pyg.key_RIGHT
        
        self.detail = True

    def run(self):   
        
        # Generate cursor and dictionaries
        self.update_data()
        
        # Handle keystrokes
        for event in pygame.event.get():
            
            # Wait for sequence
            if event.type == pygame.KEYDOWN:
                
                ## >>SEQUENCE<<
                if event.key in pyg.key_HOLD:
                    self.sequence_toggle = True
                if self.sequence_toggle and (event.key in self.keys):                        
                    self.key_sequence.append(event.key)
                    
                    # Restrict to three cached values
                    if len(self.key_sequence) > 3: self.key_sequence.pop(0)
                
                # >>DETAILS<<
                elif event.key in pyg.key_QUEST:
                    if not self.detail: self.detail = True
                    else:               self.detail = False
                
                # >>NAVIGATE DICTIONARY<<
                elif event.key in pyg.key_MINUS:
                    
                    self.choice -= 1
                    if self.cursor_pos[1] == 32: self.offset -= 1
                    else:                        self.cursor_pos[1] -= pyg.tile_height
                
                elif event.key in pyg.key_PLUS:
                    self.choice += 1
                    if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
                    else: self.cursor_pos[1] += pyg.tile_height
            
            # Return to game
            elif event.type == pygame.KEYUP:
                if event.key in pyg.key_HOLD:
                    self.sequence_toggle = False
                    pyg.overlay = None
                    return
            
            # Trigger an event
            elif len(self.key_sequence) == 3:
                sequence_string = ''
                for key in self.key_sequence:
                    if key in pyg.key_LEFT:    sequence_string += '⮜'
                    elif key in pyg.key_DOWN:  sequence_string += '⮟'
                    elif key in pyg.key_RIGHT: sequence_string += '⮞'
                    elif key in pyg.key_UP:    sequence_string += '⮝'
                self.check_sequence(sequence_string)
                self.key_sequence = []

        pyg.overlay = 'hold'
        return

    def update_data(self):
        
        # Restrict keystroke speed
        mech.movement_speed(toggle=False, custom=2)
        
        # Initialize cursor
        if bool(self.locked): size, width, alpha = 30, 2, 192
        else:                 size, width, alpha = 31, 1, 128
        self.cursor_border = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)
        
        # Initialize tile selection
        inventory_dics      = {'effects': {}}
        self.dic_categories = ['effects']
        self.sequences      = {}
        for effect in player_obj.ent.effects:
            inventory_dics['effects'][effect.img_names[1]] = img.dict[effect.img_names[0]][effect.img_names[1]]
            self.sequences[effect.img_names[1]] = effect.sequence
        for key, value in inventory_dics.items():
            if not value: self.dic_categories.remove(key)
        
        # Restore last selection
        if len(self.dic_indices) != len(self.dic_categories):
            self.dic_indices = [[0, 0] for _ in self.dic_categories] # offset, choice
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
        self.dic = inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]

    def check_sequence(self, sequence_string):
        
        # Look through item effects
        for effect in player_obj.ent.effects:
            if effect.sequence == sequence_string:
                if time.time()-effect.last_press_time > effect.cooldown_time:
                    effect.last_press_time = float(time.time())
                    effect.function()
                    return

    def render(self):
        pyg.message_height = 1
        pyg.update_gui()
        render_all()
        
        pyg.screen.blit(self.cursor_fill,   self.cursor_pos)
        pyg.screen.blit(self.cursor_border, self.cursor_pos)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                effects_list = list(self.dic.keys())
                effect_name  = effects_list[(i+self.offset)%len(self.dic)]
                
                # Render details
                if self.detail:
                    Y_cache = int(Y)

                    self.menu_choices = [effect_name, self.sequences[effect_name]]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, pyg.dark_gray))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.screen.blit(menu_choice_surface, (40, Y_cache))
                        Y_cache += 12
                
                # Render image
                pyg.screen.blit(self.dic[effect_name], (0, Y))
                Y += pyg.tile_height
                counter += 1
            
            else: break
        pyg.screen.blit(self.cursor_border, self.cursor_pos)

class Trade:

    def __init__(self):
        
        # Data for select_item and locked_item
        self.cursor_pos_bnm = [pyg.screen_width-pyg.tile_width, 32]
        self.dic_index_bnm = 0
        self.dic_categories_bnm = img.other_names[:-1]
        self.dic_indices_bnm = [[0, 0] for _ in self.dic_categories_bnm] # offset, choice
        self.img_names_bnm = ['null', 'null']
        self.img_x_bnm = 0
        self.img_y_bnm = 0
        
        # Data for select_item and locked_item
        self.cursor_pos = [0, 32]
        self.dic_index = 0
        self.img_names = ['null', 'null']
        self.img_x = 0
        self.img_y = 0
        self.dic_indices = [[0, 0]]
        
        self.detail = True
        self.cooldown_time = 0.1
        self.last_press_time = 0
        
        self.menu_toggle = 'right'
        self.ent         = None

        ## Cursors
        # Left cursor
        size, width, alpha = 30, 2, 192
        self.cursor_border = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)
        
        # Right cursor
        self.cursor_border_bnm = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill_bnm   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill_bnm.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border_bnm, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)

    def update_data(self):
        
        # Restrict movement speed
        mech.movement_speed(toggle=False, custom=2)
        
        ## Dictionaries
        # Left dictionary
        self.inventory_dics = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        for key, value in player_obj.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics[key][item.name] = [img.dict[item.img_names[0]][item.img_names[1]], item]
        self.inv_dics = {}
        for key, value in self.inventory_dics.items():
            if value: self.inv_dics[key] = value
        
        # Right dictionary
        self.inventory_dics_bnm = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        for key, value in self.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics_bnm[key][item.name] = [img.dict[item.img_names[0]][item.img_names[1]], item]
        self.inv_dics_bnm = {}
        for key, value in self.inventory_dics_bnm.items():
            if value: self.inv_dics_bnm[key] = value
        
        ## Selection
        # Left selection restoration
        if len(self.dic_indices) != len(self.inv_dics):
            self.dic_indices = [[0, 0] for _ in self.inv_dics] # offset, choice
        
        # Quit if the inventory is empty
        if self.dic_indices:
            self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
            self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]%len(self.inv_dics)
            self.dic    = self.inv_dics[list(self.inv_dics.keys())[self.dic_index%len(self.inv_dics)]]
        else:
            pyg.overlay = None
            return
        
        # Right selection restoration
        if len(self.dic_indices_bnm) != len(self.inv_dics_bnm):
            self.dic_indices_bnm = [[0, 0] for _ in self.inv_dics_bnm] # offset, choice
        
        # Quit if the inventory is empty
        if self.dic_indices_bnm:
            self.offset_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0]
            self.choice_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1]%len(self.inv_dics_bnm)
            self.dic_bnm    = self.inv_dics_bnm[list(self.inv_dics_bnm.keys())[self.dic_index_bnm%len(self.inv_dics_bnm)]]
        else:
            pyg.overlay = None
            return

    def run(self):   
        
        # Update dictionaries and create cursors
        self.update_data()
        
        if self.menu_toggle == 'right':
            self.dic_jkl           = self.dic_bnm
            self.choice_jkl        = self.choice_bnm
            self.cursor_pos_jkl    = self.cursor_pos_bnm
            self.offset_jkl        = self.offset_bnm
            self.dic_index_jkl     = self.dic_index_bnm
            self.dic_indices_jkl   = self.dic_indices_bnm
            self.inv_dics_jkl      = self.inv_dics_bnm
            self.owner             = self.ent
            self.recipient         = player_obj.ent
            self.cursor_fill_jkl   = self.cursor_fill_bnm
            self.cursor_border_jkl = self.cursor_border_bnm
        else:
            self.dic_jkl           = self.dic
            self.choice_jkl        = self.choice
            self.cursor_pos_jkl    = self.cursor_pos
            self.offset_jkl        = self.offset
            self.dic_index_jkl     = self.dic_index
            self.dic_indices_jkl   = self.dic_indices
            self.inv_dics_jkl      = self.inv_dics
            self.owner             = self.ent
            self.recipient         = player_obj.ent
            self.cursor_fill_jkl   = self.cursor_fill
            self.cursor_border_jkl = self.cursor_border
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                ## >>PLAY GAME<<
                if (event.key in pyg.key_BACK) or (event.key in pyg.key_HOLD):
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay = None
                        return
                
                ## >>SWITCH<<
                elif event.key in pyg.key_INV: self.menu_toggle = 'left'
                elif event.key in pyg.key_DEV: self.menu_toggle = 'right'    
                
                ## >>NAVIGATE DICTIONARY<<
                elif event.key in pyg.key_UP:
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        self.choice_bnm = (self.choice_bnm - 1)%len(self.dic_bnm)
                        if self.cursor_pos_bnm[1] == 32: self.offset_bnm -= 1
                        else: self.cursor_pos_bnm[1] -= pyg.tile_height
                    
                    # Navigate player's inventory
                    else:
                        self.choice = (self.choice - 1)%len(self.dic)
                        if self.cursor_pos[1] == 32: self.offset -= 1
                        else: self.cursor_pos[1] -= pyg.tile_height
                
                elif event.key in pyg.key_DOWN:
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        self.choice_bnm = (self.choice_bnm + 1)%len(self.dic_bnm)
                        if self.cursor_pos_bnm[1] >= (min(len(self.dic_bnm), 12) * 32): self.offset_bnm += 1
                        else: self.cursor_pos_bnm[1] += pyg.tile_height
                    
                    # Navigate player's inventory
                    else:
                        self.choice = (self.choice + 1)%len(self.dic)
                        if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
                        else: self.cursor_pos[1] += pyg.tile_height
                
                ## >>CHANGE DICTIONARY<<
                elif (event.key in pyg.key_LEFT) or (event.key in pyg.key_RIGHT):
                
                    if event.key in pyg.key_LEFT:
                        if self.menu_toggle == 'right': self.dic_index_bnm = (self.dic_index_bnm - 1)%len(self.dic_indices_bnm)
                        else:                           self.dic_index     = (self.dic_index - 1)%len(self.dic_indices)
                    
                    elif event.key in pyg.key_RIGHT:
                        if self.menu_toggle == 'right': self.dic_index_bnm = (self.dic_index_bnm + 1)%len(self.dic_indices_bnm)
                        else:                           self.dic_index     = (self.dic_index + 1)%len(self.dic_indices)
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        if self.dic_indices_bnm:
                            self.dic_bnm    = self.inv_dics_bnm[list(self.inv_dics_bnm.keys())[self.dic_index_bnm%len(self.inv_dics_bnm)]]
                            self.offset_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0]
                            self.choice_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1]%len(self.dic_bnm)
                            self.choice_bnm = (self.cursor_pos_bnm[1]//32 + self.offset_bnm - 1)%len(self.dic_bnm)
                            
                            # Move cursor to the highest spot in the dictionary
                            if self.cursor_pos_bnm[1] > 32*len(self.dic_bnm):
                                self.cursor_pos_bnm[1] = 32*len(self.dic_bnm)
                                self.choice_bnm = (len(self.dic_bnm) - self.offset_bnm - 1)%len(self.dic_bnm)
                        else:
                            pyg.overlay = None
                            return
                    
                    # Navigate player's inventory
                    else:
                        if self.dic_indices:
                            self.dic    = self.inv_dics[list(self.inv_dics.keys())[self.dic_index%len(self.inv_dics)]]
                            self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                            self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]%len(self.dic)
                            self.choice = (self.cursor_pos[1]//32 + self.offset - 1)%len(self.dic)
                            
                            # Move cursor to the highest spot in the dictionary
                            if self.cursor_pos[1] > 32*len(self.dic):
                                self.cursor_pos[1] = 32*len(self.dic)
                                self.choice = (len(self.dic) - self.offset - 1)%len(self.dic)
                        else:
                            pyg.overlay = None
                            return
                
                ## >>DETAILS<<
                elif event.key in pyg.key_QUEST:
                    if not self.detail: self.detail = True
                    else:               self.detail = False
                
                ## >>SELECT<<
                elif event.key in pyg.key_ENTER:
                    self.select()
            
            # Save for later reference
            if self.menu_toggle == 'right':
                if self.dic_indices_bnm:
                    self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0] = self.offset_bnm
                    self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1] = self.choice_bnm
                else:
                    pyg.overlay = None
                    return
            else:
                if self.dic_indices:
                    self.dic_indices[self.dic_index%len(self.dic_indices)][0] = self.offset
                    self.dic_indices[self.dic_index%len(self.dic_indices)][1] = self.choice
                else:
                    pyg.overlay = None
                    return
        
        pyg.overlay = 'trade'
        return

    def select(self):
        """
        dic         : name, surface, and Item object; ex. {'green clothes': [<Surface>, <Item>]}
        offset      : 
        choice      : 
        dic_indices : list of tuples; one tuple for each nonempty pocket; the first entry is 
        dic index   : int between 0 and the number of pockets; increases when 

        """
        
        # Find owner and item
        if self.menu_toggle == 'right':
            owner     = self.ent
            recipient = player_obj.ent
            index     = self.dic_indices_bnm[self.dic_index_bnm%len(self.inv_dics_bnm)][1]
            item      = list(self.dic_bnm.values())[index][1]
        else:
            owner     = player_obj.ent
            recipient = self.ent
            index     = self.dic_indices[self.dic_index%len(self.inv_dics)][1]
            item      = list(self.dic.values())[index][1]
        
        # Trade item
        item.trade(owner, recipient)
        
        # Adjust cursor
        if self.menu_toggle == 'right':
            if self.cursor_pos_bnm[1] >= 32*len(self.dic_bnm):
                self.cursor_pos_bnm[1] = 32*(len(self.dic_bnm)-1)
                self.choice_bnm = len(self.dic_bnm) - self.offset_bnm - 2
        else:
            if self.cursor_pos[1] >= 32*len(self.dic):
                self.cursor_pos[1] = 32*(len(self.dic)-1)
                self.choice = len(self.dic) - self.offset - 2
    
    def find_item(self, ent, offset=None):
        
        if self.menu_toggle == 'right':
            dic_index = self.dic_index_bnm
            choice    = self.choice_bnm
            offset    = self.offset_bnm
        
        else:
            dic_index = self.dic_index
            choice    = self.choice
            offset    = self.offset
        
        # Retrieve inventory list
        outer_list   = list(ent.inventory.items())
        length       = len(outer_list)
        filter_empty = []
        
        # Remove names without objects
        for i in range(length):
            if outer_list[i][1]: filter_empty.append(outer_list[i])
        
        # Name and list of objects for the selected category
        outer_key, inner_list = filter_empty[dic_index%len(filter_empty)]
        
        # Remove hidden items
        filtered_list = [item for item in inner_list if not item.hidden]
        
        # Select the item
        if filtered_list:
            
            try:
                if type(offset) == int: item = filtered_list[offset]
                else: item = filtered_list[choice%len(filtered_list)]
                return item
            except:
                pass

    def render(self):
        pyg.message_height = 1
        pyg.update_gui()
        render_all()
        
        if self.menu_toggle == 'right': pyg.screen.blit(self.cursor_fill_bnm, self.cursor_pos_bnm)
        else:                           pyg.screen.blit(self.cursor_fill,     self.cursor_pos)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                items_list = list(self.dic.keys())
                item_name  = items_list[(i+self.offset)%len(self.dic)]
                item       = self.dic[item_name][1]
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    cost = f"⨋ {item.cost}"
                    self.menu_choices = [item_name, cost]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, pyg.dark_gray))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.screen.blit(menu_choice_surface, (40, Y_detail))
                        Y_detail += 12
                
                # Render image
                pyg.screen.blit(self.dic[item_name][0], (0, Y))
                Y += pyg.tile_height
                counter += 1                
            else: break
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic_bnm))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                items_list = list(self.dic_bnm.keys())
                item_name  = items_list[(i+self.offset_bnm)%len(self.dic_bnm)]
                item       = self.dic_bnm[item_name][1]
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    cost = f"⨋ {item.cost}"
                    self.menu_choices = [item_name, cost]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, pyg.gray))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        X = pyg.screen_width - pyg.tile_width - menu_choice_surface.get_width() - 8
                        pyg.screen.blit(menu_choice_surface,  (X, Y_detail))
                        Y_detail += 12
                
                # Render image
                pyg.screen.blit(self.dic_bnm[item_name][0],  (pyg.screen_width-pyg.tile_width, Y))
                Y += pyg.tile_height
                counter += 1                
            else: break
        
        if self.menu_toggle == 'right': pyg.screen.blit(self.cursor_border_bnm, self.cursor_pos_bnm)
        else:                           pyg.screen.blit(self.cursor_border,     self.cursor_pos)

## Constructions
class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name        : str; identifier for image
            room        : Room object
            entity      : Entity object; entity that occupies the tile
            item        : Item object; entity that occupies the tile
            img_names   : list of strings
            
            X           : int; location of the tile in screen coordinate
            Y           : int; location of the tile in screen coordinate

            blocked     : bool; prevents items and entities from occupying the tile 
            hidden      : bool; prevents player from seeing the tile
            unbreakable : bool; prevents player from changing the tile """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def draw(self, surface):
        
        # Set location
        X = self.X - player_obj.ent.env.camera.X
        Y = self.Y - player_obj.ent.env.camera.Y
        
        # Add shift effect
        if (self.img_names[0] != 'roofs') and (self.img_names[1] != 'wood'):
            image = img.shift(self.img_names, [abs(self.rand_X), abs(self.rand_Y)])
        
        # Draw without effect
        else:
            image = img.dict[self.img_names[0]][self.img_names[1]]
        
        # Animate tiles
        if self.biome in img.biomes['sea']:
            image = img.static(image, offset=20, rate=100)
        
        # Draw result
        surface.blit(image, (X, Y))

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __eq__(self, other):
        return self.X == other.Y and self.Y == other.Y

    def __hash__(self):
        return hash((self.X, self.Y))

class Item:
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            name          : string
            role          : string in ['weapons', 'armor', 'potions', 'scrolls', 'other']
            slot          : string in ['non-dominant hand', 'dominant hand', 'body', 'head', 'face']
            
            X             :
            Y             : 
            
            img_names[0]  : string
            img_names[1]  : string
            
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
        self.X      = None
        self.Y      = None
        
        # Seed a seed for individual adjustments
        self.rand_X = random.randint(-self.rand_set, self.rand_set)
        self.rand_Y = random.randint(0,              self.rand_set)
        
        # Notify code of big object
        self.big = False

    def draw(self, surface):
        """ Draws the object at its position. """
        
        # Blit a tile
        if not self.big:
            
            # Set custom placement
            if self.img_names[0] == 'decor':
                if self.img_names[1] == 'blades': X = self.X - player_obj.ent.env.camera.X - self.rand_X
                else:                             X = self.X - player_obj.ent.env.camera.X
                Y = self.Y - player_obj.ent.env.camera.Y - self.rand_Y
            
            else:
                X = self.X-player_obj.ent.env.camera.X
                Y = self.Y-player_obj.ent.env.camera.Y
        
            # Add effects and draw
            if self.rand_set:
                if (self.img_names[1] in ['tree', 'leafy']) and not self.rand_Y:
                    surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]), (X-32, Y-32))
                else:
                    surface.blit(img.dict[self.img_names[0]][self.img_names[1]], (X, Y))
            else: surface.blit(img.dict[self.img_names[0]][self.img_names[1]], (X, Y))
        
        # Blit multiple tiles
        else:
            
            # Blot every tile in the image
            for i in range(len(img.big)):
                for j in range(len(img.big[0])):
                    X = self.X - player_obj.ent.env.camera.X - pyg.tile_width * i
                    Y = self.Y - player_obj.ent.env.camera.Y - pyg.tile_height * j
                    surface.blit(img.big[len(img.big)-j-1][len(img.big[0])-i-1], (X, Y))

    def pick_up(self, ent=None):
        """ Adds an item to the player's inventory and removes it from the map. """
        
        # Allow for NPC actions
        if not ent: ent = player_obj.ent
        
        if len(ent.inventory) >= 26:
            pyg.update_gui('Your inventory is full, cannot pick up ' + self.name + '.', pyg.dark_gray)
        else:
            
            # Pick up item if possible
            if self.movable:
                
                if self.effect:
                    self.effect
                
                ent.inventory[self.role].append(self)
                sort_inventory(ent)
                ent.tile.item = None
                pyg.update_gui("Picked up " + self.name + ".", pyg.dark_gray)

    def drop(self, ent=None):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at
            the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home. """
        
        # Allow for NPC actions
        if not ent: ent = player_obj.ent
        
        # Prevent dropping items over other items
        if not ent.tile.item:
        
            # Dequip before dropping
            if self in ent.equipment.values():
                self.toggle_equip(ent)
            
            self.X = ent.X
            self.Y = ent.Y
            ent.inventory[self.role].remove(self)
            ent.tile.item = self

    def trade(self, owner, recipient):
        
        # Dequip before trading
        if self in owner.equipment.values():
            self.toggle_equip(owner)
        
        if (owner.wallet - self.cost) > 0:
            
            # Remove from owner
            owner.inventory[self.role].remove(self)
            owner.wallet += self.cost
            
            # Give to recipient
            recipient.inventory[self.role].append(self)
            recipient.wallet -= self.cost
        
        else:
            pyg.update_gui("Not enough cash!", color=pyg.red)

    def use(self, ent=None):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        # Allow for NPC actions
        if not ent: ent = player_obj.ent
        
        # Handle equipment
        if self.equippable: self.toggle_equip(ent)
        
        # Handle items
        elif self.effect:
            
            # Add active effect
            if (self.role == 'player') and (self.role in ['potions', 'weapons', 'armor']):
                ent.effects.append(self.effect)
            
            # Activate the item
            else: self.effect.function()
        
        elif self.role == 'player': pyg.update_gui("The " + self.name + " cannot be used.", pyg.dark_gray)

    def toggle_equip(self, ent):
        """ Toggles the equip/unequip status. """
        
        if not ent: ent = player_obj.ent
        if self.equipped: self.dequip(ent)
        else:             self.equip(ent)

    def equip(self, ent):
        """ Unequips object if the slot is already being used. """
        
        # Check if anything is already equipped
        if ent.equipment[self.slot] is not None:
            ent.equipment[self.slot].dequip(ent)
        
        # Apply stat adjustments
        ent.equipment[self.slot] = self
        ent.max_hp  += self.hp_bonus
        ent.attack  += self.attack_bonus
        ent.defense += self.defense_bonus
        if self.effect: ent.effects.append(self.effect)
        
        self.equipped = True

        if ent.role == 'player':
            if not self.hidden:
                pyg.update_gui('Equipped ' + self.name + ' on ' + self.slot + '.', pyg.dark_gray)

    def dequip(self, ent):
        """ Unequips an object and shows a message about it. """
        
        # Update player
        player_obj.ent.equipment[self.slot] = None
        player_obj.ent.attack  -= self.attack_bonus
        player_obj.ent.defense -= self.defense_bonus
        player_obj.ent.max_hp  -= self.hp_bonus
        if player_obj.ent.hp > player_obj.ent.max_hp: 
            player_obj.ent.hp = player_obj.ent.max_hp 
        if self.effect:
            player_obj.ent.effects.remove(self.effect)
        
        self.equipped = False
        
        if self.role == 'player':
            if not self.hidden:
                pyg.update_gui('Dequipped ' + self.name + ' from ' + self.slot + '.', pyg.dark_gray)

    def __getstate__(self):
        state = self.__dict__.copy()
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
            X              : int; horizontal position in screen coordinates
            Y              : int; vertical position in screen coordinates
            X0             : int; initial horizontal position
            Y0             : int; initial vertical position
            reach          : int or None; number of tiles the entity can move from its initial position

            inventory      : list of Item objects
            equipment      : list of Item objects
            death          : 
            follow         : bool or Entity object; sets entity as follower
            aggression     : int; toggles attack functions
            dialogue       : list or tuple of strings; quest or general dialogue """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Images
        self.direction   = self.img_names[1]
        self.handedness  = 'left'

        # Location
        self.env        = None
        self.last_env   = None
        self.tile       = None
        self.prev_tile  = None
        self.X          = 0
        self.Y          = 0
        self.X0         = 0
        self.Y0         = 0
        self.vicinity   = []

        # Movement
        self.cooldown   = 0.25
        self.last_press = 0
        
        # Mechanics
        self.dead       = False
        self.dialogue   = None
        self.default_dialogue = []
        self.quest      = None
        self.wallet     = 5
        self.trader     = False
        self.inventory  = {'weapons': [], 'armor': [],  'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
        self.equipment  = {'head': None,  'face': None, 'chest': None, 'body': None,  'dominant hand': None, 'non-dominant hand': None}
        self.effects    = [Effect(
            name          = 'suicide',
            img_names     = ['decor', 'bones'],
            function      = mech.suicide,
            sequence      = '⮟⮟⮟',
            cooldown_time = 1)]
        
        # Randomizer
        self.rand_X = random.randint(-pyg.tile_width,  pyg.tile_width)
        self.rand_Y = random.randint(-pyg.tile_height, pyg.tile_height)

    def ai(self):
        """ Preset movements. """
        
        # Only allow one motion
        moved = False
        
        if not self.dead:
            if time.time()-self.last_press > self.cooldown:
                self.last_press = float(time.time())
                distance = self.distance_to(player_obj.ent)
                
                # Flee
                if self.fear and (type(self.fear) == int):
                    if not random.randint(0, self.lethargy//10):
                        self.move_towards(self.X0, self.Y0)
                        self.fear -= 1
                        if self.fear < 0: self.fear = 0
                
                # Follow or idle
                elif self.follow and (distance < 320):
                    if not random.randint(0, self.lethargy//2):
                        self.move_towards(player_obj.ent.X, player_obj.ent.Y)
                
                    # Attack if close and aggressive; chance based on miss_rate
                    if self.aggression:
                        if (distance < 64) and not random.randint(0, self.miss_rate):
                            self.attack_target(player_obj.ent)
                
                # Attack or move if aggressive
                elif self.aggression and (player_obj.ent.hp > 0):
                    
                    # Attack if close and aggressive; chance based on miss_rate
                    if (distance < 64) and not random.randint(0, self.miss_rate):
                        self.attack_target(player_obj.ent)
                    
                    # Move towards the player if distant; chance based on lethargy
                    elif (distance < self.aggression*pyg.tile_width) and not random.randint(0, self.lethargy//2) and not moved:
                        self.move_towards(player_obj.ent.X, player_obj.ent.Y)
                
                # Idle if not following or aggressive
                else:
                    if self.role != 'player': self.idle()

    def idle(self):
        """ Randomly walks around """
        
        # Choose direction
        if random.randint(0, 1):
            dX = random.randint(-1, 1) * pyg.tile_width
            dY = 0
        else:
            dX = 0
            dY = random.randint(-1, 1) * pyg.tile_width
        
        # Move
        if self.distance_new([self.X+dX, self.Y+dY], [self.X0, self.Y0]) <= self.reach:
            if   (dX < 0) and (self.img_names[1] == 'left'):  chance = 5
            elif (dX > 0) and (self.img_names[1] == 'right'): chance = 5
            elif (dY < 0) and (self.img_names[1] == 'back'):  chance = 5
            elif (dY > 0) and (self.img_names[1] == 'front'): chance = 5
            else:                                             chance = 1
            if not random.randint(0, self.lethargy//chance):
                self.move(dX, dY)

    def move(self, dX, dY):
        """ Moves the player by the given amount if the destination is not blocked.
            May activate any of the following:
            - motion
            - floor effects
            - dialogue
            - combat
            - digging """
        
        # Determine direction
        if   dY > 0: self.direction = 'front'
        elif dY < 0: self.direction = 'back'
        elif dX < 0: self.direction = 'left'
        elif dX > 0: self.direction = 'right'
        else:        self.direction = random.choice(['front', 'back', 'left', 'right'])
        
        # Change orientation before moving
        if self.img_names[1] != self.direction:
            if self.img_names[1]: self.img_names[1] = self.direction
        else:
            
            # Find new position
            x = int((self.X + dX)/pyg.tile_width)
            y = int((self.Y + dY)/pyg.tile_height)
            
            # Move player
            if self.role == 'player': self.move_player(x, y, dX, dY)
            
            # Move pet
            if self.img_names[0] == 'radish': self.move_pet(x, y, dX, dY)
            
            # Move NPC or enemy
            else:
                if not is_blocked(self.env, [x, y]):
                    
                    # Keep the entity in its native habitat
                    if self.env.map[x][y].biome in img.biomes[self.habitat]:
                        
                        if self.env.map[x][y].item and self.role == 'enemy':
                            if self.env.map[x][y].item.img_names[0] != 'stairs':
                                self.X          += dX
                                self.Y          += dY
                                self.tile.entity = None
                                player_obj.ent.env.map[x][y].entity = self
                                self.tile        = player_obj.ent.env.map[x][y]
                        
                        else:
                            self.X          += dX
                            self.Y          += dY
                            self.tile.entity = None
                            player_obj.ent.env.map[x][y].entity = self
                            self.tile        = player_obj.ent.env.map[x][y]

    def move_player(self, x, y, dX, dY):
        """ Annex of move() for player actions. """
        
        # Move forwards
        if not is_blocked(self.env, [x, y]):
            
            # Move player and update map
            self.prev_tile              = self.env.map[int(self.X/pyg.tile_width)][int(self.Y/pyg.tile_height)]
            self.X                      += dX
            self.Y                      += dY
            self.tile.entity            = None
            self.env.map[x][y].entity   = self
            self.tile                   = self.env.map[x][y]
            self.env.player_coordinates = [x, y]
            check_tile(x, y)
            
            # Trigger floor effects
            if self.env.map[x][y].item:
                if self.env.map[x][y].item.effect:
                    floor_effects(self.env.map[x][y].item.effect.name)
            
            # Check stamina
            if (mech.movement_speed_toggle == 1) and (self.stamina > 0):
                self.stamina -= 1/2
                pyg.update_gui()
        
        # Interact with an entity
        elif self.env.map[x][y].entity:
            ent = self.env.map[x][y].entity
            
            # Talk to the entity
            if ent.dialogue or ent.default_dialogue:
                
                # Quest dialogue
                if ent.dialogue: dialogue = ent.dialogue
                
                # Idle chat and trading
                else:
                    
                    # Idle chat
                    dialogue = random.choice(ent.default_dialogue)
                    
                    # Trading
                    if ent.trader:
                        trade_obj.ent = ent
                        pyg.overlay = 'trade'
                
                # Play speech and update quests
                if time.time() - aud.last_press_time_speech > aud.speech_speed//100:
                    pyg.update_gui(dialogue, pyg.white)
                    aud.play_speech(dialogue)
                    if ent.dialogue:
                        ent.dialogue = ent.quest.dialogue(ent)
            
            # Make them flee
            elif type(ent.fear) == int: ent.fear += 30
            
            # Attack the entity
            elif self.env.name != 'home': self.attack_target(ent)
        
        # Dig a tunnel
        elif self.equipment['dominant hand'] is not None:
            if self.equipment['dominant hand'].name in ['shovel', 'super shovel']:
                # Move player and reveal tiles
                if self.X >= 64 and self.Y >= 64:
                    if super_dig or not self.env.map[x][y].unbreakable:
                        self.env.create_tunnel(x, y)
                        self.prev_tile                 = self.env.map[int(self.X/pyg.tile_width)][int(self.Y/pyg.tile_height)]
                        self.X                         += dX
                        self.Y                         += dY
                        self.tile.entity               = None
                        self.env.map[x][y].blocked     = False
                        self.env.map[x][y].unbreakable = False
                        self.env.map[x][y].img_names   = self.env.floors
                        self.env.map[x][y].entity      = self
                        self.tile                      = self.env.map[x][y]
                        self.env.player_coordinates    = [x, y]
                        check_tile(x, y)
                    else:
                        pyg.update_gui('The shovel strikes the wall but does not break it.', pyg.dark_gray)
                    
                    # Update durability
                    if self.equipment['dominant hand'].durability <= 100:
                        self.equipment['dominant hand'].durability -= 1
                    if self.equipment['dominant hand'].durability <= 0:
                        self.equipment['dominant hand'].drop()
                        self.tile.item = None # removes item from world
        
        self.env.camera.update() # omit this if you want to modulate when the camera focuses on the player

    def move_pet(self, x, y, dX, dY):
        
        # Move forwards
        if not is_blocked(self.env, [x, y]):
            
            # Move and update map
            self.X                      += dX
            self.Y                      += dY
            self.tile.entity            = None
            player_obj.ent.env.map[x][y].entity   = self
            self.tile                   = self.env.map[x][y]
            
        # Trigger floor effects
        if self.env.map[x][y].item:
            if self.env.map[x][y].item.effect:
                self.env.map[x][y].item.effect.function(self)

    def move_towards(self, target_X, target_Y):
        """ Moves object towards target. """
        
        dX       = target_X - self.X
        dY       = target_Y - self.Y
        distance = (dX ** 2 + dY ** 2)**(1/2)
        if distance:
            
            if dX and not dY:
                dX = round(dX/distance) * pyg.tile_width
                dY = 0
            
            elif dY and not dX:
                dX = 0
                dY = round(dX/distance) * pyg.tile_width
            
            elif dX and dY:
                if random.randint(0, 1):
                    dX = round(dX/distance) * pyg.tile_width
                    dY = 0
                else:
                    dX = 0
                    dY = round(dY/distance) * pyg.tile_width
            
            self.move(dX, dY)

    def distance_to(self, other):
        """ Returns the distance to another object. """
        
        if type(other) in [tuple, list]:
            dX = other[0] - self.X
            dY = other[1] - self.Y
        else:
            dX = other.X - self.X
            dY = other.Y - self.Y
        return (dX ** 2 + dY ** 2)**(1/2)

    def distance(self, X, Y):
        """ Returns the distance to some coordinates. """
        
        return ((X - self.X) ** 2 + (Y - self.Y) ** 2)**(1/2)

    def distance_new(self, loc_1, loc_2):
        return ((loc_2[0] - loc_1[0]) ** 2 + (loc_2[1] - loc_1[1]) ** 2)**(1/2)

    def get_vicinity(self):
        (x, y) = self.X//pyg.tile_width, self.Y//pyg.tile_width
        self.vicinity = [
            self.env.map[x-1][y-1], self.env.map[x][y-1], self.env.map[x+1][y-1],
            self.env.map[x-1][y],                         self.env.map[x+1][y],
            self.env.map[x-1][y+1], self.env.map[x][y+1], self.env.map[x+1][y+1]]
        return self.vicinity

    def attack_target(self, target):
        """ Calculates and applies attack damage. """
        
        if self.name != target.name:
            damage = self.attack - target.defense
            if damage > 0:
                pyg.update_gui(self.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', pyg.red)
                target.take_damage(damage)
            elif self.role != 'player':
                pyg.update_gui(self.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!', pyg.red)
        return

    def take_damage(self, damage):
        """ Applies damage if possible. """
        
        if damage > 0:
            
            # Apply damage
            self.hp -= damage
            
            # Damage animation
            img.entity_flash(self)
            
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
            player_obj.ent.dead        = True
            player_obj.ent.tile.entity = None
            
            item = create_item('skeleton')
            item.name = f"the corpse of {self.name}"
            place_object(item, [self.X//pyg.tile_width, self.Y//pyg.tile_height], self.env)
            pygame.event.clear()
        
        else:
            pyg.update_gui('The ' + self.name + ' is dead! You gain ' + str(self.exp) + ' experience points.', pyg.red)
            self.dead        = True
            self.role        = 'corpse'
            self.tile.entity = None
            self.env.entities.remove(self)
            if self in player_obj.ent.env.entities: player_obj.ent.env.entities.remove(self)
            
            if not self.tile.item:
                item = create_item('bones')
                item.name = f"the corpse of {self.name}"
                place_object(item, [self.X//pyg.tile_width, self.Y//pyg.tile_height], self.env)
            del self

            pygame.event.get()
        pygame.event.clear()

    def heal(self, amount):
        """ Heals player by the given amount without going over the maximum. """
        
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def draw(self, surface, loc=None):
        """ Draws the object at its position.

            Parameters
            ----------
            surface : pygame image
            loc     : list of int; screen coordinates """
        
        # Used without reference to an environment
        if loc:
            X = loc[0]
            Y = loc[1]
        else:
            X = self.X - self.env.camera.X
            Y = self.Y - self.env.camera.Y
        
        # Swimming
        if self.tile.biome in img.biomes['sea']: swimming = True
        else:                                    swimming = False
        
        # Blit skin
        if self.handedness == 'left': 
            if swimming: surface.blit(img.halved([self.img_names[0], self.img_names[1]]), (X, Y))
            else:        surface.blit(img.dict[self.img_names[0]][self.img_names[1]],     (X, Y))
        
        # Blit flipped skin
        else:
            if swimming: surface.blit(img.halved([self.img_names[0], self.img_names[1]], flipped=True), (X, Y))
            else:        surface.blit(img.flipped.dict[self.img_names[0]][self.img_names[1]],           (X, Y))
        
        # Blit chest
        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'chest':
                    if self.handedness == 'left':
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]]), (X, Y))
                        else:        surface.blit(img.dict[item.img_names[0]][self.img_names[1]],     (X, Y))
                    else:
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                        else:        surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                else: pass

        # Blit armor
        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'body':
                    if self.handedness == 'left':
                        if swimming:          surface.blit(img.halved([item.img_names[0], self.img_names[1]]),        (X, Y))
                        elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]), (X, Y))
                        else:                 surface.blit(img.dict[item.img_names[0]][self.img_names[1]],            (X, Y))
                    else:
                        if swimming:          surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                        elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]), (X, Y))
                        else:                 surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                else: pass

        # Blit face
        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'face':
                    if self.handedness == 'left':
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]]), (X, Y))
                        else:        surface.blit(img.dict[item.img_names[0]][self.img_names[1]],     (X, Y))
                    else:
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                        else:        surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                else: pass
        
        # Blit hair
        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'head':
                    if self.handedness == 'left':
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]]), (X, Y))
                        else:        surface.blit(img.dict[item.img_names[0]][self.img_names[1]],     (X, Y))
                    else:
                        if swimming: surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                        else:        surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                else: pass
        
        # Blit weapons and shields
        for item in self.equipment.values():
            if item is not None:
                if item.role in ['weapons', 'armor']:
                    if item.slot in ['dominant hand', 'non-dominant hand']:
                        if self.handedness == 'left':
                            if swimming:          surface.blit(img.halved([item.img_names[0], self.img_names[1]]),               (X, Y))
                            elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]), (X, Y))
                            else:                 surface.blit(img.dict[item.img_names[0]][self.img_names[1]],                   (X, Y))
                        else:
                            if swimming:          surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                            elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]), (X, Y))
                            else:                 surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                    else: pass
        
        # Blit dialogue bubble
            if self.dialogue: pyg.display.blit(img.dict['decor']['bubble'], (X, Y-pyg.tile_height))

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

class Environment:
    """ Generates and manages each world, such as each floor of the dungeon. """
    
    def __init__(self, name, size, soundtrack, lvl_num, walls, floors, roofs, blocked=True, hidden=True, img_names=['', '']):
        """ Environment parameters
            ----------------------
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
        
        # Identity
        self.name       = name
        self.lvl_num    = lvl_num
        self.size       = size
        self.soundtrack = soundtrack
        
        # Images and rooms
        self.walls  = walls
        self.floors = floors
        self.roofs  = roofs
        self.rooms  = []
        
        # Generate map tiles
        self.map = []
        X_range  = [0, self.size * pyg.screen_width]
        Y_range  = [0, self.size * pyg.screen_height]
        for X in range(X_range[0], X_range[1]+1, pyg.tile_width):
            row = [] 
            for Y in range(Y_range[0], Y_range[1]+1, pyg.tile_height):
                
                # Handle edges
                if (X in X_range) or (Y in Y_range):
                    tile = Tile(
                        name        = None,
                        room        = None,
                        entity      = None,
                        item        = None,
                        
                        img_names   = img_names,
                        walls       = walls,
                        floor       = floors,
                        roof        = roofs,
                        
                        X           = X,
                        Y           = Y,
                        rand_X      = random.randint(-pyg.tile_width, pyg.tile_width),
                        rand_Y      = random.randint(-pyg.tile_height, pyg.tile_height),
                        
                        biome       = None,
                        blocked     = True,
                        hidden      = hidden,
                        unbreakable = True)
                
                # Handle bulk
                else:
                    tile = Tile(
                        room        = None,
                        entity      = None,
                        item        = None,
                        
                        img_names   = img_names,
                        walls       = walls,
                        floor       = floors,
                        roof        = roofs,
                        
                        X           = X,
                        Y           = Y,
                        rand_X      = random.randint(-pyg.tile_width, pyg.tile_width),
                        rand_Y      = random.randint(-pyg.tile_height, pyg.tile_height),
                        
                        biome       = None,
                        blocked     = blocked,
                        hidden      = hidden,
                        unbreakable = False)
                
                row.append(tile)
            self.map.append(row)
        
        # Other
        self.entities           = []
        self.player_coordinates = [0, 0]
        self.camera             = None
        self.center             = [int(len(self.map)/2), int(len(self.map[0])/2)]

    def create_h_tunnel(self, x1, x2, y, img_set=None):
        """ Creates horizontal tunnel. min() and max() are used if x1 is greater than x2. """
        
        if img_set: img_names = img_set
        else:       img_names = self.floors
        
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked   = False
            self.map[x][y].img_names = img_set
            
            # Remove items and entities
            self.map[x][y].item = None
            if self.map[x][y].entity:
                self.entities.remove(self.map[x][y].entity)
                self.map[x][y].entity = None

    def create_v_tunnel(self, y1, y2, x, img_set=None):
        """ Creates vertical tunnel. min() and max() are used if y1 is greater than y2. """
        
        if img_set: img_names = img_set
        else:       img_names = self.floors
        
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked   = False
            self.map[x][y].img_names = img_set
            
            # Remove items and entities
            self.map[x][y].item = None
            if self.map[x][y].entity:
                self.entities.remove(self.map[x][y].entity)
                self.map[x][y].entity = None

    @debug_call
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
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

class Room:
    """ Defines rectangles on the map. Used to characterize a room. """
    
    def __init__(self, name, env, x1, y1, width, height, hidden, floor, walls, roof, objects, biome):
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

            delete             : bool; mark to be removed from environment """
        
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
        self.tiles_list   = []
        self.walls_list   = []
        self.corners_list = []
        
        # Properties
        self.hidden  = hidden
        self.delete  = False
        self.objects = objects
        
        self.set_tiles()

    def set_tiles(self):

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

## Gameplay    
class Mechanics:
    """ Game parameters. Does not need to be saved. """
    
    def __init__(self):
        
        # Environments
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

        self.level_up_base     = 200
        self.level_up_factor   = 150

        self.torch_radius      = 10
        
        self.movement_speed_toggle = 0
        self.speed_list = [
            ['Default', (250, 150)],
            ['Fast',    (1,   130)],
            ['Fixed',   (0,   0)]]

        self.cooldown_time = 10
        self.last_press_time = 0

    def bowl(self):
        if 'dungeon' not in player_obj.envs.keys(): player_obj.envs['dungeon'] = []
        build_dungeon_level()
        place_player(env=player_obj.envs['dungeon'][-1], loc=player_obj.envs['dungeon'][-1].center)    # mech (bowl)

    @debug_call
    def enter_dungeon(self):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if 'dungeon' not in player_obj.envs.keys(): 
                pyg.update_gui('You step into the darkness.', pyg.dark_gray)
                player_obj.envs['dungeon'] = []
                build_dungeon_level()
            
            # Enter the first dungeon
            if player_obj.ent.env.name != 'dungeon':
                place_player(env=player_obj.envs['dungeon'][0], loc=player_obj.envs['dungeon'][0].center)    # mech (dungeon)
            
            # Enter the next saved dungeon
            elif player_obj.ent.env.lvl_num < len(player_obj.envs['dungeon']):
                lvl_num = player_obj.ent.env.lvl_num
                place_player(env=player_obj.envs['dungeon'][lvl_num], loc=player_obj.envs['dungeon'][lvl_num].center)    # mech (dungeon)
            
            # Enter a new dungeon
            else:
                build_dungeon_level()
                place_player(env=player_obj.envs['dungeon'][-1], loc=player_obj.envs['dungeon'][-1].center)    # mech (dungeon)

    @debug_call
    def enter_cave(self):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
                
            if 'cave' not in player_obj.envs.keys(): 
                pyg.update_gui('The ground breaks beneath you and reveals a cave.', pyg.dark_gray)
                player_obj.envs['cave'] = []
                build_cave_level()
            
            # Enter the first cave
            if player_obj.ent.env.name != 'cave':
                place_player(env=player_obj.envs['cave'][0], loc=player_obj.envs['cave'][0].center)    # mech (cave)
            
            # Enter the next saved cave
            elif player_obj.ent.env.lvl_num < len(player_obj.envs['cave']):
                lvl_num = player_obj.ent.env.lvl_num
                place_player(env=player_obj.envs['cave'][lvl_num], loc=player_obj.envs['cave'][lvl_num].center)    # mech (cave)
            
            # Enter a new cave
            else:
                build_cave_level()
                place_player(env=player_obj.envs['cave'][-1], loc=player_obj.envs['cave'][-1].center)    # mech (cave)

    @debug_call
    def enter_overworld(self):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if 'overworld' not in player_obj.envs.keys(): build_overworld()
            place_player(env=player_obj.envs['overworld'], loc=player_obj.envs['overworld'].center)    # mech (overworld)

    @debug_call
    def enter_home(self):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].player_coordinates)    # mech (home)

    def movement_speed(self, toggle=True, custom=None):
        """ Toggles and sets movement speed. """
        
        # Check stamina
        if player_obj.ent.stamina > 0:
        
            # Change speed
            if toggle:
                if self.movement_speed_toggle == len(self.speed_list)-1: 
                    self.movement_speed_toggle = 0
                else:
                    self.movement_speed_toggle += 1
                pyg.update_gui(f"Movement speed: {self.speed_list[self.movement_speed_toggle][0]}", pyg.dark_gray)
                (hold_time, repeat_time) = self.speed_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Set custom speed
            elif custom is not None:
                (hold_time, repeat_time) = self.speed_list[custom][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Restore previous speed
            else:
                (hold_time, repeat_time) = self.speed_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
        else:
            self.movement_speed_toggle = 0
            (hold_time, repeat_time) = self.speed_list[self.movement_speed_toggle][1]
            pygame.key.set_repeat(hold_time, repeat_time)

    def cast_heal(self):
        """ Heals the player. """
        
        if player_obj.ent.fighter.hp == player_obj.ent.fighter.max_hp:
            pyg.update_gui('You are already at full health.', pyg.dark_gray)
            return 'cancelled'
        pyg.update_gui('Your wounds start to feel better!', pyg.dark_gray)
        player_obj.ent.fighter.heal(mech.heal_amount)

    def cast_lightning(self):
        """ Finds the closest enemy within a maximum range and attacks it. """
        
        monster = closest_monster(mech.lightning_range)
        if monster is None:  #no enemy found within maximum range
            pyg.update_gui('No enemy is close enough to strike.', pyg.dark_gray)
            return 'cancelled'
        pyg.update_gui('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(mech.lightning_damage) + ' hit points.', pyg.red)
        monster.fighter.take_damage(mech.lightning_damage)

    def cast_fireball(self):
        """ Asks the player for a target tile to throw a fireball at. """
        
        pyg.update_gui('Left-click a target tile for the fireball, or right-click to cancel.', pyg.red)
        (X, Y) = target_tile()
        if X is None: return 'cancelled'
        pyg.update_gui('The fireball explodes, burning everything within ' + str(int(mech.fireball_radius/pyg.tile_width)) + ' tiles!', pyg.red)
        for ent in player_obj.ent.env.entities: # Damages every fighter in range, including the player
            if ent.distance(X, Y) <= mech.fireball_radius and ent.fighter:
                pyg.update_gui('The ' + ent.name + ' gets burned for ' + str(mech.fireball_damage) + ' hit points.', pyg.red)
                ent.fighter.take_damage(mech.fireball_damage)

    def cast_confuse(self):
        """ Asks the player for a target to confuse, then replaces the monster's AI with a "confused" one. After some turns, it restores the old AI. """
        
        pyg.update_gui('Left-click an enemy to confuse it, or right-click to cancel.', pyg.red)
        monster = target_monster(mech.confuse_range)
        if monster is None: return 'cancelled'
        old_ai = monster.ai
        monster.ai = ConfusedMonster(old_ai)
        pyg.update_gui('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', pyg.red)

    def swing(self):
        image = img.dict[player_obj.ent.equipment['dominant hand'].img_names[0]]['dropped']
        img.vicinity_flash(player_obj.ent, image)
        for tile in player_obj.ent.get_vicinity():
            if tile.entity:
                player_obj.ent.attack_target(tile.entity)

    def suicide(self):
        
        # Activate animation
        image = img.dict['decor']['bones']
        img.vicinity_flash(player_obj.ent, image)
        img.entity_flash(player_obj.ent)
        
        # Kill player
        player_obj.ent.death()
        return

    def attack_combos(self):
        self.attack_init = pyg.key_BACK
        self.attack_crit = [pyg.key_INFO, pyg.key_EQUIP, pyg.key_DROP]

    def radish_eat(self, ent):
        ent.rank += 1
        image = img.dict['drugs']['bubbles']
        img.flash_above(ent, image)
        ent.tile.item = None

    def boost_stamina(self):
        player_obj.ent.stamina += 50
        if player_obj.ent.stamina > 100: player_obj.ent.stamina = 100
        pyg.update_gui()

class Effect:

    def __init__(self, name, img_names, function, sequence, cooldown_time):
        
        self.name            = name
        self.img_names       = img_names
        self.function        = function # set as a function in Mechanics

        self.sequence        = sequence
        
        self.cooldown_time   = cooldown_time
        self.last_press_time = 0

class Camera:
    """ Defines a camera to follow the player. """
    
    def __init__(self, target):
        """ Defines a camera and its parameters. 
            Parameters
            ----------
            target          : Entity object; focus of camera
            width           : int; translational offset in number of pixels
            height          : int; translational offset in number of pixels
            X               : 
            Y               : 
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
        self.X               = int((self.target.X * pyg.zoom) - int(self.width / 2))
        self.Y               = int((self.target.Y * pyg.zoom) - int(self.height / 2))
        self.center_X        = int(self.X + int(self.width / 2))
        self.center_Y        = int(self.Y + int(self.height / 2))
        self.right           = self.X + self.width
        self.bottom          = self.Y + self.height
        self.tile_map_x      = int(self.X / pyg.tile_width)
        self.tile_map_y      = int(self.Y / pyg.tile_height)
        self.tile_map_width  = int(self.width / pyg.tile_width)
        self.tile_map_height = int(self.height / pyg.tile_height)
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        
        self.fixed           = False
        self.fix_position()

    def update(self):
        """ ? """
        
        if not self.fixed:
            X_move          = int(self.target.X - self.center_X)
            self.X          = int(self.X + X_move)
            self.center_X   = int(self.center_X + X_move)
            self.right      = int(self.right + X_move)
            self.tile_map_x = int(self.X / pyg.tile_width)
            self.x_range    = int(self.tile_map_x + self.tile_map_width)

            Y_move          = int(self.target.Y - self.center_Y)
            self.Y          = int(self.Y + Y_move)
            self.center_Y   = int(self.center_Y + Y_move)
            self.bottom     = int(self.bottom + Y_move)
            self.tile_map_y = int(self.Y / pyg.tile_height)
            self.y_range    = int(self.tile_map_y + self.tile_map_height)
            
            self.fix_position()

    def fix_position(self):
        """ ? """
        if self.X < 0:
            self.X          = 0
            self.center_X   = self.X + int(self.width / 2)
            self.right      = self.X + self.width
            self.tile_map_x = int(self.X / (pyg.tile_width / pyg.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        elif self.right > (len(player_obj.ent.env.map)-1) * pyg.tile_width:
            self.right      = (len(player_obj.ent.env.map)) * pyg.tile_width
            self.X          = self.right - self.width
            self.center_X   = self.X + int(self.width / 2)
            self.tile_map_x = int(self.X / (pyg.tile_width / pyg.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        if self.Y < 0:
            self.Y          = 0
            self.center_Y   = self.Y + int(self.height / 2)
            self.bottom     = (self.Y + self.height) / pyg.zoom
            self.tile_map_y = int(self.Y / (pyg.tile_height / pyg.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height
        
        elif self.bottom > (len(player_obj.ent.env.map[0])) * pyg.tile_height:
            self.bottom     = (len(player_obj.ent.env.map[0])) * pyg.tile_height
            self.Y          = self.bottom - self.height
            self.center_Y   = self.Y + int(self.height / 2)
            self.tile_map_y = int(self.Y / (pyg.tile_height / pyg.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height

    def zoom_in(self, factor=0.1, custom=None):
        """ Zoom in by reducing the camera's width and height. """
        
        # Set to a specific value
        if custom and (pyg.zoom != custom):
            pyg.zoom = custom
            pyg.zoom_cache = pyg.zoom
            pyg.update_gui()
            self.width  = int(pyg.screen_width / pyg.zoom)
            self.height = int(pyg.screen_height / pyg.zoom)
            pyg.display = pygame.Surface((self.width, self.height))
            self._recalculate_bounds()
            
        elif not self.fixed:
            pyg.zoom += factor
            pyg.zoom_cache = pyg.zoom
            pyg.update_gui()
            self.width  = int(pyg.screen_width / pyg.zoom)
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

    def _recalculate_bounds(self):
        """ Recalculate dependent properties after zooming. """
        self.X               = self.target.X - int(self.width / 2)
        self.Y               = self.target.Y - int(self.height / 2)
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

## Quests
class Quest:
    """ Holds quest information. """

    def __init__(self, name, notes, tasks, category, function=None):
        """ name     : string; title of quest
            content  : list of strings; notes and checklists
            category : string in ['main', 'side']; organizes quest priority
            finished : Boolean; notes if the quest has been completed """

        self.name     = name
        self.notes    = notes
        self.tasks    = tasks
        self.category = category
        self.finished = False
        self.ent      = None
        
        self.categories = ['Notes' for i in range(len(notes))]
        self.categories += ['Tasks' for i in range(len(tasks))]
        
        self.function = function

    def dialogue(self, ent):
        """ Sends dialogue from the entity to the quest's function, then updates
            the entity's dialogue if needed. """
        
        message = self.function(ent.dialogue, ent)
        if message:
            return message

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

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
        
        furnishing_a_home   = Quest(name='Furnishing a home',
                                    notes=['My house is empty. Maybe I can spruce it up.'],
                                    tasks=['☐ Use the shovel to build new rooms.',
                                           '☐ Drop items to be saved for later use.',
                                           '☐ Look for anything interesting.'],
                                    category='Side')
        gathering_supplies.content = gathering_supplies.notes + gathering_supplies.tasks
        finding_a_future.content   = finding_a_future.notes + finding_a_future.tasks
        furnishing_a_home.content  = furnishing_a_home.notes + furnishing_a_home.tasks

        self.quests = {
            gathering_supplies.name: gathering_supplies,
            finding_a_future.name:   finding_a_future,
            furnishing_a_home.name:  furnishing_a_home}
        self.update_questlog()

    def back_to_menu(self):
        """ Toggle menus. """
        
        if self.menu_index == 0: self.menu_index += 1
        else:                    self.menu_index  = 0
    
    def update_questlog(self, name=None):
        """ Updates and sorts main quests and side quests. """
        
        # Update quest
        if name:
            quest = self.quests[name]
            
            # Check off task
            if not quest.finished:
                for i in range(len(quest.tasks)):
                    task = quest.tasks[i]
                    if task[0] == "☐":
                        quest.tasks[i] = task.replace("☐", "☑")
                        pyg.update_gui(quest.tasks[i], pyg.violet)
                        quest.content = quest.notes + quest.tasks
                        break
            
            # Remove finished quests
            else:
                quest.tasks[-1] = quest.tasks[-1].replace("☐", "☑")
                pyg.update_gui(quest.tasks[-1], pyg.violet)
                pyg.update_gui(f"Quest complete: {quest.name}", pyg.violet)
                del self.quests[quest.name]

        # Initialize data containers
        self.main_quests = []
        self.side_quests = []
        self.categories  = []
        quests_cache     = {}
        
        # Find main quests
        for quest in self.quests.values():
            if not quest.finished:
                if quest.category == 'Main':
                    quests_cache[quest.name] = quest
                    self.main_quests.append(quest)
                    self.categories.append(quest.category)
        
        # Find side quests
        for quest in self.quests.values():
            if not quest.finished:
                if quest.category == 'Side':
                    quests_cache[quest.name] = quest
                    self.side_quests.append(quest)
                    self.categories.append(quest.category)
        self.quests = quests_cache

    def questlog_menu(self):
        """ Manages menu for quest titles and details. """
        
        # Show list of quests
        if self.menu_index == 0:
        
            # List of quests
            quest_index = new_menu(
                header             = 'Questlog',
                options            = list(self.quests.keys()),
                options_categories = self.categories)
            
            # Description of selected quest
            if type(quest_index) == int:
                self.selected_quest = self.quests[list(self.quests.keys())[quest_index]]
                self.update_questlog()
                
                selected_index = new_menu(
                    header             = self.selected_quest.name,
                    options            = self.selected_quest.content,
                    options_categories = self.selected_quest.categories)
                
                # Go back to list of quests
                if type(selected_index) != int:
                    self.back_to_menu()
        
        # Show description of selected quest
        else:
            
            # Description of selected quest
            selected_index = new_menu(
                header             = self.selected_quest.name,
                options            = self.selected_quest.content,
                options_categories = self.selected_quest.categories)
            
            # Go back to list of quests
            if type(selected_index) == int:
                player_obj.questlog.back_to_menu()

class QuestTemplate:
    """ Steps
        -----
        1. Write a questline class containing each subquest
        
        2. Initialize the questline class externally.
            player_obj.questlines['Bloodkin'] = Bloodkin()

        3. Assign a subquest to an object
            obj        = create_item('scroll of death')
            obj.name   = 'mysterious note'
            obj.effect = self.mysterious_note
            place_object(obj, loc, env)
        
        4. Activate the quest object via Item.use()
        
        5. Complete tasks by sending dialogue and an entity from Entity.move()

        6. Send new dialogue to entity from Quest.dialogue() or complete the quest """

    def __init__(self):
        
        # Optional parameters
        pass
    
    def subquest(self, dialogue=None, ent=None):
        
        # Run something upon activating an effect
        if not dialogue and not ent:
            note_text = ["line 1", "line 2", "line 3"]
            new_menu(header="header", options=note_text)
        
        # Generate the Quest object
        if "quest name" not in player_obj.questlog.quests.keys():
            quest = Quest(
                name     = 'quest name',
                notes    = ["description", "", "details"],
                tasks    = ["☐ Task."],
                category = 'Main or Side',
                function = self)
            
            # Initialize dialogue
            quest.dialogue_list = ["first message", "second message"]
            quest.content = quest.notes + quest.tasks
            
            # Add quest to questlog
            player_obj.questlog.quests[quest.name] = quest
            player_obj.questlog.update_questlog()
            pyg.update_gui("Quest added!", pyg.violet)
            
            # Generate main characters
            if 'NPC name' not in player_obj.ents.keys():
                create_NPC('NPC name')
            player_obj.ents['NPC name'].quest = quest
            player_obj.ents['NPC name'].dialogue = "NPC name: ..."
        
        else:
            
            # Remove last piece of dialogue and log progression
            ent.quest.dialogue_list.remove(dialogue)
            quest_lvl = 9 - len(ent.quest.dialogue_list)
            
            # Check off a task
            if quest_lvl == 1:
                player_obj.questlog.update_questlog(name='quest name')
            
            # Complete quest
            if quest_lvl == 9:
                player_obj.questlog.quests['quest name'].finished = True
                player_obj.questlog.update_questlog(name='quest name')
                
                # Place object to trigger next subquest
                pass
            
            # Return next piece of dialogue if not complete
            if ent.quest.dialogue_list:
                return ent.quest.dialogue_list[0]

class Bloodkin:
    """ Bloodkin quest.
        
        Summary
        -------
        The Bloodkin is a religion that worships the Sigil of Thanato, which is a blood-drawn rune with cryptic and sentient powers.
        They are led by Kyrio, who sentences to death anybody outside of the Bloodkin that know of the Sigil, as well as all kin that speak of it.
        The Sigil can be used for many purposes.
            - A weapon endowed by it will drip with blood; anyone killed in a dream by such a weapon with perish in the Overworld.
            - Any corpse painted with the Sigil will rise and attack anything in sight, stopping only upon second death.
            - When applied to a scroll, it yields the Scroll of Death, which is the only means of accessing the Abyssal Gallery.
        
        Events and triggers
        -------------------
        1.  The quest begins when the player first encounters a Scroll of Death.
            Upon use, the player enters the Abyssal Gallery and swiftly dies from the residing creatures.
        2a. The next possible step is a direct encounter with Kyrio. 
            Disquised as an aging trader, he indirectly leads the player to a path of assured demise. """

    def __init__(self):
        pass

    def making_a_friend(self, dialogue, ent):
        """ Manages friend quest, including initialization and dialogue. """
        
        # Initialization
        if dialogue == "Walk into something to interact with it, or press Enter if you're above it.":
            ent.quest.dialogue_list = [
                "Walk into something to interact with it, or press Enter if you're above it.",
                "Press Backspace to view the main menu. Try it again to return!",
                "Press 9 to view your questlog. Hold Enter to see more details.",
                "Press 4 to open your inventory. Backspace returns you, and Enter activates!",
                "Try holding 0. Press the arrow keys for special actions, or press 9 to toggle details.",
                "Check out Options in the main menu -- and don't forget to die!"]
            
            #ent.quest.dialogue_list = [
            #    "... The creature seems curious.",
            #    "A creakng sound reverberates from its body.",
            #    "The creature seems affectionate.",
            #    "Your friend looks happy to see you.",
            #    "Your friend seems friendlier now.",
            #    "Who is this, anyways?",
            #    "You give your friend a playful nudge.",
            #    "Your friend feels calmer in your presence.",
            #    "Your friend fidgets but seems content."]
        
        # Increase friendship level
        ent.quest.dialogue_list.remove(dialogue)
        friend_level = 9 - len(ent.quest.dialogue_list)
        
        # First checkpoint
        if friend_level == 1:
            player_obj.questlog.update_questlog(name="Making a friend")
        
        # Complete quest
        if friend_level == 9:
            
            player_obj.questlog.quests['Making a friend'].finished = True
            player_obj.questlog.update_questlog(name="Making a friend")
            pyg.update_gui("Woah! What's that?", pyg.violet)
            
            x = lambda dX : int((player_obj.ent.X + dX)/pyg.tile_width)
            y = lambda dY : int((player_obj.ent.Y + dY)/pyg.tile_height)
            
            # Find a nearby space to place the mysterious note
            found = False
            for i in range(3):
                if found: break
                x_test = x(pyg.tile_width*(i-1))
                for j in range(3):
                    y_test = y(pyg.tile_height*(j-1))
                    if not player_obj.ent.env.map[x_test][y_test].entity:
                        player_obj.cache = False
                        
                        obj = create_item('scroll of death')
                        obj.name = 'mysterious note'
                        obj.effect = Effect(
                            name          = 'mysterious note',
                            img_names     = ['scrolls', 'open'],
                            function      = self.mysterious_note,
                            sequence      = None,
                            cooldown_time = 0)
                        place_object(
                            obj = obj,
                            loc = [x_test, y_test],
                            env = ent.env)
                        
                        found = True
                        break
        
        if ent.quest.dialogue_list:
            return ent.quest.dialogue_list[0]

    def mysterious_note(self, dialogue=None, ent=None):
        """ Manages friend quest, including initialization and dialogue.
            Upon finding a scroll of death, the player must first learn to descipher it.
            People in the town seem to suggest that the church is involved.
            The best lead is Kyrio, who is secretly a leader of the church.
            
            Church: Coax a lizard to the altar (by following). """
        
        # Read the note
        if not dialogue and not ent:
            note_text = ["ξνμλ λξ ξλι ξγθιβξ ξ θθ.", "Ηκρσ σρσ λβνξθι νθ.", "Ψπθ αβνιθ πθμ."]
            new_menu(header="mysterious note", options=note_text, position="top left")
        
        if 'Learning a language' not in player_obj.questlog.quests.keys():
            
            # Initialize quest
            quest = Quest(
                name = 'Learning a language',
                notes = [
                    "A mysterious note. Someone in town might know what it means.",
                    "",
                    "ξνμλ λξ ξλι ξγθιβξ ξ θθ,", "Ηκρσ σρσ λβνξθι νθ,", "Ψπθ αβνιθ πθμ."],
                tasks = [
                    "☐ See if anyone in town can decipher the note."],
                category = 'Main',
                function = player_obj.questlines['Bloodkin'].mysterious_note)
            
            # Add quest to questlog
            quest.content = quest.notes + quest.tasks
            player_obj.questlog.quests[quest.name] = quest
            player_obj.questlog.update_questlog()
            pyg.update_gui(f"Quest added: {quest.name}", pyg.violet)
            
            # Generate characters and dialogue
            if 'Kyrio' not in player_obj.ents.keys(): player_obj.ents['Kyrio'] = create_NPC('Kyrio')
            quest.Kyrio_dialogue = [
                "Kyrio: Huh? I know nothing about such things.",
                "Kyrio: Rather inquisitive, are you? Never turns out well.",
                "Kyrio: Fine, yes, my brother might know. I am busy."]
            quest.Kyrio_progress              = 0
            player_obj.ents['Kyrio'].quest    = quest
            player_obj.ents['Kyrio'].dialogue = quest.Kyrio_dialogue[0]
            
            if 'Kapno' not in player_obj.ents.keys(): player_obj.ents['Kapno'] = create_NPC('Kapno')
            quest.Kapno_dialogue = [
                "Kapno: Exquisite! Where was this symbol found?",
                "Kapno: I have a strange curiosity for such things. They seem more frequent as of late.",
                "Kapno: Let me know if you find anything else."]
            quest.Kapno_progress              = 0
            player_obj.ents['Kapno'].quest    = quest
            player_obj.ents['Kapno'].dialogue = quest.Kapno_dialogue[0]
        
        if dialogue and ent:
            quest = player_obj.ents['Kyrio'].quest
            
            # Talk to Kyrio
            if ent.name == 'Kyrio':
                
                # Check for task completion
                quest.Kyrio_dialogue.remove(dialogue)
                quest.Kyrio_progress = 3 - len(ent.quest.Kyrio_dialogue)
                if quest.Kyrio_progress == 2:
                    player_obj.questlog.update_questlog(name='Learning a language')
                
                # Provide next piece of dialogue
                if quest.Kyrio_dialogue:
                    return quest.Kyrio_dialogue[0]
            
            elif ent.name == 'Kapno':
                
                # Check for task completion
                quest.Kapno_dialogue.remove(dialogue)
                quest.Kapno_progress = 3 - len(ent.quest.Kapno_dialogue)
                if quest.Kapno_progress == 2:
                    player_obj.questlog.update_questlog(name='Learning a language')
                
                # Provide next piece of dialogue
                if quest.Kapno_dialogue:
                    return quest.Kapno_dialogue[0]
            
            # Complete quest
            if (quest.Kyrio_progress == 3) or (quest.Kapno_progress == 3):
                
                player_obj.questlog.quests['Learning a language'].finished = True
                player_obj.questlog.update_questlog(name='Learning a language')

#######################################################################################################################################################
# Creation
## Environments
def build_garden():
    """ Generates the overworld environment. """
    
    ## Initialize environment
    env = Environment(
        name       = 'garden',
        lvl_num    = 0,
        size       = 1,
        soundtrack = list(aud.dict.keys()),
        img_names  = ['floors', 'grass4'],
        floors     = ['floors', 'grass4'],
        walls      = ['walls', 'gray'],
        roofs      = ['roofs', 'tiled'],
        blocked    = False,
        hidden     = False)
    player_obj.envs['garden'] = env
    player_obj.envs['garden'].camera = Camera(player_obj.ent)
    player_obj.envs['garden'].camera.fixed = True
    player_obj.envs['garden'].camera.zoom_in(custom=1)

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
        floor   = player_obj.envs['garden'].floors,
        walls   = player_obj.envs['garden'].walls,
        roof    = None)
    x, y = new_room.center()[0], new_room.center()[1]
    
    # Generate items and entities
    items    = [['forest', 'tree',   10]]
    entities = [['forest', 'radish', 50]]
    place_objects(env, items, entities)
    
    # Place player in first room
    env.player_coordinates = [x, y]
    env.map[x][y].item     = None
    player_obj.envs['garden'].entity = player_obj.ent
    player_obj.ent.tile = player_obj.envs['garden'].map[x][y]
    player_obj.envs['garden'].center = new_room.center()
    
    return env

def build_home():
    """ Generates player's home. """

    # Initialize environment
    player_obj.envs['home'] = Environment(
        name       = 'home',
        lvl_num    = 0,
        size       = 5,
        soundtrack = ['menu'],
        img_names  = ['walls', 'gray'],
        floors     = ['floors', 'green'],
        walls      = ['walls', 'gray'],
        roofs      = ['roofs', 'tiled'])

    # Construct rooms
    main_room = Room(
        name    = 'home room 1',
        env     = player_obj.envs['home'],
        x1      = 1,
        y1      = 10,
        width   = mech.room_max_size,
        height  = mech.room_max_size,
        biome   = 'any',
        hidden  = False,
        objects = False,
        floor   = player_obj.envs['home'].floors,
        walls   = player_obj.envs['home'].walls,
        roof    = None)
    hallway = Room(
        name    = 'home room 1',
        env     = player_obj.envs['home'],
        x1      = 0,
        y1      = 14,
        width   = 10,
        height  = 2,
        biome   = 'any',
        hidden  = False,
        objects = False,
        floor   = player_obj.envs['home'].floors,
        walls   = player_obj.envs['home'].walls,
        roof    = None)
    player_obj.envs['home'].combine_rooms()
    
    secret_room = Room(
        name    = 'secret room',
        env     = player_obj.envs['home'],
        x1      = 30,
        y1      = 30,
        width   = mech.room_min_size*2,
        height  = mech.room_min_size*2,
        biome   = 'any',
        hidden  = True,
        objects = False,
        floor   = player_obj.envs['home'].floors,
        walls   = player_obj.envs['home'].walls,
        roof    = None)
    player_obj.envs['home'].center = main_room.center()

    # Place items in home
    for i in range(5): 

        # Healing potion
        x, y = 4, 11
        item = create_item('healing potion')
        place_object(item, [x, y], player_obj.envs['home'])
        
        # Lightning scroll
        x, y = 5, 11
        item = create_item('scroll of lightning bolt')
        place_object(item, [x, y], player_obj.envs['home'])

        # Fireball scroll
        x, y = 6, 11
        item = create_item('scroll of fireball')
        place_object(item, [x, y], player_obj.envs['home'])

        # Blood sword
        x, y = 24, 33
        item = create_item('blood sword')
        place_object(item, [x, y], player_obj.envs['home'])

        # Shield
        x, y = 29, 34
        item = create_item('iron shield')
        place_object(item, [x, y], player_obj.envs['home'])

        # Bug fix
        x, y = 0, 0
        item = create_item('scroll of fireball')
        place_object(item, [x, y], player_obj.envs['home'])
    
    # Generate stairs
    x, y = 9, 15
    item = create_item('portal')
    item.name = 'dungeon'
    place_object(item, [x, y], player_obj.envs['home'])
    
    # Generate door
    x, y = 0, 15
    item = create_item('door')
    item.name = 'overworld'
    place_object(item, [x, y], player_obj.envs['home'])
    player_obj.envs['home'].map[x][y].blocked = False
    player_obj.envs['home'].map[x][y].unbreakable = False
    
    # Generate friend
    x, y = 9, 18
    ent = create_entity('friend')
    place_object(ent, [x, y], player_obj.envs['home'])
    ent.dialogue = "Walk into something to interact with it, or press Enter if you're above it."
    player_obj.questlines = {}
    player_obj.questlines['Bloodkin'] = Bloodkin()
    ent.quest    = Quest(
        name     = "Making a friend",
        notes    = ["I wonder who this is. Maybe I should say hello."],
        tasks    = ["☐ Say hello to the creature.",
                    "☐ Get to know them."],
        category = 'Side',
        function = player_obj.questlines['Bloodkin'].making_a_friend)
    ent.quest.content = ent.quest.notes + ent.quest.tasks
    player_obj.questlog.quests['Making a friend'] = ent.quest
    player_obj.questlog.update_questlog()
    
    return player_obj.envs['home']

def build_dungeon_level():
    """ Generates the overworld environment. """
    
    # Initialize environment
    if not player_obj.envs['dungeon']: lvl_num = 1
    else:                              lvl_num = 1 + player_obj.envs['dungeon'][-1].lvl_num
    
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
    
    player_obj.envs['dungeon'].append(env)
    env.camera = Camera(player_obj.ent)
    env.camera.fixed = False
    env.camera.zoom_in(custom=1)

    # Generate biomes
    biomes = [['dungeon', ['walls', 'gray']]]
    voronoi_biomes(env, biomes)
    
    # Construct rooms
    rooms, room_counter, counter = [], 0, 0
    num_rooms = int(mech.max_rooms * env.lvl_num) + 1
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(mech.room_min_size, mech.room_max_size)
        height   = random.randint(mech.room_min_size, mech.room_max_size)
        x        = random.randint(0, len(env.map)    - width  - 1)
        y        = random.randint(0, len(env.map[0]) - height - 1)
        
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
                    env.create_h_tunnel(x_1, x_2, y_1, img_set=new_room.floor)
                    env.create_v_tunnel(y_1, y_2, x_2, img_set=new_room.floor)
                except: raise Exception('Error')
            else:
                env.create_v_tunnel(y_1, y_2, y_1, img_set=new_room.floor)
                env.create_h_tunnel(x_1, x_2, y_2, img_set=new_room.floor)
    
    # Generate items and entities
    items = [
        ['dungeon', 'healing potion', 10],
        ['dungeon', 'bones',          50],
        ['dungeon', 'sword',          1000//env.lvl_num],
        ['dungeon', 'iron shield',    1000//env.lvl_num],
        ['dungeon', 'skeleton',       500],
        ['dungeon', 'fire',           100]]
    entities = [
        ['dungeon', 'plant',          100],
        ['dungeon', 'eye',            25],
        ['dungeon', 'radish',         1000],
        ['dungeon', 'round1',         100]]
    place_objects(env, items, entities)
    
    # Place player in first room
    (x, y) = env.rooms[0].center()
    env.player_coordinates = [x, y]
    env.entity = player_obj.ent
    env.center = new_room.center()
    player_obj.ent.tile = env.map[x][y]
    
    # Generate stairs in the last room
    (x, y) = env.rooms[-2].center()
    stairs = create_item('portal')
    stairs.name = 'dungeon'
    place_object(stairs, [x, y], player_obj.envs['dungeon'][-1])

def build_overworld():
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
    player_obj.envs['overworld'] = env
    
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
        ['forest', 'radish', 50],
        ['wet',    'frog',   500],
        ['forest', 'grass',  1000],
        ['desert', 'rock',   50]]
    place_objects(env, items, entities)
    
    ## Construct rooms
    num_rooms             = 20
    rooms                 = []
    room_counter, counter = 0, 0
    center                = player_obj.envs['overworld'].center
    (x_1, y_1)            = center
    x_2                   = lambda width:  len(player_obj.envs['overworld'].map)    - width  - 1
    y_2                   = lambda height: len(player_obj.envs['overworld'].map[0]) - height - 1
    while room_counter < num_rooms:
        
        # Generate location
        width  = random.randint(mech.room_min_size, mech.room_max_size)
        height = random.randint(mech.room_min_size, mech.room_max_size)
        x      = random.randint(x_1, x_2(width))
        y      = random.randint(y_1, y_2(height))
        
        # Check for solid ground
        failed = False
        for u in range(width):
            for v in range(height):
                if env.map[x+u][y+v].biome in img.biomes['sea']: failed = True
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
                walls  = player_obj.envs['overworld'].walls,
                roof   = player_obj.envs['overworld'].roofs)

            room_counter += 1
            x, y = new_room.center()[0], new_room.center()[1]
        
        # Spawn rooms elsewhere if needed
        else: counter += 1
        if counter > num_rooms:
            counter = 0
            (x_1, y_1) = (0, 0)
    
    # Combine rooms and add doors
    player_obj.envs['overworld'].combine_rooms()
    for room in player_obj.envs['overworld'].rooms:
        add_doors(room)
    
    # Place player in first room
    (x, y) = player_obj.envs['overworld'].rooms[-1].center()
    env.player_coordinates = [x, y]
    player_obj.envs['overworld'].entity = player_obj.ent
    player_obj.ent.tile                 = player_obj.envs['overworld'].map[x][y]
    player_obj.envs['overworld'].center = new_room.center()
    
    # Generate stairs
    stairs = create_item('door')
    stairs.name = 'home'
    place_object(stairs, [x, y], player_obj.envs['overworld'])
    
    ## Place NPCs
    bools = lambda room, i: [
        env.map[room.center()[0]+i][room.center()[1]+i].item,
        env.map[room.center()[0]+i][room.center()[1]+i].entity]
    
    # Set named characters to spawn
    for name in ['Kyrio', 'Kapno', 'Erasti', 'Merci']:
        
        # Create NPC if needed
        if name not in player_obj.ents.keys(): player_obj.ents[name] = create_NPC(name)
        
        # Select room not occupied by player
        room = random.choice(player_obj.envs['overworld'].rooms)
        while room == player_obj.envs['overworld'].rooms[-1]:
            room = random.choice(player_obj.envs['overworld'].rooms)
        
        # Select spawn location
        for i in range(3):
            occupied = bools(room, i-1)
            if occupied[0] == occupied[1]:
                (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
        
        # Spawn entity
        place_object(player_obj.ents[name], (x, y), env)
    
    # Set number of random characters
    for _ in range(10):
        
        # Create entity
        ent = create_NPC('random')
        
        # Select room not occupied by player
        room = random.choice(player_obj.envs['overworld'].rooms)
        while room == player_obj.envs['overworld'].rooms[-1]:
            room = random.choice(player_obj.envs['overworld'].rooms)
        
        # Select spawn location
        for i in range(3):
            occupied = bools(room, i-1)
            if occupied[0] == occupied[1]:
                (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
        
        # Spawn entity
        place_object(ent, (x, y), env)

def build_cave_level():
    """ Generates a cave environment. """
    
    # Initialize environment
    if not player_obj.envs['cave']: lvl_num = 1
    else:                           lvl_num = 1 + player_obj.envs['cave'][-1].lvl_num
    
    env = Environment(
        name       = 'cave',
        lvl_num    = lvl_num,
        size       = 1,
        soundtrack = [f'dungeon {lvl_num}'],
        img_names  = ['walls', 'dark red'],
        floors     = ['floors', 'dirt1'],
        walls      = ['walls', 'dark red'],
        roofs      = None,
        blocked    = True,
        hidden     = True)
    
    player_obj.envs['cave'].append(env)
    env.camera = Camera(player_obj.ent)
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
        width    = random.randint(mech.room_min_size, mech.room_max_size)
        height   = random.randint(mech.room_min_size, mech.room_max_size)
        x        = random.randint(0, len(env.map)    - width  - 1)
        y        = random.randint(0, len(env.map[0]) - height - 1)
        
        new_room = Room(
            name    = 'cave room',
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
    
    # Paths
    for i in range(len(env.rooms)):
        room_1, room_2 = env.rooms[i], env.rooms[i-1]
        chance_1, chance_2 = 0, random.randint(0, 1)
        if not chance_1:
            (x_1, y_1), (x_2, y_2) = room_1.center(), room_2.center()
            if not chance_2:
                try:
                    env.create_h_tunnel(x_1, x_2, y_1, img_set=new_room.floor)
                    env.create_v_tunnel(y_1, y_2, x_2, img_set=new_room.floor)
                except: raise Exception('Error')
            else:
                env.create_v_tunnel(y_1, y_2, y_1, img_set=new_room.floor)
                env.create_h_tunnel(x_1, x_2, y_2, img_set=new_room.floor)
    
    # Generate items and entities
    items = [
        ['dungeon', 'healing potion', 10],
        ['dungeon', 'bones',          50],
        ['dungeon', 'sword',          1000//env.lvl_num],
        ['dungeon', 'iron shield',    1000//env.lvl_num],
        ['dungeon', 'skeleton',       500],
        ['dungeon', 'fire',           100]]
    entities = [
        ['dungeon', 'plant',          100],
        ['dungeon', 'eye',            25],
        ['dungeon', 'radish',         1000],
        ['dungeon', 'round1',         100]]
    place_objects(env, items, entities)
    
    # Place player in first room
    (x, y) = env.rooms[0].center()
    env.player_coordinates = [x, y]
    env.entity = player_obj.ent
    env.center = new_room.center()
    player_obj.ent.tile = env.map[x][y]
    
    # Generate stairs in the last room
    (x, y) = env.rooms[-1].center()
    stairs = create_item('cave')
    stairs.img_names = ['floors', 'dirt2']
    place_object(stairs, [x, y], player_obj.envs['cave'][-1])

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
            hidden        = False,
            blocked       = True,
            movable       = True,
            rand_set      = 0,
            cost          = 20,
            
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
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 5,
            
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
            hidden        = False,
            blocked       = True,
            movable       = False,
            rand_set      = 0,
            cost          = 5,
            
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
            hidden        = False,
            blocked       = True,
            movable       = False,
            rand_set      = 0,
            cost          = 20,
            
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
            hidden        = False,
            blocked       = True,
            movable       = True,
            rand_set      = 2,
            cost          = 25,
            
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
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
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
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'shrooms': Item(
            name          = 'shrooms',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'shrooms'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 15,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'red plant left': Item(
            name          = 'red plant left',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'red plant left'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 15,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'red plant right': Item(
            name          = 'red plant right',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'red plant right'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 15,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'cup shroom': Item(
            name          = 'cup shroom',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'cup shroom'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 15,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'frond': Item(
            name          = 'frond',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'frond'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 15,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'blades': Item(
            name          = 'blades',
            role          = 'other',
            slot          = None,
            img_names     = ['decor', 'blades'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 10,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

    # Drugs (drugs_options)

        'needle': Item(
            name          = 'needle',
            role          = 'drugs',
            slot          = None,
            img_names     = ['drugs', 'needle'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 25,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'skin': Item(
            name          = 'skin',
            role          = 'drugs',
            slot          = None,
            img_names     = ['drugs', 'skin'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'teeth': Item(
            name          = 'teeth',
            role          = 'drugs',
            slot          = None,
            img_names     = ['drugs', 'teeth'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'bowl': Item(
            name          = 'bowl',
            role          = 'drugs',
            slot          = None,
            img_names     = ['drugs', 'bowl'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 30,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = mech.bowl),

        'plant': Item(
            name          = 'plant',
            role          = 'drugs',
            slot          = None,
            img_names     = ['drugs', 'plant'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = Effect(
                name          = 'food',
                img_names     = ['drugs', 'plant'],
                function      = mech.boost_stamina,
                sequence      = None,
                cooldown_time = 0.1)),

        'bubbles': Item(
            name          = 'bubbles',
            role          = 'drugs',
            slot          = None,
            img_names     = ['drugs', 'bubbles'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 50,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = Effect(
                name          = 'food',
                img_names     = ['drugs', 'bubbles'],
                function      = mech.radish_eat,
                sequence      = None,
                cooldown_time = 0.1)),

    # Potions and scrolls (potions_options, scrolls_options)
    
        'healing potion': Item(
            name          = 'healing potion',
            role          = 'potions',
            slot          = None,
            img_names     = ['potions', 'red'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'transformation potion': Item(
            name          = 'transformation potion',
            role          = 'potions',
            slot          = None,
            img_names     = ['potions', 'purple'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'blue potion': Item(
            name          = 'transformation potion',
            role          = 'potions',
            slot          = None,
            img_names     = ['potions', 'blue'],

            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'gray potion': Item(
            name          = 'transformation potion',
            role          = 'potions',
            slot          = None,
            img_names     = ['potions', 'gray'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of lightning bolt': Item(
            name          = 'scroll of lightning bolt',
            role          = 'scrolls',
            slot          = None,
            img_names     = ['scrolls', 'closed'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 20,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of fireball': Item(
            name          = 'scroll of fireball',
            role          = 'scrolls',
            slot          = None,
            img_names     = ['scrolls', 'closed'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 20,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of confusion': Item(
            name          = 'scroll of confusion',
            role          = 'scrolls',
            slot          = None,
            img_names     = ['scrolls', 'closed'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 20,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'scroll of death': Item(
            name          = 'scroll of death',
            role          = 'scrolls',
            slot          = None,
            img_names     = ['scrolls', 'open'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 1000,
            
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
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
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
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'cave': Item(
            name          = 'cave',
            role          = 'other',
            slot          = None,
            img_names     = ['floors', 'sand2'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'path left right': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['paths', 'left right'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
        'path up down': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['paths', 'up down'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
        'path down right': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['paths', 'down right'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
        'path down left': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['paths', 'down left'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
        'paths up right': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['paths', 'up right'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
        'paths up left': Item(
            name          = 'path',
            role          = 'other',
            slot          = None,
            img_names     = ['paths', 'up left'],
            
            durability    = 101,
            equippable    = False,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
    
    # Weapons (equip_names)
    
        'shovel': Item(
            name          = 'shovel',
            role          = 'weapons',
            slot          = 'dominant hand',
            img_names     = ['shovel', 'dropped'],

            durability    = 100,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 15,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'super shovel': Item(
            name          = 'super shovel',
            role          = 'weapons',
            slot          = 'dominant hand',
            img_names     = ['super shovel', 'dropped'],

            durability    = 1000,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 1000,
            defense_bonus = 0,
            effect        = effect),

        'dagger': Item(
            name          = 'dagger',
            role          = 'weapons',
            slot          = 'dominant hand',
            img_names     = ['dagger', 'dropped'],
            
            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 25,
            
            hp_bonus      = 0,
            attack_bonus  = 2,
            defense_bonus = 0,
            effect        = effect),

        'sword': Item(
            name          = 'sword',
            role          = 'weapons',
            slot          = 'dominant hand',
            img_names     = ['sword', 'dropped'],
            
            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 75,
            
            hp_bonus      = 0,
            attack_bonus  = 5,
            defense_bonus = 0,
            effect        = effect),

        'blood dagger': Item(
            name          = 'blood dagger',
            role          = 'weapons',
            slot          = 'dominant hand',
            img_names     = ['blood dagger', 'dropped'],
            
            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 500,
            
            hp_bonus      = 0,
            attack_bonus  = 10,
            defense_bonus = 0,
            effect        = effect),

        'blood sword': Item(
            name          = 'blood sword',
            role          = 'weapons',
            slot          = 'dominant hand',
            img_names     = ['blood sword', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 1000,
            
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
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 1,
            effect        = effect),

        'orange clothes': Item(
            name          = 'orange clothes',
            role          = 'armor',
            slot          = 'body',
            img_names     = ['orange clothes', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 1,
            effect        = effect),

        'exotic clothes': Item(
            name          = 'exotic clothes',
            role          = 'armor',
            slot          = 'body',
            img_names     = ['exotic clothes', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 20,
            
            hp_bonus      = 1,
            attack_bonus  = 0,
            defense_bonus = 1,
            effect        = effect),

        'yellow dress': Item(
            name          = 'yellow dress',
            role          = 'armor',
            slot          = 'body',
            img_names     = ['yellow dress', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 10,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 1,
            effect        = effect),

        'chain dress': Item(
            name          = 'chain dress',
            role          = 'armor',
            slot          = 'body',
            img_names     = ['chain dress', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 20,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 2,
            effect        = effect),

        'iron armor': Item(
            name          = 'iron armor',
            role          = 'armor',
            slot          = 'body',
            img_names     = ['iron armor', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 100,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 10,
            effect        = effect),

        'bald': Item(
            name          = 'bald',
            role          = 'armor',
            slot          = 'head',
            img_names     = ['bald', 'front'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = False,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),
        
        'brown hair': Item(
            name          = 'brown hair',
            role          = 'armor',
            slot          = 'head',
            img_names     = ['brown hair', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'blue hair': Item(
            name          = 'blue hair',
            role          = 'armor',
            slot          = 'head',
            img_names     = ['blue hair', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'short brown hair': Item(
            name          = 'short brown hair',
            role          = 'armor',
            slot          = 'head',
            img_names     = ['short brown hair', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'clean': Item(
            name          = 'clean',
            role          = 'armor',
            slot          = 'face',
            img_names     = ['clean', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'brown beard': Item(
            name          = 'brown beard',
            role          = 'armor',
            slot          = 'face',
            img_names     = ['brown beard', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'blue beard': Item(
            name          = 'blue beard',
            role          = 'armor',
            slot          = 'face',
            img_names     = ['blue beard', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'white beard': Item(
            name          = 'white beard',
            role          = 'armor',
            slot          = 'face',
            img_names     = ['white beard', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'flat': Item(
            name          = 'flat',
            role          = 'armor',
            slot          = 'chest',
            img_names     = ['flat', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 0,
            effect        = effect),

        'bra': Item(
            name          = 'bra',
            role          = 'armor',
            slot          = 'chest',
            img_names     = ['bra', 'dropped'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = True,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
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
            movable       = True,
            rand_set      = 0,
            cost          = 50,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 10,
            effect        = effect),
    
    # Big objects
            'logo': Item(
            name          = 'logo',
            role          = 'decor',
            img_names     = ['top', 'left'],

            durability    = 101,
            equippable    = True,
            equipped      = False,
            hidden        = False,
            blocked       = False,
            movable       = True,
            rand_set      = 0,
            cost          = 0,
            
            hp_bonus      = 0,
            attack_bonus  = 0,
            defense_bonus = 10,
            effect        = effect)}
    
    # Search with image names
    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if val.img_names == names:
                item = val
    
    # Search with dictionary names
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
    ent_dict = {
        
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
            stamina    = 100,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0,
            fear       = None,
            reach      = 640),
    
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
    
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),

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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
    
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
    
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
    
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
    
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 40,
            aggression = 20,
            fear       = None,
            reach      = 1000),

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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
        
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
            stamina    = 100,
            
            follow     = True,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
        
        'rock': Entity(
            name       = 'rock',
            role       = 'enemy',
            img_names = ['rock', 'front'],
            habitat    = 'desert',
            
            exp        = 500,
            rank       = 1,
            hp         = 10,
            max_hp     = 10,
            attack     = 0,
            defense    = 500,
            stamina    = 100,
            
            follow     = False,
            lethargy   = 2,
            miss_rate  = 0,
            aggression = 0,
            fear       = None,
            reach      = 0),
        
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
            stamina    = 100,
            
            follow     = False,
            lethargy   = 10,
            miss_rate  = 10,
            aggression = 10,
            fear       = None,
            reach      = 1000),
        
        'radish': Entity(
            name       = 'radish',
            role       = 'enemy',
            img_names  = ['radish', 'front'],
            habitat    = 'forest',
            
            exp        = 0,
            rank       = 1,
            hp         = 25,
            max_hp     = 25,
            attack     = 0,
            defense    = 25,
            stamina    = 100,
            
            follow     = True,
            lethargy   = 6,
            miss_rate  = 6,
            aggression = 0,
            fear       = 0,
            reach      = 1000),
    
        'snake': Entity(
            name       = 'snake',
            role       = 'enemy',
            img_names  = ['snake', 'front'],
            habitat    = 'forest',
            
            exp        = 0,
            rank       = 1,
            hp         = 25,
            max_hp     = 25,
            attack     = 0,
            defense    = 25,
            stamina    = 100,
            
            follow     = True,
            lethargy   = 6,
            miss_rate  = 6,
            aggression = 0,
            fear       = None,
            reach      = 1000),
    
        'star': Entity(
            name       = 'star',
            role       = 'enemy',
            img_names  = ['star', 'front'],
            habitat    = 'forest',
            
            exp        = 0,
            rank       = 1,
            hp         = 25,
            max_hp     = 25,
            attack     = 0,
            defense    = 25,
            stamina    = 100,
            
            follow     = True,
            lethargy   = 6,
            miss_rate  = 6,
            aggression = 0,
            fear       = None,
            reach      = 1000),
    
        'plant': Entity(
            name       = 'plant',
            role       = 'enemy',
            img_names = ['plant', 'front'],
            habitat    = 'forest',
            
            exp        = 0,
            rank       = 1,
            hp         = 25,
            max_hp     = 25,
            attack     = 0,
            defense    = 25,
            stamina    = 100,
            
            follow     = True,
            lethargy   = 6,
            miss_rate  = 6,
            aggression = 0,
            fear       = None,
            reach      = 1000)}
    
    if type(names) in [tuple, list]:
        for val in ent_dict.values():
            if (val.img_names[0] == names[0]) and (val.img_names[1] == names[1]):
                item = val
    else:
        item = ent_dict[names]
    
    if not item: raise Exception(names)
    else:        return item

def create_NPC(name):
    """ A more specific version of create_entity. """
    
    if name == 'Kyrio':
        
        # Equipment
        ent = create_entity('black')
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        ent.inventory[clothes.role].append(clothes)
        ent.inventory[beard.role].append(beard)
        ent.inventory[dagger.role].append(dagger)
        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Kyrio: *furrows his brow*",
            "Kyrio: Talk to my brother, Kapno. I know little of mercantile.",
            "Kyrio: *seems not to notice*",
            "Kyrio: Is there something you need?"]
    
    elif name == 'Kapno':
        
        # Equipment
        ent     = create_entity('black')
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        ent.inventory[clothes.role].append(clothes)
        ent.inventory[beard.role].append(beard)
        ent.inventory[dagger.role].append(dagger)
        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Inventory
        ent.trader = True
        inv = ['shovel', 'sword', 'iron shield',
               'orange clothes', 'exotic clothes',
               'healing potion', 'transformation potion', 'blue potion', 'gray potion',
               'boxes', 'fire', 'shrooms', 'cup shroom']
        for item in inv:
            item = create_item(item)
            ent.inventory[item.role].append(item)
        
        # Dialogue
        ent.default_dialogue = [
            "Kapno: Huh?",
            "Kapno: Too many dry days, it seems. The lake is rather shallow.",
            "Kapno: Have you seen my brother? He seems distracted as of late.",
            "Kapno: My bones may be brittle, but I know good products when I see them.",
            "Kapno: *mumbles*"]
    
    elif name == 'Erasti':
        
        # Equipment
        ent     = create_entity('black')
        hair    = create_item('brown hair')
        bra     = create_item('bra')
        clothes = create_item('yellow dress')
        shovel  = create_item('shovel')
        ent.inventory[hair.role].append(hair)
        ent.inventory[bra.role].append(bra)
        ent.inventory[clothes.role].append(clothes)
        ent.inventory[shovel.role].append(shovel)
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        shovel.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Erasti: ...",
            "Erasti: Are you new to the region? Sorry, my memory is terrible!",
            "Erasti: I know... the town needs work. I guess we should all pitch in.",
            "Erasti: Sorry, I have a lot on my mind.",
            "Erasti: Good to see you!",
            "Erasti: Rumor has it that Kapno stashes a jar of herbs under his bed."]
    
    elif name == 'Merci':
        
        # Equipment
        ent     = create_entity('white')
        hair    = create_item('blue hair')
        bra     = create_item('bra')
        clothes = create_item('chain dress')
        shovel  = create_item('shovel')
        ent.inventory[hair.role].append(hair)
        ent.inventory[bra.role].append(bra)
        ent.inventory[clothes.role].append(clothes)
        ent.inventory[shovel.role].append(shovel)
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        shovel.toggle_equip(ent)
        
        # Inventory
        ent.trader = True
        inv = ['shovel',
               'chain dress', 'green clothes', 'yellow dress',
               'bubbles', 'plant']
        for item in inv:
            item = create_item(item)
            ent.inventory[item.role].append(item)
        
        # Dialogue
        ent.default_dialogue = [
            "Merci: Are you looking to buy anything in particular? Please, take a look at my stock.",
            "Merci: We specialize in exotic goods, but the basics are available as well.",
            "Merci: I prefer coins, but I could use the sale. Are you looking to trade?",
            "Merci: Your purchase is free if you can find my keys. I can't sell my blades without them!",
            "Merci: We have many items for sale.",
            "Merci: ... Oh, welcome in!"]
    
    elif name == 'random':
        ent     = create_entity(str(random.choice(img.skin_options)))
        hair    = create_item(str(random.choice(img.hair_options)))
        bra     = create_item(str(random.choice(img.chest_options)))
        face    = create_item(str(random.choice(img.face_options)))
        clothes = create_item(str(random.choice(img.armor_names)))
        ent.inventory[hair.role].append(hair)
        ent.inventory[bra.role].append(bra)
        ent.inventory[face.role].append(face)
        ent.inventory[clothes.role].append(clothes)
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        face.toggle_equip(ent)
        clothes.toggle_equip(ent)
        ent.lethargy = random.randint(1, 10)
        ent.default_dialogue = [
            "NPC: ...",
            "NPC: Howdy!",
            "NPC: *seems busy*"]
    
    return ent

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

def place_object(obj, loc, env, names=None):
    """ Places a single object in the given location.

        Parameters
        ----------
        obj   : class object in [Tile, Item, Entity]; object to be placed
        loc   : list of int; tile coordinates
        env   : Environment object; desired location
        names : list of str; Image dictionary names """    
    
    # Place tile
    if type(obj) == Tile:
        env.map[loc[0]][loc[1]].img_names = names
        
        # Set properties
        if names[1] in img.biomes['sea']:
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
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].item = obj
        if obj.blocked:
            env.map[loc[0]][loc[1]].blocked = True
    
    # Place entity
    elif type(obj) == Entity:
        obj.X    = loc[0] * pyg.tile_width
        obj.X0   = loc[0] * pyg.tile_width
        obj.Y    = loc[1] * pyg.tile_height
        obj.Y0   = loc[1] * pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].entity = obj
        env.entities.append(obj)

def place_objects(env, items, entities):
    """ Places entities and items according to probability and biome.

        Parameters
        ----------
        env      : Environment object; location to be placed
        items    : list of lists; [[<biome str>, <object str>, <unlikelihood int>], ...]
        entities :  """
    
    # Sort through each tile
    for y in range(len(env.map[0])):
        for x in range(len(env.map)):
            
            # Check that the space is not already occupied
            if not is_blocked(env, [x, y]):

                ## Randomly select an object
                selection = random.choice(items)
                
                # Check that the object matches the biome
                if env.map[x][y].biome in img.biomes[selection[0]]:
                    if not random.randint(0, selection[2]) and not env.map[x][y].item:
                        
                        ## Place object
                        item = create_item(selection[1])
                        place_object(item, [x, y], env)
                    
                # Randomly select an entity
                selection = random.choice(entities)
                
                # Check that the entity matches the biome
                if env.map[x][y].biome in img.biomes[selection[0]]:
                    if not random.randint(0, selection[2]):
                        
                        ## Place entity
                        entity = create_entity(selection[1])
                        entity.biome = env.map[x][y].biome
                        env.entities.append(entity)
                        place_object(entity, [x, y], env)

@debug_call
def place_player(env, loc):
    """ Sets player in a new position.

        Parameters
        ----------
        env : Environment object; new environment of player
        loc : list of integers; new location of player in tile coordinates """
    
    if not player_obj.ent.dead:
        if not pyg.startup_toggle:
            
            # Remove and extra motions
            pygame.event.clear()
            
            # Remove from current location
            if player_obj.ent.env:
                last_env_name = player_obj.ent.env.name
                if last_env_name != env.name:
                    
                    player_obj.ent.last_env = player_obj.ent.env
                player_obj.ent.env.player_coordinates = [player_obj.ent.X//32, player_obj.ent.Y//32]
                player_obj.ent.env.entities.remove(player_obj.ent)
                player_obj.ent.tile.entity = None
                player_obj.ent.tile = None

            # Set current environment and tile
            player_obj.ent.env  = env
            player_obj.ent.tile = player_obj.ent.env.map[loc[0]][loc[1]]
            player_obj.ent.X    = loc[0] * pyg.tile_width
            player_obj.ent.X0   = loc[0] * pyg.tile_width
            player_obj.ent.Y    = loc[1] * pyg.tile_height
            player_obj.ent.Y0   = loc[1] * pyg.tile_height

            # Notify environmnet of player position
            player_obj.ent.env.entities.append(player_obj.ent)
            player_obj.ent.tile.entity = player_obj.ent
            
            check_tile(loc[0], loc[1])
            
            if not env.camera: env.camera = Camera(player_obj.ent)
            env.camera.update()
            player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
            
            time.sleep(0.5)
            pyg.update_gui()
            
            if player_obj.ent.env.name != last_env_name:
                aud.control(soundtrack=env.soundtrack)
        
        # Startup
        else:
            
            # Set current environment and tile
            player_obj.ent.env  = env
            player_obj.ent.last_env = player_obj.ent.env
            player_obj.ent.tile = player_obj.ent.env.map[loc[0]][loc[1]]
            player_obj.ent.X    = loc[0] * pyg.tile_width
            player_obj.ent.X0   = loc[0] * pyg.tile_width
            player_obj.ent.Y    = loc[1] * pyg.tile_height
            player_obj.ent.Y0   = loc[1] * pyg.tile_height

            # Notify environmnet of player position
            player_obj.ent.env.entities.append(player_obj.ent)
            player_obj.ent.tile.entity = player_obj.ent
            
            check_tile(loc[0], loc[1])
            
            if not env.camera: env.camera = Camera(player_obj.ent)
            env.camera.update()
            player_obj.ent.env.camera.zoom_in(custom=pyg.zoom_cache)
            
            time.sleep(0.5)
            pyg.update_gui()

#######################################################################################################################################################
# Mechanics
## Common
def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    
    level_up_exp = mech.level_up_base + player_obj.ent.rank * mech.level_up_factor
    if player_obj.ent.exp >= level_up_exp:
        player_obj.ent.rank += 1
        player_obj.ent.exp -= level_up_exp
        pyg.update_gui('Leveled up to ' + str(player_obj.ent.rank) + '!', pyg.yellow)
        choice = None
        while choice == None: # Keeps asking until a choice is made
            choice = new_menu(
                header   = 'Leveled up! Choose your progress:',
                options  = ['Max HP (+20 HP, from ' + str(player_obj.ent.max_hp)  + ')',
                            'Attack (+1 attack, from '  + str(player_obj.ent.attack)  + ')',
                            'Defense (+1 defense, from '  + str(player_obj.ent.defense) + ')'], 
                position = 'center')

        if choice == 0:
            player_obj.ent.max_hp += 20
            player_obj.ent.hp += 20
        elif choice == 1:
            player_obj.ent.attack += 1
        elif choice == 2:
            player_obj.ent.defense += 1
        pyg.update_gui()

## Effects
def floor_effects(floor_effect):
    if floor_effect:
        if floor_effect == 'damage':
            player_obj.ent.take_damage(10)

def active_effects():
    """ Applies effects from items and equipment. Runs constantly. """
    global friendly, teleport, dig, super_dig
    
    #if 'transformation potion' in inventory_cache:
    #    player_obj.ent.image = img.dict['monsters'][0]
    #    friendly = True
    #else:
    #    friendly = False
    
    try:
        if get_equipped_in_slot('dominant hand').name == 'super shovel': super_dig = True
        else:                                                            super_dig = False
    except:                                                              super_dig = False

#######################################################################################################################################################
# Utilities
## Gameplay
def is_blocked(env, loc):
    """ Checks for barriers and triggers dialogue. """
    
    # Check for barriers
    if env.map[loc[0]][loc[1]].blocked:
        return True
    
    # Check for monsters
    if env.map[loc[0]][loc[1]].entity: 
        return True
    
    # Triggers message for hidden passages
    if env.map[loc[0]][loc[1]].unbreakable:
        pyg.update_gui('A mysterious breeze seeps through the cracks.', pyg.dark_gray)
        pygame.event.clear()
        return True
    
    return False

def sort_inventory(ent=None):   
    
    # Allow for NPC actions
    if not ent: ent = player_obj.ent
        
    inventory_cache = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
    other_cache     = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}

    # Sort by category
    for item_list in player_obj.ent.inventory.values():
        for item in item_list:
            inventory_cache[item.role].append(item)
    
    # Sort by stats:
    sorted(inventory_cache['weapons'], key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
    sorted(inventory_cache['armor'],  key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
    sorted(inventory_cache['potions'], key=lambda obj: obj.name)
    sorted(inventory_cache['scrolls'], key=lambda obj: obj.name)
    sorted(inventory_cache['other'],  key=lambda obj: obj.name)

    player_obj.ent.inventory = inventory_cache

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

def screenshot(size='display', visible=False, folder="Data/.Cache", filename="screenshot.png", blur=False):
    """ Takes a screenshot.
        cache:  saves a regular screenshot under Data/.Cache/screenshot.png
        save:   moves regular cached screenshot to Data/File_#/screenshot.png 
        blur:   adds a blur effect """
    
    # Turn off gui
    pyg.gui_toggle, pyg.msg_toggle = False, False
    
    # Select display size
    if size == 'full':
        camera_cache = [player_obj.ent.env.camera.X, player_obj.ent.env.camera.Y]
        pyg.display = pygame.display.set_mode((len(player_obj.ent.env.map[0])*16, len(player_obj.ent.env.map)*16),)
        player_obj.ent.env.camera.X = 0
        player_obj.ent.env.camera.Y = 0
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
        player_obj.ent.env.camera.X = camera_cache[0]
        player_obj.ent.env.camera.Y = camera_cache[1]
        player_obj.ent.env.camera.update()
    render_all()
    pyg.gui_toggle, pyg.msg_toggle = True, True

#######################################################################################################################################################
# Global scripts
if __name__ == "__main__":
    main()

#######################################################################################################################################################