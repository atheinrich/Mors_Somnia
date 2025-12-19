########################################################################################################################################################
# Utilities
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import time
import pickle
import sys
import copy

## Specific
import pygame
from   pygame.locals import *

## Local
import session

########################################################################################################################################################
# Standard objects and parameters
spacing = 24

def choice_pos(List):
    return (48, 436 - len(List) * spacing)

def cursor_pos(List):
    return (32, 436 - len(List) * spacing)

def cursor():
    cursor_surface = pygame.Surface((16, 16)).convert()
    cursor_surface.set_colorkey(cursor_surface.get_at((0, 0)))
    pygame.draw.polygon(cursor_surface, session.pyg.gray, [(5, 8), (10, 12), (5, 16)], 0)
    return cursor_surface

def background_fade():
    pyg = session.pyg
    background_surface = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
    background_surface.fill((0, 0, 0, 50))
    return background_surface

########################################################################################################################################################
# Classes
class MainMenu:
    """ Host a menu for file management and gameplay options. """

    # Core
    def __init__(self):
        
        #########################################################
        # Menu details
        ## Basics
        self.game_state = 'play_garden'
        self.header     = "MORS SOMNIA"
        self.choices    = ["NEW GAME", "LOAD", "SAVE", "CONTROLS", "QUIT"]

        ## Positions
        self.logo_pos   = []                       # set later (list of tuples)
        self.choice_pos = choice_pos(self.choices) # top choice
        self.cursor_pos = cursor_pos(self.choices) # top choice

        ## Other
        self.choice = 0

        #########################################################
        # Surface initialization
        ## Shorthand
        pyg = session.pyg
        img = session.img

        ## Background
        self.background_fade = background_fade()

        ## Header
        self.header_font    = pygame.font.SysFont('segoeuisymbol', 40, bold=True)
        self.header_surface = self.header_font.render(self.header, True, pyg.gray)
        self.header_pos     = (int((pyg.screen_width - self.header_surface.get_width())/2), 85)

        ## Logo (2x2)
        self.logo_surfaces = []
        for i in range(len(img.big)):
            for j in range(len(img.big[0])):
                X = pyg.screen_width - pyg.tile_width * (i+2)
                Y = pyg.screen_height - pyg.tile_height * (j+2)
                self.logo_surfaces.append(img.big[len(img.big)-j-1][len(img.big[0])-i-1])
                self.logo_pos.append((X, Y))

        ## Options
        self.choice_surfaces = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]

        ## Cursor
        self.cursor_surface = cursor()

    def run(self):
        
        #########################################################
        # Initialize
        ## Define shorthand
        pyg = session.pyg

        ## Switch overlay
        if self.game_state != pyg.game_state:
            self.game_state = pyg.game_state
            self.update_choices()

        ## Restrict keystroke speed
        session.effects.movement_speed(toggle=False, custom=2)
        
        ## Wait for input
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                
                #########################################################
                # Move cursor
                if event.key in pyg.key_UP:
                    self.key_UP()
                elif event.key in pyg.key_DOWN:
                    self.key_DOWN()
                
            elif event.type == KEYUP:
            
                #########################################################
                # Adjust music
                if event.key in pyg.key_PLUS:
                    session.aud.pause(paused=False)
                elif event.key in pyg.key_MINUS:
                    session.aud.pause(paused=True)
                
                #########################################################
                # Adjust window
                elif event.key in pyg.key_INFO:
                    self.key_INFO()
                
                elif event.key in pyg.key_ENTER:
                    
                    #########################################################
                    # Switch between garden and game
                    if self.choices[self.choice] in ["GARDEN", "CONTINUE"]:
                        self.switch_states()
                    
                    #########################################################
                    # Enter new game menu
                    elif self.choices[self.choice] == "NEW GAME":
                        pyg.overlay_state = 'new_game'
                        return
                    
                    #########################################################
                    # Enter load game menu
                    elif self.choices[self.choice] == "LOAD":
                        pyg.overlay_state = 'load'
                        return
                    
                    #########################################################
                    # Enter save game menu
                    elif self.choices[self.choice] == "SAVE":
                        if not pyg.startup_toggle:
                            pyg.overlay_state = 'save'
                            return
                    
                    #########################################################
                    # Enter controls menu
                    elif self.choices[self.choice] == "CONTROLS":
                        pyg.overlay_state = 'ctrl_menu'
                        return
                    
                    #########################################################
                    # Quit the game
                    elif self.choices[self.choice] == "QUIT":
                        pygame.quit()
                        sys.exit()
        
                #########################################################
                # Return to game
                elif event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
        pyg.overlay_state = 'menu'
        return

    def render(self):
        pyg = session.pyg
        
        #########################################################
        # Render surfaces
        ## Background
        pyg.overlay_queue.append([self.background_fade, (0, 0)])

        ## Header
        if pyg.startup_toggle:
            pyg.overlay_queue.append([self.header_surface, self.header_pos])
        
        ## Logo
        else:
            for i in range(len(self.logo_surfaces)):
                pyg.overlay_queue.append([self.logo_surfaces[i], self.logo_pos[i]])
        
        ## Choices
        for i in range(len(self.choices)):
            
            # Darken unavailable choices
            if (self.choices[i] == "SAVE") and (pyg.startup_toggle):
                surface = pyg.font.render(self.choices[i], True, pyg.dark_gray)
            else: surface = self.choice_surfaces[i]

            offset   = spacing * i
            position = (self.choice_pos[0], self.choice_pos[1] + offset)
            pyg.overlay_queue.append([surface, position])
        
        ## Cursor
        offset     = spacing * self.choice
        cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] + offset)
        pyg.overlay_queue.append([self.cursor_surface, cursor_pos])

    # Keys
    def key_UP(self):
        self.choice = (self.choice - 1) % len(self.choices)

    def key_DOWN(self):
        self.choice = (self.choice + 1) % len(self.choices)
    
    def key_INFO(self):
        pyg = session.pyg

        if pyg.windowed:
            pygame.display.set_mode((pyg.screen_width, pyg.screen_height), pygame.NOFRAME)
            pyg.windowed = False
        else:
            pygame.display.set_mode((pyg.screen_width, pyg.screen_height))
            pyg.windowed = True

    def key_BACK(self):
        pyg = session.pyg

        if pyg.game_state != 'play_garden':
            pyg.hud_state = 'on'
        pyg.overlay_state = None

    # Tools
    def update_choices(self):
        """ Adds a toggle to place player in the garden or main game. """

        pyg = session.pyg
        option_dict = {
            'play_game':   "GARDEN",
            'play_garden': "CONTINUE"}

        if len(self.choices) == 5:
            self.choices.insert(0, option_dict[self.game_state])
            self.choice_surfaces.insert(0, pyg.font.render(option_dict[self.game_state], True, pyg.gray))
            self.choice_pos = choice_pos(self.choices) # top choice
            self.cursor_pos = cursor_pos(self.choices) # top choice
            self.choice     += 1

        else:
            self.choices[0]         = option_dict[self.game_state]
            self.choice_surfaces[0] = pyg.font.render(option_dict[self.game_state], True, pyg.gray)
        
    def switch_states(self):
        """ Places player in the garden or main game. """

        pyg = session.pyg
        ent = session.player_obj.ent

        from mechanics import place_player

        #########################################################
        # Place player in garden
        if ent.env.name != 'garden':

            place_player(
                ent = ent,
                env = session.player_obj.envs.areas['underworld']['garden'],
                loc = session.player_obj.envs.areas['underworld']['garden'].player_coordinates)
            
            pyg.game_state = 'play_garden'
            pyg.hud_state  = 'off'
        
        #########################################################
        # Place player in world
        elif not pyg.startup_toggle:

            place_player(
                ent = ent,
                env = ent.last_env,
                loc = ent.last_env.player_coordinates)
            
            ent.role       = 'player'
            pyg.game_state = 'play_game'
            pyg.hud_state  = 'on'

class NewGameMenu:
    """ Hosts a menu for character creation.

        Creates a temporary player for customization in the Womb environment.
        Can discard the temporary player or keep it to replace the current player.
        If kept, an introduction screen is displayed before entering a dungeon.
    """

    # Core
    def __init__(self):

        pyg = session.pyg

        #########################################################
        # Menu details
        ## Basics
        self.choices      = ["HAIR", "FACE", "SEX", "SKIN", "HANDEDNESS", "", "ACCEPT", "BACK"]        
        self.orientations = ['front', 'right', 'back', 'left'] # character rotation

        ## Positions
        self.choice_pos = choice_pos(self.choices) # top choice
        self.cursor_pos = cursor_pos(self.choices) # top choice

        ## Other
        self.choice = 0

        self.last_rotate_time = 0
        self.rotate_time      = 0.7

        #########################################################
        # Menu
        ## Cursor
        self.cursor_surface = cursor()

        ## Options
        self.choice_surfaces = []
        for i in range(len(self.choices)):
            if   i == len(self.choices)-2:  color = pyg.green
            elif i == len(self.choices)-1:  color = pyg.red
            else:                           color = pyg.gray
            self.choice_surfaces.append(pyg.font.render(self.choices[i], True, color))

    def run(self):
        """ Functions
            ---------
            init_player     : womb and garden; stays in NewGameMenu
            startup         : womb and garden; scrapped after _finalize_player
            _finalize_player : womb, garden, home, overworld, and dungeon; persistent
        """
        
        pyg = session.pyg

        #########################################################
        # Initialize
        ## Return to garden at startup
        if not session.player_obj.ent:
            self.temp_obj      = self.init_player()
            session.player_obj = self.startup()
            return
        
        ## Pause the game
        pyg.pause = True

        ## Set navigation speed
        session.effects.movement_speed(toggle=False, custom=2)
        
        ## Wait for input
        for event in pygame.event.get():

            if event.type == KEYDOWN:
            
                #########################################################
                # Move cursor
                if event.key in pyg.key_UP:
                    self.key_UP()
                elif event.key in pyg.key_DOWN:
                    self.key_DOWN()

            elif event.type == KEYUP:

                if event.key in pyg.key_ENTER:

                    #########################################################
                    # Apply option
                    if self.choice <= 4:
                        self.apply_option()
                        
                    #########################################################
                    # Accept and start game
                    elif self.choice == 6:
                        self.fade_to_game()
                        return
                    
                    #########################################################
                    # Return to main menu
                    elif self.choice == 7:
                        self.key_BACK()
                        return

                elif event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
                
        pyg.overlay_state = 'new_game'
        return

    def render(self):
        
        pyg = session.pyg
        
        #########################################################
        # Render environment and character
        ## Rotate character
        if time.time() - self.last_rotate_time > self.rotate_time:
            self.last_rotate_time = float(time.time())
            self.temp_obj.ent.img_IDs[1] = self.orientations[
                self.orientations.index(self.temp_obj.ent.img_IDs[1]) - 1]
        
        #########################################################
        # Render menu
        ## Choices
        for i in range(len(self.choices)):
            surface  = self.choice_surfaces[i]
            offset   = spacing * i
            position = (self.choice_pos[0], self.choice_pos[1] + offset)
            pyg.overlay_queue.append([surface, position])
        
        ## Cursor
        offset     = spacing * self.choice
        cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] + offset)
        pyg.overlay_queue.append([self.cursor_surface, cursor_pos])

    # Keys
    def key_UP(self):
        self.choice = (self.choice - 1) % len(self.choices)

        # Skip blank line
        if not self.choices[self.choice]:
            self.choice = (self.choice - 1) % len(self.choices)

    def key_DOWN(self):
        self.choice = (self.choice + 1) % len(self.choices)

        # Skip blank line
        if not self.choices[self.choice]:
            self.choice = (self.choice + 1) % len(self.choices)

    def key_BACK(self):
        pyg = session.pyg
        
        pyg.pause         = False
        pyg.overlay_state = 'menu'

    # Tools
    def init_player(self):
        """ Creates a temporary player and womb environment. """
        
        from entities import PlayerData

        temp_obj = PlayerData()
        temp_obj.new_player_ent()
        return temp_obj

    def startup(self):
        """ Creates a second temporary player. This is meant to be a placeholder for the actual
            player object, separate from the temporary player used only in the New Game menu.
        """

        from mechanics import place_player

        #########################################################
        # Make temporary player
        session.player_obj = self.init_player()

        place_player(
            ent = session.player_obj.ent,
            env = session.player_obj.envs.areas['underworld']['garden'],
            loc = session.player_obj.envs.areas['underworld']['garden'].center)
        
        #########################################################
        # Fade into the main menu and garden
        session.pyg.game_state = 'play_garden'

        return session.player_obj

    def apply_option(self):
        from items import create_item

        if self.choice in [0, 1, 2]:
        
            #########################################################
            # Select option
            if self.choice == 0:
                role     = 'head'
                img_dict = session.img.hair_options

            elif self.choice == 1:
                role     = 'face'
                img_dict = session.img.face_options

            elif self.choice == 2:
                role     = 'chest'
                img_dict = session.img.chest_options
            
            #########################################################
            # Find next option
            index    = (img_dict.index(self.temp_obj.ent.equipment[role].img_IDs[0]) + 1) % len(img_dict)
            img_name = img_dict[index]
            
            #########################################################
            # Equip next option if already generated
            if img_name in [[x[i].img_IDs[0] for i in range(len(x))] for x in self.temp_obj.ent.inventory.values()]:
                session.items.toggle_equip(self.temp_obj.ent.inventory[img_name][0], silent=True)
            
            ## Generate option before equip
            else:
                item = create_item(img_name)
                session.items.pick_up(self.temp_obj.ent, item, silent=True)
                session.items.toggle_equip(item, silent=True)
        
        #########################################################
        # Apply skin option
        elif self.choice == 3:
            if self.temp_obj.ent.img_IDs[0] == 'white_skin':   self.temp_obj.ent.img_IDs[0] = 'black_skin'
            elif self.temp_obj.ent.img_IDs[0] == 'black_skin': self.temp_obj.ent.img_IDs[0] = 'white_skin'
        
        #########################################################
        # Apply handedness option
        elif self.choice == 4:
            if self.temp_obj.ent.handedness == 'left':      self.temp_obj.ent.handedness = 'right'
            elif self.temp_obj.ent.handedness == 'right':   self.temp_obj.ent.handedness = 'left'

    def fade_to_game(self):
        pyg = session.pyg

        # Prepare fade screen
        text = "Your hands tremble as the ground shudders in tune... something is wrong."
        pyg.add_intertitle(text)
        pyg.fn_queue.append([self._finalize_player,         {}])
        pyg.fn_queue.append([session.effects.enter_dungeon, {}])
        pyg.fade_state = 'out'

    def _finalize_player(self):
        """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
            Called in fade queue after the character creation menu is accepted. """
        
        pyg = session.pyg

        session.player_obj = copy.deepcopy(self.temp_obj)
        session.player_obj.finalize_player_ent()
        
        self.temp_obj      = self.init_player()
        pyg.msg_history    = {}
        pyg.pause          = False
        pyg.startup_toggle = False
        pyg.game_state     = 'play_game'
        pyg.hud_state      = 'on'
        pyg.overlay_state  = None

class FileMenu:
    """ Hosts file saving and loading. Takes screenshots for background images. """

    # Core
    def __init__(self):
        
        pyg = session.pyg

        #########################################################
        # Menu details
        ## Basics
        self.game_state  = 'load'
        self.headers     = ['SAVE', 'LOAD']
        self.choices     = ["FILE 1", "FILE 2", "FILE 3"]
        self.backgrounds = [
            "Data/File_1/screenshot.png",
            "Data/File_2/screenshot.png",
            "Data/File_3/screenshot.png"]
        
        ## Positions
        self.choice_pos = choice_pos(self.choices) # top choice
        self.cursor_pos = cursor_pos(self.choices) # top choice

        ## Other
        self.choice = 0

        #########################################################
        # Surface initialization
        ## Background
        self.background_fade    = background_fade()
        self.backgrounds_render = [pygame.image.load(path).convert() for path in self.backgrounds]

        ## Header
        self.header_surfaces = {
            'save': pyg.font.render(self.headers[0], True, pyg.gray),
            'load': pyg.font.render(self.headers[1], True, pyg.gray)}
        self.header_pos = (48, 32)

        ## Options
        self.choice_surfaces = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]

        ## Cursor
        self.cursor_surface = cursor()

    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        self.game_state = pyg.overlay_state

        ## Pause the game
        pyg.pause = True

        ## Set navigation speed
        session.effects.movement_speed(toggle=False, custom=2)
        
        ## Wait for input
        for event in pygame.event.get():
            
            if event.type == KEYDOWN:
                
                #########################################################
                # Select file
                if event.key in pyg.key_UP:
                    self.key_UP()
                elif event.key in pyg.key_DOWN:
                    self.key_DOWN()
                
            elif event.type == KEYUP:

                #########################################################
                # Activate and return
                if event.key in pyg.key_ENTER:
                    if self.game_state == 'save':
                        self.save_account()
                        self.key_BACK()
                        return
                    elif self.game_state == 'load':
                        self.load_account()
                        self.key_BACK()
                        return
            
                #########################################################
                # Return to main menu
                elif event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
        pyg.overlay_state = self.game_state
        return

    def render(self):
        #########################################################
        # Render surfaces
        pyg = session.pyg

        ## Background
        pyg.overlay_queue.append([self.backgrounds_render[self.choice], (0, 0)])
        pyg.overlay_queue.append([self.background_fade,                 (0, 0)])
        
        ## Header
        pyg.overlay_queue.append([self.header_surfaces[self.game_state], self.header_pos])
        
        ## Choices
        for i in range(len(self.choices)):
            offset   = spacing * i
            position = (self.choice_pos[0], self.choice_pos[1] + offset)
            pyg.overlay_queue.append([self.choice_surfaces[i], position])

        ## Cursor
        offset     = spacing * self.choice
        cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] + offset)
        pyg.overlay_queue.append([self.cursor_surface, cursor_pos])

    # Keys
    def key_UP(self):
        self.choice = (self.choice - 1) % len(self.choices)
        
    def key_DOWN(self):
        self.choice = (self.choice + 1) % len(self.choices)

    def key_BACK(self):
        pyg = session.pyg

        pyg.pause         = False
        pyg.overlay_state = 'menu'

    # Tools
    def save_account(self):
        """ Pickles a Player object and takes a screenshot. """

        from pygame_utilities import screenshot
        pyg = session.pyg

        #########################################################
        # Add asterisk to active option
        for i in range(len(self.choices)):
            if self.choices[i][-1] == '*': self.choices[i] = self.choices[i][:-2]
        self.choices[self.choice] += ' *'
        self.choice_surfaces = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]
        
        #########################################################
        # Save data from current player
        file_num = self.choice + 1
        session.player_obj.file_num = file_num
        with open(f"Data/File_{file_num}/player_obj.pkl", 'wb') as file:
            pickle.dump(session.player_obj, file)
        
        #########################################################
        # Take a screenshot
        screenshot(
            folder   = f"Data/File_{file_num}",
            filename = "screenshot.png",
            blur     = True)
        self.backgrounds_render = [pygame.image.load(path).convert() for path in self.backgrounds]

    def load_account(self):
        """ Loads a pickled Player object. """
        
        pyg = session.pyg
        
        #########################################################
        # Add asterisk to active option
        for i in range(len(self.choices)):
            if self.choices[i][-1] == '*':
                self.choices[i] = self.choices[i][:-2]
        self.choices[self.choice] += ' *'
        self.choice_surfaces = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]

        #########################################################
        # Load data onto fresh player
        session.player_obj.__init__()
        with open(f"Data/File_{self.choice+1}/player_obj.pkl", "rb") as file:
            session.player_obj = pickle.load(file)
        
        #########################################################
        # Clean up and return
        ## Check if dead
        if session.player_obj.ent.dead:
            session.play_game_obj.death_checked = True

        ## Update zoom
        session.player_obj.ent.env.camera.zoom_in(factor=0)

        ## Update gamestate
        pyg.msg_history    = {}
        pyg.gui_toggle     = True
        pyg.msg_toggle     = True
        pyg.startup_toggle = False
        pyg.game_state     = 'play_game'

    def check_player_id(self, id):
        """ Overwrites a save if it matches the provided ID of a living save file. """

        for choice in range(3):
            with open(f"Data/File_{choice+1}/player_obj.pkl", "rb") as file:
                player_obj = pickle.load(file)
                if (player_obj.ent.player_id == id) and (not player_obj.ent.dead):
                    self.choice = choice
                    self.save_account()

class CtrlMenu:

    # Core
    def __init__(self):
        """ Shows controls and allows preset selection. Menu design is set in update_controls.
            The options are keywords set in the Pygame class.
            Module: pygame_mechanics
        """
        
        pyg = session.pyg

        #########################################################
        # Menu details
        ## Basics
        self.name   = 'ctrl_menu'
        self.header = "Controls"
        self.options = [
            'numpad 1',
            'numpad 2',
            'arrows']
        
        ## Other
        self.choice = 0

        #########################################################
        # Surface initialization
        self.header_render = pyg.font.render(self.header, True, pyg.white)
        self.update_controls()

    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        ## Set navigation speed
        session.effects.movement_speed(toggle=False, custom=2)
        
        ## Pause the game
        pyg.pause = True

        ## Wait for input
        for event in pygame.event.get():
            
            if event.type == KEYDOWN:
                
                #########################################################
                # Change layout
                if event.key in pyg.key_LEFT:
                    self.update_controls(-1)
                elif event.key in pyg.key_RIGHT:
                    self.update_controls(1)
                
            elif event.type == KEYUP:

                #########################################################
                ## Return to main menu
                if event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
                if event.key in pyg.key_ENTER:
                    self.key_BACK()
                    return
                
        pyg.overlay_state = self.name
        return
    
    def render(self):
        pyg = session.pyg

        # Render background
        black = pygame.Surface(pyg.overlays.get_size())
        black.fill(pyg.black)
        pyg.overlay_queue.append([black, (0, 0)])
        
        # Render header
        pyg.overlay_queue.append([self.header_render, (25, 10)])
        
        # Render categories and options
        for i in range(len(self.layout_render)):
            offset = spacing * i
            pyg.overlay_queue.append([self.layout_render[i], (50, 38+offset)])

    # Keys
    def key_BACK(self):
        pyg = session.pyg

        pyg.pause         = False
        pyg.overlay_state = 'menu'

    # Tools
    def update_controls(self, direction=None):
        
        pyg = session.pyg

        #########################################################
        # Change layout
        if direction:
            current_index = self.options.index(pyg.controls_preset)
            new_index = (current_index + direction) % len(self.options)
            pyg.set_controls(self.options[new_index])

        #########################################################
        # Reconstruct options for rendering
        layout = [
            f"Move up:                                {pyg.key_UP[0]}                     Exit:                                         {pyg.key_BACK[0]}",
            f"Move down:                           {pyg.key_DOWN[0]}                     Activate 1:                             {pyg.key_ENTER[0]}",
            f"Move left:                               {pyg.key_LEFT[0]}                     Activate 2:                               {pyg.key_PERIOD[0]}",
            f"Move right:                            {pyg.key_RIGHT[0]}",
            "",
            
            f"Toggle inventory:                  {pyg.key_INV[0]}                     Enter combo:                         {pyg.key_HOLD[0]}",
            f"Toggle Catalog:                   {pyg.key_DEV[0]}                     Change speed:                      {pyg.key_SPEED[0]}",
            f"Toggle GUI:                            {pyg.key_GUI[0]}                     Zoom in:                                {pyg.key_PLUS[0]}",
            f"View stats:                             {pyg.key_INFO[0]}                     Zoom out:                              {pyg.key_MINUS[0]}",
            f"View questlog:                      {pyg.key_QUEST[0]}"]
    
        self.layout_render = [pyg.font.render(row, True, pyg.gray) for row in layout]

class StatsMenu:
    
    def __init__(self):
        """ Hosts display for player and pet stats. """

        pyg = session.pyg

        #########################################################
        # Menu details
        ## Basics
        self.game_state = 'play_garden'

        self.stats = {
            
            'play_game': {
                '            STATS': None,
                '':           None,
                'rank':       None,
                'rigor':      None,
                'attack':     None,
                'defense':    None,
                'sanity':     None},
            
            'play_garden': {
                '      RADIX ATRIUM': None,
                '':         None,
                'mood':     None,
                'stamina':  None,
                'strength': None,
                'appeal':   None}}
        
        self.moods = {
            'happiness': '( ^_^ )',
            'sadness':   '( Q_Q )',
            'anger':     '( >_< )',
            'boredom':   '( . _ .  )',
            'lethargy':  '( =_= )',
            'confusion': '(@_@)'}
        
        ## Positions
        self.X1      = pyg.tile_height + pyg.tile_height // 4
        self.X2      = pyg.tile_height * 4
        self.spacing = pyg.tile_height//2

        #########################################################
        # Surface initialization
        ## Background
        fill_width  = pyg.tile_width  * 5 + pyg.tile_width // 2
        fill_height = pyg.tile_height * 4 + pyg.tile_height // 2
        self.background_fill = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.background_fill.fill((0, 0, 0, 128))
        
        ## Border
        self.background_border = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.background_border, 
            pyg.gray, 
            [
                (0, 0),
                (fill_width-1, 0),
                (fill_width-1, fill_height-1),
                (0, fill_height-1)
            ],
            1)
        
    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        self.game_state = pyg.game_state
        pyg.hud_state   = 'off'
        self.update()
        
        ## Wait for input
        for event in pygame.event.get():
            
            if event.type == KEYUP:

                #########################################################
                # Close after any key is pressed
                self.key_BACK()
                return
                
        return

    def render(self):
        pyg = session.pyg

        pyg.msg_height = 1
        pyg.update_gui()
        
        # Background
        pyg.overlay_queue.append([self.background_fill, (32, 32)])
        pyg.overlay_queue.append([self.background_border, (32, 32)])
        
        # Stats
        Y = 32
        for i in range(len(list(self.stats[self.game_state]))):
            key, val = list(self.stats[self.game_state].items())[i]
            key = pyg.font.render(key, True, pyg.gray)
            val = pyg.font.render(val, True, pyg.gray)

            pyg.overlay_queue.append([key, (self.X1, Y)])
            pyg.overlay_queue.append([val, (self.X2, Y)])

            Y += self.spacing

    # Keys
    def key_BACK(self):
        pyg = session.pyg

        pyg.overlay_state = None
        if pyg.game_state != 'play_garden':
            pyg.hud_state = 'on'
        
    # Tools
    def update(self):
        """ Convert numerical stats to a number of stars. """
        
        ent = session.player_obj.ent

        if self.game_state == 'play_game':
            
            self.stats[self.game_state]['rank']    = self._set_stars(ent.rank)
            self.stats[self.game_state]['rigor']   = self._set_stars(ent.max_hp)
            self.stats[self.game_state]['attack']  = self._set_stars(ent.attack)
            self.stats[self.game_state]['defense'] = self._set_stars(ent.defense)
            self.stats[self.game_state]['sanity']  = self._set_stars(ent.sanity)

        else:

            self.stats[self.game_state]['mood']     = self.moods[session.pets.mood]
            self.stats[self.game_state]['stamina']  = self._set_stars(ent.env.pet_stats['stamina'])
            self.stats[self.game_state]['strength'] = self._set_stars(ent.env.pet_stats['strength'])
            self.stats[self.game_state]['appeal']   = self._set_stars(ent.env.pet_stats['appeal'])

    def _set_stars(self, stat):
        stat = int(stat)

        if stat < 5:    stars = 0
        elif stat < 20: stars = 1
        elif stat < 40: stars = 2
        elif stat < 65: stars = 3
        elif stat < 99: stars = 4
        else:           stars = 5

        no_stars = 5 - stars

        return "★" * stars + "☆" * no_stars

# Needs updating
class Textbox:

    def __init__(self, header='', text=''):
        """ Basic textbox inlay. No controls or anything complicated. """
        
        pyg = session.pyg

        #########################################################
        # Parameters
        ## Basics
        self.header = header
        self.text   = text

        ## Positions
        self.backdrop_pos = (32, 32)
        self.header_pos   = (37, 32)
        self.text_pos     = [(62, 54+32*(i+1)) for i in range(len(text))]

        ## Other
        self.backdrop_size = (32*18, 32*13)
        
        #########################################################
        # Surface initialization
        ## Headers and text
        self.header_render = pyg.font.render(header, True, pyg.white)
        self.text_render   = [pyg.font.render(row, True, pyg.gray) for row in text]
        
        ## Background
        self.background_fade = background_fade()
        
        ## Backdrop
        self.backdrop = pygame.Surface(self.backdrop_size, pygame.SRCALPHA)
        self.backdrop.fill((0, 0, 0, 128))

        self.border = pygame.Surface(self.backdrop_size, pygame.SRCALPHA)
        pygame.draw.polygon(
            surface = self.border, 
            color   = pyg.gray,
            points = [
                (0,                       0),
                (self.backdrop_size[0]-1, 0),
                (self.backdrop_size[0]-1, self.backdrop_size[1]-1),
                (0,                       self.backdrop_size[1]-1)],
            width = 1)
        
    def run(self):
        pyg = session.pyg

        for event in pygame.event.get():

            #########################################################
            # Close after any key is pressed
            if event.type == KEYUP:
                self.key_BACK()
                return

        pyg.overlay_state = 'textbox'
        return

    def render(self):
        pyg = session.pyg
        
        # Render backdrop
        pyg.overlay_queue.append([self.background_fade, (0, 0)])
        pyg.overlay_queue.append([self.backdrop,        self.backdrop_pos])
        pyg.overlay_queue.append([self.border,          self.backdrop_pos])
                
        # Render header and text
        pyg.overlay_queue.append([self.header_render, self.header_pos])
        for i in range(len(self.text_render)):
            pyg.overlay_queue.append([self.text_render[i], self.text_pos[i]])

    def key_BACK(self):
        pyg = session.pyg

        if pyg.game_state != 'play_garden':
            pyg.hud_state = 'on'
        pyg.overlay_state = None

########################################################################################################################################################