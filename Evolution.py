########################################################################################################################################################
##
## MORS SOMNIA
##
########################################################################################################################################################

########################################################################################################################################################
# Plot
""" Overview
    --------
    There are many paths, but (almost) all lead to death. (One leads to immortality.)
    In the Overworld, mystery trickles beneath the floorboards.
    There are people to talk to, missions to complete, hidden opportunities, and clues to the endgame.
    Daylight passes quickly. Sleep and drug use lead to roguelike dreams.
    Death is the only way to wake up from a dream or hallucination and return to the Overworld. Death in the Overworld is absolute.
    Only some items and modifications are retained upon death in a dream or hallucination.
    
    Main Quests
    -----------
    Making a Friend     : A tutorial for controls that allows early access to the Sigil.
    Learning a Language : Introduction of the Sigil as a leading artifact in the overarching plot.
    
    Side Quests
    -----------
    Upgrade : A tutorial for trading mechanics that allows early access to a dagger.
    
    The Garden
    ----------
    Let There Be Water : A tutorial for item use and radish interaction in the Garden.
    
    Endgames
    --------
    No Risk, No Reward : The player does nothing substantial and dies in the Overworld. Upon death, the player cannot move (due to death).
    Introspection      : The player escapes the Overworld and returns to Player Creation. Upon death, they arise in the Garden.
    Becoming a God     : The player breaches polynomial depth in dreams and hallucinations. Death results in a stochastic environments forever.
    Resident           : The player mostly survives and helps out around town. One death is prevented; the next results in a funeral.
    Believer           : The player serves the church and saves it from destruction. 
    * additional
    
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

########################################################################################################################################################
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

# Aesthetics
from PIL import Image, ImageFilter, ImageOps

########################################################################################################################################################
# Global values
super_dig = False

########################################################################################################################################################
# Core
def debug_call(func):
    """ Just a print statement for debugging. Shows which function is called alongside variable details. """
    def wrapped_function(*args, **kwargs):
        print(f"{func.__name__:<30}{time.strftime('%M:%S', time.localtime())}")
        return func(*args, **kwargs)
    return wrapped_function

def main():
    """ Initializes the essentials and opens the main menu. """
    
    global pyg, mech, img, aud
    global player_obj, play_game_obj, new_game_obj, garden_obj, weather
    global dev, inv, hold_obj, trade_obj
    global main_menu_obj, big_menu, small_menu, ctrl_menu, info_obj, questlog_obj, pet_obj
    global save_account_obj, load_account_obj

    # Initialize pygame (parameters, display, clock, etc.)
    pyg              = Pygame()
    pyg.game_state   = 'startup'
    pyg.overlay      = None

    # Initialize mechanics and audio
    mech             = Mechanics()
    aud              = Audio()
    
    # Import images (sorted dictionary and cache)
    img              = Images()
    img.flipped      = Images(flipped=True)
    pygame.display.set_icon(img.dict['decor']['skeleton'])
    
    # Create player
    player_obj       = Player()
    player_obj.temp  = True
    
    # Initialize gamestates
    play_game_obj    = PlayGame()
    new_game_obj     = NewGame()
    garden_obj       = PlayGarden()
    pet_obj          = Pets()
    
    # Initialize overlays
    main_menu_obj    = MainMenu()
    ctrl_menu        = NewMenu(
        name         = 'controls',
        header       = "Controls", 
        options = [
            f"Move up:                                {pyg.key_UP[0]}                     Exit:                                         {pyg.key_BACK[0]}",
            f"Move down:                           {pyg.key_DOWN[0]}                     Activate 1:                             {pyg.key_ENTER[0]}",
            f"Move left:                               {pyg.key_LEFT[0]}                     Activate 2:                               {pyg.key_PERIOD[0]}",
            f"Move right:                            {pyg.key_RIGHT[0]}",
            "",
            
            f"Toggle inventory:                  {pyg.key_INV[0]}                     Enter combo:                         {pyg.key_HOLD[0]}",
            f"Toggle DevTools:                   {pyg.key_DEV[0]}                     Change speed:                      {pyg.key_SPEED[0]}",
            f"Toggle GUI:                            {pyg.key_GUI[0]}                     Zoom in:                                {pyg.key_PLUS[0]}",
            f"View stats:                             {pyg.key_INFO[0]}                     Zoom out:                              {pyg.key_MINUS[0]}",
            f"View questlog:                      {pyg.key_QUEST[0]}"])
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
    questlog_obj = BigMenu(
        name      = 'questlog',
        header    = "                                                        QUESTLOG", 
        options   = ["Test"])
    questlog_obj.init_questlog()
    questlog_obj.init_gardenlog()
    inv              = Inventory()
    dev              = DevTools()
    hold_obj         = Hold()
    trade_obj        = Trade()
    small_menu       = SmallMenu()
    info_obj         = Info()
    big_menu         = BigMenu(
        name      = 'temp',
        header    = "temp", 
        options   = [""])
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
            
            ## Extra adjustments
            player_obj.ent.env.weather.run()
            player_obj.ent.env.weather.render()
        
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
            ctrl_menu.run()
            ctrl_menu.render()
        
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
        
        elif pyg.overlay == 'stats':
            small_menu.render()
        
        elif pyg.overlay == 'questlog':
            questlog_obj.run()
            questlog_obj.render()
        
        elif pyg.overlay == 'temp':
            big_menu.run()
            big_menu.render()
        
        img.render()
        pygame.display.flip()
        pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
        pyg.clock.tick(30)

def render_all(size='display', visible=False):
    """ Draws tiles and stuff. Constantly runs. """
    
    def bw_binary():
        import numpy as np
        
        # Extract screen as image
        screen_surface = pygame.display.get_surface()
        raw_str = pygame.image.tostring(screen_surface, 'RGB')
        image = Image.frombytes('RGB', screen_surface.get_size(), raw_str)
        
        # Apply PIL effects
        image = image.convert('L')
        
        # Apply numpy effects
        image = np.array(image)
        image = np.where(image > 50, 255, 0)
        image = image.T
        image = np.stack([image] * 3, axis=-1)
        image = pygame.surfarray.make_surface(image)
        pyg.screen.blit(image, (0, 0))
    
    pyg.display.fill(pyg.black)
    
    # Set tiles to render
    if size == 'full':
        y_range_1, y_range_2 = 0, len(player_obj.ent.env.map[0])
        x_range_1, x_range_2 = 0, len(player_obj.ent.env.map)
    
    else:
        if not player_obj.ent.env.camera:
            player_obj.ent.env.camera = Camera(player_obj.ent)
        
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
    
    # Apply effects
    if img.render_fx == 'bw_binary': bw_binary()
    
    # Render GUI
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
        
        # Print status bars and time
        if pyg.gui_toggle:
            gui = list(pyg.gui.values())
            for i in range(len(pyg.gui)):
                
                # Left
                if i == 0:   x = 16
                
                # Central
                elif i == 1: x = pyg.screen_width//2 - gui[2].get_width()//2 - gui[1].get_width()
                elif i == 2: x = pyg.screen_width//2 - gui[2].get_width()//2
                elif i == 3: x = pyg.screen_width//2 + gui[2].get_width()//2
                
                # Right
                elif i == 4: x = pyg.screen_width - gui[i].get_width() - 16
                
                y = pyg.screen_height - 27
                pyg.screen.blit(gui[i], (x, y))
    
    aud.shuffle()

def check_tile(x, y, startup=False):
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
            if (tile.room != player_obj.ent.prev_tile.room) or (startup == True):
                
                # Hide the roof if the player enters a room
                if tile.room and tile.room.roof:
                    for spot in tile.room.tiles_list:
                        if spot not in tile.room.walls_list:
                            spot.img_names = tile.room.floor
    
    # Reveal the roof if the player leaves the room
    if player_obj.ent.prev_tile:
        prev_tile = player_obj.ent.prev_tile
        if prev_tile.room and not tile.room:
            if prev_tile.room.roof:
                for spot in prev_tile.room.tiles_list:
                    if spot not in prev_tile.room.walls_list:
                        spot.img_names = prev_tile.room.roof

########################################################################################################################################################
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
        self.screen   = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        self.frame    = False
        self.font     = pygame.font.SysFont('segoeuisymbol', 16, bold=True) # pygame.font.Font('Data/font.ttf', 24)
        self.minifont = pygame.font.SysFont('segoeuisymbol', 14, bold=True) # pygame.font.Font('Data/font.ttf', 24)
        self.clock    = pygame.time.Clock()
        self.display  = pygame.Surface((int(self.screen_width / self.zoom), int(self.screen_height / self.zoom)))
        self.gui      = {
            'health':   self.font.render('', True, self.red),
            'stamina':  self.font.render('', True, self.green),
            'location': self.font.render('', True, self.gray)}

    def set_controls(self, controls='numpad 1'):
        
        self.controls_preset = controls
        
        # Extended controls
        if controls == 'arrows':
            
            # Movement
            self.key_UP       = ['↑', K_UP,    K_w]             # up
            self.key_DOWN     = ['↓', K_DOWN,  K_s]             # down
            self.key_LEFT     = ['←', K_LEFT,  K_a]             # left
            self.key_RIGHT    = ['→', K_RIGHT, K_d]             # right
            
            # Actions
            self.key_BACK     = ['/', K_BACKSPACE, K_ESCAPE, K_SLASH, K_KP_DIVIDE]  # exit/main menu
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY] # show/hide gui
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]  # action 1
            self.key_PERIOD   = ['.', K_KP_PERIOD]              # action 2
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS]   # zoom
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]  # zoom
            self.key_HOLD     = ['0', K_0, K_KP0]
            
            # Menus
            self.key_INV      = ['4', K_4, K_KP4]               # inventory
            self.key_DEV      = ['6', K_6, K_KP6]               # DevTools
            self.key_INFO     = ['7', K_7, K_KP7]               # player information
            self.key_SPEED    = ['8', K_8, K_KP8]               # movement speed
            self.key_QUEST    = ['9', K_9, K_KP9]               # questlog
            
            # Other
            self.key_EQUIP    = ['2', K_2, K_KP2]               # inventory (equip)
            self.key_DROP     = ['3', K_3, K_KP3]               # inventory (drop)

        # Alternate controls
        elif controls == 'numpad 1':
            
            # Movement
            self.key_UP       = ['5', K_5, K_KP5,  K_UP]          # up
            self.key_DOWN     = ['2', K_2, K_KP2,  K_DOWN]        # down
            self.key_LEFT     = ['1', K_1, K_KP1,  K_LEFT]        # left
            self.key_RIGHT    = ['3', K_3, K_KP3,  K_RIGHT]       # right

            # Actions
            self.key_BACK     = ['/', K_SLASH,     K_KP_DIVIDE]   # exit/main menu
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY] # show/hide gui
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]    # action 1
            self.key_PERIOD   = ['.', K_KP_PERIOD]                # action 2
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS]     # zoom
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]    # zoom
            self.key_HOLD     = ['0', K_0, K_KP0]                 # attack sequences
            
            # Menus
            self.key_INV      = ['4', K_4, K_KP4]                 # inventory
            self.key_DEV      = ['6', K_6, K_KP6]                 # DevTools
            self.key_INFO     = ['7', K_7, K_KP7]                 # player information
            self.key_SPEED    = ['8', K_8, K_KP8]                 # movement speed
            self.key_QUEST    = ['9', K_9, K_KP9]                 # questlog
            
            # Unused
            self.key_EQUIP    = []                           # inventory (equip)
            self.key_DROP     = []                           # inventory (drop)

        # Alternate controls
        elif controls == 'numpad 2':
            
            # Movement
            self.key_UP       = ['8', K_8, K_KP8,  K_UP]          # up
            self.key_DOWN     = ['5', K_5, K_KP5,  K_DOWN]        # down
            self.key_LEFT     = ['4', K_4, K_KP4,  K_LEFT]        # left
            self.key_RIGHT    = ['6', K_6, K_KP6,  K_RIGHT]       # right

            # Actions
            self.key_BACK     = ['/', K_SLASH,     K_KP_DIVIDE]   # exit/main menu
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY] # show/hide gui
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]    # action 1
            self.key_PERIOD   = ['.', K_KP_PERIOD]                # action 2
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS]     # zoom
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]    # zoom
            self.key_HOLD     = ['0', K_0, K_KP0]                 # attack sequences
            
            # Menus
            self.key_INV      = ['7', K_7, K_KP7]                 # inventory
            self.key_DEV      = ['9', K_9, K_KP9]                 # DevTools
            self.key_INFO     = ['1', K_1, K_KP1]                 # player information
            self.key_SPEED    = ['2', K_2, K_KP2]                 # movement speed
            self.key_QUEST    = ['3', K_3, K_KP3]                 # questlog
            
            # Unused
            self.key_EQUIP    = []                           # inventory (equip)
            self.key_DROP     = []                           # inventory (drop)

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
        self.colors            = [self.black, self.dark_gray, self.gray, self.white,
                                  self.red, self.orange, self.yellow, self.green, self.blue, self.violet]

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
        self.msg_width         = int(self.screen_width / 6)
        self.msg_height        = 4 # number of lines shown
        self.msg_history       = {}

    def textwrap(self, text, width):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if sum(len(w) for w in current_line) + len(current_line) + len(word) <= width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def fadeout_screen(self, screen, fade_in, env=None, loc=None, text="", font=None, duration=4):
        
        # Set functionality
        if not fade_in:
            alpha, change = 0, 10
        else:
            alpha, change = 255*2, -10
            player_obj.ent.env.weather.run()
            player_obj.ent.env.weather.render()

        # Set fade color and speed
        fade_surface = pygame.Surface(screen.get_size())
        fade_surface.fill((0, 0, 0))
        
        # Set text color and position
        if not font: font = self.font
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        
        # Increase alpha channel over time
        clock = pygame.time.Clock()
        gui_cache = copy.copy(pyg.gui_toggle)
        msg_cache = copy.copy(pyg.msg_toggle)
        pyg.gui_toggle = False
        pyg.msg_toggle = False
        running = True
        while running:
            
            # Handle gamestate
            alpha += change
            if alpha > 255*duration: running = False
            elif alpha < 0:          running = False
            
            fade_surface.set_alpha(alpha)
            pyg.screen.blit(pygame.transform.scale(pyg.display, (pyg.screen_width, pyg.screen_height)), (0, 0))
            screen.blit(fade_surface, (0, 0))
            if img.render_fx: render_all()
            
            # Show text
            if alpha >= 255:
                val = alpha - 255
                if val > 255: val = 255
                text_surface.set_alpha(random.randint(val-50, val))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.update()
            clock.tick(15)
        
        pyg.gui_toggle = gui_cache
        pyg.msg_toggle = msg_cache
        if env: place_player(env, loc) # fadeout screen

    def update_gui(self, new_msg=None, color=None):
        
        # Prepare colors
        img.average()
        if not color: color = pygame.Color(255-img.top_color[0], 255-img.top_color[1], 255-img.top_color[2])
        bottom_color = pygame.Color(255-img.bottom_color[0], 255-img.bottom_color[1], 255-img.bottom_color[2])
        
        if player_obj.ent.env:
            
            ## Upper gui
            # Create and delete messages
            if new_msg:
                if new_msg in self.msg_history.keys():
                    del self.msg_history[new_msg]
                for line in pyg.textwrap(new_msg, pyg.msg_width):
                    self.msg_history[line] = color
                    
                    # Delete older messages
                    if len(self.msg) == pyg.msg_height:
                        del self.msg[0]
            
            # Reconstruct message list
            self.msg = []
            index = len(self.msg_history) - self.msg_height
            if index < 0:
                index = 0
            lines = list(self.msg_history.keys())[index:]
            colors = list(self.msg_history.values())[index:]
            for i in range(len(lines)):
                if colors[i] in pyg.colors:
                    self.msg.append(self.font.render(lines[i], True, colors[i]))
                else:
                    self.msg.append(self.font.render(lines[i], True, color))
            
            ## Lower gui
            # Health
            current_health = int(player_obj.ent.hp / player_obj.ent.max_hp * 10)
            leftover_health = 10 - current_health
            health = '⚪' * leftover_health + '⚫' * current_health
            
            # Stamina
            current_stamina = int((player_obj.ent.stamina % 101) / 10)
            leftover_stamina = 10 - current_stamina
            stamina = '⚫' * current_stamina + '⚪' * leftover_stamina
            
            # Time
            time = ['🌗', '🌘', '🌑', '🌒', '🌓', '🌔', '🌕', '🌖'][player_obj.ent.env.env_time-1]
            
            # Update bottom gui
            if not pyg.overlay:
                
                self.gui = {
                    'first':   self.minifont.render('', True, self.white),
                    'health':  self.minifont.render(health,  True, self.red),
                    'time':    self.minifont.render(time, True, bottom_color),
                    'stamina': self.minifont.render(stamina, True, self.green),
                    'last':    self.minifont.render('', True, self.white)}
            
            # Additional details
            else:
                if self.msg: self.msg = [self.msg[-1]]
                
                # Location
                env = str(player_obj.ent.env.name)
                if player_obj.ent.env.lvl_num: env = env + ' (level ' + str(player_obj.ent.env.lvl_num) + ')'
                
                self.gui = {
                    'wallet':   self.minifont.render('⨋ '+str(player_obj.ent.wallet), True, bottom_color),
                    'health':  self.minifont.render(health,  True, self.red),
                    'time':    self.minifont.render(time, True, bottom_color),
                    'stamina': self.minifont.render(stamina, True, self.green),
                    'location': self.minifont.render(env, True, bottom_color)}

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
        self.load_other(flipped, alt=True)
        
        # Create combined dictionary
        self.dict = self.ent | self.equip | self.other
        
        # Assign tiles to biomes
        self.biomes()
        
        # Gather images for character_creation
        self.hair_options  = ['bald',  'brown hair',  'blue hair',  'short brown hair']
        self.face_options  = ['clean', 'brown beard', 'blue beard', 'white beard', 'glasses']
        self.chest_options = ['flat',  'bra']
        self.skin_options  = ['white', 'black', 'fat']
        
        self.big_img()

        self.impact_image      = self.get_impact_image()
        self.impact_images     = []
        self.impact_image_pos  = []
        self.impact            = False        
        self.blank_surface     = pygame.Surface((pyg.tile_width, pyg.tile_height)).convert()
        self.blank_surface.set_colorkey(self.blank_surface.get_at((0,0)))
        self.render_log = []
        
        self.render_fx = None

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
                    tileset = ImageOps.posterize(tileset.convert('RGB'), 6).convert('RGB')
                    tileset.putalpha(img_a)
            
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
            'white',     'black',  'fat',
            'friend',    'eye',    'eyes',   'troll',      'triangle',      'purple',
            'tentacles', 'round1', 'round2', 'grass',      'round3',        'lizard',
            'red',       'rock',   'frog',   'red radish', 'orange radish', 'purple radish',
            'star',      'plant',  'snake',  'buzz',       'egg',           'green blob',
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
            'iron armor', 'green clothes', 'iron shield', 'orange clothes', 'exotic clothes', 'yellow dress', 'chain dress',      'bra',   'lamp',
            'glasses',    'brown hair',    'blue hair',   'blue beard',     'brown beard',    'white beard',  'short brown hair', 
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
    
    def load_other(self, flipped=False, alt=False):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Choose tileset
        if alt:
            file_name = 'Data/.Images/tileset_other_alt.png'
            self.other_alt = {}
            tile_dict = self.other_alt
        else:
            file_name = 'Data/.Images/tileset_other.png'
            self.other = {}
            tile_dict = self.other
        
        # Import tiles
        other_matrix = self.import_tiles(file_name, flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        self.other_names = [
            'decor', 'bubbles', 'furniture', 'drugs', 'potions', 'scrolls',
            'stairs', 'floors', 'walls', 'roofs', 'paths', 'concrete',
            'null']
        decor_options = [
            'tree', 'bones', 'boxes',  'fire', 'leafy', 'skeleton', 'shrooms',
            'red plant right', 'red plant left', 'cup shroom', 'frond',  'blades', 'purple bulbs',
            'lights']
        bubbles_options = [
            'dots', 'exclamation', 'dollar', 'cart', 'question', 'skull', 'heart', 'water']
        furniture_options = [
            'purple bed', 'red bed', 'shelf left', 'shelf right', 'long table left', 'long table right', 
            'table', 'red chair left', 'red chair right',
            'red rug bottom left', 'red rug bottom middle', 'red rug bottom right',
            'red rug middle left', 'red rug middle middle', 'red rug middle right',
            'red rug top left',    'red rug top middle',    'red rug top right',
            'green rug bottom left', 'green rug bottom middle', 'green rug bottom right',
            'green rug middle left', 'green rug middle middle', 'green rug middle right',
            'green rug top left',    'green rug top middle',    'green rug top right']
        drugs_options = [
            'needle', 'skin', 'teeth', 'bowl', 'plant', 'bubbles']
        potions_options = [
            'red', 'blue', 'gray', 'purple']
        scrolls_options = [
            'closed', 'open']
        stairs_options = [
            'door', 'portal']
        floors_options = [
            'dark green', 'dark blue', 'dark red',  'green',  'red',    'blue',
            'wood',       'water',     'sand1',     'sand2',  'grass1', 'grass2',
            'bubbles1',   'bubbles2',  'bubbles3',  'dirt1',  'dirt2',
            'grass3',     'grass4',    'gray tile', 'brown tile']
        walls_options = [
            'dark green', 'dark red', 'dark blue', 'gray', 'red', 'green', 'gold']
        roofs_options = [
            'tiled', 'slats']
        paths_options = [
            'left right', 'up down', 'down right', 'down left', 'up right', 'up left']
        concrete_options = [
            'gray window', 'gray door', 'gray wall left', 'gray wall', 'gray wall right', 'gray floor']
        null_options  = [
            'null']
        other_options = [
            decor_options, bubbles_options, furniture_options, drugs_options, potions_options, scrolls_options,
            stairs_options, floors_options, walls_options, roofs_options, paths_options, concrete_options, null_options]
        
        # Create image dictionary
        index = 0
        for _ in self.other_names:
            tile_dict[self.other_names[index]] = {option: image for (option, image) in zip(other_options[index], other_matrix[index])}
            index += 1
        self.other_count = sum([len(options_list) for options_list in other_options])

    def big_img(self):
    
        # Import tiles
        self.big = self.import_tiles('Data/.Images/decor_1_m_logo.png', flipped=False, effects=['posterize'])

    def biomes(self):
        """ Manages biome types. """
        
        self.biomes = {
            
            'any':     ['any', 'land', 'wet', 'sea', 'forest', 'desert', 'dungeon', 'water', 'city', 'cave'],
            'wet':     ['any', 'wet', 'forest', 'water'],
        
            'land':    ['any', 'land', 'forest', 'desert', 'dungeon', 'cave'],
            'forest':  ['any', 'forest'],
            'desert':  ['any', 'desert'],
            'dungeon': ['any', 'dungeon', 'cave'],
            'city':    ['any', 'city'],
            'cave':    ['any', 'cave', 'dungeon'],
            
            'sea':     ['water'],
            'water':   ['water']}

    # Utility
    def average(self):
        
        # Identify regions of interest
        top_rect     = pygame.Rect(0, 0, pyg.screen_width, 50)
        bottom_rect  = pygame.Rect(0, pyg.screen_height-50, pyg.screen_width, 50)
        left_rect    = pygame.Rect(50, 50, 50, 50)
        right_rect   = pygame.Rect(pyg.screen_width-100, 50, 50, 50)
        menu_rect    = pygame.Rect(100, pyg.screen_height-100, 50, 50)
        
        self.top_color    = pygame.transform.average_color(pyg.screen, rect=top_rect,    consider_alpha=False)
        self.bottom_color = pygame.transform.average_color(pyg.screen, rect=bottom_rect, consider_alpha=False)
        self.left_color   = pygame.transform.average_color(pyg.screen, rect=left_rect,   consider_alpha=False)
        self.right_color  = pygame.transform.average_color(pyg.screen, rect=right_rect,  consider_alpha=False)
        self.menu_color   = pygame.transform.average_color(pyg.screen, rect=menu_rect,   consider_alpha=False)
        
        # Relative luminance formula
        top_brightness    = 0.2126 * self.top_color[0]    + 0.7152 * self.top_color[1]    + 0.0722 * self.top_color[2]
        bottom_brightness = 0.2126 * self.bottom_color[0] + 0.7152 * self.bottom_color[1] + 0.0722 * self.bottom_color[2]
        left_brightness   = 0.2126 * self.left_color[0]   + 0.7152 * self.left_color[1]   + 0.0722 * self.left_color[2]
        right_brightness  = 0.2126 * self.right_color[0]  + 0.7152 * self.right_color[1]  + 0.0722 * self.right_color[2]
        menu_brightness   = 0.2126 * self.menu_color[0]   + 0.7152 * self.menu_color[1]   + 0.0722 * self.menu_color[2]
        
        # Quadratic version
        #top_brightness    = (top_color[0]**2    + top_color[1]**2    + top_color[2]**2)**(1/2)
        #bottom_brightness = (bottom_color[0]**2 + bottom_color[1]**2 + bottom_color[2]**2)**(1/2)
        #left_brightness   = (left_color[0]**2   + left_color[1]**2   + left_color[2]**2)**(1/2)
        #right_brightness  = (right_color[0]**2  + right_color[1]**2  + right_color[2]**2)**(1/2)
        #menu_brightness   = (menu_color[0]**2   + menu_color[1]**2   + menu_color[2]**2)**(1/2)
        
        # Restrict corrections to [0, 255]
        if top_brightness < 35:    top_brightness    = 35
        if bottom_brightness < 35: bottom_brightness = 35
        if left_brightness < 35:   left_brightness   = 35
        if right_brightness < 35:  right_brightness  = 35
        if menu_brightness < 35:   menu_brightness   = 35
        
        # Calculate a good shade of gray
        self.top_correct    = int(((255 - top_brightness)**2    + (255/3)**2)**(1/2))
        self.bottom_correct = int(((255 - bottom_brightness)**2 + (255/3)**2)**(1/2))
        self.left_correct   = int(((255 - left_brightness)**2   + (255/3)**2)**(1/2))
        self.right_correct  = int(((255 - right_brightness)**2  + (255/3)**2)**(1/2))
        self.menu_correct   = int(((255 - menu_brightness)**2   + (255/3)**2)**(1/2))

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

    def flash_over(self, ent):
        """ Death animation. """
        
        self.impact = True
        
        image     = self.impact_image
        x         = lambda: ent.X - player_obj.ent.env.camera.X
        y         = lambda: ent.Y - player_obj.ent.env.camera.Y
        image_pos = (x, y)
        duration  = 0.2
        delay     = 0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

    def vicinity_flash(self, ent, image):
        """ Death animation. """
        
        self.impact = True
        vicinity_list = list(get_vicinity(ent).values())
        for i in range(len(vicinity_list)):
            
            image     = image
            x         = vicinity_list[i%len(vicinity_list)].X - player_obj.ent.env.camera.X
            y         = vicinity_list[i%len(vicinity_list)].Y - player_obj.ent.env.camera.Y
            image_pos = (x, y)
            duration  = 0.5
            last_time = time.time()
            delay     = i*0.1
            
            self.render_log.append([image, image_pos, duration, last_time, delay])
        
        image     = image
        x         = vicinity_list[0].X - player_obj.ent.env.camera.X
        y         = vicinity_list[0].Y - player_obj.ent.env.camera.Y
        image_pos = (x, y)
        duration  = 0.5
        last_time = time.time()
        delay     = len(vicinity_list)*0.1
        
        self.render_log.append([image, image_pos, duration, last_time, delay])

    def flash_above(self, ent, image):
        """ Death animation. """
        
        short_list = ['red radish', 'orange radish', 'purple radish']
        if ent.name in short_list: shift = 12
        else:                      shift = 0
        
        self.impact = True
        
        image     = image
        x         = lambda: ent.X - player_obj.ent.env.camera.X
        y         = lambda: ent.Y - pyg.tile_height - player_obj.ent.env.camera.Y + shift
        image_pos = (x, y)
        duration  = 0.8
        delay     = 0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

        x         = lambda: ent.X - player_obj.ent.env.camera.X
        y         = lambda: ent.Y - pyg.tile_height - player_obj.ent.env.camera.Y + shift
        image_pos = (x, y)
        duration  = 0.2
        delay     = 1.0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

    def flash_on(self, ent, image):
        """ Death animation. """
        
        self.impact = True
        
        image     = image
        x         = lambda: ent.X - player_obj.ent.env.camera.X
        y         = lambda: ent.Y - player_obj.ent.env.camera.Y
        image_pos = (x, y)
        duration  = 0.8
        delay     = 0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

        x         = lambda: ent.X - player_obj.ent.env.camera.X
        y         = lambda: ent.Y - player_obj.ent.env.camera.Y
        image_pos = (x, y)
        duration  = 0.2
        delay     = 1.0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

    def render(self):
        """ Temporarily renders images in the queue, such as impact images.
        
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
                    image     = self.render_log[j][0]
                    duration  = self.render_log[j][2]
                    last_time = self.render_log[j][3]
                    delay     = self.render_log[j][4]
                    if type(self.render_log[j][1][0]) == int:
                        position = [self.render_log[j][1][0], self.render_log[j][1][1]]
                    else:
                        position = [self.render_log[j][1][0](), self.render_log[j][1][1]()]

                    # Count down before showing image
                    if delay > 0:
                        self.render_log[j][4] -= (time.time() - last_time)
                        self.render_log[j][3] = time.time()
                    
                    # Count down before hiding image
                    elif duration > 0:
                        self.render_log[j][2] -= (time.time() - last_time)
                        self.render_log[j][3] = time.time()
                        pyg.display.blit(image, position)
                        
                    else:
                        self.render_log.pop(j)

class Audio:
    """ Manages audio. One save for each file. """

    def __init__(self):
        
        # Initialize music player
        pygame.mixer.init()
        
        # Define song titles
        self.dict = {
            'home':              "Data/.Music/menu.mp3",
            'menu':              "Data/.Music/menu.mp3",
            'overworld 1':       "Data/.Music/overworld_1.mp3",
            'overworld 2':       "Data/.Music/overworld_2.mp3",
            'overworld 3':       "Data/.Music/overworld_3.wav",
            'overworld 4':       "Data/.Music/overworld_4.mp3",
            'dungeon 1':         "Data/.Music/dungeon_1.wav",
            'dungeon 2':         "Data/.Music/dungeon_2.mp3",
            'dungeon 3':         "Data/.Music/dungeon_3.wav",
            'dungeon 4':         "Data/.Music/dungeon_4.mp3",
            'dungeon 5':         "Data/.Music/dungeon_5.mp3",
            'dungeon 6':         "Data/.Music/dungeon_6.mp3",
            'hallucination 1':   "Data/.Music/dungeon_1.wav",
            'hallucination 2':   "Data/.Music/dungeon_2.mp3",
            'hallucination 3':   "Data/.Music/dungeon_3.wav",
            'hallucination 4':   "Data/.Music/dungeon_4.mp3",
            'hallucination 5':   "Data/.Music/dungeon_5.mp3"}
        
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
        
        # Select next track
        if not song:
            self.i = (self.i+1) % self.soundtrack_len
            song   = self.soundtrack[self.i]
        
        # Play the next track with fade-in if not already playing
        if self.current_track:
            if self.dict[song] != self.dict[self.current_track]:
                
                # Fade out current track
                if pygame.mixer.music.get_busy(): pygame.mixer.music.fadeout(fade_out_time)
                
                # Begin next track
                self.current_track = song
                pygame.mixer.music.load(self.dict[song])
                pygame.mixer.music.play(fade_ms=fade_in_time)
        
        else:
            
            # Fade out current track
            if pygame.mixer.music.get_busy(): pygame.mixer.music.fadeout(fade_out_time)
            
            # Begin next track
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
            
            # Move to the next song when complete
            elif pygame.mixer.music.get_busy():
                song = pygame.mixer.Sound(self.dict[self.current_track])
                self.duration = song.get_length()
                current_time = pygame.mixer.music.get_pos() / 1000
                self.remaining_time = self.duration - current_time
                if self.remaining_time <= 3:
                    print(1)
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
        self.envs     = {}
        self.file_num = 0
        self.temp     = False

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
            hp         = 10,
            max_hp     = 10,
            attack     = 0,
            defense    = 1,
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
        
        self.ent.discoveries = {
            'walls':     {'gray':   ['walls', 'gray'],
                          'green':  ['walls', 'green']},
            'floors':    {'grass4': ['floors', 'grass4'],
                          'wood':   ['floors', 'wood'],
                          'water':  ['floors', 'water']},
            'paths':     {},
            'stairs':    {'door': ['stairs', 'door']},
            'decor':     {'blades': ['decor', 'blades'],
                          'lights': ['decor', 'lights']},
            'furniture': {'table':  ['furniture', 'table'],
                          'red chair left': ['furniture', 'red chair left'],
                          'red chair right': ['furniture', 'red chair right']},
            'entities':  {}}
        
        hair   = create_item('bald')
        face   = create_item('clean')
        chest  = create_item('flat')
        dagger = create_item('dagger')
        
        dagger.effect = Effect(
            name          = 'swing',
            img_names     = ['dagger', 'dropped'],
            function      = mech.swing,
            trigger       = 'active',
            sequence      = '⮜⮟⮞',
            cooldown_time = 0.1,
            other         = None)
        
        hair.pick_up(ent=self.ent)
        face.pick_up(ent=self.ent)
        chest.pick_up(ent=self.ent)
        dagger.pick_up(ent=self.ent)
        
        hair.toggle_equip(self.ent)
        face.toggle_equip(self.ent)
        chest.toggle_equip(self.ent)
        dagger.toggle_equip(self.ent)

## States
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
            tab_x, tab_y = 70, 10
            self.options_categories_cache_2 = self.options_categories[0]
        else:
            tab_x, tab_y = 0, 0

        # Set initial position of each text type
        self.header_position = {
            'top left':     [5, 10],
            'center':       [int((pyg.screen_width - main_menu_obj.game_title.get_width())/2), 85],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        self.cursor_position = {
            'top left':     [50+tab_x, 38+tab_y],
            'center':       [50, 300],
            'bottom left':  [50+tab_x, 65-tab_y],
            'bottom right': [60 ,70]}
        self.options_positions = {
            'top left':     [80+tab_x, 34],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        self.category_positions = {
            'top left':     [5, 34],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}

        # Set mutable copies of text positions
        self.cursor_position_mutable    = self.cursor_position[self.position].copy()
        self.options_positions_mutable  = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()

        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0,0)))
        pygame.draw.polygon(self.cursor_img, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
        
        # Initialize menu options
        self.header_render = pyg.font.render(self.header, True, pyg.white)
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
                elif event.key in pyg.key_LEFT:
                    if self.name == 'controls': self.set_controls('left')
                elif event.key in pyg.key_RIGHT:
                    if self.name == 'controls': self.set_controls('right')
                
                # Process selection or return to main menu
                elif event.key in pyg.key_ENTER:
                    
                    if self.name == 'save':
                        self.save_account()
                    elif self.name == 'load':
                        self.load_account()
                    
                    pyg.overlay = 'menu'
                    return

                # >>RESUME<<
                else:
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay = 'menu'
                        return None
                
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
                self.cursor_position_mutable[1] += tab_y * (len(set(self.options_categories)) - 1)
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] -= tab_y

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
                self.cursor_position_mutable[1] += tab_y

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
        
        # Update file menu
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
            with open(f"Data/File_{self.choice}/player_obj.pkl", 'wb') as file: pickle.dump(player_obj, file)
            
            # Take a screenshot for the load menu
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
            with open(f"Data/File_{self.choice}/player_obj.pkl", "rb") as file:
                player_obj = pickle.load(file)

            # Load cameras
            for env in player_obj.envs.values():
                if type(env) == list:
                    for sub_env in env: sub_env.camera = Camera(player_obj.ent)
                else:                   env.camera     = Camera(player_obj.ent)
            
            self.reset(self.name, self.header, self.options, self.options_categories, self.position, self.backgrounds)
            pyg.game_state = 'play_game'
            play_game_obj.fadein = None
            pyg.overlay = 'main_menu'

        # Turn on gui
        pyg.gui_toggle, pyg.msg_toggle = True, True

    def set_controls(self, direction):
        if pyg.controls_preset == 'numpad 1':
            if direction == 'right': pyg.set_controls('numpad 2')
            else:                    pyg.set_controls('arrows')
        elif pyg.controls_preset == 'numpad 2':
            if direction == 'right': pyg.set_controls('arrows')
            else:                    pyg.set_controls('numpad 1')
        elif pyg.controls_preset == 'arrows':
            if direction == 'right': pyg.set_controls('numpad 1')
            else:                    pyg.set_controls('numpad 2')
    
        self.options = [
            f"Move up:                                {pyg.key_UP[0]}                     Exit:                                         {pyg.key_BACK[0]}",
            f"Move down:                           {pyg.key_DOWN[0]}                     Activate 1:                             {pyg.key_ENTER[0]}",
            f"Move left:                               {pyg.key_LEFT[0]}                     Activate 2:                               {pyg.key_PERIOD[0]}",
            f"Move right:                            {pyg.key_RIGHT[0]}",
            "",
            
            f"Toggle inventory:                  {pyg.key_INV[0]}                     Enter combo:                         {pyg.key_HOLD[0]}",
            f"Toggle DevTools:                   {pyg.key_DEV[0]}                     Change speed:                      {pyg.key_SPEED[0]}",
            f"Toggle GUI:                            {pyg.key_GUI[0]}                     Zoom in:                                {pyg.key_PLUS[0]}",
            f"View stats:                             {pyg.key_INFO[0]}                     Zoom out:                              {pyg.key_MINUS[0]}",
            f"View questlog:                      {pyg.key_QUEST[0]}"]
    
        for i in range(len(self.options)):
            self.options_render[i] = pyg.font.render(self.options[i], True, pyg.gray)
    
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
                    self.options_positions_mutable[1] += tab_y
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
        player_obj.ent.last_env = player_obj.envs['garden']
        place_player(player_obj.envs['garden'], player_obj.envs['garden'].center)    # new game
        player_obj.ent.env.camera = Camera(player_obj.ent)
        player_obj.ent.env.camera.fixed = True
        player_obj.ent.env.camera.zoom_in(custom=1)
        
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
        
        # Triggers fadeout
        self.fadeout = False

        # Construct character creation level
        player_obj.envs['womb'] = build_womb()

    def run(self):
        mech.movement_speed(toggle=False, custom=2)
        env = player_obj.envs['womb']
        if player_obj.ent.env.name != env.name:
            place_player(env, env.center)
            render_all()
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # >>MAIN MENU<<
                if (event.key in pyg.key_BACK) and (time.time()-pyg.last_press_time > pyg.cooldown_time):
                    pyg.last_press_time = float(time.time())
                    
                    self.fadeout = False
                    if player_obj.ent.last_env.name == 'garden':
                        pyg.game_state = 'play_garden'
                        place_player(player_obj.envs['garden'], player_obj.envs['garden'].player_coordinates)
                    else:
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
                    elif self.choice == 3:
                        if player_obj.ent.img_names[0] == 'white':   player_obj.ent.img_names[0] = 'black'
                        elif player_obj.ent.img_names[0] == 'black': player_obj.ent.img_names[0] = 'white'
                    
                    # >>HANDEDNESS<<
                    elif self.choice == 4:
                        if player_obj.ent.handedness == 'left':
                            player_obj.ent.handedness = 'right'
                        elif player_obj.ent.handedness == 'right':
                            player_obj.ent.handedness = 'left'
                    
                    # >>ACCEPT<<
                    elif self.choice == 6:
                        pyg.startup_toggle = False
                        new_game_obj.new_game()
                        pyg.game_state = 'play_game'
                        self.fadeout = True
                        return
                    
                    # >>MAIN MENU<<
                    elif self.choice == 7:
                        self.fadeout = False
                        if player_obj.ent.last_env.name == 'garden':
                            pyg.game_state = 'play_garden'
                            place_player(player_obj.envs['garden'], player_obj.envs['garden'].player_coordinates)
                        else:
                            pyg.game_state = 'play_game'
                        pyg.overlay = 'menu'
                        return
                    
                    else:
                        pyg.game_state = 'play_game'
                        pyg.overlay = None
                        self.fadeout = False
                        return
        
        pyg.game_state = 'new_game'

    @debug_call
    def new_game(self):
        """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
            Called when starting a new game or loading a previous game.

            new:  creates player as Object with Fighter stats, calls make_home(), then loads initial inventory
            else: calls load_objects_from_file() to load player, inventory, and current floor """
        
        # Clear prior data
        if not player_obj.temp:
            player_obj.envs = {}
            player_obj.ents = {}
            questlog_obj = None
            player_obj.envs['garden'] = build_garden()
        
        else:
            player_obj.temp = False
        
        # Prepare player
        player_obj.ent.role         = 'player'
        player_obj.ent.img_names[1] = 'front'
        questlog_obj = BigMenu(
            name      = 'questlog',
            header    = "                                                        QUESTLOG", 
            options   = ["Test"])
        questlog_obj.init_questlog()        
        questlog_obj.init_gardenlog()
            
        player_obj.envs['home'] = build_home()
        env = player_obj.envs['home']
        
        # Create items
        if player_obj.ent.equipment['chest'].img_names[0] == 'bra': name = 'yellow dress'
        else: name = 'green clothes'
        clothes = create_item(name)
        hair    = create_item('bald')
        face    = create_item('clean')
        chest   = create_item('flat')
        shovel  = create_item('shovel')
        lamp    = create_item('lamp')
        
        clothes.pick_up(ent=player_obj.ent)
        hair.pick_up(ent=player_obj.ent)
        face.pick_up(ent=player_obj.ent)
        chest.pick_up(ent=player_obj.ent)
        shovel.pick_up(ent=player_obj.ent)
        lamp.pick_up(ent=player_obj.ent)
        
        clothes.toggle_equip(player_obj.ent)
        lamp.toggle_equip(player_obj.ent)
        shovel.durability = 20
        sort_inventory()
        
        # Prepare gui
        pyg.msg = []
        pyg.msg_history = {}
        pyg.msg_toggle = True
        pyg.gui_toggle = True

    def render(self):
        
        # Implement timed rotation of character
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = float(time.time()) 
            player_obj.ent.img_names[1] = self.orientations[self.orientations.index(player_obj.ent.img_names[1]) - 1]
        
        # Renders menu to update cursor location
        Y = self.top_choice[1] - 4
        for self.menu_choice in self.menu_choices:
            pyg.screen.blit(self.menu_choice, (80, Y))
            Y += 24
        pyg.screen.blit(self.cursor_img, self.cursor_pos)
        pyg.screen.blit(img.dict['floors']['dark green'], [player_obj.ent.tile.X, player_obj.ent.tile.Y])
        player_obj.ent.draw(pyg.screen, loc=[player_obj.ent.tile.X, player_obj.ent.tile.Y])
        
        if self.fadeout:
            self.fadeout = False
            text = "Your hands tremble, and the ground shudders in tune... something is not right."
            mech.enter_dungeon(text=text, lvl_num=4)

class PlayGame:

    def __init__(self):
        self.cooldown_time = 1
        self.last_press_time = 0
        self.gui_set = 0
        self.death_cooldown = 1
        
        self.fadein = "Your hands tremble, and the ground shudders in tune... something is not right."

    def run(self):
        active_effects()
        info_obj.update()
        
        player_obj.ent.role = 'player'
        mech.movement_speed(toggle=False)
        
        if pyg.overlay in [None, 'stats']:
            
            # Play game if alive
            if not player_obj.ent.dead:
                for event in pygame.event.get():

                    # Save and quit
                    if event.type == QUIT:
                        save_account()
                        pygame.quit()
                        sys.exit()
                    
                    # Keep playing
                    if event.type == KEYDOWN:
                        
                        # Movement
                        if event.key in pyg.key_UP:       self.key_UP()
                        elif event.key in pyg.key_DOWN:   self.key_DOWN()
                        elif event.key in pyg.key_LEFT:   self.key_LEFT()
                        elif event.key in pyg.key_RIGHT:  self.key_RIGHT()
                        
                        # Actions
                        elif event.key in pyg.key_ENTER:  self.key_ENTER()
                        elif event.key in pyg.key_GUI:    self.key_GUI()
                        elif event.key in pyg.key_PERIOD: self.key_PERIOD()
                        elif event.key in pyg.key_PLUS:   self.key_PLUS()
                        elif event.key in pyg.key_MINUS:  self.key_MINUS()
                        
                        # Menus
                        elif event.key in pyg.key_SPEED:  self.key_SPEED()
                        
                        # >>MAIN MENU<<
                        elif event.key in pyg.key_BACK:
                            
                            if pyg.overlay:
                                pyg.overlay = None
                            
                            elif time.time()-pyg.last_press_time > pyg.cooldown_time:
                                pyg.last_press_time = float(time.time())
                                pyg.overlay = 'menu'
                                pygame.event.clear()
                                return
            
                        # >>COMBOS<<
                        elif event.key in pyg.key_HOLD:
                            hold_obj.sequence_toggle = True
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
                            #trade_obj.ent = player_obj.ent
                            pyg.overlay = 'dev'
                            pygame.event.clear()
                            return
                
                        # >>STATS<<
                        elif event.key in pyg.key_INFO:
                            if pyg.overlay != 'stats':
                                small_menu.dic = info_obj.stats
                                pyg.overlay = 'stats'
                            else:
                                pyg.overlay = None
                            pygame.event.clear()
                            return
            
                        # >>QUESTLOG<<
                        elif event.key in pyg.key_QUEST:
                            questlog_obj.update_questlog()
                            pyg.overlay = 'questlog'
                            pygame.event.clear()
                            return
            
            # Handle player death
            else:
                env      = player_obj.ent.env
                last_env = player_obj.ent.last_env
                permadeath_locs = ['garden', 'home', 'overworld', 'cave', 'womb']
                drug_locs       = ['hallucination', 'bitworld']
                dream_locs      = ['dungeon']
                
                # Survive
                if env.name not in permadeath_locs:
                    
                    # Wait for animations to finish
                    if not img.render_log:
                        if not self.death_cooldown:
                        
                            # Restore player state
                            player_obj.ent.dead = False
                            pyg.gui             = {}
                            pyg.msg             = []
                            pyg.msg_history     = {}
                            mech.movement_speed(toggle=False, custom=0)
                            self.death_cooldown = 5
                            
                            # Regain consciousness
                            if env.name in drug_locs:
                                player_obj.ent.hp = player_obj.ent.max_hp // 2
                                self.fadein = "Delirium passes, but nausea remains."
                            
                            # Wake up at home
                            elif env.name in dream_locs:
                                player_obj.ent.hp = player_obj.ent.max_hp
                                self.fadein = "Your cling to life has slipped, yet you wake unscarred in bed."
                            
                            else:
                                player_obj.ent.hp = player_obj.ent.max_hp
                                self.fadein = "???"
                            
                            if last_env.name in ['garden', 'womb']: last_env = player_obj.envs['home']
                            pyg.overlay = None
                            pyg.fadeout_screen(
                                screen  = pyg.screen,
                                fade_in = False,
                                env     = last_env,
                                loc     = last_env.player_coordinates,
                                text    = self.fadein)
                            img.render_fx = None
                            pygame.event.clear()
                        
                        else: self.death_cooldown -= 1
                
                # End the game
                else:
                    
                    for event in pygame.event.get():
                        
                        # Restrict movement speed
                        mech.movement_speed(toggle=False, custom=2)
                        
                        # Menus
                        if event.type == KEYDOWN:
                            
                            # >>MAIN MENU<<
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
                            
                            # >>STATS<<
                            elif event.key in pyg.key_INFO:
                                if pyg.overlay != 'stats':
                                    small_menu.dic = info_obj.stats
                                    pyg.overlay = 'stats'
                                else:
                                    pyg.overlay = None
                                pygame.event.clear()
                            
                            # >>QUESTLOG<<
                            elif event.key in pyg.key_QUEST:
                                questlog_obj.update_questlog()
                                pyg.overlay = 'questlog'
                                pygame.event.clear()
                                return
                            
                            # Other
                            elif event.key in pyg.key_SPEED:  self.key_SPEED()
        
        for entity in player_obj.ent.env.entities: entity.ai()
        
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
            
            # >>PICKUP/STAIRS<<
            # Check if an item is under the player
            if player_obj.ent.tile.item:
                tile = player_obj.ent.tile
                
                # Activate entryway
                if tile.item.name == 'dungeon':     mech.enter_dungeon()
                elif tile.item.name == 'cave':      mech.enter_cave()
                elif tile.item.name == 'overworld': mech.enter_overworld()
                elif tile.item.name == 'home':      mech.enter_home()
                
                # Activate bed
                elif tile.item.name in ['red bed', 'purple bed']:
                    
                    # Check if it is the player's bed
                    if tile.room:
                        if tile.room.name == 'home room':
                            
                            # Go to sleep if it's not daytime
                            if player_obj.ent.env.env_time in [1, 2, 7, 8]:
                                player_obj.ent.env.env_time = (player_obj.ent.env.env_time + 3) % 8
                                mech.enter_dungeon(text="The evening dims to night... sleep trustly follows.")
                            else: pyg.update_gui("Time to face the day.", pyg.dark_gray)
                        
                        # No sleeping in owned beds
                        else: pyg.update_gui("This is not your bed.", pyg.dark_gray)
                    
                    else: pyg.update_gui("This is not your bed.", pyg.dark_gray)
                
                # Activate chair
                elif tile.item.name in ['red chair left', 'red chair right']:
                    player_obj.ent.env.weather.set_day_and_time(increment=True)
                    pyg.update_gui("You sit down to rest for a while.", pyg.dark_gray)
                
                # Pick up or activate
                else: player_obj.ent.tile.item.pick_up()

    def key_GUI(self):
        
        # >>TOGGLE GUI<<
        self.gui_set = (self.gui_set + 1) % 4
        
        # Show all
        if self.gui_set == 0:
            pyg.gui_toggle = True
            pyg.msg_toggle = True
        
        # Hide GUI
        elif self.gui_set == 1:
            pyg.gui_toggle = False
            pyg.msg_toggle = True
        
        # Hide both
        elif self.gui_set == 2:
            pyg.gui_toggle = False
            pyg.msg_toggle = False

        # Hide messages
        elif self.gui_set == 3:
            pyg.gui_toggle = True
            pyg.msg_toggle = False

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

    def key_PLUS(self):
        
        # >>ZOOM<<
        player_obj.ent.env.camera.zoom_in()

    def key_MINUS(self):
        
        # >>ZOOM<<
        player_obj.ent.env.camera.zoom_out()

    def key_SPEED(self):
        
        # >>MOVEMENT SPEED<<
        if time.time()-pyg.last_press_time > pyg.cooldown_time:
            pyg.last_press_time = float(time.time())
            mech.movement_speed()

    def render(self):
        pyg.msg_height = 4
        if not pyg.overlay: pyg.update_gui()
        render_all()
        
        if self.fadein:
            pyg.fadeout_screen(
                screen  = pyg.screen,
                fade_in = True,
                text    = self.fadein)
            self.fadein = False

class PlayGarden:

    def run(self):
        
        # Update pets and quests
        pet_obj.update()
        
        # Active or deactivate AI
        if pyg.overlay == 'menu': player_obj.ent.role = 'NPC'
        else:                     player_obj.ent.role = 'player'
        
        # Set camera and movement speed
        player_obj.envs['garden'].camera.zoom_in(custom=1)
        mech.movement_speed(toggle=False, custom=2)
        
        # Handle input
        if pyg.overlay in [None, 'stats']:
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
                        if event.key in pyg.key_UP:       self.key_UP()
                        elif event.key in pyg.key_DOWN:   self.key_DOWN()
                        elif event.key in pyg.key_LEFT:   self.key_LEFT()
                        elif event.key in pyg.key_RIGHT:  self.key_RIGHT()
                        
                        # Actions
                        elif event.key in pyg.key_ENTER:  self.key_ENTER()
                        elif event.key in pyg.key_PERIOD: self.key_PERIOD()
                        
                        # Menus
                        elif event.key in pyg.key_SPEED:  self.key_SPEED()
                        
                        # >>MAIN MENU<<
                        elif event.key in pyg.key_BACK:
                            
                            if pyg.overlay == 'stats':
                                pyg.overlay = None
                            
                            elif time.time()-pyg.last_press_time > pyg.cooldown_time:
                                pyg.last_press_time = float(time.time())
                                pyg.overlay = 'menu'
                                pygame.event.clear()
                                return
                        
                        # >>COMBOS<<
                        elif event.key in pyg.key_HOLD:
                            hold_obj.sequence_toggle = True
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
                            pyg.overlay = 'dev'
                            pygame.event.clear()
                            return
                
                        # >>STATS<<
                        elif event.key in pyg.key_INFO:
                            if pyg.overlay != 'stats':
                                small_menu.dic = pet_obj.stats
                                pyg.overlay = 'stats'
                            else:
                                pyg.overlay = None
                            pygame.event.clear()
                            return
                
                        # >>QUESTLOG<<
                        elif event.key in pyg.key_QUEST:
                            questlog_obj.update_questlog(questlog = player_obj.ent.gardenlog)
                            pyg.overlay = 'questlog'
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

    def key_SPEED(self):

        # >>MOVEMENT SPEED<<
        if time.time()-pyg.last_press_time > pyg.cooldown_time:
            pyg.last_press_time = float(time.time())
            mech.movement_speed()

    def render(self):
        pyg.msg_toggle = False
        pyg.gui_toggle = False
        render_all()

## Side bars
class DevTools:
    
    def __init__(self):
        """ Parameters
            ----------
            dic_indices    : list of tuples of ints; one tuple for each category; offset and item index
            dic_index      : int; selects a tuple in dic_indices
            dic_categories : list of str; name of each category in dic_indices """
        
        # Design
        self.cursor_pos = [pyg.screen_width-pyg.tile_width, 32]
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))
        
        # Item management
        self.img_names = ['null', 'null']
        self.img_x = 0
        self.img_y = 0
        self.locked = False
        self.update_dict()

    def run(self):  
        """ Handles side menu for placing objects. """        
        
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
        self.dic    = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
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
                        if not self.locked:
                            self.dic_index -= 1
                            self.dic = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                            while not len(self.dic):
                                self.dic_index -= 1
                                self.dic = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                        else: player_obj.ent.move(-pyg.tile_height, 0)
                        
                    elif event.key in pyg.key_RIGHT:
                        if not self.locked:
                            self.dic_index += 1
                            self.dic = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                            while not len(self.dic):
                                self.dic_index += 1
                                self.dic = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                        else: player_obj.ent.move(pyg.tile_width, 0)
                    
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

    def update_dict(self):
        
        # Dictionary management
        self.dic_categories = list(player_obj.ent.discoveries.keys())
        self.dic_index = 0
        self.dic = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]] # {first name: {second name: surface}}
        while not len(self.dic):
            self.dic_index += 1
            self.dic = player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        self.dic_indices = [[0, 0] for _ in self.dic_categories]

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
            obj = player_obj.ent.env.map[self.img_x][self.img_y]
            obj.placed = True
            place_object(
                obj = obj,
                loc = [self.img_x, self.img_y],
                env = player_obj.ent.env,
                names = self.img_names.copy())
            self.build_room(obj)
        
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
        elif self.img_names[1] not in img.ent_names:
            item = create_item(
                names = self.img_names)
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = player_obj.ent.env,
                names = self.img_names.copy())
            if item.img_names[0] == 'stairs':
                item.tile.blocked = False
        
        else:
            ent = create_entity(
                names = self.img_names[1])
            place_object(
                obj   = ent,
                loc   = [self.img_x, self.img_y],
                env   = player_obj.ent.env,
                names = self.img_names.copy())
        
        self.img_x, self.img_y = None, None
        pyg.overlay = None

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
                name    = 'placed',
                env     = player_obj.ent.env,
                x1      = min_x,
                y1      = min_y,
                width   = int(max_x - min_x),
                height  = int(max_y - min_y),
                biome   = 'city',
                hidden  = False,
                objects = True,
                floor   = player_obj.ent.env.floors,
                walls   = player_obj.ent.env.walls,
                roof    = player_obj.ent.env.roofs,
                boundary = boundary)
    
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
        if not self.locked: pyg.screen.blit(self.background_fade, (0, 0))
        
        pyg.msg_height = 1
        pyg.update_gui()
        
        pyg.screen.blit(self.cursor_fill, self.cursor_pos)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                img_names = self.dic[list(self.dic.keys())[(i+self.offset)%len(self.dic)]]
                pyg.screen.blit(img.dict[img_names[0]][img_names[1]], (pyg.screen_width-pyg.tile_width, Y))
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
        
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def update_data(self):
        
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
        if self.dic_indices:
            self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
            self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
            self.dic    = self.inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        else: pyg.overlay = None

    def run(self):
        
        # Restrict movement speed
        mech.movement_speed(toggle=False, custom=2)
        
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
                    if len(self.dic_categories) > 1:
                        
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
            if self.dic_indices:
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
            
            if type(offset) == int: item = filtered_list[offset%len(filtered_list)]
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
        if not self.locked: pyg.screen.blit(self.background_fade, (0, 0))
        
        # Basics
        pyg.msg_height = 1
        pyg.update_gui()
        
        if self.cursor_pos[1] < 32: self.cursor_pos[1] = 32
        pyg.screen.blit(self.cursor_fill, self.cursor_pos)
        img.average()
        color = pygame.Color(img.left_correct, img.left_correct, img.left_correct)
        
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
                        self.menu_choices_surfaces.append(
                            pyg.minifont.render(self.menu_choices[i], True, color))
                    
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
        """ Shows a sidebar menu when a key is held down, then processes input as a combo.
            Options are based on the player's effects, which are managed in Player. 
            
            Parameters
            ----------
            cursor_pos      : list of two ints; top left corner of the cursor; first value changed by self.run() in multiples of 32
            dic_indices     : list of lists of two ints; offset from wraparound, and choice index from cursor; one for each dictionary
            
            sequence_toggle : bool; True when the botton is held down
            keys            : list of key codes; sets which keys count as a combo
            key_sequence    : three csv strings in [⮜, ⮟, ⮞, ⮝]; combo set in self.run() and cleared after some time
            cooldown_time   : float; the time before the sequence is automatically cleared
            last_press_time : float; the last time the sequence was cleared
            
            detail          : bool; toggles descriptions; altered in self.run() """
        
        # Cursor and position saving
        self.dic_indices = [[0, 0]]
        
        # Combo sequences
        self.sequence_toggle = True
        self.keys            = pyg.key_LEFT + pyg.key_DOWN + pyg.key_RIGHT
        self.key_sequence    = []
        self.cooldown_time   = 0.5
        self.last_press_time = 0
        
        # GUI
        self.detail = True

    def run(self):
        """ Processes input sequences while a key is held down. """
        
        # Restrict movement speed
        mech.movement_speed(toggle=False, custom=2)
        
        # Generate cursor and dictionaries
        self.update_data()
        
        # Handle keystrokes
        for event in pygame.event.get():
            
            # Clear sequence after some time
            if time.time()-self.last_press_time > self.cooldown_time:
                self.last_press_time = time.time()
                self.key_sequence    = []
            
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
        """ Sets dictionary for icons and restores location. """
        
        # Finds images and sequences of player effects, then saves them in a dictionary
        inventory_dics      = {'effects': {}}
        self.dic_categories = ['effects']
        self.sequences      = {}
        for effect in player_obj.ent.effects:
            if effect.sequence:
                inventory_dics['effects'][effect.name] = img.dict[effect.img_names[0]][effect.img_names[1]]
                self.sequences[effect.name] = effect.sequence
        
        # Restore last selection
        if len(self.dic_indices) != len(self.dic_categories):
            self.dic_indices = [[0, 0] for _ in self.dic_categories]
        self.dic = inventory_dics[self.dic_categories[0]]

    def check_sequence(self, sequence_string):
        
        # Look through item effects
        for effect in player_obj.ent.effects:
            if effect.sequence == sequence_string:
                if time.time()-effect.last_press_time > effect.cooldown_time:
                    effect.last_press_time = float(time.time())
                    effect.function()
                    return

    def render(self):
        pyg.msg_height = 1
        pyg.update_gui()
        
        img.average()
        color = pygame.Color(img.left_correct, img.left_correct, img.left_correct)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                effects_list = list(self.dic.keys())
                effect_name  = effects_list[i%len(self.dic)]
                
                # Render details
                if self.detail:
                    Y_cache = int(Y)

                    self.menu_choices = [effect_name, self.sequences[effect_name]]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(
                            pyg.minifont.render(self.menu_choices[i], True, color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.screen.blit(menu_choice_surface, (40, Y_cache))
                        Y_cache += 12
                
                # Render image
                pyg.screen.blit(self.dic[effect_name], (0, Y))
                Y += pyg.tile_height
                counter += 1
            
            else: break

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

        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def run(self):
        
        # Restrict movement speed
        mech.movement_speed(toggle=False, custom=2)
        
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
        
        # Apply background fade
        pyg.screen.blit(self.background_fade, (0, 0))
        
        # Basics
        pyg.msg_height = 1
        pyg.update_gui()
        
        # Cursor background and font colors
        img.average()
        if self.menu_toggle == 'right':
            left_color  = pygame.Color(img.left_correct - 20, img.left_correct - 20, img.left_correct - 20)
            right_color = pygame.Color(img.right_correct, img.right_correct, img.right_correct)
            pyg.screen.blit(self.cursor_fill_bnm, self.cursor_pos_bnm)
        else:
            left_color  = pygame.Color(img.left_correct, img.left_correct, img.left_correct)
            right_color = pygame.Color(img.right_correct - 20, img.right_correct - 20, img.right_correct - 20)
            pyg.screen.blit(self.cursor_fill, self.cursor_pos)
        
        ## Player's inventory
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
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, left_color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.screen.blit(menu_choice_surface, (40, Y_detail))
                        Y_detail += 12
                
                # Render image
                pyg.screen.blit(self.dic[item_name][0], (0, Y))
                Y += pyg.tile_height
                counter += 1                
            else: break
        
        ## Trader's inventory
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
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, right_color))
                    
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

## Overlays
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
        
        img.average()
        self.color = pygame.Color(img.menu_correct, img.menu_correct, img.menu_correct)
        for i in range(len(self.menu_choices)):
            self.menu_choices_surfaces.append(pyg.font.render(self.menu_choices[i], True, self.color))
        self.choice, self.choices_length = 0, len(self.menu_choices) - 1
        
        # Allows access to garden
        self.menu_toggle = True
        
        # Other
        self.last_press_time, self.cooldown_time = 0, 0.5
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

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
            self.menu_choices_surfaces[2] = pyg.font.render(self.menu_choices[2], True, self.color)

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
                elif event.key in pyg.key_HOLD:   self.key_HOLD()
                elif event.key in pyg.key_INFO:   self.key_INFO()
                
                # >>RESUME<<
                elif event.key in pyg.key_BACK:
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay = None
                        return
                
                # Select option
                elif event.key in pyg.key_ENTER:
                    
                    # >>NEW GAME<<
                    if self.choice == 0:
                        pyg.game_state = 'new_game'
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
        if pyg.frame:
            pygame.display.set_mode((pyg.screen_width, pyg.screen_height), pygame.NOFRAME)
            pyg.frame = False
        else:
            pygame.display.set_mode((pyg.screen_width, pyg.screen_height))
            pyg.frame = True

    def key_DEV(self):
        aud.play_track()

    def render(self):
        
        # Apply background fade
        pyg.screen.blit(self.background_fade, (0, 0))
        
        # Blit menu options
        Y = 316
        
        self.menu_choices_surfaces = []
        
        img.average()
        #self.color = pygame.Color(img.menu_correct, img.menu_correct, img.menu_correct)
        self.color = pygame.Color(255-img.bottom_color[0], 255-img.bottom_color[1], 255-img.bottom_color[2])
        for i in range(len(self.menu_choices)):
            if (i == 2) and pyg.startup_toggle:
                color = pyg.dark_gray
            else: color = self.color
            self.menu_choices_surfaces.append(pyg.font.render(self.menu_choices[i], True, color))
        for menu_choice_surface in self.menu_choices_surfaces:
            pyg.screen.blit(menu_choice_surface, (48, Y))
            Y += 24
        
        # Blit cursor
        pygame.draw.polygon(self.cursor_img, self.color, [(5, 3), (10, 7), (5, 11)], 0)
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

class BigMenu:

    def __init__(self, name, header, options, options_categories=None, position='top left'):
        """ IMPORTANT. Creates cursor, background, and menu options, then returns index of choice.

            header             : string; top line of text
            options            : list of strings; menu choices
            options_categories : list of strings; categorization; same length as options
            position           : chooses layout preset """
        
        # Basics
        self.name               = name
        self.header             = header
        self.options            = options
        self.options_categories = options_categories
        self.position           = position
        
        # Initialize temporary data containers
        self.choice                   = 0                   # holds index of option pointed at by cursor
        self.choices_length           = len(self.options)-1 # number of choices
        self.options_categories_cache = ''                  # holds current category
        self.options_render           = self.options.copy()
        
        # Alter layout if categories are present
        if self.options_categories: 
            self.tab_x, self.tab_y = 70, 10
            self.options_categories_cache_2 = self.options_categories[0]
        else:
            self.tab_x, self.tab_y = 0, 0

        # Set initial position of each text type
        self.header_position = {
            'top left':     [5+32, 32],
            'center':       [pyg.screen_width//2, 85],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        self.cursor_position = {
            'top left':     [43+self.tab_x, 27+32+self.tab_y],
            'center':       [50, 300],
            'bottom left':  [50+self.tab_x, 65-self.tab_y],
            'bottom right': [60 ,70]}
        self.options_positions = {
            'top left':     [pyg.tile_height*3+self.tab_x-34, 22+32],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        self.category_positions = {
            'top left':     [pyg.tile_height+pyg.tile_height // 4, 22+32],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        
        # Set mutable copies of text positions
        self.cursor_position_mutable    = copy.deepcopy(self.cursor_position[self.position])
        self.options_positions_mutable  = copy.deepcopy(self.options_positions[self.position])
        self.category_positions_mutable = copy.deepcopy(self.category_positions[self.position])
        
        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, pyg.gray, [(5, 3), (10, 7), (5, 11)], 0)
        
        # Initialize menu options
        self.header_render = pyg.font.render(self.header, True, pyg.white)
        for i in range(len(self.options)):
            color = pyg.gray
            self.options_render[i] = pyg.font.render(options[i], True, color)
        
        # GUI
        self.msg_toggle = None
        self.gui_toggle = None
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))
        
        # Other
        self.questlog_header = "                                                        QUESTLOG"

    def reset(self, name, header, options, options_categories, position):
        choice_cache = self.choice
        cursor_pos_cache = self.cursor_position_mutable.copy()
        
        self.__init__(name, header, options, options_categories, position)
        
        self.choice = choice_cache
        self.cursor_position_mutable = self.cursor_position[self.position].copy()
        
        if self.header == self.questlog_header:
            self.cursor_position_mutable[1] += self.choice * 16
            
            # Handle additional spacing for categories
            if self.options_categories:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                for i in range(self.choice+1):  # Adjust for category shifts
                    if i > 0 and self.options_categories[i] != self.options_categories[i - 1]:
                        self.cursor_position_mutable[1] += self.tab_y

    def run(self):
        mech.movement_speed(toggle=False, custom=2)
        
        # Save gui settings before clearing the screen
        if self.msg_toggle is None:
            self.msg_toggle = pyg.msg_toggle
            self.gui_toggle = pyg.gui_toggle
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                
                # Navigation
                if event.key in pyg.key_UP:
                    if self.header == self.questlog_header: self.key_UP()
                elif event.key in pyg.key_DOWN:
                    if self.header == self.questlog_header: self.key_DOWN()
                
                # Handle selection
                elif event.key in (pyg.key_ENTER + pyg.key_LEFT + pyg.key_RIGHT):
                    
                    # >>TEXT MENU<<
                    if self.name == 'temp':
                        pyg.overlay = None
                        return
                    
                    # >>QUESTLOG<<
                    elif self.name == 'questlog':
                        
                        # Selected quest
                        if self.header == self.questlog_header:
                            
                            # Select questlog or gardenlog
                            if pyg.game_state != 'play_garden':
                                self.selected_quest = player_obj.ent.questlog[list(player_obj.ent.questlog.keys())[self.choice]]
                            else:
                                self.selected_quest = player_obj.ent.gardenlog[list(player_obj.ent.gardenlog.keys())[self.choice]]
                            
                            # Set new values to be displayed
                            self.reset(
                                name               = 'questlog',
                                header             = self.selected_quest.name,
                                options            = self.selected_quest.content,
                                options_categories = self.selected_quest.categories,
                                position           = self.position)
                        
                        # Full questlog
                        else:
                            
                            # Select questlog or gardenlog
                            if pyg.game_state != 'play_garden': options = list(player_obj.ent.questlog.keys())
                            else:                               options = list(player_obj.ent.gardenlog.keys())
                            
                            self.reset(
                                name      = 'questlog',
                                header    = self.questlog_header,
                                options   = options,
                                options_categories = self.categories,
                                position = self.position)
                    
                else:
                    pyg.overlay     = None
                    pyg.msg_toggle  = self.msg_toggle
                    pyg.gui_toggle  = self.gui_toggle
                    self.msg_toggle = None
                    self.gui_toggle = None
                    return

        pyg.overlay = copy.copy(self.name)
        return

    def key_UP(self):

        # >>SELECT MENU ITEM<<        
        # Move cursor up
        self.cursor_position_mutable[1]     -= 16
        self.choice                         -= 1
        
        # Move to lowest option
        if self.choice < 0:
            self.choice                     = self.choices_length
            self.cursor_position_mutable[1] = self.cursor_position[self.position][1] + (len(self.options)-1) * 16
            if self.options_categories:
                self.cursor_position_mutable[1] += self.tab_y * (len(set(self.options_categories)) - 1)
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] -= self.tab_y

    def key_DOWN(self):

        # >>SELECT MENU ITEM<<        
        # Move cursor down
        self.cursor_position_mutable[1]     += 16
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
                self.cursor_position_mutable[1] += self.tab_y

    def init_questlog(self):
        """ Sets intro quests and updates menu. Only runs once when a new game is started.

            quests          : list of Quest objects
            quest_names     : list of strings
            categories      : list of strings; 'main' or 'side'
            main_quests     : list of Quest objects
            side_quests     : list of Quest objects
            selected_quest  : Quest object
            
            menu_index      : int; toggles questlog pages """
        
        # Initialize parameters
        self.menu_index = 0
        
        # Create default quests
        gathering_supplies = Quest(
            name='Gathering supplies',
            notes=['My bag is nearly empty.',
                   'It would be good to have some items on hand.'],
            tasks=['☐ Collect 3 potions.',
                   '☐ Find a spare shovel.'],
            category='Main')

        finding_a_future = Quest(
            name='Finding a future',
            notes=['I should make my way into town.'],
            tasks=['☐ Wander east.'],
            category='Main')
        
        furnishing_a_home = Quest(
            name='Furnishing a home',
            notes=['My house is empty. Maybe I can spruce it up.'],
            tasks=['☐ Use the shovel to build new rooms.',
                   '☐ Drop items to be saved for later use.',
                   '☐ Look for anything interesting.'],
            category='Side')
        
        gathering_supplies.content = gathering_supplies.notes + gathering_supplies.tasks
        finding_a_future.content   = finding_a_future.notes + finding_a_future.tasks
        furnishing_a_home.content  = furnishing_a_home.notes + furnishing_a_home.tasks

        player_obj.ent.questlog = {
            gathering_supplies.name: gathering_supplies,
            finding_a_future.name:   finding_a_future,
            furnishing_a_home.name:  furnishing_a_home}
        self.update_questlog()

    def init_gardenlog(self):
        
        # Initialize parameters
        self.menu_index = 0
        
        # Create default quests
        water = Quest(
            name='Leading a radix to water',
            notes=['These odd beings seem thirsty.',
                   'I should pour out some water for them.'],
            tasks=['☐ Empty your jug of water.',
                   '☐ Make a radix drink.'],
            category='Main')

        food = Quest(
            name='Fruit of the earth',
            notes=['Set out some food.'],
            tasks=['☐ Get a radix to eat.'],
            category='Main')
        
        building_shelter = Quest(
            name='Build a house',
            notes=['Shelter would be nice.'],
            tasks=['☐ Contruct walls.',
                   '☐ Set a floor.',
                   '☐ Decorate.'],
            category='Side')
        
        water.content = water.notes + water.tasks
        food.content   = food.notes + food.tasks
        building_shelter.content  = building_shelter.notes + building_shelter.tasks

        player_obj.ent.gardenlog = {
            water.name: water,
            food.name:   food,
            building_shelter.name:  building_shelter}
        self.update_questlog()

    def update_questlog(self, name=None, questlog=None):
        """ Updates and sorts main quests and side quests. """
        
        if not questlog: questlog = player_obj.ent.questlog
        
        ## Look for completed tasks and quests
        if name:
            quest = questlog[name]
            
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
                del questlog[quest.name]
        
        ## Sort quests
        self.main_quests = []
        self.side_quests = []
        self.categories  = []
        quests_cache     = {}
        
        # Find main quests
        for quest in questlog.values():
            if not quest.finished:
                if quest.category == 'Main':
                    quests_cache[quest.name] = quest
                    self.main_quests.append(quest)
                    self.categories.append(quest.category)
        
        # Find side quests
        for quest in questlog.values():
            if not quest.finished:
                if quest.category == 'Side':
                    quests_cache[quest.name] = quest
                    self.side_quests.append(quest)
                    self.categories.append(quest.category)
        questlog = quests_cache
        self.reset(
            name      = 'questlog',
            header    = "                                                        QUESTLOG", 
            options   = list(questlog.keys()),
            options_categories = self.categories,
            position = self.position)

    def render(self):
        
        # Apply background fade
        pyg.screen.blit(self.background_fade, (0, 0))
        
        ## Update tiles
        if self.msg_toggle is not None:
            pyg.msg_toggle = False
            pyg.gui_toggle = False
        pyg.update_gui()
        render_all()
        if player_obj.ent.env.name != 'garden': player_obj.ent.env.weather.render()
        
        ## Render background
        fill_width  = pyg.tile_width  * 18
        fill_height = pyg.tile_height * 13
        self.backdrop = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.backdrop.fill((0, 0, 0, 128))
        pyg.screen.blit(self.backdrop, (32, 32))
        
        # Render border
        self.cursor_border = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.backdrop.fill((0, 0, 0, 128))
        pygame.draw.polygon(
            self.cursor_border, 
            pyg.gray,
            [(0, 0),
             (fill_width-1, 0),
             (fill_width-1, fill_height-1),
             (0, fill_height-1)], 1)
        pyg.screen.blit(self.cursor_border, (32, 32))
        
        # Render header and cursor
        pyg.screen.blit(self.header_render, self.header_position[self.position])
        if self.header == self.questlog_header:
            pyg.screen.blit(self.cursor_img, self.cursor_position_mutable)
        
        ## Render categories and options
        for i in range(len(self.options_render)):
            
            # Render category text if it is not present 
            if self.options_categories:
                if self.options_categories[i] != self.options_categories_cache:
                    self.options_categories_cache = self.options_categories[i]
                    text = pyg.font.render(f'{self.options_categories_cache.lower()}', True, pyg.gray)
                    self.options_positions_mutable[1] += self.tab_y
                    pyg.screen.blit(text, (self.category_positions_mutable[0], self.options_positions_mutable[1]))
                
            # Render option text
            pyg.screen.blit(self.options_render[i], self.options_positions_mutable)
            self.options_positions_mutable[1] += pyg.tile_height//2
        self.options_positions_mutable = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()
        pygame.display.flip()

class SmallMenu:
    
    def render(self):
        pyg.msg_height = 1
        pyg.update_gui()
        render_all()
        if player_obj.ent.env.name != 'garden': player_obj.ent.env.weather.render()
        
        # Render background
        fill_width  = pyg.tile_width  * 5 + pyg.tile_width // 2
        fill_height = pyg.tile_height * 3 + pyg.tile_height // 2
        self.cursor_fill   = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.cursor_fill.fill((0, 0, 0, 128))
        pyg.screen.blit(self.cursor_fill, (32, 32))
        
        # Render border
        self.cursor_border = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.cursor_fill.fill((0, 0, 0, 128))
        pygame.draw.polygon(
            self.cursor_border, 
            pyg.gray, 
            [(0, 0),
             (fill_width-1, 0),
             (fill_width-1, fill_height-1),
             (0, fill_height-1)], 1)
        pyg.screen.blit(self.cursor_border, (32, 32))
        
        # Render items
        Y = 32
        for i in range(len(list(self.dic))):
            X1 = pyg.tile_height + pyg.tile_height // 4
            X2 = pyg.tile_height * 4
            key, val = list(self.dic.items())[i]
            key = pyg.font.render(key, True, pyg.gray)
            val = pyg.font.render(val, True, pyg.gray)
            pyg.screen.blit(key, (X1, Y))
            pyg.screen.blit(val, (X2, Y))
            Y += pyg.tile_height//2

class Info:
    """ Manages stats in the Garden. """

    def __init__(self):

        self.stats = {
            'Character Information': None,
            '': None,
            'rank':       None,
            'rigor':      None,
            'attack':     None,
            'defense':    None}

    def update(self):

        self.stats['rank']  = '★' * int(player_obj.ent.rank)
        if len(self.stats['rank']) < 5:
            while len(self.stats['rank']) < 5:
                self.stats['rank'] += '☆'
            
        self.stats['rigor']   = '★' * int(player_obj.ent.max_hp // 10)
        if len(self.stats['rigor']) < 5:
            while len(self.stats['rigor']) < 5:
                self.stats['rigor'] += '☆'
        
        self.stats['attack']   = '★' * int(player_obj.ent.attack // 10)
        if len(self.stats['attack']) < 5:
            while len(self.stats['attack']) < 5:
                self.stats['attack'] += '☆'
        
        self.stats['defense']   = '★' * int(player_obj.ent.defense // 10)
        if len(self.stats['defense']) < 5:
            while len(self.stats['defense']) < 5:
                self.stats['defense'] += '☆'

class Pets:
    """ Manages stats in the Garden. """

    def __init__(self):
        
        # General
        self.ents = player_obj.envs['garden'].entities
        
        self.stats = {
            '      RADIX ATRIUM': None,
            '': None,
            'mood':     None,
            'stamina':  None,
            'strength': None,
            'appeal':   None}
        
        # Numerical stats
        self.levels = {
            'stamina':  0,
            'strength': 1,
            'appeal':   1}
        
        self.moods = {
            'happiness': 5,
            'sadness':   0,
            'anger':     0,
            'boredom':   0,
            'lethargy':  0,
            'confusion': 0}
        
        # String conversions
        self.faces = {
            'happiness': '( ^_^ )',
            'sadness':   '( Q_Q )',
            'anger':     '( >_< )',
            'boredom':   '( . _ .  )',
            'lethargy':  '( =_= )',
            'confusion': '(@_@)'}
        
        # Utility
        self.happiness_cooldown = 10
        self.happiness_press = 0
        self.emoji_cooldown = 10
        self.emoji_press = 0

    def import_pets(self):
        self.ents = player_obj.envs['garden'].entities

    def stat_check(self, dic):
        for key, value in dic.items():
            if value > 10:  dic[key] = 10
            elif value < 0: dic[key] = 0

    def update(self):
        
        ## Lose happiness
        if self.moods['happiness']:
            if time.time() - self.happiness_press > self.happiness_cooldown:
                self.happiness_press = time.time()
                
                if not random.randint(0, 1):
                    self.moods['happiness'] -= 1
                    self.moods[random.choice(list(self.moods.keys()))] += 1
        
        # Clean up
        self.stat_check(self.levels)
        self.stat_check(self.moods)
        
        ## Set mood
        max_val = max(self.moods.values())
        current_moods = [mood for mood, val in self.moods.items() if val == max_val]
        
        # Alternate between tied moods
        if len(current_moods) > 1:
            if time.time() - self.emoji_press > self.emoji_cooldown:
                self.emoji_press = time.time()
                self.stats['mood'] = self.faces[random.choice(current_moods)]        
        
        # Set the current mood
        else:
            self.stats['mood'] = self.faces[current_moods[0]]
        
        # Apply mood effects
        if self.moods['happiness'] <= 2:
            if self.ents[-1].img_names[0] != 'purple radish':
                for ent in self.ents:
                    if ent != player_obj.ent:
                        if ent.img_names[0] != 'purple radish':
                            ent.img_names[0] = 'purple radish'
        elif self.moods['happiness'] >= 8:
            if self.ents[-1].img_names[0] != 'orange radish':
                for ent in self.ents:
                    if ent != player_obj.ent:
                        if ent.img_names[0] != 'orange radish':
                            ent.img_names[0] = 'orange radish'
        else:
            if self.ents[-1].img_names[0] != 'red radish':
                for ent in self.ents:
                    if ent != player_obj.ent:
                        if ent.img_names[0] != 'red radish':
                            ent.img_names[0] = 'red radish'
        
        ## Set levels
        self.stats['stamina']  = '★' * self.levels['stamina']
        while len(self.stats['stamina']) < 5:
            self.stats['stamina'] += '☆'
        self.stats['strength'] = '★' * self.levels['strength']
        while len(self.stats['strength']) < 5:
            self.stats['strength'] += '☆'
        self.stats['appeal']   = '★' * self.levels['appeal']
        while len(self.stats['appeal']) < 5:
            self.stats['appeal'] += '☆'

class Weather:

    def __init__(self, light_set=None, clouds=True):
        
        # Dark blue background
        self.overlay = pygame.Surface((pyg.screen_width * 10, pyg.screen_height * 10), pygame.SRCALPHA)
        
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
            player_obj.ent.env.env_date = ((player_obj.ent.env.env_date+1) % 8) + 1
        
        # Set time of day
        if int(time.localtime().tm_min / 10) != self.last_min:
            self.last_min = int(time.localtime().tm_min / 10)
            player_obj.ent.env.env_time = (player_obj.ent.env.env_time + 1) % 8
        
        # Change the weather
        if self.light_set is None:
            
            # Make days bright and nights dark
            self.change_brightness()
            
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
            if day is not None:  player_obj.ent.env.env_date = (day % 8) + 1
            if time is not None: player_obj.ent.env.env_time = time % 8
        
        # Move forwards in time by one step
        else: player_obj.ent.env.env_time = (player_obj.ent.env.env_time + 1) % 8

    def change_brightness(self):
        if player_obj.ent.env.env_time == 0:   alpha = 170 # 🌖
        elif player_obj.ent.env.env_time == 1: alpha = 85  # 🌗
        elif player_obj.ent.env.env_time == 2: alpha = 34  # 🌘
        elif player_obj.ent.env.env_time == 3: alpha = 0   # 🌑
        elif player_obj.ent.env.env_time == 4: alpha = 34  # 🌒
        elif player_obj.ent.env.env_time == 5: alpha = 85  # 🌓
        elif player_obj.ent.env.env_time == 6: alpha = 170 # 🌔
        elif player_obj.ent.env.env_time == 7: alpha = 255 # 🌕
        self.overlay.set_alpha(alpha)

    def create_cloud(self):
        
        # Set direction of travel
        env       = player_obj.ent.env
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

    def render_clouds(self):
        camera = player_obj.ent.env.camera
        
        # Draw visible tiles
        for y in range(int(camera.Y/32), int(camera.bottom/pyg.tile_height + 1)):
            for x in range(int(camera.X/32), int(camera.right/pyg.tile_width + 1)):
                try:    tile = player_obj.ent.env.map[x][y]
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
                                        image = img.shift(img.dict['concrete']['gray floor'], [int((x_char+y_char)*13)%32, int(abs(x_char-y_char)*10)%32])
                                        
                                        # Set transparency
                                        if char == '-':   image.set_alpha(64)
                                        elif char == '.': image.set_alpha(128)
                                        else:             image.set_alpha(96)
                                        
                                        # Set the corresponding map tile
                                        X = x * pyg.tile_width - player_obj.ent.env.camera.X
                                        Y = y * pyg.tile_height - player_obj.ent.env.camera.Y
                                        
                                        pyg.display.blit(image, [X, Y])

    def render_lamps(self):
        for lamp in self.lamp_list:
            
            # Center light on entity
            if lamp.owner and lamp.equipped:
                X = lamp.owner.X - player_obj.ent.env.camera.X
                Y = lamp.owner.Y - player_obj.ent.env.camera.Y
                failed = False
            
            # Or center light on item
            elif not lamp.owner:
                X = lamp.X - player_obj.ent.env.camera.X
                Y = lamp.Y - player_obj.ent.env.camera.Y
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
                    self.overlay.fill((0, 0, 0, 255-alpha*i), transparent_rect)

    def render(self):
        """ Creates a black overlay and cuts out regions for lighting.
            Light is shown for any of the following conditions.
                1. The object has mech.lamp as an effect and is not owned by an entity.
                2. The object has mech.lamp as an effect and is equipped by an entity. """
        
        # Set background color
        self.overlay.fill((0, 0, 0))
        
        # Render lights
        self.render_lamps()
        
        # Render clouds
        if self.cloudy: self.render_clouds()
        
        # Blit to screen
        pyg.display.blit(self.overlay, (0, 0))

## Constructions
class Tile:
    """ Defines a tile of the map and its parameters. Sight is blocked if a tile is blocked. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
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
            placed      : bool; notifies custom placement via DevTools """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def draw(self, surface):
        
        # Set location
        X = self.X - player_obj.ent.env.camera.X
        Y = self.Y - player_obj.ent.env.camera.Y
        
        # Load tile
        if self.timer:
            if (time.time() // self.timer) % self.timer == 0:
                image = img.other_alt[self.img_names[0]][self.img_names[1]]
            else:
                image = img.other[self.img_names[0]][self.img_names[1]]
        else:
            image = img.other[self.img_names[0]][self.img_names[1]]
        
        ## (Optional) Add shift effect
        if (self.img_names[0] != 'roofs') and (self.img_names[1] != 'wood'):
            image = img.shift(image, [abs(self.rand_X), abs(self.rand_Y)])
        
        ## (Optional) Apply static effect
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
        self.owner  = None
        
        # Seed a seed for individual adjustments
        self.rand_X = random.randint(-self.rand_X, self.rand_X)
        self.rand_Y = random.randint(0,            self.rand_Y)
        self.flipped = random.choice([0, self.rand_Y])
        
        # Notify code of big object
        self.big = False
        
        # Initialize effect if passive
        if self.effect:
            if self.effect.trigger == 'passive':
                if self.role != 'weapons':
                    self.effect.function(self)

    def draw(self, surface):
        """ Draws the object at its position. """
        
        # Blit a tile
        if not self.big:
            
            # Set custom placement
            if self.img_names[0] == 'decor':
                X = self.X - player_obj.ent.env.camera.X - self.rand_X
                Y = self.Y - player_obj.ent.env.camera.Y - self.rand_Y
            
            else:
                X = self.X-player_obj.ent.env.camera.X
                Y = self.Y-player_obj.ent.env.camera.Y
        
            # Add effects and draw
            if (self.img_names[1] in ['leafy']) and not self.rand_Y:
                surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]), (X-32, Y-32))
            else:
                if self.flipped: surface.blit(img.flipped.dict[self.img_names[0]][self.img_names[1]], (X, Y))
                else:            surface.blit(img.dict[self.img_names[0]][self.img_names[1]], (X, Y))
                
        
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
            pyg.update_gui("Your inventory is full, cannot pick up " + self.name + ".", pyg.dark_gray)
        else:
            
            # Pick up item if possible
            if self.movable:
                
                # Add to inventory
                self.owner = ent
                if self.effect:
                    if self.effect.trigger == 'passive':
                        ent.item_effects.append(self.effect)
                
                ent.inventory[self.role].append(self)
                sort_inventory(ent)
                
                # Remove from environment
                if ent.tile:
                    if ent.tile.item:
                        ent.tile.item = None
                        self.tile     = ent.tile
                
                if ent.role == 'player':
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
            
            self.owner = None
            self.X     = ent.X
            self.Y     = ent.Y
            if self.effect:
                if self.effect in ent.effects: ent.effects.remove(self.effect)
            ent.inventory[self.role].remove(self)
            ent.tile.item = self

    def trade(self, owner, recipient):
        
        # Dequip before trading
        if self in owner.equipment.values():
            self.toggle_equip(owner)
        
        # Check wallet for cash
        if (owner.wallet - self.cost) >= 0:
            
            # Remove from owner
            owner.inventory[self.role].remove(self)
            owner.wallet += self.cost
            
            # Give to recipient
            self.pick_up(ent=recipient)
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
            else: self.effect.function(ent)
        
        elif self.role == 'player': pyg.update_gui("The " + self.name + " cannot be used.", pyg.dark_gray)

    def toggle_equip(self, ent):
        """ Toggles the equip/unequip status. """
        
        # Assign entity
        if not ent:        ent = player_obj.ent
        if not self.owner: self.owner = ent
        
        # Equip or dequip
        if self.equipped:  self.dequip(ent)
        else:              self.equip(ent)

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
        if self.effect:
            if self.effect.trigger == 'active': ent.effects.append(self.effect)
        self.equipped = True

        if ent.role == 'player':
            if not self.hidden:
                pyg.update_gui("Equipped " + self.name + " on " + self.slot + ".", pyg.dark_gray)

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
            if self.effect in ent.effects: ent.effects.remove(self.effect)

        self.equipped = False
        
        if self.role == 'player':
            if not self.hidden:
                pyg.update_gui("Dequipped " + self.name + " from " + self.slot + ".", pyg.dark_gray)

    def move(self, direction):
        
        self.direction = direction
        
        if direction == 'up':      self.Y += 32
        elif direction == 'down':  self.Y -= 32
        elif direction == 'left':  self.X += 32
        elif direction == 'right': self.X -= 32
        
        if self.tile: self.tile.item = None
        place_object(self, [self.X//32, self.Y//32], player_obj.ent.env)

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
        self.img_names_backup = self.img_names
        self.direction        = self.img_names[1]
        self.handedness       = 'left'

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
        self.motions_log = [] # list of lists of int; prescribed motions for ai
        
        # Mechanics
        self.dead       = False
        self.dialogue   = None
        self.default_dialogue = []
        self.quest      = None
        self.wallet     = 100
        self.trader     = False
        self.inventory  = {'weapons': [], 'armor': [],  'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
        self.equipment  = {'head': None,  'face': None, 'chest': None, 'body': None,  'dominant hand': None, 'non-dominant hand': None}
        
        # Effects
        self.garden_effects = [
            Effect(
                name          = 'scare',
                img_names     = ['bubbles', 'exclamation'],
                function      = mech.entity_scare,
                trigger       = 'active',
                sequence      = '⮟⮜⮟',
                cooldown_time = 1,
                other         = None),
            
            Effect(
                name          = 'comfort',
                img_names     = ['bubbles', 'heart'],
                function      = mech.entity_comfort,
                trigger       = 'active',
                sequence      = '⮟⮞⮜',
                cooldown_time = 1,
                other         = None),
            
            Effect(
                name          = 'clean',
                img_names     = ['bubbles', 'dots'],
                function      = mech.entity_clean,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None)]
        
        self.item_effects = [
            Effect(
                name          = 'suicide',
                img_names     = ['decor', 'bones'],
                function      = mech.suicide,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None),
            Effect(
                name          = 'scare',
                img_names     = ['bubbles', 'exclamation'],
                function      = mech.entity_scare,
                trigger       = 'active',
                sequence      = '⮟⮜⮟',
                cooldown_time = 1,
                other         = None),
            Effect(
                name          = 'capture',
                img_names     = ['bubbles', 'heart'],
                function      = mech.entity_capture,
                trigger       = 'active',
                sequence      = '⮟⮞⮟',
                cooldown_time = 1,
                other         = None)]
        self.effects    = []
        
        # Randomizer
        self.rand_X = random.randint(-pyg.tile_width,  pyg.tile_width)
        self.rand_Y = random.randint(-pyg.tile_height, pyg.tile_height)

    def ai(self):
        """ Preset movements. """
        
        # Only allow one motion
        moved = False
        
        # Check that the entity is alive
        if not self.dead:
            if time.time()-self.last_press > self.cooldown:
                self.last_press = float(time.time())
                
                # Move or follow
                if not self.motions_log:
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
                
                # Continue a prescribed pattern
                else:
                    loc = self.motions_log[0]
                    self.move(loc[0], loc[1])
                    self.motions_log.remove(loc)

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
            if self.img_names[1]:
                self.img_names[1] = self.direction

        else:
            
            # Find new position
            x = int((self.X + dX)/pyg.tile_width)
            y = int((self.Y + dY)/pyg.tile_height)
            
            # Move player
            if self.role == 'player': self.move_player(x, y, dX, dY)
            
            # Move pet
            pet_list = ['red radish', 'orange radish', 'purple radish']
            if self.img_names[0] in pet_list: self.move_pet(x, y, dX, dY)
            
            # Move NPC, enemy, or projectile
            else:
                
                # Move NPC or enemy
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
                
                # Projectiles
                else:
                    if self.role == 'projectile':
                        if self.env.map[x][y].entity:
                            self.attack_target(self.env.map[x][y].entity)
                            self.death()
                        else:
                            self.death()

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
                        if player_obj.ent.env.env_time in ent.trader:
                            trade_obj.ent = ent
                            pyg.overlay = 'trade'
                
                # Play speech and update quests
                if time.time() - aud.last_press_time_speech > aud.speech_speed//100:
                    pyg.update_gui(dialogue)
                    aud.play_speech(dialogue)
                    if ent.dialogue:
                        ent.dialogue = ent.quest.dialogue(ent)
            
            # Make them flee
            elif type(ent.fear) == int: ent.fear += 30
            
            # Attack the entity
            elif (self.env.name != 'home') or (self.equipment['dominant hand'] in ['blood dagger', 'blood sword']):
                self.attack_target(ent)
        
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
                        pyg.update_gui("The shovel strikes the barrier but does not break it.", pyg.dark_gray)
                    
                    # Update durability
                    if self.equipment['dominant hand'].durability <= 100:
                        self.equipment['dominant hand'].durability -= 1
                    if self.equipment['dominant hand'].durability <= 0:
                        pyg.update_gui(f"Broken {self.equipment['dominant hand'].name}!", color=pyg.dark_gray)
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
                if self.env.map[x][y].item.effect.function == mech.entity_eat:
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

    def attack_target(self, target, effect_check=True):
        """ Calculates and applies attack damage. """
        
        # Only attack living targets
        if not target.dead:
            
            # No attacking yourself
            if self.name != target.name:
                
                # Default damage calculation
                damage = self.attack - target.defense
                
                # Deal damage
                if damage > 0:
                    
                    # Apply an effect
                    if effect_check and not random.randint(0, 1):
                        if self.equipment['dominant hand']:
                            if self.equipment['dominant hand'].effect:
                                if self.equipment['dominant hand'].effect.trigger == 'passive':
                                    self.equipment['dominant hand'].effect.function(self)
                        
                        # Regular attack
                        else:
                            pyg.update_gui(self.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points.", pyg.red)
                            target.take_damage(damage)
                    
                    # Regular attack
                    else:
                        pyg.update_gui(self.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points.", pyg.red)
                        target.take_damage(damage)
                else:
                    pyg.update_gui(self.name.capitalize() + " strikes " + target.name + " but it has no effect!", pyg.red)
        return

    def take_damage(self, damage):
        """ Applies damage if possible. """
        
        if damage > 0:
            
            # Apply damage
            self.hp -= damage
            
            # Damage animation
            img.flash_over(self)
            
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
        
        # Player death
        if self.role == 'player':
            pyg.update_gui("You died!", pyg.red)
            player_obj.ent.dead        = True
            player_obj.ent.tile.entity = None
            player_obj.ent.img_names   = player_obj.ent.img_names_backup
            
            item = create_item('skeleton')
            item.name = f"the corpse of {self.name}"
            place_object(item, [self.X//pyg.tile_width, self.Y//pyg.tile_height], self.env)
            pygame.event.clear()
        
        # Entity or projectile death
        else:
            self.dead        = True
            self.tile.entity = None
            self.env.entities.remove(self)
            if self in player_obj.ent.env.entities: player_obj.ent.env.entities.remove(self)
            
            if self.role != 'projectile':
                pyg.update_gui("The " + self.name + " is dead! You gain " + str(self.exp) + " experience points.", pyg.red)
                
                if not self.tile.item:
                    item = create_item('bones')
                    item.name = f"the corpse of {self.name}"
                    place_object(item, [self.X//pyg.tile_width, self.Y//pyg.tile_height], self.env)
                    self.role = 'corpse'

            del self

            pygame.event.get()
        pygame.event.clear()

    def heal(self, amount):
        """ Heals player by the given amount without going over the maximum. """
        
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def jug_of_blood(self, amount):
        """ Heals player by the given amount without going over the maximum. """
        
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        else:
            self.attack += 1

    def toggle_effects(self):
        """ Switches between different sets of effects. """
        
        if self.env.name == 'garden': self.effects = self.garden_effects
        else:                         self.effects = self.item_effects

    def capture(self):
        pyg.update_gui("The " + self.name + " has been captured!", pyg.red)

        # Update entity
        self.dead        = True
        self.tile.entity = None
        self.env.entities.remove(self)
        if self in player_obj.ent.env.entities: player_obj.ent.env.entities.remove(self)
        
        player_obj.ent.discoveries['entities'][self.name] = self.img_names

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
        
        # Apply equipment to humans
        if self.img_names[0] in img.skin_options:
            
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
                            elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]),        (X, Y))
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
                    if not item.hidden:
                        if item.role in ['weapons', 'armor']:
                            if item.slot in ['dominant hand', 'non-dominant hand']:
                                if self.handedness == 'left':
                                    if swimming:          surface.blit(img.halved([item.img_names[0], self.img_names[1]]),               (X, Y))
                                    elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]),        (X, Y))
                                    else:                 surface.blit(img.dict[item.img_names[0]][self.img_names[1]],                   (X, Y))
                                else:
                                    if swimming:          surface.blit(img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                                    elif not self.rand_Y: surface.blit(img.scale(img.dict[self.img_names[0]][self.img_names[1]]),        (X, Y))
                                    else:                 surface.blit(img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                            else: pass
        
        # Blit dialogue bubble
        if self.dialogue: pyg.display.blit(img.dict['bubbles']['dots'], (X, Y-pyg.tile_height))
        
        # Blit trading bubble
        elif self.trader:
            if player_obj.ent.env.env_time in self.trader:
                pyg.display.blit(img.dict['bubbles']['cart'], (X, Y-pyg.tile_height))

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
            if not (0 <= x < len(player_obj.ent.env.map) and 0 <= y < len(player_obj.ent.env.map[0])):
                continue
            
            tile = player_obj.ent.env.map[x][y]
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
                    floors.append(player_obj.ent.env.map[x][y])
        
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
            if self.roof and (player_obj.ent.tile not in self.tiles_list):
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
            ['Default', (250, 200)],
            ['Fast',    (1,   150)],
            ['Fixed',   (0,   0)]]
        self.slow_list = [
            ['Fixed',   (0,   0)],
            ['Default', (250, 200)]]
        
        self.cooldown_time = 10
        self.last_press_time = 0

    # Environments
    def enter_dungeon(self, ent=None, text='', lvl_num=0):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if text:
                pyg.fadeout_screen(
                    screen   = pyg.screen,
                    fade_in  = False,
                    text     = text,
                    duration = 2)
                play_game_obj.fadein = text
            
            if 'dungeon' not in player_obj.envs.keys():
                player_obj.envs['dungeon'] = []
                build_dungeon_level(lvl_num)
            
            # Enter the first dungeon
            if player_obj.ent.env.name != 'dungeon':
                place_player(env=player_obj.envs['dungeon'][0], loc=player_obj.envs['dungeon'][0].center)    # mech (dungeon)
            
            # Enter the next saved dungeon
            elif player_obj.ent.env.lvl_num < len(player_obj.envs['dungeon']):
                lvl_num = player_obj.ent.env.lvl_num
                place_player(env=player_obj.envs['dungeon'][lvl_num], loc=player_obj.envs['dungeon'][lvl_num].center)    # mech (dungeon)
            
            # Enter a new dungeon
            else:
                build_dungeon_level(lvl_num)
                place_player(env=player_obj.envs['dungeon'][-1], loc=player_obj.envs['dungeon'][-1].center)    # mech (dungeon)

    def enter_hallucination(self, ent=None, text='. . . ! Your vision blurs as the substance seeps through your veins.'):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if 'hallucination' not in player_obj.envs.keys():
                player_obj.envs['hallucination'] = []
                
                pyg.fadeout_screen(
                    screen   = pyg.screen,
                    fade_in  = False,
                    text     = text,
                    duration = 2)
                pyg.overlay = None
                build_hallucination_level()
                play_game_obj.fadein = text

            # Enter the first hallucination
            if player_obj.ent.env.name != 'hallucination':
                place_player(env=player_obj.envs['hallucination'][0], loc=player_obj.envs['hallucination'][0].center)    # mech (hallucination)
            
            # Enter the next saved hallucination
            elif player_obj.ent.env.lvl_num < len(player_obj.envs['hallucination']):
                lvl_num = player_obj.ent.env.lvl_num
                place_player(env=player_obj.envs['hallucination'][lvl_num], loc=player_obj.envs['hallucination'][lvl_num].center)    # mech (hallucination)
            
            # Enter a new hallucination
            else:
                build_hallucination_level()
                place_player(env=player_obj.envs['hallucination'][-1], loc=player_obj.envs['hallucination'][-1].center)    # mech (hallucination)

    def enter_bitworld(self, ent=None, text='. . . ! Your vision blurs as the substance seeps through your veins.'):
        """ Advances player to bitworld. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if 'bitworld' not in player_obj.envs.keys():
                player_obj.envs['bitworld'] = []
                
                pyg.fadeout_screen(
                    screen   = pyg.screen,
                    fade_in  = False,
                    text     = text,
                    duration = 2)
                pyg.overlay = None
                build_bitworld()
                play_game_obj.fadein = text

            if player_obj.ent.env.name != 'bitworld':
                img.render_fx = 'bw_binary'
                place_player(env=player_obj.envs['bitworld'], loc=player_obj.envs['bitworld'].center)    # mech (bitworld)
    
    def enter_cave(self, ent=None):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if 'cave' not in player_obj.envs.keys(): 
                pyg.update_gui("The ground breaks beneath you and reveals a cave.", pyg.dark_gray)
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

    def enter_overworld(self, ent=None):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            if 'overworld' not in player_obj.envs.keys(): build_overworld()
            loc = player_obj.envs['overworld'].center
            print(1, player_obj.ent.env.weather)
            place_player(env=player_obj.envs['overworld'], loc=[loc[0], loc[1]])    # mech (overworld)
            print(player_obj.ent.env.weather)

    def enter_home(self, ent=None):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            place_player(env=player_obj.envs['home'], loc=player_obj.envs['home'].player_coordinates)    # mech (home)

    # Item effects
    def swing(self, ent=None):
        
        # Set entity
        if not ent: ent = player_obj.ent
        
        # Check for remaining stamina
        if ent.stamina:
            
            # Send animation to queue
            image = img.dict[ent.equipment['dominant hand'].img_names[0]]['dropped']
            img.vicinity_flash(ent, image)
            
            # Apply attack to enemies
            for tile in get_vicinity(ent).values():
                if tile.entity:
                    ent.attack += 5
                    ent.attack_target(tile.entity, effect_check=False)
                    ent.attack -= 5
            
            # Decrease stamina
            ent.stamina -= 5

    def boost_stamina(self, ent):
        ent.stamina += 50
        if ent.stamina > 100: ent.stamina = 100
        pyg.update_gui()

    def lamp(self, item):
        """ Adds or removes a light to be rendered under the following conditions.
            1. The object is not owned by an entity.
            2. The object is equipped by an entity. """
        
        if hasattr(item, 'env'):
            lamp_list = item.env.weather.lamp_list
        else:
            lamp_list = player_obj.ent.env.weather.lamp_list
        
        if item.owner:
            if item.equipped:
                if item not in lamp_list: lamp_list.append(item)
            else:
                if item in lamp_list:     lamp_list.remove(item)
                    
        
        else:
            if item not in lamp_list: lamp_list.append(item)
            else:                     lamp_list.remove(item)

    def propagate(self, ent=None):
        
        # Set entity
        if not ent: ent = player_obj.ent
        
        # Note location and image names
        img_x, img_y = int(ent.X/pyg.tile_width), int(ent.Y/pyg.tile_height)
        
        # Set location for drop
        if ent.direction == 'front':   img_y += 1
        elif ent.direction == 'back':  img_y -= 1
        elif ent.direction == 'right': img_x += 1
        elif ent.direction == 'left':  img_x -= 1
        
        # Place item
        item = create_entity('green blob')
        item.lethargy = 0
        item.cooldown = 0.1
        item.direction = None
        place_object(
            obj   = item,
            loc   = [img_x, img_y],
            env   = ent.env,
            names = item.img_names)
        
        # Prepare movements
        motions_log = []
        directions = {
            'front': [0, pyg.tile_height],
            'back':  [0, -pyg.tile_height],
            'left':  [-pyg.tile_width, 0],
            'right': [pyg.tile_width, 0]}
        
        for _ in range(100):
            motions_log.append(directions[ent.direction])
        
        # Send directions to entity
        item.motions_log = motions_log

    # Gameplay
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
            
            # Change speed
            if toggle:
                if self.movement_speed_toggle == len(self.slow_list)-1: 
                    self.movement_speed_toggle = 0
                else:
                    self.movement_speed_toggle += 1
                pyg.update_gui(f"Movement speed: {self.slow_list[self.movement_speed_toggle][0]}", pyg.dark_gray)
                (hold_time, repeat_time) = self.slow_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Set custom speed
            elif custom is not None:
                custom = custom % 2
                (hold_time, repeat_time) = self.slow_list[custom][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Restore previous speed
            else:
                (hold_time, repeat_time) = self.slow_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)

    def suicide(self):
        
        # Activate animation
        image = img.dict['decor']['bones']
        img.vicinity_flash(player_obj.ent, image)
        
        # Kill player
        player_obj.ent.death()
        return

    def spin(self, ent):
        
        # Prepare movements
        motions_log = []
        
        # Look forward first
        if ent.img_names[0] != 'front':
            motions_log.append([0, pyg.tile_height])
        motions_log.append([-pyg.tile_width, 0])
        
        # Spin around
        motions_log.append([0, -pyg.tile_height])
        motions_log.append([pyg.tile_width, 0])
        motions_log.append([0, pyg.tile_height])
        
        # Send directions to entity
        ent.motions_log = motions_log

    def find_water(self, ent):
        """ Moves entity towards water. """
        
        # Look for water
        if ent.tile.img_names[1] != 'water':
            
            # Prepare movements
            motions_log = []
            
            # Look for water
            for y in range(len(ent.env.map[0])):
                for x in range(len(ent.env.map)):
                    if ent.env.map[x][y].img_names[1] == 'water':
                        
                        # Construct a path
                        dX       = int(x*32) - ent.X
                        dY       = int(y*32) - ent.Y
                        distance = (dX ** 2 + dY ** 2)**(1/2)
                        while distance > 0:
                            
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
                            
                            motions_log.append([dX, dY])
                            motions_log.append([dX, dY])
                            distance -= 32
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = img.dict['bubbles']['question']

        # Bathe
        else:
            if pet_obj.moods['anger']:
                pet_obj.moods['anger'] -= 1
                image = img.dict['bubbles']['water']
            
            else:
                pet_obj.moods['boredom'] += 1
                image = img.dict['bubbles']['dots']
            
        img.flash_above(ent, image)

    def find_bed(self, ent):
        """ Moves entity towards water. """
        
        # Look for a bed
        item = bool(ent.tile.item)
        if item: bed = bool(ent.tile.item.name == 'bed')
        else:    bed = False
        if not item and not bed:
            
            # Prepare movements
            motions_log = []
            
            # Look for a bed
            for y in range(len(ent.env.map[0])):
                for x in range(len(ent.env.map)):
                    if ent.env.map[x][y].item:
                        if ent.env.map[x][y].item.name == 'bed':
                            if not ent.env.map[x][y].item.occupied:
                                ent.env.map[x][y].item.occupied = True
                                
                                # Construct a path
                                dX       = int(x*32) - ent.X
                                dY       = int(y*32) - ent.Y
                                distance = (dX ** 2 + dY ** 2)**(1/2)
                                while distance > 0:
                                    
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
                                    
                                    motions_log.append([dX, dY])
                                    motions_log.append([dX, dY])
                                    distance -= 32
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = img.dict['bubbles']['question']

        # Sleep
        else:
            image = img.dict['bubbles']['dots']
            
        img.flash_above(ent, image)

    # Entity interactions
    def entity_eat(self, ent):
        """ Dropped item effect. """
        
        pet_obj.moods['happiness'] += 1
        pet_obj.moods['boredom']   -= 1
        image = img.dict['bubbles']['heart']
        img.flash_above(ent, image)
        ent.tile.item = None

    def entity_scare(self):
        """ Combo effect. """
        
        # Find entities in vicinity
        ent_list = []
        for tile in get_vicinity(player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            
            if player_obj.ent.env.name == 'garden':
                pet_obj.moods['lethargy'] -= 1
                pet_obj.moods['boredom']  -= 1
            
            image = img.dict['bubbles']['exclamation']
            for ent in ent_list:
                for tile in get_vicinity(ent).values():
                    if not tile.blocked:
                        ent.move_towards(tile.X, tile.Y)
                img.flash_above(ent, image)
        
        else:
            pyg.update_gui("There are no entities in your vicinity.", pyg.dark_gray)

    def entity_capture(self):
        """ Combo effect. """
        
        # Find entities in vicinity
        ent = None
        for tile in get_vicinity(player_obj.ent).values():
            if tile.entity:
                if tile.entity.role != 'NPC':
                    ent = tile.entity
                    break
        
        # Activate effect if entities are found
        if ent:
            image = img.dict['bubbles']['heart']
            img.flash_above(ent, image)
            img.flash_on(ent, img.dict[ent.img_names[0]][ent.img_names[1]])
            
            if player_obj.ent.discoveries['entities'].values():
                for names in player_obj.ent.discoveries['entities'].values():
                    if ent.name not in names:
                        ent.capture()
                        break
                    else:
                        pyg.update_gui("The " + ent.name + " has already been logged.", pyg.dark_gray)
            else:
                ent.capture()
        else:
            pyg.update_gui("There are no entities in your vicinity.", pyg.dark_gray)

    def entity_comfort(self):
        """ Combo effect. """
        
        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            pet_obj.moods['sadness'] -= 1
            if pet_obj.moods['sadness'] <= 0: pet_obj.moods['boredom'] += 1
            image = img.dict['bubbles']['heart']
            for ent in ent_list:
                img.flash_above(ent, image)
                self.spin(ent)

    def entity_clean(self):
        """ Combo effect. """
        
        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            for ent in ent_list:
                self.find_water(ent)

class Effect:

    def __init__(self, name, img_names, function, trigger, sequence, cooldown_time, other):
        
        self.name            = name
        self.img_names       = img_names
        self.function        = function # set as a function in Mechanics
        
        self.trigger         = trigger
        self.sequence        = sequence
        
        self.cooldown_time   = cooldown_time
        self.last_press_time = 0
        
        self.other           = other

class Camera:
    """ Defines a camera to follow the player. """
    
    def __init__(self, target):
        """ Defines a camera and its parameters. 
            
            Parameters
            ----------
            target          : Entity object; focus of camera
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
            
            center_x        : int; middle of the camera in screen coordinates
            center_y        : int; middle of the camera in screen coordinates
            
            fix_position    : bool; prevents adjustment of parameters """
        
        self.target          = target
        self.width           = int(pyg.screen_width / pyg.zoom)
        self.height          = int((pyg.screen_height + pyg.tile_height) / pyg.zoom)
        self.tile_map_width  = int(self.width / pyg.tile_width)
        self.tile_map_height = int(self.height / pyg.tile_height)
        
        self.X               = int((self.target.X * pyg.zoom) - int(self.width / 2))
        self.Y               = int((self.target.Y * pyg.zoom) - int(self.height / 2))
        self.tile_map_x      = int(self.X / pyg.tile_width)
        self.tile_map_y      = int(self.Y / pyg.tile_height)
        
        self.right           = self.X + self.width
        self.bottom          = self.Y + self.height
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        
        self.center_X        = int(self.X + int(self.width / 2))
        self.center_Y        = int(self.Y + int(self.height / 2))
        
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
            self.bottom     = (self.Y + self.height + 320) / pyg.zoom
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
        
        elif not custom and not self.fixed:
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
        
        message = self.function(ent, ent.dialogue)
        if message:
            return message

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

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
            #BigMenu(header="header", options=note_text)
        
        # Generate the Quest object
        if "quest name" not in player_obj.ent.questlog.keys():
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
            player_obj.ent.questlog[quest.name] = quest
            questlog_obj.update_questlog()
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
                questlog_obj.update_questlog(name='quest name')
            
            # Complete quest
            if quest_lvl == 9:
                player_obj.ent.questlog['quest name'].finished = True
                questlog_obj.update_questlog(name='quest name')
                
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
        
        # One string for each subquest
        self.path_vals = []

    def making_a_friend(self, ent, dialogue):
        """ Manages friend quest, including initialization and dialogue. """
        
        # Initialization
        if dialogue == "Walk into something to interact with it, or press Enter (↲) if you're above it.":
            ent.quest.dialogue_list = [
                "Walk into something to interact with it, or press Enter (↲) if you're above it.",
                "Press Slash (/) to view the main menu. Try it again to return!",
                "Use Plus (+) to zoom in, or use Minus (-) to zoom out.",
                "Press Four (4) to open your inventory. Period (.) drops, and Enter activates!",
                "Try holding Zero (0) to enter combos. Nine (9) can be used to view details.",
                "Check out Options in the Main Menu!"]
        
        # Increase friendship level
        ent.quest.dialogue_list.remove(dialogue)
        friend_level = 9 - len(ent.quest.dialogue_list)
        
        # First checkpoint
        if friend_level == 1:
            questlog_obj.update_questlog(name="Making a friend")
        
        # Complete quest
        if friend_level == 9:
            
            player_obj.ent.questlog['Making a friend'].finished = True
            questlog_obj.update_questlog(name="Making a friend")
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
                            trigger       = 'active',
                            sequence      = None,
                            cooldown_time = 0,
                            other         = None)
                        place_object(
                            obj = obj,
                            loc = [x_test, y_test],
                            env = ent.env)
                        
                        found = True
                        break
        
        if ent.quest.dialogue_list:
            return ent.quest.dialogue_list[0]

    def mysterious_note(self, ent=None, dialogue=None):
        """ Manages friend quest, including initialization and dialogue.
            Upon finding a scroll of death, the player must first learn to descipher it.
            People in the town seem to suggest that the church is involved.
            The best lead is Kyrio, who is secretly a leader of the church.
            
            Church: Coax a lizard to the altar (by following). """
        
        global big_menu
        
        # Read the note
        if not dialogue:
            note_text = ["ξνμλ λξ ξλι ξγθιβξ ξ θθ.", "Ηκρσ σρσ λβνξθι νθ.", "Ψπθ αβνιθ πθμ."]
            big_menu = BigMenu(
                name     = 'temp',
                header   = "mysterious note",
                options  = note_text,
                position = 'top left')
            pyg.overlay = 'temp'
        
        # Initialize quest and characters
        if 'Learning a language' not in player_obj.ent.questlog.keys():
            quest = Quest(
                name = 'Learning a language',
                notes = [
                    "A mysterious note. Someone in town might know what it means.",
                    "",
                    "ξνμλ λξ ξλι ξγθιβξ ξ θθ,", "Ηκρσ σρσ λβνξθι νθ,", "Ψπθ αβνιθ πθμ."],
                tasks = [
                    "☐ See if anyone in town can decipher the note."],
                category = 'Main',
                function = player_obj.ent.questlines['Bloodkin'].mysterious_note)

            quest.content = quest.notes + quest.tasks
            player_obj.ent.questlog[quest.name] = quest
            questlog_obj.update_questlog()
            pyg.update_gui(f"Quest added: {quest.name}", pyg.violet)
            
            self.names_list, self.dialogue_list, self.progress_list = self.set_entities(quest)
        
        # Update quest
        if dialogue and ent:
            quest = player_obj.ents['Kyrio'].quest
            
            # Look for checkpoints
            for i in range(len(self.names_list)):
                if ent.name == self.names_list[i]:
                
                    # Check for task completion
                    if self.progress_list[i] < 3:
                        self.dialogue_list[i].remove(dialogue)
                        self.progress_list[i] = 3 - len(self.dialogue_list[i])
                    
                        # Provide next piece of dialogue
                        if self.dialogue_list[i]:
                            return self.dialogue_list[i][0]
            
            # Complete quest
            if (self.progress_list[0] == 3) and (self.progress_list[1] == 3):
                self.path_vals.append('religion')
                player_obj.ent.questlog['Learning a language'].finished = True
                questlog_obj.update_questlog(name='Learning a language')
            
            elif self.progress_list[2] == 3:
                self.path_vals.append('drugs')
                player_obj.ent.questlog['Learning a language'].finished = True
                questlog_obj.update_questlog(name='Learning a language')

    def set_entities(self, quest):
        names_list, dialogue_list, progress_list = [], [], []
        
        # Generate characters and dialogue
        if 'Kyrio' not in player_obj.ents.keys(): player_obj.ents['Kyrio'] = create_NPC('Kyrio')
        quest.Kyrio_dialogue = [
            "Kyrio: Huh? A glyph of some sort? I know nothing of such things.",
            "Kyrio: Rather inquisitive, are you? Never turns out well.",
            "Kyrio: Fine, yes, my brother might know. I am busy."]
        quest.Kyrio_progress              = 0
        player_obj.ents['Kyrio'].quest    = quest
        player_obj.ents['Kyrio'].dialogue = quest.Kyrio_dialogue[0]
        names_list.append('Kyrio')
        dialogue_list.append(quest.Kyrio_dialogue)
        progress_list.append(quest.Kyrio_progress)
        
        if 'Kapno' not in player_obj.ents.keys(): player_obj.ents['Kapno'] = create_NPC('Kapno')
        quest.Kapno_dialogue = [
            "Kapno: Exquisite! Where was this symbol found?",
            "Kapno: It certainly peaks my interest. Strange occurances are frequent as of late.",
            "Kapno: Let me know if you find anything else, and check out my shop if you need anything."]
        quest.Kapno_progress              = 0
        player_obj.ents['Kapno'].quest    = quest
        player_obj.ents['Kapno'].dialogue = quest.Kapno_dialogue[0]
        names_list.append('Kapno')
        dialogue_list.append(quest.Kapno_dialogue)
        progress_list.append(quest.Kapno_progress)
        
        if 'Oxi' not in player_obj.ents.keys(): player_obj.ents['Oxi'] = create_NPC('Oxi')
        quest.Oxi_dialogue = [
            "Oxi: What do you want? You selling something?",
            "Oxi: Hey! Don't just wave the arcane around like that.",
            "Oxi: Yeah, I've seen it before. Come find me later tonight... we can talk then."]
        quest.Oxi_progress              = 0
        player_obj.ents['Oxi'].quest    = quest
        player_obj.ents['Oxi'].dialogue = quest.Oxi_dialogue[0]
        names_list.append('Oxi')
        dialogue_list.append(quest.Oxi_dialogue)
        progress_list.append(quest.Oxi_progress)
        
        if 'Erasti' not in player_obj.ents.keys(): player_obj.ents['Erasti'] = create_NPC('Erasti')
        quest.Erasti_dialogue = [
            "Erasti: Oh...! Hi!",
            "Erasti: That symbol... have you seen it before? It gives me an eerie sense of déjà vu.",
            "Erasti: I saw Kyrio with something like that once. Or maybe it was a dream..."]
        quest.Erasti_progress              = 0
        player_obj.ents['Erasti'].quest    = quest
        player_obj.ents['Erasti'].dialogue = quest.Erasti_dialogue[0]
        names_list.append('Erasti')
        dialogue_list.append(quest.Erasti_dialogue)
        progress_list.append(quest.Erasti_progress)
    
        if 'Merci' not in player_obj.ents.keys(): player_obj.ents['Merci'] = create_NPC('Merci')
        quest.Merci_dialogue = [
            "Merci: Welcome! ...are you not here for my merchandise?",
            "Merci: I do not deal in the occult, so I will be of no help to you. Sorry.",
            "Merci: Oxi is shady enough... he seems like the type to ask."]
        quest.Merci_progress              = 0
        player_obj.ents['Merci'].quest    = quest
        player_obj.ents['Merci'].dialogue = quest.Merci_dialogue[0]
        names_list.append('Merci')
        dialogue_list.append(quest.Merci_dialogue)
        progress_list.append(quest.Merci_progress)
    
        return names_list, dialogue_list, progress_list

class FriendlyFaces:
    """ FriendlyFaces quest.
        
        Summary
        -------
        Meet the town. """

    def making_an_introduction(self, ent=None, dialogue=None):
        
        # Initialize quest and characters
        if 'Making an introduction' not in player_obj.ent.questlog.keys():
            quest = Quest(
                name = 'Making an introduction',
                notes = ["I should get to know my neighbors."],
                tasks = ["☐ Talk to people."],
                category = 'Main',
                function = player_obj.ent.questlines['Friendly Faces'].making_an_introduction)

            quest.content = quest.notes + quest.tasks
            player_obj.ent.questlog[quest.name] = quest
            questlog_obj.update_questlog()
            
            self.names_list, self.dialogue_list, self.progress_list = self.set_entities(quest)
        
        # Update quest
        if dialogue and ent:
            quest = player_obj.ents[ent.name].quest
            
            # Look for checkpoints
            for i in range(len(self.names_list)):
                if ent.name == self.names_list[i]:
                
                    # Check for task completion
                    if self.progress_list[i] < 1:
                        self.dialogue_list[i].remove(dialogue)
                        self.progress_list[i] = 1
            
            # Complete quest
            if 0 not in self.progress_list:
                player_obj.ent.questlog['Making an introduction'].finished = True
                questlog_obj.update_questlog(name='Making an introduction')

    def set_entities(self, quest):
        names_list, dialogue_list, progress_list = [], [], []
        
        # Generate characters and dialogue
        if 'Kyrio' not in player_obj.ents.keys(): player_obj.ents['Kyrio'] = create_NPC('Kyrio')
        quest.Kyrio_dialogue = ["Kyrio: ... Yes, hello. Do you need something?"]
        quest.Kyrio_progress              = 0
        player_obj.ents['Kyrio'].quest    = quest
        player_obj.ents['Kyrio'].dialogue = quest.Kyrio_dialogue[0]
        names_list.append('Kyrio')
        dialogue_list.append(quest.Kyrio_dialogue)
        progress_list.append(quest.Kyrio_progress)
        
        if 'Kapno' not in player_obj.ents.keys(): player_obj.ents['Kapno'] = create_NPC('Kapno')
        quest.Kapno_dialogue = ["Kapno: Hello! I run a general store. Looking for anything specific?"]
        quest.Kapno_progress              = 0
        player_obj.ents['Kapno'].quest    = quest
        player_obj.ents['Kapno'].dialogue = quest.Kapno_dialogue[0]
        names_list.append('Kapno')
        dialogue_list.append(quest.Kapno_dialogue)
        progress_list.append(quest.Kapno_progress)
        
        if 'Oxi' not in player_obj.ents.keys(): player_obj.ents['Oxi'] = create_NPC('Oxi')
        quest.Oxi_dialogue = ["Oxi: Can't sleep? I might have something for that. Come find me at night."]
        quest.Oxi_progress              = 0
        player_obj.ents['Oxi'].quest    = quest
        player_obj.ents['Oxi'].dialogue = quest.Oxi_dialogue[0]
        names_list.append('Oxi')
        dialogue_list.append(quest.Oxi_dialogue)
        progress_list.append(quest.Oxi_progress)
        
        if 'Erasti' not in player_obj.ents.keys(): player_obj.ents['Erasti'] = create_NPC('Erasti')
        quest.Erasti_dialogue = ["Erasti: Oh! My name is Erasi. Have we met?"]
        quest.Erasti_progress              = 0
        player_obj.ents['Erasti'].quest    = quest
        player_obj.ents['Erasti'].dialogue = quest.Erasti_dialogue[0]
        names_list.append('Erasti')
        dialogue_list.append(quest.Erasti_dialogue)
        progress_list.append(quest.Erasti_progress)
    
        if 'Merci' not in player_obj.ents.keys(): player_obj.ents['Merci'] = create_NPC('Merci')
        quest.Merci_dialogue = ["Merci: Welcome! ...are you not here for my merchandise?"]
        quest.Merci_progress              = 0
        player_obj.ents['Merci'].quest    = quest
        player_obj.ents['Merci'].dialogue = quest.Merci_dialogue[0]
        names_list.append('Merci')
        dialogue_list.append(quest.Merci_dialogue)
        progress_list.append(quest.Merci_progress)
    
        if 'Aya' not in player_obj.ents.keys(): player_obj.ents['Aya'] = create_NPC('Aya')
        quest.Aya_dialogue = ["Aya: You look like you can handle a blade... Oh! Did I say that out loud?"]
        quest.Aya_progress              = 0
        player_obj.ents['Aya'].quest    = quest
        player_obj.ents['Aya'].dialogue = quest.Aya_dialogue[0]
        names_list.append('Aya')
        dialogue_list.append(quest.Aya_dialogue)
        progress_list.append(quest.Aya_progress)
    
        if 'Zung' not in player_obj.ents.keys(): player_obj.ents['Zung'] = create_NPC('Zung')
        quest.Zung_dialogue = ["Zung: Hey, good to meet you. See you around."]
        quest.Zung_progress              = 0
        player_obj.ents['Zung'].quest    = quest
        player_obj.ents['Zung'].dialogue = quest.Zung_dialogue[0]
        names_list.append('Zung')
        dialogue_list.append(quest.Zung_dialogue)
        progress_list.append(quest.Zung_progress)
    
        if 'Lilao' not in player_obj.ents.keys(): player_obj.ents['Lilao'] = create_NPC('Lilao')
        quest.Lilao_dialogue = ["Lilao: Huh?"]
        quest.Lilao_progress              = 0
        player_obj.ents['Lilao'].quest    = quest
        player_obj.ents['Lilao'].dialogue = quest.Lilao_dialogue[0]
        names_list.append('Lilao')
        dialogue_list.append(quest.Lilao_dialogue)
        progress_list.append(quest.Lilao_progress)
    
        return names_list, dialogue_list, progress_list

########################################################################################################################################################
# Creation
## Environments
@debug_call
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
        floor   = player_obj.envs['garden'].floors,
        walls   = player_obj.envs['garden'].walls,
        roof    = None)
    x, y = new_room.center()[0], new_room.center()[1]
    
    # Generate items and entities
    items    = [['forest', 'tree',       10]]
    entities = [['forest', 'red radish', 50, [None]]]
    place_objects(env, items, entities)
    
    # Create pet management
    pet_obj = Pets()
    
    # Place player in first room
    env.player_coordinates = [x, y]
    env.map[x][y].item     = None
    player_obj.envs['garden'].entity = player_obj.ent
    player_obj.ent.tile = player_obj.envs['garden'].map[x][y]
    player_obj.envs['garden'].center = new_room.center()
    
    return env

@debug_call
def build_womb():
    """ Generates the overworld environment. """
    
    ## Initialize environment
    env = Environment(
        name       = 'womb',
        lvl_num    = 0,
        size       = 1,
        soundtrack = list(aud.dict.keys()),
        img_names  = ['floors', 'dark green'],
        floors     = ['floors', 'dark green'],
        walls      = ['walls', 'gray'],
        roofs      = ['roofs', 'tiled'],
        blocked    = False,
        hidden     = True)
    player_obj.envs['womb'] = env
    env.camera = Camera(player_obj.ent)
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
        floor   = player_obj.envs['womb'].floors,
        walls   = player_obj.envs['womb'].walls,
        roof    = None)
    x, y = new_room.center()[0], new_room.center()[1]
    
    # Place player in first room
    env.player_coordinates = [x, y]
    env.map[x][y].item     = None
    env.entity = player_obj.ent
    player_obj.ent.tile = env.map[x][y]
    env.center = new_room.center()
    
    return env

@debug_call
def build_home():
    """ Generates player's home. """

    ## Initialize environment
    env = Environment(
        name       = 'home',
        lvl_num    = 0,
        size       = 5,
        soundtrack = ['menu'],
        img_names  = ['walls', 'gray'],
        floors     = ['floors', 'green'],
        walls      = ['walls', 'gray'],
        roofs      = ['roofs', 'tiled'])
    player_obj.envs['home'] = env
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
        width   = mech.room_max_size,
        height  = mech.room_max_size,
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
        width   = mech.room_min_size*2,
        height  = mech.room_min_size*2,
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
    player_obj.ent.questlines = {}
    player_obj.ent.questlines['Bloodkin'] = Bloodkin()
    ent.quest    = Quest(
        name     = "Making a friend",
        notes    = ["I wonder who this is. Maybe I should say hello."],
        tasks    = ["☐ Say hello to the creature.",
                    "☐ Get to know them."],
        category = 'Side',
        function = player_obj.ent.questlines['Bloodkin'].making_a_friend)
    ent.quest.content = ent.quest.notes + ent.quest.tasks
    player_obj.ent.questlog['Making a friend'] = ent.quest
    questlog_obj.update_questlog()
    
    # Initial position
    env.player_coordinates = env.center
    
    return env

@debug_call
def build_dungeon_level(lvl_num=0):
    """ Generates the overworld environment. """
    
    # Initialize environment
    if lvl_num:                          lvl_num = lvl_num
    elif not player_obj.envs['dungeon']: lvl_num = 1
    else:                                lvl_num = 1 + player_obj.envs['dungeon'][-1].lvl_num
    
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
    
    player_obj.envs['dungeon'].append(env)
    env.camera = Camera(player_obj.ent)
    env.camera.fixed = False
    env.camera.zoom_in(custom=1)

    # Generate biomes
    biomes = [['dungeon', ['walls', 'gray']]]
    voronoi_biomes(env, biomes)
    
    # Construct rooms
    rooms, room_counter, counter = [], 0, 0
    num_rooms = int(mech.max_rooms * env.lvl_num) + 2
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(mech.room_min_size, mech.room_max_size)
        height   = random.randint(mech.room_min_size, mech.room_max_size)
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
    env.entity = player_obj.ent
    env.center = new_room.center()
    player_obj.ent.tile = env.map[x][y]
    
    # Generate stairs in the last room
    (x, y) = env.rooms[-2].center()
    stairs = create_item('door')
    stairs.name = 'dungeon'
    place_object(stairs, [x, y], player_obj.envs['dungeon'][-1])

@debug_call
def build_hallucination_level():
    """ Generates the overworld environment. """
    
    ## Initialize environment
    if not player_obj.envs['hallucination']: lvl_num = 1
    else:                                    lvl_num = 1 + player_obj.envs['hallucination'][-1].lvl_num
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
    
    player_obj.envs['hallucination'].append(env)
    env.camera = Camera(player_obj.ent)
    env.camera.fixed = False
    env.camera.zoom_in(custom=1)
    
    # Construct rooms
    rooms, room_counter, counter = [], 0, 0
    num_rooms = int(mech.max_rooms*2 * env.lvl_num) + 2
    for i in range(num_rooms):
        
        # Construct room
        width    = random.randint(mech.room_min_size*2, mech.room_max_size*2)
        height   = random.randint(mech.room_min_size*2, mech.room_max_size*2)
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
    player_obj.ent.img_names_backup = player_obj.ent.img_names
    player_obj.ent.img_names = ['tentacles', 'front']
    
    # Place player in first room
    (x, y) = env.rooms[0].center()
    env.player_coordinates = [x, y]
    env.entity = player_obj.ent
    env.center = new_room.center()
    player_obj.ent.tile = env.map[x][y]
    
    # Generate stairs in the last room
    (x, y) = env.rooms[-2].center()
    stairs = create_item('portal')
    stairs.name = 'hallucination'
    place_object(stairs, [x, y], env)

@debug_call
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
                walls  = player_obj.envs['overworld'].walls,
                roof   = player_obj.envs['overworld'].roofs,
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
        width  = random.randint(mech.room_min_size, mech.room_max_size)
        height = random.randint(mech.room_min_size, mech.room_max_size)
        x      = random.randint(x_1, x_2(width))
        y      = random.randint(y_1, y_2(height))
        
        # Check for solid ground
        failed = False
        for u in range(width):
            for v in range(height):
                if env.map[x+u][y+v].biome in img.biomes['sea']: failed = True
                elif env.map[x+u][y+v].room:                     failed = True
        if not failed:
            
            main_room = Room(
                name    = 'home room',
                env     = env,
                x1      = x,
                y1      = y,
                width   = mech.room_max_size,
                height  = mech.room_max_size,
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
    env.entity             = player_obj.ent
    player_obj.ent.tile    = env.map[door_x][door_y]
    
    ## Create church
    main_room = Room(
        name    = 'church',
        env     = env,
        x1      = 20,
        y1      = 20,
        width   = mech.room_max_size,
        height  = mech.room_max_size,
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
        if name not in player_obj.ents.keys(): player_obj.ents[name] = create_NPC(name)
        
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
        place_object(player_obj.ents[name], (x, y), env)
    
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
    
    player_obj.ent.questlines['Friendly Faces'] = FriendlyFaces()
    player_obj.ent.questlines['Friendly Faces'].making_an_introduction()

@debug_call
def build_bitworld():
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
    player_obj.envs['bitworld'] = env
    
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
    center                = player_obj.envs['bitworld'].center
    (x_1, y_1)            = center
    x_2                   = lambda width:  len(player_obj.envs['bitworld'].map)    - width  - 1
    y_2                   = lambda height: len(player_obj.envs['bitworld'].map[0]) - height - 1
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
                walls  = player_obj.envs['bitworld'].walls,
                roof   = player_obj.envs['bitworld'].roofs,
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
        env     = player_obj.envs['bitworld'],
        x1      = player_obj.envs['bitworld'].center[0],
        y1      = player_obj.envs['bitworld'].center[1],
        width   = mech.room_max_size,
        height  = mech.room_max_size,
        biome   = 'any',
        hidden  = False,
        objects = False,
        floor   = ['floors', 'dark green'],
        walls   = player_obj.envs['bitworld'].walls,
        roof    = player_obj.envs['bitworld'].roofs,
        plan = ['  -----     ',
                ' --...----- ',
                ' -........--',
                ' -.........-',
                '--.........|',
                '-.........--',
                '--.....---- ',
                ' --...--    ',
                '  -----     '])
    #player_obj.envs['bitworld'].center = main_room.center()
    env.player_coordinates = player_obj.envs['bitworld'].center # [0, 10]
    player_obj.envs['bitworld'].entity = player_obj.ent
    player_obj.ent.tile                 = player_obj.envs['bitworld'].map[0][10]
    
    # Door
    x, y = center[0]+1, center[1]+5
    item = create_item('door')
    item.name = 'home'
    place_object(item, [x, y], player_obj.envs['bitworld'])
    player_obj.envs['bitworld'].map[x][y].blocked = False
    player_obj.envs['bitworld'].map[x][y].unbreakable = False
    
    ## Create church
    main_room = Room(
        name    = 'church',
        env     = player_obj.envs['bitworld'],
        x1      = 20,
        y1      = 20,
        width   = mech.room_max_size,
        height  = mech.room_max_size,
        biome   = 'any',
        hidden  = False,
        objects = False,
        floor   = ['floors', 'red'],
        walls   = player_obj.envs['bitworld'].walls,
        roof    = player_obj.envs['bitworld'].roofs,
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
        room = random.choice(player_obj.envs['bitworld'].rooms)
        while room == player_obj.envs['bitworld'].rooms[-1]:
            room = random.choice(player_obj.envs['bitworld'].rooms)
        
        # Select spawn location
        for i in range(3):
            occupied = bools(room, i-1)
            if occupied[0] == occupied[1]:
                (x, y) = (room.center()[0]+i-1, room.center()[1]+i-1)
        
        # Spawn entity
        place_object(ent, (x, y), env)

@debug_call
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
    env.entity = player_obj.ent
    env.center = new_room.center()
    player_obj.ent.tile = env.map[x][y]
    
    # Generate stairs in the last room
    (x, y) = env.rooms[-1].center()
    stairs = create_item('cave')
    stairs.img_names = ['floors', 'dirt2']
    place_object(stairs, [x, y], player_obj.envs['cave'][-1])

## Tools
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

def create_item(names, effect=None):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names : string or list of strings; name of object """
    
    item = None
    item_dict = {
    
    ## Decor (decor_options)
    
        'tree': {
            'name':           'tree',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'tree'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        True,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'bones': {
            'name':           'bones',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'bones'],

            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           5,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'boxes': {
            'name':           'boxes',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'boxes'],

            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           5,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'fire': {
            'name':           'fire',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'fire'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'leafy': {
            'name':           'leafy tree',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'leafy'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        True,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         2,
            'cost':           25,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'skeleton': {
            'name':           'skeleton',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'skeleton'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'shrooms': {
            'name':           'shrooms',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'shrooms'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        False,
            'rand_X':         10,
            'rand_Y':         10,
            'cost':           15,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red plant left': {
            'name':           'red plant left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'red plant left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           15,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red plant right': {
            'name':           'red plant right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'red plant right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           15,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'cup shroom': {
            'name':           'cup shroom',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'cup shroom'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           15,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'frond': {
            'name':           'frond',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'frond'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           15,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'blades': {
            'name':           'blades',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'blades'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         10,
            'rand_Y':         10,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'purple bulbs': {
            'name':           'purple bulbs',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'purple bulbs'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         10,
            'rand_Y':         10,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'lights': {
            'name':           'lights',
            'role':           'other',
            'slot':           None,
            'img_names':      ['decor', 'lights'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         5,
            'rand_Y':         5,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'lamp',
                img_names     = ['lights', 'dropped'],
                function      = mech.lamp,
                trigger       = 'passive',
                sequence      = None,
                cooldown_time = 0,
                other         = 5)},

    # Dialogue bubbles (bubbles_options)

        'dots': {
            'name':           'dots',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'dots'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'exclamation': {
            'name':           'exclamation',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'exclamation'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'dollar': {
            'name':           'dollar',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'dollar'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'cart': {
            'name':           'cart',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'cart'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'question': {
            'name':           'question',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'question'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'skull': {
            'name':           'skull',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'skull'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'heart': {
            'name':           'heart',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'heart'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'water': {
            'name':           'water',
            'role':           'other',
            'slot':           None,
            'img_names':      ['bubbles', 'water'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

    # Furniture
    
        'purple bed': {
            'name':           'purple bed',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'purple bed'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red bed': {
            'name':           'red bed',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red bed'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'shelf left': {
            'name':           'shelf left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'shelf left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'shelf right': {
            'name':           'shelf right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'shelf right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'long table left': {
            'name':           'long table left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'long table left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'long table right': {
            'name':           'long table right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'long table right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'table': {
            'name':           'table',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'table'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red chair left': {
            'name':           'red chair left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red chair left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red chair right': {
            'name':           'red chair right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red chair right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug bottom left': {
            'name':           'red rug bottom left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug bottom left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug bottom middle': {
            'name':           'red rug bottom middle',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug bottom middle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug bottom right': {
            'name':           'red rug bottom right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug bottom right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug middle left': {
            'name':           'red rug middle left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug middle left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug middle middle': {
            'name':           'red rug middle middle',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug middle middle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug middle right': {
            'name':           'red rug middle right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug middle right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug top left': {
            'name':           'red rug top left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug top left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug top middle': {
            'name':           'red rug top middle',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug top middle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'red rug top right': {
            'name':           'red rug top right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'red rug top right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug bottom left': {
            'name':           'green rug bottom left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug bottom left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug bottom middle': {
            'name':           'green rug bottom middle',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug bottom middle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug bottom right': {
            'name':           'green rug bottom right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug bottom right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug middle left': {
            'name':           'green rug middle left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug middle left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug middle middle': {
            'name':           'green rug middle middle',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug middle middle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug middle right': {
            'name':           'green rug middle right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug middle right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug top left': {
            'name':           'green rug top left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug top left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug top middle': {
            'name':           'green rug top middle',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug top middle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'green rug top right': {
            'name':           'green rug top right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['furniture', 'green rug top right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

    ## Drugs (drugs_options)

        'needle': {
            'name':           'needle',
            'role':           'drugs',
            'slot':           None,
            'img_names':      ['drugs', 'needle'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           25,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'bowl',
                img_names     = ['drugs', 'bowl'],
                function      = mech.enter_hallucination,
                trigger       = 'active',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

        'skin': {
            'name':           'skin',
            'role':           'drugs',
            'slot':           None,
            'img_names':      ['drugs', 'skin'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'bowl',
                img_names     = ['drugs', 'bowl'],
                function      = mech.enter_hallucination,
                trigger       = 'active',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

        'teeth': {
            'name':           'teeth',
            'role':           'drugs',
            'slot':           None,
            'img_names':      ['drugs', 'teeth'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'bowl',
                img_names     = ['drugs', 'bowl'],
                function      = mech.enter_bitworld,
                trigger       = 'active',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

        'bowl': {
            'name':           'bowl',
            'role':           'drugs',
            'slot':           None,
            'img_names':      ['drugs', 'bowl'],

            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           30,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'bowl',
                img_names     = ['drugs', 'bowl'],
                function      = mech.enter_hallucination,
                trigger       = 'active',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

        'plant': {
            'name':           'plant',
            'role':           'drugs',
            'slot':           None,
            'img_names':      ['drugs', 'plant'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'food',
                img_names     = ['drugs', 'plant'],
                function      = mech.boost_stamina,
                trigger       = 'active',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

        'bubbles': {
            'name':           'bubbles',
            'role':           'drugs',
            'slot':           None,
            'img_names':      ['drugs', 'bubbles'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           50,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'food',
                img_names     = ['drugs', 'bubbles'],
                function      = mech.entity_eat,
                trigger       = 'active',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

    # Potions and scrolls (potions_options, scrolls_options)

        'jug of blood': {
            'name':          'jug of blood',
            'role':          'potions',
            'slot':          None,
            'img_names':     ['potions', 'red'],

            'durability':    101,
            'equippable':    False,
            'equipped':      False,
            'hidden':        False,
            'blocked':       False,
            'movable':       True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':          10,
            
            'hp_bonus':      0,
            'attack_bonus':  0,
            'defense_bonus': 0,
            'effect':        effect},

        'jug of grapes': {
            'name':          'jug of grapes',
            'role':          'potions',
            'slot':          None,
            'img_names':     ['potions', 'purple'],

            'durability':    101,
            'equippable':    False,
            'equipped':      False,
            'hidden':        False,
            'blocked':       False,
            'movable':       True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':          10,
            
            'hp_bonus':      0,
            'attack_bonus':  0,
            'defense_bonus': 0,
            'effect':        effect},

        'jug of water': {
            'name':          'jug of water',
            'role':          'potions',
            'slot':          None,
            'img_names':     ['potions', 'blue'],

            'durability':    101,
            'equippable':    False,
            'equipped':      False,
            'hidden':        False,
            'blocked':       False,
            'movable':       True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':          10,
            
            'hp_bonus':      0,
            'attack_bonus':  0,
            'defense_bonus': 0,
            'effect':        effect},

        'jug of cement': {
            'name':           'jug of cement',
            'role':           'potions',
            'slot':           None,
            'img_names':      ['potions', 'gray'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'scroll of lightning bolt': {
            'name':           'scroll of lightning bolt',
            'role':           'scrolls',
            'slot':           None,
            'img_names':      ['scrolls', 'closed'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'scroll of fireball': {
            'name':           'scroll of fireball',
            'role':           'scrolls',
            'slot':           None,
            'img_names':      ['scrolls', 'closed'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'scroll of confusion': {
            'name':           'scroll of confusion',
            'role':           'scrolls',
            'slot':           None,
            'img_names':      ['scrolls', 'closed'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'scroll of death': {
            'name':           'scroll of death',
            'role':           'scrolls',
            'slot':           None,
            'img_names':      ['scrolls', 'open'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           1000,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

    # Structures (stairs_options, floors_options)

        'door': {
            'name':           'door',
            'role':           'other',
            'slot':           None,
            'img_names':      ['stairs', 'door'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'portal': {
            'name':           'portal',
            'role':           'other',
            'slot':           None,
            'img_names':      ['stairs', 'portal'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'cave': {
            'name':           'cave',
            'role':           'other',
            'slot':           None,
            'img_names':      ['floors', 'sand2'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'path left right': {
            'name':           'path',
            'role':           'other',
            'slot':           None,
            'img_names':      ['paths', 'left right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},
    
        'path up down': {
            'name':           'path',
            'role':           'other',
            'slot':           None,
            'img_names':      ['paths', 'up down'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},
    
        'path down right': {
            'name':           'path',
            'role':           'other',
            'slot':           None,
            'img_names':      ['paths', 'down right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},
    
        'path down left': {
            'name':           'path',
            'role':           'other',
            'slot':           None,
            'img_names':      ['paths', 'down left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},
    
        'paths up right': {
            'name':           'path',
            'role':           'other',
            'slot':           None,
            'img_names':      ['paths', 'up right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},
    
        'paths up left': {
            'name':           'path',
            'role':           'other',
            'slot':           None,
            'img_names':      ['paths', 'up left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

    # Concrete structures (concrete_options)

        'gray window': {
            'name':           'gray window',
            'role':           'other',
            'slot':           None,
            'img_names':      ['concrete', 'gray window'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'gray door': {
            'name':           'gray door',
            'role':           'other',
            'slot':           None,
            'img_names':      ['concrete', 'gray door'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'gray wall left': {
            'name':           'gray wall left',
            'role':           'other',
            'slot':           None,
            'img_names':      ['concrete', 'gray wall left'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'gray wall': {
            'name':           'gray wall',
            'role':           'other',
            'slot':           None,
            'img_names':      ['concrete', 'gray wall'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'gray wall right': {
            'name':           'gray wall right',
            'role':           'other',
            'slot':           None,
            'img_names':      ['concrete', 'gray wall right'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        True,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'gray floor': {
            'name':           'gray floor',
            'role':           'other',
            'slot':           None,
            'img_names':      ['concrete', 'gray floor'],
            
            'durability':     101,
            'equippable':     False,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

    # Weapons (equip_names)

        'shovel': {
            'name':           'shovel',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['shovel', 'dropped'],

            'durability':     100,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           15,
            
            'hp_bonus':       0,
            'attack_bonus':   2,
            'defense_bonus':  10,
            'effect':         Effect(
                name          = 'dirtball',
                img_names     = ['green blob', 'right'],
                function      = mech.propagate,
                trigger       = 'active',
                sequence      = '⮞⮜⮞',
                cooldown_time = 1,
                other         = None)},

        'super shovel': {
            'name':           'super shovel',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['super shovel', 'dropped'],

            'durability':     1000,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   100,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'the way of the spade',
                img_names     = ['shovel', 'dropped'],
                function      = mech.suicide,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None)},

        'dagger': {
            'name':           'dagger',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['dagger', 'dropped'],
            
            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           25,
            
            'hp_bonus':       0,
            'attack_bonus':   2,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'swing',
                img_names     = ['decor', 'boxes'],
                function      = mech.swing,
                trigger       = 'active',
                sequence      = '⮜⮟⮞',
                cooldown_time = 0.1,
                other         = None)},

        'sword': {
            'name':           'sword',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['sword', 'dropped'],
            
            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           75,
            
            'hp_bonus':       0,
            'attack_bonus':   5,
            'defense_bonus':  0,
            'effect':         effect},

        'blood dagger': {
            'name':           'blood dagger',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['blood dagger', 'dropped'],
            
            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           500,
            
            'hp_bonus':       0,
            'attack_bonus':   10,
            'defense_bonus':  0,
            'effect':         effect},

        'blood sword': {
            'name':           'blood sword',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['blood sword', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           1000,
            
            'hp_bonus':       0,
            'attack_bonus':   15,
            'defense_bonus':  0,
            'effect':         effect},

    # Effects

        'eye': {
            'name':           'eye',
            'role':           'weapons',
            'slot':           'dominant hand',
            'img_names':      ['blood dagger', 'dropped'],
            
            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'swing',
                img_names     = ['null', 'null'],
                function      = mech.swing,
                trigger       = 'passive',
                sequence      = None,
                cooldown_time = 0.1,
                other         = None)},

    # Armor (equip_names)

        'green clothes': {
            'name':           'green clothes',
            'role':           'armor',
            'slot':           'body',
            'img_names':      ['green clothes', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  1,
            'effect':         effect},

        'orange clothes': {
            'name':           'orange clothes',
            'role':           'armor',
            'slot':           'body',
            'img_names':      ['orange clothes', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  1,
            'effect':         effect},

        'exotic clothes': {
            'name':           'exotic clothes',
            'role':           'armor',
            'slot':           'body',
            'img_names':      ['exotic clothes', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       1,
            'attack_bonus':   0,
            'defense_bonus':  1,
            'effect':         effect},

        'yellow dress': {
            'name':           'yellow dress',
            'role':           'armor',
            'slot':           'body',
            'img_names':      ['yellow dress', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           10,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  1,
            'effect':         effect},

        'chain dress': {
            'name':           'chain dress',
            'role':           'armor',
            'slot':           'body',
            'img_names':      ['chain dress', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           20,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  2,
            'effect':         effect},

        'iron armor': {
            'name':           'iron armor',
            'role':           'armor',
            'slot':           'body',
            'img_names':      ['iron armor', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           100,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  10,
            'effect':         effect},

        'lamp': {
            'name':           'lamp',
            'role':           'armor',
            'slot':           'non-dominant hand',
            'img_names':      ['lamp', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           100,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         Effect(
                name          = 'lamp',
                img_names     = ['iron shield', 'dropped'],
                function      = mech.lamp,
                trigger       = 'passive',
                sequence      = None,
                cooldown_time = 0,
                other         = 5)},

        'bald': {
            'name':           'bald',
            'role':           'armor',
            'slot':           'head',
            'img_names':      ['bald', 'front'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        False,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'brown hair': {
            'name':           'brown hair',
            'role':           'armor',
            'slot':           'head',
            'img_names':      ['brown hair', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'blue hair': {
            'name':           'blue hair',
            'role':           'armor',
            'slot':           'head',
            'img_names':      ['blue hair', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'short brown hair': {
            'name':           'short brown hair',
            'role':           'armor',
            'slot':           'head',
            'img_names':      ['short brown hair', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'clean': {
            'name':           'clean',
            'role':           'armor',
            'slot':           'face',
            'img_names':      ['clean', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'brown beard': {
            'name':           'brown beard',
            'role':           'armor',
            'slot':           'face',
            'img_names':      ['brown beard', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'blue beard': {
            'name':           'blue beard',
            'role':           'armor',
            'slot':           'face',
            'img_names':      ['blue beard', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'white beard': {
            'name':           'white beard',
            'role':           'armor',
            'slot':           'face',
            'img_names':      ['white beard', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'flat': {
            'name':           'flat',
            'role':           'armor',
            'slot':           'chest',
            'img_names':      ['flat', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'bra': {
            'name':           'bra',
            'role':           'armor',
            'slot':           'chest',
            'img_names':      ['bra', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'glasses': {
            'name':           'glasses',
            'role':           'armor',
            'slot':           'face',
            'img_names':      ['glasses', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         True,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  0,
            'effect':         effect},

        'iron shield': {
            'name':           'iron shield',
            'role':           'armor',
            'slot':           'non-dominant hand',
            'img_names':      ['iron shield', 'dropped'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           50,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  10,
            'effect':         effect},

    # Big objects
            'logo': {
            'name':           'logo',
            'role':           'decor',
            'img_names':      ['top', 'left'],

            'durability':     101,
            'equippable':     True,
            'equipped':       False,
            'hidden':         False,
            'blocked':        False,
            'movable':        True,
            'rand_X':         0,
            'rand_Y':         0,
            'cost':           0,
            
            'hp_bonus':       0,
            'attack_bonus':   0,
            'defense_bonus':  10,
            'effect':         effect}}
    
    # Search with image names
    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if val['img_names'] == names:
                item = Item(**val)
    
    # Search with dictionary names
    else:
        item = Item(**item_dict[names])
    
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

    ## Actual entities

        'white': {
            'name':        'white NPC',
            'role':        'NPC',
            'img_names':   ['white', 'front'],
            'habitat':     'any',
            
            'exp':         0,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

        'black': {
            'name':        'black NPC',
            'role':        'NPC',
            'img_names':   ['black', 'front'],
            'habitat':     'any',
            
            'exp':         0,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

        'fat': {
            'name':        'fat NPC',
            'role':        'NPC',
            'img_names':   ['fat', 'front'],
            'habitat':     'any',
            
            'exp':         0,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

        'friend': {
            'name':        'friend',
            'role':        'NPC',
            'img_names':   ['friend', 'front'],
            'habitat':     'land',

            'exp':         0,
            'rank':        100,
            'hp':          100,
            'max_hp':      100,
            'attack':      0,
            'defense':     100,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  0,
            'fear':        None,
            'reach':       640},

        'eye': {
            'name':        'eye',
            'role':        'enemy',
            'img_names':   ['eye', 'front'],
            'habitat':     'land',
            
            'exp':         35,
            'rank':        1,
            'hp':          100,
            'max_hp':      100,
            'attack':      20,
            'defense':     20,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   20,
            'aggression':  50,
            'fear':        None,
            'reach':       1000},

        'eyes': {
            'name':        'eyes',
            'role':        'enemy',
            'img_names':   ['eyes', 'front'],
            'habitat':     'land',
            
            'exp':         35,
            'rank':        1,
            'hp':          20,
            'max_hp':      20,
            'attack':      4,
            'defense':     0,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  10,
            'fear':        None,
            'reach':       1000},

        'troll': {
            'name':        'troll',
            'role':        'enemy',
            'img_names':   ['troll', 'front'],
            'habitat':     'land',

            'exp':         100,
            'rank':        1,
            'hp':          30,
            'max_hp':      30,
            'attack':      8,
            'defense':     2,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  10,
            'fear':        None,
            'reach':       1000},

        'triangle': {
            'name':        'triangle',
            'role':        'enemy',
            'img_names':   ['triangle', 'front'],
            'habitat':     'land',

            'exp':         100,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      15,
            'defense':     10,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    1,
            'miss_rate':   5,
            'aggression':  100,
            'fear':        None,
            'reach':       1000},

        'purple': {
            'name':        'purple',
            'role':        'enemy',
            'img_names':   ['purple', 'front'],
            'habitat':     'land',
            
            'exp':         500,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  10,
            'fear':        None,
            'reach':       1000},

        'tentacles': {
            'name':        'tentacles',
            'role':        'enemy',
            'img_names':   ['tentacles', 'front'],
            'habitat':     'any',

            'exp':         50,
            'rank':        1,
            'hp':          35,
            'max_hp':      35,
            'attack':      10,
            'defense':     10,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    2,
            'miss_rate':   1,
            'aggression':  100,
            'fear':        None,
            'reach':       1000},

        'round1': {
            'name':        'round1',
            'role':        'enemy',
            'img_names':   ['round1', 'front'],
            'habitat':     'land',
            
            'exp':         50,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    0,
            'miss_rate':   5,
            'aggression':  100,
            'fear':        None,
            'reach':       1000},

        'round2': {
            'name':        'round2',
            'role':        'enemy',
            'img_names':   ['round2', 'front'],
            'habitat':     'land',
            
            'exp':         500,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  10,
            'fear':        None,
            'reach':       1000},

        'grass': {
            'name':        'grass',
            'role':        'enemy',
            'img_names':   ['grass', 'front'],
            'habitat':     'forest',
            
            'exp':         500,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   40,
            'aggression':  20,
            'fear':        None,
            'reach':       1000},

        'round3': {
            'name':        'round3',
            'role':        'enemy',
            'img_names':   ['round3', 'front'],
            'habitat':     'any',
            
            'exp':         500,
            'rank':        1,
            'hp':          1,
            'max_hp':      1,
            'attack':      0,
            'defense':     0,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    10,
            'miss_rate':   10,
            'aggression':  0,
            'fear':        None,
            'reach':       64},

        'lizard': {
            'name':        'lizard',
            'role':        'enemy',
            'img_names':   ['lizard', 'front'],
            'habitat':     'desert',
            
            'exp':         500,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    5,
            'miss_rate':   10,
            'aggression':  10,
            'fear':        None,
            'reach':       1000},

        'red': {
            'name':        'red',
            'role':        'enemy',
            'img_names':   ['red', 'front'],
            'habitat':     'land',
            
            'exp':         500,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      15,
            'defense':     5,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    100,
            'miss_rate':   10,
            'aggression':  1,
            'fear':        None,
            'reach':       0},

        'rock': {
            'name':        'rock',
            'role':        'enemy',
            'img_names':   ['rock', 'front'],
            'habitat':     'desert',
            
            'exp':         500,
            'rank':        1,
            'hp':          10,
            'max_hp':      10,
            'attack':      0,
            'defense':     500,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    2,
            'miss_rate':   0,
            'aggression':  0,
            'fear':        None,
            'reach':       0},

        'frog': {
            'name':        'frog',
            'role':        'enemy',
            'img_names':   ['frog', 'front'],
            'habitat':     'any',
            
            'exp':         15,
            'rank':        1,
            'hp':          50,
            'max_hp':      50,
            'attack':      1,
            'defense':     5,
            'stamina':     100,
            
            'follow':      False,
            'lethargy':    10,
            'miss_rate':   10,
            'aggression':  10,
            'fear':        None,
            'reach':       32},

        'red radish': {
            'name':        'red radish',
            'role':        'enemy',
            'img_names':   ['red radish', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        0,
            'reach':       1000},

        'orange radish': {
            'name':        'orange radish',
            'role':        'enemy',
            'img_names':   ['orange radish', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        0,
            'reach':       1000},

        'purple radish': {
            'name':        'purple radish',
            'role':        'enemy',
            'img_names':   ['purple radish', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        0,
            'reach':       1000},

        'snake': {
            'name':        'snake',
            'role':        'enemy',
            'img_names':   ['snake', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

        'buzz': {
            'name':        'buzz',
            'role':        'enemy',
            'img_names':   ['buzz', 'front'],
            'habitat':     'city',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

        'egg': {
            'name':        'egg',
            'role':        'enemy',
            'img_names':   ['egg', 'front'],
            'habitat':     'any',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

        'star': {
            'name':        'star',
            'role':        'enemy',
            'img_names':   ['star', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    20,
            'miss_rate':   20,
            'aggression':  10,
            'fear':        None,
            'reach':       1000},

        'plant': {
            'name':        'plant',
            'role':        'enemy',
            'img_names':   ['plant', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        None,
            'reach':       1000},

    ## Projectiles

        'green blob': {
            'name':        'green blob',
            'role':        'projectile',
            'img_names':   ['green blob', 'front'],
            'habitat':     'forest',
            
            'exp':         0,
            'rank':        1,
            'hp':          25,
            'max_hp':      25,
            'attack':      0,
            'defense':     25,
            'stamina':     100,
            
            'follow':      True,
            'lethargy':    6,
            'miss_rate':   6,
            'aggression':  0,
            'fear':        None,
            'reach':       1000}}
    
    if type(names) in [tuple, list]:
        for val in ent_dict.values():
            if val.img_names == names:
                ent = Entity(**val)
                ent.handedness = random.choice(['left', 'right'])
    else:
        ent = Entity(**ent_dict[names])
    
    if not ent: raise Exception(names)
    else:        return ent

def create_NPC(name):
    """ A more specific version of create_entity. """
    
    if name == 'Kyrio':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Kyrio'
        ent.reach = 1000
        
        # Equipment
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        
        clothes.pick_up(ent=ent)
        beard.pick_up(ent=ent)
        dagger.pick_up(ent=ent)

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
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Kapno'
        ent.reach = 2

        # Equipment
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        
        clothes.pick_up(ent=ent)
        beard.pick_up(ent=ent)
        dagger.pick_up(ent=ent)
        
        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Inventory
        ent.trader = [3, 4, 5, 6]
        inv = ['shovel', 'sword', 'iron shield',
               'orange clothes', 'exotic clothes',
               'jug of blood', 'jug of grapes', 'jug of water', 'jug of cement',
               'boxes', 'fire', 'shrooms', 'cup shroom']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Kapno: Huh?",
            "Kapno: Too many dry days, it seems. The lake is rather shallow.",
            "Kapno: Have you seen my brother? He seems distracted as of late.",
            "Kapno: My bones may be brittle, but I know good products when I see them.",
            "Kapno: *mumbles*"]
    
    elif name == 'Blodo':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Blodo'
        ent.reach = 2

        # Equipment
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        
        clothes.pick_up(ent=ent)
        beard.pick_up(ent=ent)
        dagger.pick_up(ent=ent)
        
        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Inventory
        ent.trader = [3, 4, 5, 6]
        inv = ['shovel', 'sword', 'iron shield',
               'orange clothes', 'exotic clothes',
               'jug of blood', 'jug of grapes', 'jug of water', 'jug of cement',
               'boxes', 'fire', 'shrooms', 'cup shroom']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Blodo: Huh?",
            "Blodo: Too many dry days, it seems. The lake is rather shallow.",
            "Blodo: Have you seen my brother? He seems distracted as of late.",
            "Blodo: My bones may be brittle, but I know good products when I see them.",
            "Blodo: *mumbles*"]
    
    elif name == 'Erasti':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Erasti'
        ent.reach = 10
        
        # Equipment
        hair    = create_item('brown hair')
        bra     = create_item('bra')
        clothes = create_item('yellow dress')
        shovel  = create_item('shovel')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        shovel.pick_up(ent=ent)
        
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
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Merci'
        ent.reach = 4
        
        # Equipment
        hair    = create_item('blue hair')
        bra     = create_item('bra')
        clothes = create_item('chain dress')
        shovel  = create_item('shovel')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        shovel.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        shovel.toggle_equip(ent)
        
        # Inventory
        ent.trader = [3, 4, 5, 6]
        inv = ['shovel',
               'chain dress', 'green clothes', 'yellow dress',
               'bubbles', 'plant']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Merci: Are you looking to buy anything in particular? Please, take a look at my stock.",
            "Merci: We specialize in exotic goods, but the basics are available as well.",
            "Merci: I prefer coins, but I could use the sale. Are you looking to trade?",
            "Merci: Your purchase is free if you can find my keys. I can't sell my blades without them!",
            "Merci: We have many items for sale.",
            "Merci: ... Oh, welcome in!"]
    
    elif name == 'Oxi':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Oxi'
        ent.reach = 25
        
        # Equipment
        hair    = create_item('blue hair')
        face    = create_item('blue beard')
        clothes = create_item('orange clothes')
        
        hair.pick_up(ent=ent)
        face.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        face.toggle_equip(ent)
        clothes.toggle_equip(ent)
        clothes.hidden = True
        
        # Inventory
        ent.trader = [1, 2, 7, 8]
        inv = ['needle', 'skin', 'teeth', 'bowl', 'plant', 'bubbles']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Oxi: Yeah, I got it... talk to me later. You'd be surprised by what I can find.",
            "Oxi: Don't run your mouth about this. Just buy and leave.",
            "Oxi: Weren't you just here? Buy what you need, I guess.",
            "Oxi: ..."]
    
    elif name == 'Aya':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Aya'
        ent.reach = 50
        
        # Equipment
        hair    = create_item('brown hair')
        bra     = create_item('bra')
        clothes = create_item('chain dress')
        sword  = create_item('sword')
        shield  = create_item('iron shield')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        sword.pick_up(ent=ent)
        shield.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        sword.toggle_equip(ent)
        shield.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Aya: ...",
            "Aya: I chop trees, vines, grass -- whatever needs to be cut.",
            "Aya: Huh, haven't seen you around. Been busy clearing paths.",
            "Aya: Careful! My blades are sharp.",
            "Aya: I can only dream of what's out there, beyond the town.",
            "Aya: The trickle of the lake lulls me to sleep.",
            "Aya: You don't talk much, huh? Just like Kyrio... what a curious old man."]
    
    elif name == 'Zung':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Zung'
        ent.reach = 6
        
        # Equipment
        hair    = create_item('bald')
        clothes = create_item('green clothes')
        
        hair.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        clothes.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Zung: ...",
            "Zung: Have you seen my sister, Aya? She's scary, right?",
            "Zung: No, I deal in rumors. If you want goods, ask Merci or Kapno.",
            "Zung: I always thought we were the only town... until recently.",
            "Zung: The jail also houses the bank. Secure? You bet.",
            "Zung: *mumbles something about Erasti and Oxi*",
            "Zung: Kyrio is fit for his age, but he hides it well."]
    
    elif name == 'Lilao':
        
        # Basics
        ent     = create_entity('black')
        ent.name  = 'Lilao'
        ent.reach = 15
        
        # Equipment
        hair    = create_item('blue hair')
        bra     = create_item('bra')
        clothes = create_item('yellow dress')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Lilao: ..."]
    
    elif name == 'random':
        
        # Basics
        ent       = create_entity(str(random.choice(img.skin_options)))
        ent.name  = random.choice(['Traveler', 'Settler', 'Stranger'])
        ent.reach = 20
        
        # Equipment
        hair    = create_item(str(random.choice(img.hair_options)))
        bra     = create_item(str(random.choice(img.chest_options)))
        clothes = create_item(str(random.choice(img.armor_names)))
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        
        if bra.name == 'flat':
            face = create_item(str(random.choice(img.face_options)))
            face.pick_up(ent=ent)
            face.toggle_equip(ent)
        
        ent.lethargy = random.randint(1, 10)
        dialogue_options = [
            ["NPC: ...",
            "NPC: I had the strangest dream last night... Huh? Just talking to myself.",
            "NPC: *seems busy*"],
            ["NPC: Howdy!",
            "NPC: Have you seen those cracks in the sand? My neighbor fell right through one!",
            "NPC: Yeah, Merci is good. I always go to her for clothes and everyday items.",
            "NPC: Grapes are great for health, but you can't build without concrete!"],
            ["NPC: Oxi can get whatever you need, but he only sells at night.",
            "NPC: Sometimes, I just pick weeds for fun. The ground looks nice without them.",
            "NPC: ...Did you see that? Maybe I should spend less time with Oxi..."]]

        ent.default_dialogue = random.choice(dialogue_options)
    
    return ent

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
        obj.env  = env
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

                ## Randomly select and place an item
                selection = random.choice(items)
                
                # Check that the object matches the biome
                if env.map[x][y].biome in img.biomes[selection[0]]:
                    if not random.randint(0, selection[2]) and not env.map[x][y].item:
                        
                        ## Place object
                        item = create_item(selection[1])
                        place_object(item, [x, y], env)
                
                ## Randomly select and place an entity
                selection = random.choice(entities)
                
                # Check that the entity matches the biome
                if env.map[x][y].biome in img.biomes[selection[0]]:
                    if not random.randint(0, selection[2]) and not env.map[x][y].item:
                        
                        ## Create and place entity
                        entity = create_entity(selection[1])
                        for item in selection[3]:
                            if item:
                                obj = create_item(item)
                                obj.pick_up(ent=entity)
                                if obj.equippable:
                                    obj.toggle_equip(entity)
                                    if obj.effect:
                                        obj.effect.trigger = 'passive'
                        
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
        
        # Remove extra motions and animations
        pygame.event.clear()
        img.render_log = []
        
        # Remove from current location
        if player_obj.ent.env:
            if player_obj.ent.env.name != env.name:
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
        player_obj.ent.toggle_effects()
        
        # Set time and date
        if player_obj.ent.env.name in ['home', 'overworld', 'cave']:
            if player_obj.ent.last_env.name in ['home', 'overworld', 'cave']:
                player_obj.ent.env.env_date = player_obj.ent.last_env.env_date
                player_obj.ent.env.env_time = player_obj.ent.last_env.env_time

        # Notify environment of player position
        player_obj.ent.env.entities.append(player_obj.ent)
        player_obj.ent.tile.entity = player_obj.ent
        check_tile(loc[0], loc[1], startup=True)
        
        # Update camera
        if not env.camera: env.camera = Camera(player_obj.ent)
        env.camera.update()
        if not env.camera.fixed:
            player_obj.ent.env.camera.zoom_in()
            player_obj.ent.env.camera.zoom_out()
        
        # Render
        time.sleep(0.5)
        pyg.update_gui()
        
        # Change song
        if player_obj.ent.env.name != player_obj.ent.last_env.name:
            aud.control(soundtrack=env.soundtrack)

########################################################################################################################################################
# Utilities
## General
def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    
    level_up_exp = mech.level_up_base + player_obj.ent.rank * mech.level_up_factor
    if player_obj.ent.exp >= level_up_exp:
        player_obj.ent.rank += 1
        player_obj.ent.exp -= level_up_exp
        
        dialogue = [
            "You feel stronger.",
            "Flow state!",
            "Resilience flows through you."]
        pyg.update_gui(random.choice(dialogue), pyg.gray)

        player_obj.ent.rank += 1
        player_obj.ent.max_hp += 20
        player_obj.ent.hp += 20
        player_obj.ent.attack += 1
        player_obj.ent.defense += 1
        pyg.update_gui()

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

def screenshot(size='display', visible=False, folder="Data/.Cache", filename="screenshot.png", blur=False):
    """ Takes a screenshot.
        cache:  saves a regular screenshot under Data/.Cache/screenshot.png
        save:   moves regular cached screenshot to Data/File_#/screenshot.png 
        blur:   adds a blur effect """
    
    # Turn off gui
    gui_cache, msg_cache = copy.copy(pyg.gui_toggle), copy.copy(pyg.msg_toggle)
    pyg.gui_toggle, pyg.msg_toggle = False, False
    
    # Select display size
    if size == 'full':
        camera_cache = [player_obj.ent.env.camera.X, player_obj.ent.env.camera.Y]
        pyg.screen = pygame.display.set_mode((len(player_obj.ent.env.map[0])*16, len(player_obj.ent.env.map)*16),)
        player_obj.ent.env.camera.X = 0
        player_obj.ent.env.camera.Y = 0
        player_obj.ent.env.camera.update()
        render_all(size=size, visible=visible)
    
    # Save image
    path = folder + '/' + filename
    pygame.image.save(pyg.screen, path)
    
    # Add effects
    if blur:
        image_before = Image.open(folder + '/' + filename)
        image_after  = image_before.filter(ImageFilter.BLUR)
        image_after.save(folder + '/' + filename)
    
    # Reset everthing to normal
    if size == 'full':
        pyg.screen = pygame.display.set_mode((pyg.screen_width, pyg.screen_height),)
        player_obj.ent.env.camera.X = camera_cache[0]
        player_obj.ent.env.camera.Y = camera_cache[1]
        player_obj.ent.env.camera.update()
    
    pyg.gui_toggle, pyg.msg_toggle = gui_cache, msg_cache
    render_all()

def is_blocked(env, loc):
    """ Checks for barriers and triggers dialogue. """
    
    try:
        # Check for barriers
        if env.map[loc[0]][loc[1]].blocked:
            return True
        
        # Check for monsters
        if env.map[loc[0]][loc[1]].entity: 
            return True
        
        # Triggers message for hidden passages
        if env.map[loc[0]][loc[1]].unbreakable:
            #pyg.update_gui("A mysterious breeze seeps through the cracks.", pyg.dark_gray)
            pygame.event.clear()
            return True
    except: return False
    
    return False

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and PyInstaller. """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_vicinity(obj):
    """ Returns a list of tiles surrounding the given location.
    
        Returns
        -------
        obj.vicinity : dict of Tile objects

        Details
        -------
        'top left'      : 
        'top middle'    : 
        'top right'     : 
        'left'          : 
        'right'         : 
        'bottom left'   : 
        'bottom middle' : 
        'bottom right'  : """
    
    (x, y) = obj.X//pyg.tile_width, obj.Y//pyg.tile_width
    obj.vicinity = {
        'top middle'    : player_obj.ent.env.map[x][y-1],
        'top right'     : player_obj.ent.env.map[x+1][y-1],
        'right'         : player_obj.ent.env.map[x+1][y],
        'bottom right'  : player_obj.ent.env.map[x+1][y+1],
        'bottom middle' : player_obj.ent.env.map[x][y+1],
        'bottom left'   : player_obj.ent.env.map[x-1][y+1],
        'middle left'   : player_obj.ent.env.map[x-1][y],
        'top left'      : player_obj.ent.env.map[x-1][y-1]}
    return obj.vicinity

## Effects
def floor_effects(floor_effect):
    if floor_effect:
        if floor_effect == 'damage':
            player_obj.ent.take_damage(10)

def active_effects():
    """ Applies effects from items and equipment. Runs constantly. """
    global super_dig
    
    # Check for equipment
    if player_obj.ent.equipment['dominant hand']:     hand_1 = player_obj.ent.equipment['dominant hand']
    else:                                             hand_1 = None
    if player_obj.ent.equipment['non-dominant hand']: hand_2 = player_obj.ent.equipment['non-dominant hand']
    else:                                             hand_2 = None
    
    # Apply dominant hand function
    if hand_1:
        if hand_1.name == 'super shovel': super_dig = True
        else:                             super_dig = False
    
    # Apply non-dominant hand function
    if hand_2:
        if hand_2.effect.name == 'lamp':
            hand_2.effect.function(hand_2)

########################################################################################################################################################
# Global scripts
if __name__ == "__main__":
    main()

########################################################################################################################################################