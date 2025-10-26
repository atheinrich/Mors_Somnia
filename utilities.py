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

## Specific
import pygame
from   pygame.locals import *
from   PIL import Image, ImageFilter, ImageOps

## Local
import session
from data_management import img_ents_dict, img_equipment_dict, img_other_dict

########################################################################################################################################################
# Classes
class MainMenu:

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
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Wait for input
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                
                #########################################################
                # Move cursor
                if event.key in pyg.key_UP:
                    self.key_UP()
                elif event.key in pyg.key_DOWN:
                    self.key_DOWN()
                
                #########################################################
                # Adjust music
                elif event.key in pyg.key_PLUS:
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
                    if self.choices[self.choice] == "NEW GAME":
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
        
            elif event.type == KEYUP:
            
                #########################################################
                # Return to game
                if event.key in pyg.key_BACK:
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

        pyg.last_press_time = float(time.time())
        pyg.hud_state     = 'on'
        pyg.overlay_state = None

    def update_choices(self):
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

        pyg = session.pyg

        from mechanics import place_player

        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = float(time.time())

            if session.player_obj.ent.env.name != 'garden':
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.areas['underworld']['garden'],
                    loc = session.player_obj.envs.areas['underworld']['garden'].player_coordinates)
                pyg.game_state = 'play_garden'
            
            elif not pyg.startup_toggle:
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.ent.last_env,
                    loc = session.player_obj.ent.last_env.player_coordinates)
                pyg.game_state = 'play_game'
                pyg.hud_state  = 'on'

class FileMenu:

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

    def update_backgrounds(self):
        self.backgrounds_render = [pygame.image.load(path).convert() for path in self.backgrounds]

    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        self.mode = pyg.overlay_state
        session.mech.movement_speed(toggle=False, custom=2)
        
        for event in pygame.event.get():
            
            #########################################################
            # Choose a file
            if event.type == KEYDOWN:
                
                # Select file
                if event.key in pyg.key_UP:     self.key_UP()
                elif event.key in pyg.key_DOWN: self.key_DOWN()
                
                # Activate and return
                elif event.key in pyg.key_ENTER:
                    if self.mode == 'save':   self.save_account()
                    elif self.mode == 'load': self.load_account()

                    pyg.overlay_state = 'menu'
                    return
            
            #########################################################
            # Return to main menu
            elif event.type == KEYUP:

                if event.key in pyg.key_BACK:
                    pyg.last_press_time = float(time.time())
                    pyg.overlay_state = 'menu'
                    return
        
        pyg.overlay_state = self.mode
        return

    def key_UP(self):
        self.choice = (self.choice - 1) % len(self.options)
        
    def key_DOWN(self):
        self.choice = (self.choice + 1) % len(self.options)

    def save_account(self):    
        """ Pickles a Player object, """
        
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
        
        #########################################################
        # Clean up and return
        session.pyg.overlay_state = 'main_menu'

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
        if session.player_obj.ent.dead:
            session.play_game_obj.death_checked = True
        session.player_obj.ent.env.camera.zoom_in(factor=0)
        pyg.gui_toggle     = True
        pyg.msg_toggle     = True
        pyg.startup_toggle = False
        pyg.game_state     = 'play_game'
        pyg.overlay_state  = 'main_menu'

    def check_player_id(self, id):
        """ Overwrites a save if it matches the provided ID of a living save file. """

        for choice in range(3):
            with open(f"Data/File_{choice+1}/session.player_obj.pkl", "rb") as file:
                player_obj = pickle.load(file)
                if (player_obj.ent.player_id == id) and (not player_obj.ent.dead):
                    self.choice = choice
                    self.save_account()

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

class CtrlMenu:

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

    def run(self):
        
        pyg = session.pyg

        #########################################################
        # Initialize
        session.mech.movement_speed(toggle=False, custom=2)
        
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
                    pyg.overlay_state = 'menu'
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
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Switch overlay
        if self.overlay != pyg.overlay_state:
            self.overlay = pyg.overlay_state
        self.update()
        
        ## Wait for input
        for event in pygame.event.get():
            
            if event.type == KEYUP:

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

        #########################################################
        # Close after any key is pressed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                pyg.hud_state     = 'on'
                pyg.overlay_state = None
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

TILESET_PATHS = {
    'entities':  'Data/.Images/tileset_ent.png',
    'equipment': 'Data/.Images/tileset_equip.png',
    'other':     'Data/.Images/tileset_other.png',
    'other_alt': 'Data/.Images/tileset_other_alt.png',
    'big':       'Data/.Images/decor_1_m_logo.png'
}

OTHER_META = {

    'decor': [
        'tree', 'bones', 'boxes',  'fire', 'leafy', 'skeleton', 'shrooms',
        'red plant right', 'red plant left', 'cup shroom', 'frond',  'blades', 'purple bulbs',
        'lights'
    ],

    'bubbles': [
        'dots', 'exclamation', 'dollar', 'cart', 'question', 'skull', 'heart', 'water'
    ],

    'furniture': [
        'purple bed', 'red bed', 'shelf left', 'shelf right', 'long table left', 'long table right',
        'table', 'red chair left', 'red chair right',
        'red rug bottom left',   'red rug bottom middle',   'red rug bottom right',
        'red rug middle left',   'red rug middle middle',  'red rug middle right',
        'red rug top left',      'red rug top middle',      'red rug top right',
        'green rug bottom left', 'green rug bottom middle', 'green rug bottom right',
        'green rug middle left', 'green rug middle middle', 'green rug middle right',
        'green rug top left',    'green rug top middle',    'green rug top right'
    ],

    'drugs': [
        'needle', 'skin', 'teeth', 'bowl', 'plant', 'bubbles'
    ],

    'potions': [
        'red', 'blue', 'gray', 'purple'
    ],

    'scrolls': [
        'closed', 'open'
    ],

    'stairs': [
        'door', 'portal'
    ],

    'floors': [
        'dark green', 'dark blue', 'dark red',  'green',  'red',    'blue',
        'wood',       'water',     'sand1',     'sand2',  'grass1', 'grass2',
        'bubbles1',   'bubbles2',  'bubbles3',  'dirt1',  'dirt2',
        'grass3',     'grass4',    'gray tile', 'brown tile'
    ],

    'walls': [
        'dark green', 'dark red', 'dark blue', 'gray', 'red', 'green', 'gold'
    ],

    'roofs': [
        'tiled', 'slats'
    ],

    'paths': [
        'left right', 'up down', 'down right', 'down left', 'up right', 'up left'
    ],

    'concrete': [
        'gray window', 'gray door', 'gray wall left', 'gray wall', 'gray wall right', 'gray floor'
    ],

    'null': [
        'null'
    ]
}

BIOMES = {
    
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

SHORT_LIST = [
    'red radish', 'orange radish', 'purple radish']

def get_short_list():
    return SHORT_LIST

def get_tileset_path(category_key):
    return TILESET_PATHS.get(category_key)

def get_other_meta():
    return OTHER_META['names'], OTHER_META['options']

def get_biomes():
    return BIOMES

class Images:
    """ Loads images from png file and sorts them in a global dictionary. One save for each file.

        The tileset (tileset.png) is organized in rows, with each row being a category identified below
        by the categories list. This function breaks the tileset into individual tiles and adds each tile
        to its respective category in a global dictionary for later use.
        
        session.img.dict:        mutable dictionary sorted by category
        session.img.cache:  less mutable than session.img.dict """

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

        pyg = session.pyg

        self.creation_options = {
            'hair':  ['bald'],
            'face':  ['clean'],
            'chest': ['flat'],
            'skin':  [],
            'armor': []}
        
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
        self.biomes = get_biomes()
        
        # Gather images for character_creation
        self.hair_options  = self.creation_options['hair']
        self.face_options  = self.creation_options['face']
        self.chest_options = self.creation_options['chest']
        self.skin_options  = self.creation_options['skin']
        self.armor_names   = self.creation_options['armor']
        
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
        
        pyg = session.pyg

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
        path       = get_tileset_path('entities')
        ent_matrix = self.import_tiles(path, flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        entity_options = ['front', 'back', 'left', 'right']

        # Identify character creation options
        self.ent_names = []
        for key, dict in img_ents_dict.items():
            if dict['slot'] is not None:
                self.creation_options[dict['slot']].append(key)
            self.ent_names.append(key)

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
        path         = get_tileset_path('equipment')
        equip_matrix = self.import_tiles(path, flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        equip_options = ['dropped', 'front', 'back', 'left', 'right']
        equip_aliases = {
            'clean': 'null',
            'flat':  'null',
            'bald':  'null'}

        # Identify character creation options
        self.equip_names = []
        for key, dict in img_equipment_dict.items():
            if dict['slot'] is not None:
                self.creation_options[dict['slot']].append(key)
            self.equip_names.append(key)

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
        
        for key, val in equip_aliases.items():
            self.equip[key] = self.equip[val]
        
    def load_other(self, flipped=False, alt=False):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Choose tileset
        if alt:
            path           = get_tileset_path('other_alt')
            self.other_alt = {}
            tile_dict      = self.other_alt
        else:
            path           = get_tileset_path('other')
            self.other     = {}
            tile_dict      = self.other
        
        # Import tiles
        other_matrix = self.import_tiles(path, flipped=flipped, effects=['posterize'])

        # Identify character creation options
        for key, dict in img_other_dict.items():
            if dict['group'] not in tile_dict.keys():
                tile_dict[dict['group']] = []
            tile_dict[dict['group']].append(key)
        self.other_names = list(tile_dict.keys())

        decor_options     = tile_dict['decor']
        bubbles_options   = tile_dict['bubbles']
        furniture_options = tile_dict['furniture']
        drugs_options     = tile_dict['drugs']
        potions_options   = tile_dict['potions']
        scrolls_options   = tile_dict['scrolls']
        stairs_options    = tile_dict['stairs']
        floors_options    = tile_dict['floors']
        walls_options     = tile_dict['walls']
        roofs_options     = tile_dict['roofs']
        paths_options     = tile_dict['paths']
        concrete_options  = tile_dict['concrete']
        null_options      = tile_dict['null']

        other_options = [
            decor_options,  bubbles_options, furniture_options,
            drugs_options,  potions_options, scrolls_options,
            stairs_options, floors_options,  walls_options,
            roofs_options,  paths_options,   concrete_options, 
            null_options]
        
        # Create image dictionary
        index = 0
        for _ in self.other_names:
            tile_dict[self.other_names[index]] = {option: image for (option, image) in zip(other_options[index], other_matrix[index])}
            index += 1
        self.other_count = sum([len(options_list) for options_list in other_options])

    def big_img(self):
    
        # Import tiles
        path     = get_tileset_path('big')
        self.big = self.import_tiles(path, flipped=False, effects=['posterize'])

    # Utility
    def average(self):
        pyg = session.pyg

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
        """ Shift the tile by an offset. """
        
        if type(image) == list: image = self.dict[image[0]][image[1]]
        
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
        pyg = session.pyg

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
        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - session.player_obj.ent.env.camera.Y
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
            x         = vicinity_list[i%len(vicinity_list)].X - session.player_obj.ent.env.camera.X
            y         = vicinity_list[i%len(vicinity_list)].Y - session.player_obj.ent.env.camera.Y
            image_pos = (x, y)
            duration  = 0.5
            last_time = time.time()
            delay     = i*0.1
            
            self.render_log.append([image, image_pos, duration, last_time, delay])
        
        image     = image
        x         = vicinity_list[0].X - session.player_obj.ent.env.camera.X
        y         = vicinity_list[0].Y - session.player_obj.ent.env.camera.Y
        image_pos = (x, y)
        duration  = 0.5
        last_time = time.time()
        delay     = len(vicinity_list)*0.1
        
        self.render_log.append([image, image_pos, duration, last_time, delay])

    def flash_above(self, ent, image):
        """ Death animation. """
        
        pyg = session.pyg

        short_list = get_short_list()
        if ent.name in short_list: shift = 12
        else:                      shift = 0
        
        self.impact = True
        
        image     = image
        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - pyg.tile_height - session.player_obj.ent.env.camera.Y + shift
        image_pos = (x, y)
        duration  = 0.8
        delay     = 0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - pyg.tile_height - session.player_obj.ent.env.camera.Y + shift
        image_pos = (x, y)
        duration  = 0.2
        delay     = 1.0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

    def flash_on(self, ent, image):
        """ Death animation. """
        
        self.impact = True
        
        image     = image
        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - session.player_obj.ent.env.camera.Y
        image_pos = (x, y)
        duration  = 0.8
        delay     = 0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - session.player_obj.ent.env.camera.Y
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
                        session.pyg.display_queue.append([image, position])
                        
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
                    self.i = (self.i + 1) // len(soundtrack)
                    self.play_track(song=self.soundtrack[self.i])

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

########################################################################################################################################################
# Tools
def check_tile(x, y, ent=None, startup=False):
    """ Reveals newly explored regions with respect to the player's position. """
    
    # Select entity
    if not ent: ent = session.player_obj.ent

    # Define some shorthand
    tile = ent.env.map[x][y]
    
    # Reveal a square around the player
    for u in range(x-1, x+2):
        for v in range(y-1, y+2):
            ent.env.map[u][v].hidden = False
    
    # Reveal a hidden room
    if tile.room:
        
        if tile.room.hidden:
            tile.room.hidden = False
            for room_tile in tile.room.tiles_list:
                room_tile.hidden = False
        
        # Check if the player enters or leaves a room
        if ent.prev_tile:
            if (tile.room != ent.prev_tile.room) or (startup == True):
                
                # Hide the roof if the player enters a room
                if tile.room and tile.room.roof:
                    for spot in tile.room.tiles_list:
                        if spot not in tile.room.walls_list:
                            spot.img_names = tile.room.floor
    
    # Reveal the roof if the player leaves the room
    if ent.prev_tile:
        prev_tile = ent.prev_tile
        if prev_tile.room and not tile.room:
            if prev_tile.room.roof:
                for spot in prev_tile.room.tiles_list:
                    if spot not in prev_tile.room.walls_list:
                        spot.img_names = prev_tile.room.roof

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
            #session.pyg.update_gui("A mysterious breeze seeps through the cracks.", session.pyg.dark_gray)
            pygame.event.clear()
            return True
    except: return False
    
    return False

def get_vicinity(obj):
    """ Returns a list of tiles surrounding the given location.
    
        Returns
        -------
        obj.vicinity : dict of Tile objects
    """

    pyg = session.pyg

    (x, y) = obj.X//pyg.tile_width, obj.Y//pyg.tile_width
    obj.vicinity = {
        'top middle'    : session.player_obj.ent.env.map[x][y-1],
        'top right'     : session.player_obj.ent.env.map[x+1][y-1],
        'right'         : session.player_obj.ent.env.map[x+1][y],
        'bottom right'  : session.player_obj.ent.env.map[x+1][y+1],
        'bottom middle' : session.player_obj.ent.env.map[x][y+1],
        'bottom left'   : session.player_obj.ent.env.map[x-1][y+1],
        'middle left'   : session.player_obj.ent.env.map[x-1][y],
        'top left'      : session.player_obj.ent.env.map[x-1][y-1]}
    return obj.vicinity

def sort_inventory(ent=None):   
    
    # Allow for NPC actions
    if not ent: ent = session.player_obj.ent
        
    inventory_cache = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
    other_cache     = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}

    # Sort by category
    for item_list in ent.inventory.values():
        for item in item_list:
            inventory_cache[item.role].append(item)
    
    # Sort by stats:
    sorted(inventory_cache['weapons'], key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
    sorted(inventory_cache['armor'],  key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
    sorted(inventory_cache['potions'], key=lambda obj: obj.name)
    sorted(inventory_cache['scrolls'], key=lambda obj: obj.name)
    sorted(inventory_cache['other'],  key=lambda obj: obj.name)

    ent.inventory = inventory_cache

def screenshot(folder, filename, blur=False):
    """ Takes a screenshot. """
    
    pyg = session.pyg

    # Render display
    render_display()
    session.img.render()
    for (surface, pos) in pyg.display_queue:
        pyg.display.blit(surface, pos)
    display = pygame.transform.scale(
        pyg.display, (pyg.screen_width, pyg.screen_height))
    pyg.screen.blit(display, (0, 0))
    pygame.display.flip()
    
    # Save image
    path = folder + '/' + filename
    pygame.image.save(pyg.display, path)
    
    # Add effects
    if blur:
        image_before = Image.open(folder + '/' + filename)
        image_after  = image_before.filter(ImageFilter.BLUR)
        image_after.save(folder + '/' + filename)

def bw_binary():
    import numpy as np
    
    # Extract screen as image
    screen_surface = pygame.display.get_surface()
    raw_str        = pygame.image.tostring(screen_surface, 'RGB')
    image          = Image.frombytes('RGB', screen_surface.get_size(), raw_str)
    
    # Apply PIL effects
    image = image.convert('L')
    
    # Apply numpy effects
    image = np.array(image)
    image = np.where(image > 50, 255, 0)
    image = image.T
    image = np.stack([image] * 3, axis=-1)
    image = pygame.surfarray.make_surface(image)
    session.pyg.screen.blit(image, (0, 0))

def render_display():
    """ Adds tiles, entities, items, etc to the queue for rendering. """
    
    pyg = session.pyg

    #########################################################
    # Initialize
    ## Select entity to focus on
    if pyg.overlay_state == 'new_game': ent = session.new_game_obj.temp.ent
    else:                               ent = session.player_obj.ent

    ## Shorthand
    camera = ent.env.camera

    ## Clear previous screen
    pyg.display.fill(pyg.black)

    #########################################################
    # Draw visible tiles
    for y in range(int(camera.Y/32), int(camera.bottom/pyg.tile_height + 1)):
        for x in range(int(camera.X/32), int(camera.right/pyg.tile_width + 1)):
            try:    tile = ent.env.map[x][y]
            except: continue
            if not tile.hidden:
                
                # Lowest tier (floor or walls)
                image, (X, Y) = tile.draw()
                pyg.display_queue.append([image, (X, Y)])

                # Second tier (decor or item)
                if tile.item:
                    surface, pos = tile.item.draw()

                    # Handle single-tile images
                    if type(surface) != list:
                        pyg.display_queue.append([surface, pos])

                    # Handle multi-tile images
                    else:
                        for i in range(len(surface)):
                            pyg.display_queue.append([surface[i], pos])
                
                # Third tier (entity)
                if tile.entity:
                    tile.entity.draw()
                
                # Fourth tier (roof)
                if tile.room:
                    if tile.room.roof == tile.img_names:
                        image, (X, Y) = tile.draw()
                        pyg.display_queue.append([image, (X, Y)])
    
    session.aud.shuffle()

def render_hud():
    """ Draws tiles and stuff. Constantly runs. """
    
    pyg = session.pyg

    if pyg.hud_state == 'on':
        
        #########################################################
        # Messages
        if pyg.msg_toggle: 
            Y = 3
            
            # Find how many messages to write
            for message in pyg.msg:
                pyg.hud_queue.append([message, (5, Y)])
                Y += 16
        
        #########################################################
        # Status bars and time
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
                pyg.hud_queue.append([gui[i], (x, y)])

########################################################################################################################################################