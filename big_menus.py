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
        self.spacing    = 24
        self.logo_pos   = []                                         # set later (list of tuples)
        self.header_pos = (0,  85)                                   # set later (centered)
        self.choice_pos = (48, 436 - len(self.choices)*self.spacing) # top choice
        self.cursor_pos = (32, 436 - len(self.choices)*self.spacing) # top choice

        ## Other
        self.choice = 0
        
        self.last_press_time = 0
        self.cooldown_time   = 0.5
        self.gui_cache = False
        self.msg_cache = False

        #########################################################
        # Surface initialization
        ## Shorthand
        pyg = session.pyg
        img = session.img

        ## Background
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

        ## Header
        self.header_font    = pygame.font.SysFont('segoeuisymbol', 40, bold=True)
        self.header_surface = self.header_font.render(self.header, True, pyg.gray)
        self.header_pos     = (int((pyg.screen_width - self.header_surface.get_width())/2), self.header_pos[1])

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
        self.cursor_surface = pygame.Surface((16, 16)).convert()
        self.cursor_surface.set_colorkey(self.cursor_surface.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_surface, pyg.gray, [(5, 8), (10, 12), (5, 16)], 0)

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

            offset   = self.spacing * i
            position = (self.choice_pos[0], self.choice_pos[1] + offset)
            pyg.overlay_queue.append([surface, position])
        
        ## Cursor
        offset     = self.spacing * self.choice
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
            self.choice_pos = (self.choice_pos[0], 436 - len(self.choices)*self.spacing) # top choice
            self.cursor_pos = (self.cursor_pos[0], 436 - len(self.choices)*self.spacing) # top choice
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

    # Core
    def __init__(self):
        """ Creates a temporary player for customization in the Womb environment.
            Hosts a menu that can discard the temporary player or keep it to replace the current player.
            If kept, an introduction screen is displayed before entering the dungeon.
        
            HAIR:       sets hair by altering hair_index, which is used in new_game to add hair as an Object hidden in the inventory
            HANDEDNESS: mirrors player/equipment tiles, which are saved in session.img.dict and session.img.cache
            ACCEPT:     runs new_game() to generate player, home, and default items, then runs play_game() """
        
        pyg = session.pyg

        #########################################################
        # Menu details
        ## Basics
        self.choices      = ["HAIR", "FACE", "SEX", "SKIN", "HANDEDNESS", "", "ACCEPT", "BACK"]        
        self.orientations = ['front', 'right', 'back', 'left']

        ## Positions
        self.spacing    = 24
        self.logo_pos   = []                                         # set later (list of tuples)
        self.header_pos = (0,  85)                                   # set later (centered)
        self.choice_pos = (48, 436 - len(self.choices)*self.spacing) # top choice
        self.cursor_pos = (32, 436 - len(self.choices)*self.spacing) # top choice

        ## Other
        self.choice = 0

        self.last_press_time = 0
        self.cooldown_time   = 0.7

        self.gui_cache = False
        self.msg_cache = False

        #########################################################
        # Menu
        ## Cursor
        self.cursor_surface = pygame.Surface((16, 16)).convert()
        self.cursor_surface.set_colorkey(self.cursor_surface.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_surface, pyg.gray, [(5, 8), (10, 12), (5, 16)], 0)

        ## Options
        self.choice_surfaces = []
        for i in range(len(self.choices)):
            if   i == len(self.choices)-2:  color = pyg.green
            elif i == len(self.choices)-1:  color = pyg.red
            else:                           color = pyg.gray
            self.choice_surfaces.append(pyg.font.render(self.choices[i], True, color))

    def run(self):
        """ Creates a temporary player, then returns to garden at startup or hosts character creation otherwise.
        
            Player creation
            ---------------
            init_player     : womb and garden; stays in NewGameMenu
            startup         : womb and garden; scrapped after finalize_player
            finalize_player : womb, garden, home, overworld, and dungeon; persistent
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
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = float(time.time())
            self.temp_obj.ent.img_names[1] = self.orientations[
                self.orientations.index(self.temp_obj.ent.img_names[1]) - 1]
        
        #########################################################
        # Render menu
        ## Choices
        for i in range(len(self.choices)):
            surface  = self.choice_surfaces[i]
            offset   = self.spacing * i
            position = (self.choice_pos[0], self.choice_pos[1] + offset)
            pyg.overlay_queue.append([surface, position])
        
        ## Cursor
        offset     = self.spacing * self.choice
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
        temp_obj.init_player()
        return temp_obj

    def startup(self):
        """ Creates a second temporary player. This is meant to be a placeholder for the actual
            player object, separate from the temporary player used only in the New Game menu.
        """

        from mechanics import place_player

        #########################################################
        # Make temporary player
        session.player_obj = self.init_player()
        session.dev.update_dict()

        place_player(
            ent = session.player_obj.ent,
            env = session.player_obj.envs.areas['underworld']['garden'],
            loc = session.player_obj.envs.areas['underworld']['garden'].center)
        
        #########################################################
        # Fade into the main menu and garden
        session.pyg.game_state = 'play_garden'

        return session.player_obj

    def apply_option(self):

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
            index    = (img_dict.index(self.temp_obj.ent.equipment[role].img_names[0]) + 1) % len(img_dict)
            img_name = img_dict[index]
            
            #########################################################
            # Equip next option if already generated
            if img_name in [[x[i].img_names[0] for i in range(len(x))] for x in self.temp_obj.ent.inventory.values()]:
                session.items.toggle_equip(self.temp_obj.ent.inventory[img_name][0], silent=True)
            
            ## Generate option before equip
            else:
                item = session.items.create_item(img_name)
                session.items.pick_up(self.temp_obj.ent, item, silent=True)
                session.items.toggle_equip(item, silent=True)
        
        #########################################################
        # Apply skin option
        elif self.choice == 3:
            if self.temp_obj.ent.img_names[0] == 'white':   self.temp_obj.ent.img_names[0] = 'black'
            elif self.temp_obj.ent.img_names[0] == 'black': self.temp_obj.ent.img_names[0] = 'white'
        
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
        pyg.fn_queue.append([self.finalize_player,             {}])
        pyg.fn_queue.append([session.effects.enter_dungeon_queue, {'lvl_num': 4}])
        pyg.fade_state = 'out'

    def finalize_player(self):
        """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
            Called in fade queue after the character creation menu is accepted. """
        
        pyg = session.pyg

        session.player_obj = copy.deepcopy(self.temp_obj)
        session.player_obj.finalize_player()
        
        self.temp_obj      = self.init_player()
        pyg.msg_history    = {}
        pyg.pause          = False
        pyg.startup_toggle = False
        pyg.game_state     = 'play_game'
        pyg.hud_state      = 'on'
        pyg.overlay_state  = None

class FileMenu:

    # Core
    def __init__(self):
        """ Hosts file saving and loading. Takes screenshots for background images.
            The mode is passed from the game state, which also populates the header.
        """
        
        pyg = session.pyg

        #########################################################
        # Menu details
        ## Basics
        self.mode    = None
        self.header  = None

        self.options = [
            "File 1",
            "File 2",
            "File 3"]
        self.backgrounds = [
            "Data/File_1/screenshot.png",
            "Data/File_2/screenshot.png",
            "Data/File_3/screenshot.png"]
        
        ## Positions
        self.options_dict = {
            0: 38,
            1: 62,
            2: 86}

        ## Other
        self.choice = 0
        self.gui_cache = False
        self.msg_cache = False

        #########################################################
        # Surface initialization
        ## Headers
        self.header_dict = {
            'save': pyg.font.render('Save', True, pyg.white),
            'load': pyg.font.render('Load', True, pyg.white)}
        
        ## Cursor
        self.cursor_render = pygame.Surface((16, 16)).convert()
        self.cursor_render.set_colorkey(self.cursor_render.get_at((0,0)))
        pygame.draw.polygon(self.cursor_render, pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
        
        ## Backgrounds
        self.update_backgrounds()

    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        self.mode = pyg.overlay_state

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
                    if self.mode == 'save':
                        self.save_account()
                        self.key_BACK()
                        return
                    elif self.mode == 'load':
                        self.load_account()
                        self.key_BACK()
                        return
            
                #########################################################
                # Return to main menu
                elif event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
        pyg.overlay_state = self.mode
        return

    def render(self):
        pyg = session.pyg

        # Render background
        pyg.overlay_queue.append([self.backgrounds_render[self.choice], (0, 0)])
        
        # Render header and cursor
        pyg.overlay_queue.append([self.header_dict[self.mode], (25, 10)])
        pyg.overlay_queue.append([self.cursor_render, (25, self.options_dict[self.choice])])
        
        # Render categories and options
        for i in range(len(self.options)):
            option_render = pyg.font.render(self.options[i], True, pyg.gray)
            pyg.overlay_queue.append([option_render, (50, self.options_dict[i])])

    # Keys
    def key_UP(self):
        self.choice = (self.choice - 1) % len(self.options)
        
    def key_DOWN(self):
        self.choice = (self.choice + 1) % len(self.options)

    def key_BACK(self):
        pyg = session.pyg

        pyg.pause         = False
        pyg.overlay_state = 'menu'

    # Tools
    def save_account(self):
        """ Pickles a Player object and takes a screenshot. """

        from pygame_utilities import screenshot
        
        #########################################################
        # Add asterisk to active option
        for i in range(len(self.options)):
            if self.options[i][-1] == '*': self.options[i] = self.options[i][:-2]
        self.options[self.choice] += ' *'
        
        #########################################################
        # Save data from current player
        file_num = self.choice + 1
        session.player_obj.file_num = file_num
        with open(f"Data/File_{file_num}/session.player_obj.pkl", 'wb') as file:
            pickle.dump(session.player_obj, file)
        
        #########################################################
        # Take a screenshot
        screenshot(
            folder   = f"Data/File_{file_num}",
            filename = "screenshot.png",
            blur     = True)
        self.update_backgrounds()

    def load_account(self):
        """ Loads a pickled Player object. """
        
        pyg = session.pyg

        #########################################################
        # Add asterisk to active option
        for i in range(len(self.options)):
            if self.options[i][-1] == '*':
                self.options[i] = self.options[i][:-2]
        self.options[self.choice] += ' *'

        #########################################################
        # Load data onto fresh player
        session.player_obj.__init__()
        with open(f"Data/File_{self.choice+1}/session.player_obj.pkl", "rb") as file:
            session.player_obj = pickle.load(file)
        
        #########################################################
        # Clean up and return
        ## Update event bus
        session.bus.clear()

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

    def update_backgrounds(self):
        self.backgrounds_render = [pygame.image.load(path).convert() for path in self.backgrounds]

    def check_player_id(self, id):
        """ Overwrites a save if it matches the provided ID of a living save file. """

        for choice in range(3):
            with open(f"Data/File_{choice+1}/session.player_obj.pkl", "rb") as file:
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
        self.gui_cache = False
        self.msg_cache = False

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
            pyg.overlay_queue.append([self.layout_render[i], (50, 38+24*i)])

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

# Needs updating
class StatsMenu:
    
    def __init__(self):
        """ Hosts display for player stats. """

        self.overlay = 'pet_stats'
        self.pets_init()

        self.ent_stats = {
            'Character Information': None,
            '': None,
            'rank':       None,
            'rigor':      None,
            'attack':     None,
            'defense':    None,
            'sanity':     None}

    def pets_init(self):
        self.pet_stats = {
            '      RADIX ATRIUM': None,
            '':         None,
            'mood':     None,
            'stamina':  None,
            'strength': None,
            'appeal':   None}
        
        # Numerical stats
        self.pet_levels = {
            'stamina':   1,
            'strength':  1,
            'appeal':    1}
        
        self.pet_moods = {
            'happiness': 5,
            'sadness':   0,
            'anger':     0,
            'boredom':   0,
            'lethargy':  0,
            'confusion': 0}
        
        # String conversions
        self.pet_faces = {
            'happiness': '( ^_^ )',
            'sadness':   '( Q_Q )',
            'anger':     '( >_< )',
            'boredom':   '( . _ .  )',
            'lethargy':  '( =_= )',
            'confusion': '(@_@)'}
        
        # Time to lose happiness and gain something else
        self.happiness_cooldown = 10
        self.happiness_press    = 0
        
        # Time between mood switches if tied
        self.emoji_cooldown     = 10
        self.emoji_press        = 0

    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        session.effects.movement_speed(toggle=False, custom=2)
        
        ## Switch overlay
        if self.overlay != pyg.overlay_state:
            self.overlay = pyg.overlay_state
        self.update()
        
        ## Wait for input
        for event in pygame.event.get():
            
            if event.type == KEYUP:

                #########################################################
                # Close after any key is pressed
                self.key_BACK()
                return
                
        pyg.overlay_state = self.overlay
        return

    def key_BACK(self):
        pyg = session.pyg

        pyg.last_press_time = float(time.time())
        pyg.overlay_state = None

    def update(self):
        
        if self.overlay == 'ent_stats':
                
            self.ent_stats['rank']  = '★' * int(session.player_obj.ent.rank)
            if len(self.ent_stats['rank']) < 5:
                while len(self.ent_stats['rank']) < 5:
                    self.ent_stats['rank'] += '☆'
                
            self.ent_stats['rigor']   = '★' * int(session.player_obj.ent.max_hp // 10)
            if len(self.ent_stats['rigor']) < 5:
                while len(self.ent_stats['rigor']) < 5:
                    self.ent_stats['rigor'] += '☆'
            
            self.ent_stats['attack']   = '★' * int(session.player_obj.ent.attack // 10)
            if len(self.ent_stats['attack']) < 5:
                while len(self.ent_stats['attack']) < 5:
                    self.ent_stats['attack'] += '☆'
            
            self.ent_stats['defense']   = '★' * int(session.player_obj.ent.defense // 10)
            if len(self.ent_stats['defense']) < 5:
                while len(self.ent_stats['defense']) < 5:
                    self.ent_stats['defense'] += '☆'

            self.ent_stats['sanity']   = '★' * int(session.player_obj.ent.sanity // 10)
            if len(self.ent_stats['sanity']) < 5:
                while len(self.ent_stats['sanity']) < 5:
                    self.ent_stats['sanity'] += '☆'
            
            self.current_stats = self.ent_stats

        else:
            self.pet_update()
            self.current_stats = self.pet_stats

    def render(self):
        pyg = session.pyg

        pyg.msg_height = 1
        pyg.update_gui()
        
        # Render background
        fill_width  = pyg.tile_width  * 5 + pyg.tile_width // 2
        fill_height = pyg.tile_height * 4 + pyg.tile_height // 2
        self.cursor_fill   = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.cursor_fill.fill((0, 0, 0, 128))
        pyg.overlay_queue.append([self.cursor_fill, (32, 32)])
        
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
        pyg.overlay_queue.append([self.cursor_border, (32, 32)])
        
        # Render items
        Y = 32
        for i in range(len(list(self.current_stats))):
            X1 = pyg.tile_height + pyg.tile_height // 4
            X2 = pyg.tile_height * 4
            key, val = list(self.current_stats.items())[i]
            key = pyg.font.render(key, True, pyg.gray)
            val = pyg.font.render(val, True, pyg.gray)
            pyg.overlay_queue.append([key, (X1, Y)])
            pyg.overlay_queue.append([val, (X2, Y)])
            Y += pyg.tile_height//2

    def pet_startup(self, env):
        self.ents = env.entities

    def pet_stat_check(self, dic):
        for key, value in dic.items():
            if value > 10:  dic[key] = 10
            elif value < 0: dic[key] = 0

    def pet_update(self):
        """ Decreases happiness over time, sets mood to current highest stat, handles mood effects, and updates stat display. """
        
        # Lose happiness
        if self.pet_moods['happiness']:
            if time.time() - self.happiness_press > self.happiness_cooldown:
                self.happiness_press = time.time()
                
                # Random chance to lose happiness and gain something else
                if not random.randint(0, 1):
                    self.pet_moods['happiness'] -= 1
                    self.pet_moods[random.choice(list(self.pet_moods.keys()))] += 1
        
        ## Keep stats to [0, 10]
        self.pet_stat_check(self.pet_levels)
        self.pet_stat_check(self.pet_moods)
        
        # Set mood to those with the highest value
        max_val = max(self.pet_moods.values())
        current_moods = [mood for mood, val in self.pet_moods.items() if val == max_val]
        
        ## Alternate between tied moods
        if len(current_moods) > 1:
            if time.time() - self.emoji_press > self.emoji_cooldown:
                self.emoji_press = time.time()
                self.pet_stats['mood'] = self.pet_faces[random.choice(current_moods)]        
        
        ## Set the current mood
        else:
            self.pet_stats['mood'] = self.pet_faces[current_moods[0]]
        
        ## Apply mood effects
        if self.pet_moods['happiness'] <= 2:
            if self.ents[-1].img_names[0] != 'purple radish':
                for ent in self.ents:
                    if ent != session.player_obj.ent:
                        if ent.img_names[0] != 'purple radish':
                            ent.img_names[0] = 'purple radish'
        elif self.pet_moods['happiness'] >= 8:
            if self.ents[-1].img_names[0] != 'orange radish':
                for ent in self.ents:
                    if ent != session.player_obj.ent:
                        if ent.img_names[0] != 'orange radish':
                            ent.img_names[0] = 'orange radish'
        else:
            if self.ents[-1].img_names[0] != 'red radish':
                for ent in self.ents:
                    if ent != session.player_obj.ent:
                        if ent.img_names[0] != 'red radish':
                            ent.img_names[0] = 'red radish'
        
        # Set levels
        self.pet_stats['stamina']  = '★' * self.pet_levels['stamina']
        while len(self.pet_stats['stamina']) < 5:
            self.pet_stats['stamina'] += '☆'
        self.pet_stats['strength'] = '★' * self.pet_levels['strength']
        while len(self.pet_stats['strength']) < 5:
            self.pet_stats['strength'] += '☆'
        self.pet_stats['appeal']   = '★' * self.pet_levels['appeal']
        while len(self.pet_stats['appeal']) < 5:
            self.pet_stats['appeal'] += '☆'

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
        self.gui_cache = False
        self.msg_cache = False
        
        #########################################################
        # Surface initialization
        ## Headers and text
        self.header_render = pyg.font.render(header, True, pyg.white)
        self.text_render   = [pyg.font.render(row, True, pyg.gray) for row in text]
        
        ## Background
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))
        
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