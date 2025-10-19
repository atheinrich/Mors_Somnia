########################################################################################################################################################
# Local mechanics
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import time
import sys
import pickle
import copy

## Specific
import pygame
from   pygame.locals import *

## Local
import session

########################################################################################################################################################
# Core
class Pygame:

    def __init__(self):
        """ Manages pygame parameters, GUI details, and display transitions.
            Nothing here is saved elsewhere.
        """

        #########################################################
        # Set shorthand and pygame parameters
        self.set_controls()
        self.set_colors()
        self.set_graphics()
        
        #########################################################
        # Utility
        self.startup_toggle  = True
        self.last_press_time = 0
        
        #########################################################
        # Start pygame
        pygame.init()
        pygame.key.set_repeat(250, 150)
        pygame.display.set_caption("Mors Somnia") # Sets game title
        self.screen   = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        self.frame    = False
        self.font     = pygame.font.SysFont('segoeuisymbol', 16, bold=True) # pygame.font.Font('Data/font.ttf', 24)
        self.minifont = pygame.font.SysFont('segoeuisymbol', 14, bold=True) # pygame.font.Font('Data/font.ttf', 24)
        self.clock    = pygame.time.Clock()
        self.display  = pygame.Surface((self.screen_width, self.screen_height))
        self.gui      = {
            'health':   self.font.render('', True, self.red),
            'stamina':  self.font.render('', True, self.green),
            'location': self.font.render('', True, self.gray)}

    def set_controls(self, controls='numpad 1'):
        
        #########################################################
        # Change control scheme
        self.controls_preset = controls
        
        #########################################################
        # Define control schemes
        ## Extended
        if controls == 'arrows':
            
            # Movement
            self.key_UP       = ['↑', K_UP,    K_w]             # up
            self.key_DOWN     = ['↓', K_DOWN,  K_s]             # down
            self.key_LEFT     = ['←', K_LEFT,  K_a]             # left
            self.key_RIGHT    = ['→', K_RIGHT, K_d]             # right
            
            # Actions
            self.key_BACK     = ['/', K_BACKSPACE, K_ESCAPE,  K_SLASH, K_KP_DIVIDE]  # exit/main menu
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY]       # show/hide gui
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]          # action 1
            self.key_PERIOD   = ['.', K_KP_PERIOD]                      # action 2
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS, K_EQUALS] # zoom
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]          # zoom
            self.key_HOLD     = ['0', K_0, K_KP0]
            
            # Menus
            self.key_INV      = ['4', K_4, K_KP4]               # inventory
            self.key_DEV      = ['6', K_6, K_KP6]               # catalog
            self.key_INFO     = ['7', K_7, K_KP7]               # player information
            self.key_SPEED    = ['8', K_8, K_KP8]               # movement speed
            self.key_QUEST    = ['9', K_9, K_KP9]               # questlog
            
            # Other
            self.key_EQUIP    = ['2', K_2, K_KP2]               # inventory (equip)
            self.key_DROP     = ['3', K_3, K_KP3]               # inventory (drop)

        ## Alternate 1
        elif controls == 'numpad 1':
            
            # Movement
            self.key_UP       = ['5', K_5, K_KP5,  K_UP]          # up
            self.key_DOWN     = ['2', K_2, K_KP2,  K_DOWN]        # down
            self.key_LEFT     = ['1', K_1, K_KP1,  K_LEFT]        # left
            self.key_RIGHT    = ['3', K_3, K_KP3,  K_RIGHT]       # right

            # Actions
            self.key_BACK     = ['/', K_SLASH,     K_KP_DIVIDE]         # exit/main menu
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY]       # show/hide gui
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]          # action 1
            self.key_PERIOD   = ['.', K_KP_PERIOD]                      # action 2
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS, K_EQUALS] # zoom
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]          # zoom
            self.key_HOLD     = ['0', K_0, K_KP0]                       # attack sequences
            
            # Menus
            self.key_INV      = ['4', K_4, K_KP4]                 # inventory
            self.key_DEV      = ['6', K_6, K_KP6]                 # catalog
            self.key_INFO     = ['7', K_7, K_KP7]                 # player information
            self.key_SPEED    = ['8', K_8, K_KP8]                 # movement speed
            self.key_QUEST    = ['9', K_9, K_KP9]                 # questlog
            
            # Unused
            self.key_EQUIP    = []                           # inventory (equip)
            self.key_DROP     = []                           # inventory (drop)

        # Alternate 2
        elif controls == 'numpad 2':
            
            # Movement
            self.key_UP       = ['8', K_8, K_KP8,  K_UP]          # up
            self.key_DOWN     = ['5', K_5, K_KP5,  K_DOWN]        # down
            self.key_LEFT     = ['4', K_4, K_KP4,  K_LEFT]        # left
            self.key_RIGHT    = ['6', K_6, K_KP6,  K_RIGHT]       # right

            # Actions
            self.key_BACK     = ['/', K_SLASH,     K_KP_DIVIDE]         # exit/main menu
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY]       # show/hide gui
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]          # action 1
            self.key_PERIOD   = ['.', K_KP_PERIOD]                      # action 2
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS, K_EQUALS] # zoom
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]          # zoom
            self.key_HOLD     = ['0', K_0, K_KP0]                       # attack sequences
            
            # Menus
            self.key_INV      = ['7', K_7, K_KP7]                 # inventory
            self.key_DEV      = ['9', K_9, K_KP9]                 # catalog
            self.key_INFO     = ['1', K_1, K_KP1]                 # player information
            self.key_SPEED    = ['2', K_2, K_KP2]                 # movement speed
            self.key_QUEST    = ['3', K_3, K_KP3]                 # questlog
            
            # Unused
            self.key_EQUIP    = []                           # inventory (equip)
            self.key_DROP     = []                           # inventory (drop)

        # Categories
        self.key_movement = self.key_UP + self.key_DOWN + self.key_LEFT + self.key_RIGHT

    def set_colors(self):
        
        #########################################################
        # Define shorthand
        self.black     = pygame.color.THECOLORS['black']
        self.dark_gray = pygame.color.THECOLORS['gray60']
        self.gray      = pygame.color.THECOLORS['gray90']
        self.white     = pygame.color.THECOLORS['white']
        self.red       = pygame.color.THECOLORS['orangered3']
        self.green     = pygame.color.THECOLORS['palegreen4']
        self.blue      = pygame.color.THECOLORS['blue']
        self.yellow    = pygame.color.THECOLORS['yellow']
        self.orange    = pygame.color.THECOLORS['orange']
        self.violet    = pygame.color.THECOLORS['violet']
        self.colors    = [self.black, self.dark_gray, self.gray, self.white,
                          self.red, self.orange, self.yellow, self.green, self.blue, self.violet]

    def set_graphics(self):
        
        #########################################################
        # Graphics parameters
        self.screen_width      = 640 # 20 tiles
        self.screen_height     = 480 # 15 tiles
        self.tile_width        = 32
        self.tile_height       = 32
        self.map_width         = 640 * 2
        self.map_height        = 480 * 2
        self.tile_map_width    = int(self.map_width/self.tile_width)
        self.tile_map_height   = int(self.map_height/self.tile_height)

        #########################################################
        # Graphics overlays
        self.msg_toggle        = True # Boolean; shows or hides messages
        self.msg               = []   # list of font objects; messages to be rendered
        self.gui_toggle        = True # Boolean; shows or hides GUI
        self.gui               = None # font object; stats to be rendered
        self.msg_width         = int(self.screen_width / 6)
        self.msg_height        = 4    # number of lines shown
        self.msg_history       = {}

    def textwrap(self, text, width):
        """ Separates long chunks of text into consecutive lines. """
        
        #########################################################
        # Initialize
        words = text.split()
        lines = []
        current_line = []

        #########################################################
        # Split lines
        for word in words:
            if (sum(len(w) for w in current_line) + len(current_line) + len(word)) <= width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def fadeout_screen(self, text, fade_in=False, duration=2, loc=None, retain=False, alpha_start=None, alpha_end=None):
        """ Fades screen and displays text.
        
            Parameters
            ----------
            text        : str or pygame surface; text to be displayed
            fade_in     : bool; fades into black if False; fades out of black if True
            duration    : int; number of seconds for transition
            loc         : tuple of ints; custom location
            retain      : bool; prevents text from fading if True
            alpha_start : None or int; initial alpha value
            alpha_end   : None or int; final alpha value
        """
        
        #########################################################
        # Imports
        from utilities import render_all

        #########################################################
        # Set fade details
        ## End black or start black
        if not fade_in:
            if alpha_start is None: alpha, change = 0, 10
            else:                   alpha, change = alpha_start, 10
        else:
            if alpha_start is None: alpha, change = 255*2, -10
            else:                   alpha, change = alpha_start, -10

            session.player_obj.ent.env.weather.run()
            session.player_obj.ent.env.weather.render()

        ## Fade color and speed
        screen = session.pyg.screen
        fade_surface = pygame.Surface(screen.get_size())
        fade_surface.fill((0, 0, 0))
        
        #########################################################
        # Select text object and set color and position
        if type(text) == str: text_surface = self.font.render(text, True, (255, 255, 255))
        else:                 text_surface = text
        if not loc: loc = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

        #########################################################
        # Increase alpha channel over time
        clock                  = pygame.time.Clock()
        gui_cache              = copy.copy(session.pyg.gui_toggle)
        msg_cache              = copy.copy(session.pyg.msg_toggle)
        session.pyg.gui_toggle = False
        session.pyg.msg_toggle = False
        running                = True
        while running:
            
            #########################################################
            # Set fade level
            if alpha_end is not None:
                if (not fade_in) and (alpha >= alpha_end):     alpha = alpha_end
                elif (fade_in) and (alpha <= alpha_end):       alpha = alpha_end
                else:                                          alpha += change
            else:                                              alpha += change
            if (alpha > 255*duration) or (alpha == alpha_end): running = False
            elif alpha < 0:                                    running = False
            
            fade_surface.set_alpha(alpha)
            session.pyg.screen.blit(pygame.transform.scale(session.pyg.display, (session.pyg.screen_width, session.pyg.screen_height)), (0, 0))
            screen.blit(fade_surface, (0, 0))
            if session.img.render_fx: render_all()
            
            #########################################################
            # Show text
            if alpha >= int(255*duration/2):
                if not retain: val = alpha - 255
                else:          val = 255
                if val > 255:  val = 255

                # Apply flicker effect
                text_surface.set_alpha(random.randint(val-50, val))
                self.screen.blit(text_surface, loc)
            
            elif retain:
                text_surface.set_alpha(random.randint(200, 255))
                self.screen.blit(text_surface, loc)

            pygame.display.update()
            clock.tick(15)
        
        session.pyg.gui_toggle = gui_cache
        session.pyg.msg_toggle = msg_cache

    def update_gui(self, new_msg=None, color=None, ent=None):
        """ Constructs (but does not render) messages in the top GUI and stats in the bottom GUI.

            Parameters
            ----------
            new_msg     : str; text added to top GUI
            color       : pygame Color; color of new message
            ent         : Entity object; only specified at startup

            msg_history : dict; all prior messages and colors in memory
        """
        
        #########################################################
        # Initialize
        ## Shorthand
        if not ent: ent = session.player_obj.ent
        pyg             = session.pyg
        img             = session.img

        ## Prepare colors
        img.average()
        if not color:
            color    = pygame.Color(255-img.top_color[0],    255-img.top_color[1],    255-img.top_color[2])
        bottom_color = pygame.Color(255-img.bottom_color[0], 255-img.bottom_color[1], 255-img.bottom_color[2])
        
        #########################################################
        # Messages (top GUI)
        ## Add new message
        if new_msg:
            for line in pyg.textwrap(new_msg, pyg.msg_width):

                # Only show a message once
                if line in self.msg_history.keys():
                    del self.msg_history[line]
                self.msg_history[line] = color
        
        ## Find which messages to display
        lines  = list(self.msg_history.keys())[:self.msg_height]
        colors = list(self.msg_history.values())[:self.msg_height]

        ## Construct list for display
        self.msg = []
        for i in range(len(lines)):
            if colors[i] in pyg.colors: self.msg.append(self.font.render(lines[i], True, colors[i]))
            else:                       self.msg.append(self.font.render(lines[i], True, color))
        
        #########################################################
        # Stats (bottom GUI)
        ## Health text
        current_health  = int(ent.hp / ent.max_hp * 10)
        leftover_health = 10 - current_health
        health          = '⚪' * leftover_health + '⚫' * current_health
        
        ## Stamina text
        current_stamina  = int((ent.stamina % 101) / 10)
        leftover_stamina = 10 - current_stamina
        stamina          = '⚫' * current_stamina + '⚪' * leftover_stamina
        
        ## Time text
        time = ['🌗', '🌘', '🌑', '🌒', '🌓', '🌔', '🌕', '🌖'][ent.env.env_time-1]
        
        ## Construct dictionary for display
        if pyg.overlay:
            if self.msg: self.msg = [self.msg[-1]]
            
            # Wallet text
            wallet = f"⨋ {ent.wallet}"

            # Location text
            if ent.env.lvl_num: env = f"{ent.env.name} (level {ent.env.lvl_num})"
            else:               env = f"{ent.env.name}"
        else: wallet, env = '', ''
        
        self.gui = {
            'wallet':   self.minifont.render(wallet,  True, bottom_color),
            'health':   self.minifont.render(health,  True, self.red),
            'time':     self.minifont.render(time,    True, bottom_color),
            'stamina':  self.minifont.render(stamina, True, self.green),
            'location': self.minifont.render(env,     True, bottom_color)}

class NewGameMenu:

    # Core
    def __init__(self):
        """ Creates a temporary player for customization in the Womb environment.
            Hosts a menu that can discard the temporary player or keep it to replace the current player.
            If kept, an introduction screen is displayed before entering the dungeon.
        
            HAIR:       sets hair by altering hair_index, which is used in new_game to add hair as an Object hidden in the inventory
            HANDEDNESS: mirrors player/equipment tiles, which are saved in session.img.dict and session.img.cache
            ACCEPT:     runs new_game() to generate player, home, and default items, then runs play_game() """
        
        #########################################################
        # Menu details
        ## Basics
        self.menu_choices = ["HAIR", "FACE", "SEX", "SKIN", "HANDEDNESS", "", "ACCEPT", "BACK"]        
        self.orientations = ['front', 'right', 'back', 'left']

        ## Positions

        ## Other
        self.fadeout = False

        self.last_rotate_time = 0
        self.cooldown_time   = 0.7

        #########################################################
        # Menu
        ## Cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, session.pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
        
        ## Options
        for i in range(len(self.menu_choices)):
            if   i == len(self.menu_choices)-2:  color = session.pyg.green
            elif i == len(self.menu_choices)-1:  color = session.pyg.red
            else:                                color = session.pyg.gray
            self.menu_choices[i] = session.pyg.font.render(self.menu_choices[i], True, color)
        self.choice         = 0
        self.choices_length = len(self.menu_choices)-1
        self.cursor_pos     = [50, 424-len(self.menu_choices)*24]
        self.top_choice     = [50, 424-len(self.menu_choices)*24]

    def run(self):
        """ Creates a temporary player, then returns to garden at startup or hosts character creation otherwise. """
        
        #########################################################
        # Initialize
        ## Define shorthand
        pyg = session.pyg
        
        ## Return to garden at startup
        if not session.player_obj.ent:
            self.temp          = self.init_player()
            session.player_obj = self.startup()
            return
        
        ## Set navigation speed
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

                elif event.key in pyg.key_ENTER:

                    #########################################################
                    # Apply option
                    if self.choice <= 4:
                        self.apply_option()
                        
                    #########################################################
                    # Accept and start game
                    elif self.choice == 6:
                        self.start_game()
                        return
                    
                    #########################################################
                    # Return to main menu
                    elif self.choice == 7:
                        self.key_BACK()
                        return
        
                #########################################################
                # Return to main menu
                elif time.time()-pyg.last_press_time > self.cooldown_time:
                    self.key_BACK()
                    return
                
        pyg.game_state = 'new_game'
        return

    def render(self):
        
        #########################################################
        # Render environment and character
        ## Render over garden
        from utilities import render_all
        render_all(ent=self.temp.ent)

        ## Rotate character
        if time.time()-self.last_rotate_time > self.cooldown_time:
            self.last_rotate_time = float(time.time()) 
            self.temp.img_names[1] = self.orientations[self.orientations.index(self.temp.img_names[1]) - 1]
        
        #########################################################
        # Render menu
        ## Choices
        Y = self.top_choice[1] - 4
        for self.menu_choice in self.menu_choices:
            session.pyg.screen.blit(self.menu_choice, (80, Y))
            Y += 24
        
        ## Cursor
        session.pyg.screen.blit(self.cursor_img, self.cursor_pos)

        #########################################################
        # Show startup dialogue
        if self.fadeout:
            self.fadeout = False
            text = "Your hands tremble as the ground shudders in tune... something is wrong."
            session.mech.enter_dungeon(text=text, lvl_num=4)

    # Keys
    def key_UP(self):
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

    def key_DOWN(self):
        self.cursor_pos[1]     += 24
        self.choice            += 1
        
        if self.choice > self.choices_length:
            self.choice         = 0
            self.cursor_pos[1]  = self.top_choice[1]
        
        elif self.choice == (self.choices_length - 2):
            self.choice         = self.choices_length - 1
            self.cursor_pos[1]  = self.top_choice[1] + (len(self.menu_choices)-2) * 24

    def key_BACK(self):

        # Define shorthand
        pyg = session.pyg
        env = session.player_obj.ent.env

        # Reset press and turn off startup transition
        pyg.last_press_time = float(time.time())
        self.fadeout        = False

        # Set return destination
        if env.name == 'garden': pyg.game_state = 'play_garden'
        else:                    pyg.game_state = 'play_game'
        pyg.overlay = 'menu'

    # Tools
    def init_player(self):
        """ Creates a temporary player and womb environment. """

        #########################################################
        # Imports
        from items_entities import create_item
        from items_entities import Player
        from environments import Environments

        #########################################################
        # Create player and entity
        player_obj      = Player()
        player_obj.ent  = Entity(
            name        = player_obj.name,
            role        = player_obj.role,
            img_names   = player_obj.img_names,

            exp         = player_obj.exp,
            rank        = player_obj.rank,
            hp          = player_obj.hp,
            max_hp      = player_obj.max_hp,
            attack      = player_obj.attack,
            defense     = player_obj.defense,
            sanity      = player_obj.sanity,
            stamina     = player_obj.stamina,
            
            X           = player_obj.X,
            Y           = player_obj.Y,
            habitat     = player_obj.habitat,

            follow      = player_obj.follow,
            lethargy    = player_obj.lethargy,
            miss_rate   = player_obj.miss_rate,
            aggression  = player_obj.aggression,
            fear        = player_obj.fear,
            reach       = player_obj.reach)
        
        ## Player-specific attributes
        player_obj.ent.questlog        = {}
        player_obj.ent.garden_questlog = {}
        player_obj.ent.discoveries     = player_obj.discoveries
        
        #########################################################
        # Set default items
        for item_name in ['bald', 'clean', 'flat', 'dagger']:
            item = create_item(item_name)
            item.pick_up(player_obj.ent,      silent=True)
            item.toggle_equip(player_obj.ent, silent=True)
            
        #########################################################
        # Initialize character creation environment
        player_obj.envs = Environments(player_obj)
        player_obj.envs.build_womb()

        ## Place temporary player in character creator
        player_obj.ent.last_env = player_obj.envs.dict['womb']
        place_player(
            ent = player_obj.ent,
            env = player_obj.envs.dict['womb'],
            loc = player_obj.envs.dict['womb'].center)
        
        return player_obj

    def startup(self):
        """ Creates a second temporary player, a womb environment, a the garden environment.
            This is meant to be a placeholder for the actual player object, separate from the temporary
            player used only in the New Game menu.
        """

        #########################################################
        # Make temporary player
        session.player_obj = self.init_player()
        session.dev.update_dict()

        ## Initialize the garden
        session.questlog_obj.init_questlog('garden')
        session.player_obj.envs.build_garden()
        session.pets_obj.startup()

        place_player(
            ent = session.player_obj.ent,
            env = session.player_obj.envs.dict['garden'],
            loc = session.player_obj.envs.dict['garden'].center)
        
        #########################################################
        # Fade into the main menu
        session.main_menu_obj.startup()
        session.pyg.game_state = 'play_garden'
        session.pyg.overlay    = 'menu'

        return session.player_obj

    def apply_option(self):
        
        #########################################################
        # Imports
        from items_entities import create_item
        
        #########################################################
        # Apply hair or face option
        if self.choice in [0, 1, 2]:
            
            # Hair, face, or chest option
            if self.choice == 0:
                role     = 'head'
                img_dict = session.img.hair_options

            elif self.choice == 1:
                role     = 'face'
                img_dict = session.img.face_options

            elif self.choice == 2:
                role     = 'chest'
                img_dict = session.img.chest_options
            
            # Find next option and dequip last option
            index    = (img_dict.index(self.temp.ent.equipment[role].img_names[0]) + 1) % len(img_dict)
            img_name = img_dict[index]
            self.temp.ent.equipment[role].toggle_equip(self.temp.ent, silent=True)
            
            # Equip next option if already generated
            if img_name in [[x[i].img_names[0] for i in range(len(x))] for x in self.temp.ent.inventory.values()]:
                self.temp.ent.inventory[img_name][0].toggle_equip(self.temp.ent, silent=True)
            
            # Generate option before equip
            else:
                item = create_item(img_name)
                self.temp.ent.inventory['armor'].append(item)
                item.toggle_equip(self.temp.ent, silent=True)
        
        #########################################################
        # Apply skin option
        elif self.choice == 3:
            if self.temp.ent.img_names[0] == 'white':   self.temp.ent.img_names[0] = 'black'
            elif self.temp.ent.img_names[0] == 'black': self.temp.ent.img_names[0] = 'white'
        
        #########################################################
        # Apply handedness option
        elif self.choice == 4:
            if self.temp.ent.handedness == 'left':      self.temp.ent.handedness = 'right'
            elif self.temp.ent.handedness == 'right':   self.temp.ent.handedness = 'left'
        
    def start_game(self):
        """ Initializes NEW GAME. Does not handle user input. Resets player stats, inventory, map, and rooms.
            Only called after the character creation menu is accepted. """
        
        #########################################################
        # Imports
        from utilities import sort_inventory
        from items_entities import create_item

        #########################################################
        # Make object permanent
        ## Copy player and womb environment
        session.player_obj = copy.deepcopy(self.temp)
        session.dev.update_dict()

        ## Create garden environment
        session.questlog_obj.init_questlog('garden')
        session.player_obj.envs.build_garden()
        session.pets_obj.startup()

        ## Build the home environment and set it as the last environment
        session.player_obj.envs.build_home()

        place_player(
            ent = session.player_obj.ent,
            env = session.player_obj.envs.dict['home'],
            loc = session.player_obj.envs.dict['home'].center)

        #########################################################
        # Create and equip items
        items = ['shovel', 'lamp']

        if session.player_obj.ent.equipment['chest'].img_names[0] == 'bra':
            items.append('yellow dress')
        else: items.append('green clothes')

        for name in items:
            item = create_item(name)
            item.pick_up(ent=session.player_obj.ent,      silent=True)
            item.toggle_equip(ent=session.player_obj.ent, silent=True)
        
        sort_inventory()
        
        #########################################################
        # Begin game
        self.fadeout               = True
        session.pyg.gui_toggle     = True
        session.pyg.msg_toggle     = True
        session.pyg.startup_toggle = False
        session.pyg.game_state     = 'play_game'

class PlayGame:

    def __init__(self):

        #########################################################
        # Utility
        self.cooldown_time   = 1
        self.gui_set         = 0
        self.death_cooldown  = 1
        
    def run(self):

        #########################################################
        # Initialize
        active_effects()
        session.stats_obj.update()
        
        session.player_obj.ent.role = 'player'
        session.mech.movement_speed(toggle=False)
        
        if session.pyg.overlay in [None, 'stats']:
            
            #########################################################
            # Play game if alive
            if not session.player_obj.ent.dead:
                for event in pygame.event.get():

                    # Quit
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    # Keep playing
                    if event.type == KEYDOWN:
                        
                        #########################################################
                        # Movement
                        if event.key in session.pyg.key_UP:       self.key_UP()
                        elif event.key in session.pyg.key_DOWN:   self.key_DOWN()
                        elif event.key in session.pyg.key_LEFT:   self.key_LEFT()
                        elif event.key in session.pyg.key_RIGHT:  self.key_RIGHT()
                        
                        #########################################################
                        # Actions
                        elif event.key in session.pyg.key_ENTER:  self.key_ENTER()
                        elif event.key in session.pyg.key_GUI:    self.key_GUI()
                        elif event.key in session.pyg.key_PERIOD: self.key_PERIOD()
                        elif event.key in session.pyg.key_PLUS:   self.key_PLUS()
                        elif event.key in session.pyg.key_MINUS:  self.key_MINUS()
                        
                        #########################################################
                        # Menus
                        elif event.key in session.pyg.key_SPEED:  self.key_SPEED()
                        
                        ## >>MAIN MENU<<
                        elif event.key in session.pyg.key_BACK:
                            
                            if session.pyg.overlay:
                                session.pyg.overlay = None
                            
                            elif time.time()-session.pyg.last_press_time > self.cooldown_time:
                                session.pyg.last_press_time = float(time.time())
                                session.pyg.overlay = 'menu'
                                pygame.event.clear()
                                return

                        ## >>COMBOS<<
                        elif event.key in session.pyg.key_HOLD:
                            session.hold_obj.sequence_toggle = True
                            session.pyg.overlay = 'hold'
                            pygame.event.clear()
                            return
                        
                        ## >>INVENTORY<<
                        elif event.key in session.pyg.key_INV:
                            session.pyg.overlay = 'inv'
                            pygame.event.clear()
                            return
                        
                        ## >>CONSTRUCTION<<
                        elif event.key in session.pyg.key_DEV:
                            #session.trade_obj.ent = session.player_obj.ent
                            session.pyg.overlay = 'dev'
                            pygame.event.clear()
                            return

                        ## >>STATS<<
                        elif event.key in session.pyg.key_INFO:
                            if time.time()-session.pyg.last_press_time > self.cooldown_time:
                                if session.pyg.overlay != 'stats':
                                    session.stats_obj.dic = session.stats_obj.stats
                                    session.pyg.overlay = 'stats'
                                else:
                                    session.pyg.overlay = None
                                pygame.event.clear()
                                return
            
                        ## >>QUESTLOG<<
                        elif event.key in session.pyg.key_QUEST:
                            session.questlog_obj.update_questlog()
                            session.pyg.overlay = 'questlog'
                            pygame.event.clear()
                            return
            
            #########################################################
            # Handle player death
            else:
                env      = session.player_obj.ent.env
                last_env = session.player_obj.ent.last_env
                permadeath_locs = ['garden', 'home', 'overworld', 'cave', 'womb']
                drug_locs       = ['hallucination', 'bitworld']
                dream_locs      = ['dungeon']
                
                #########################################################
                # Survive
                if env.name not in permadeath_locs:
                    
                    # Wait for animations to finish
                    if not session.img.render_log:
                        if not self.death_cooldown:
                            
                            # Restore player state
                            session.player_obj.ent.dead = False
                            session.pyg.gui             = {}
                            session.pyg.msg             = []
                            session.pyg.msg_history     = {}
                            session.mech.movement_speed(toggle=False, custom=0)
                            self.death_cooldown = 5
                            
                            # Regain consciousness
                            if env.name in drug_locs:
                                session.player_obj.ent.hp = session.player_obj.ent.max_hp // 2
                                self.fadein = "Delirium passes, but nausea remains."
                            
                            # Wake up at home
                            elif env.name in dream_locs:
                                session.player_obj.ent.hp = session.player_obj.ent.max_hp
                                self.fadein = "Your cling to life has slipped, yet you wake unscarred in bed."
                            
                            else:
                                session.player_obj.ent.hp = session.player_obj.ent.max_hp
                                self.fadein = "???"
                            
                            session.pyg.overlay = None
                            session.pyg.fadeout_screen(
                                text     = self.fadein,
                                duration = 3)
                            place_player(
                                ent = session.player_obj.ent,
                                env = last_env,
                                loc = last_env.player_coordinates)
                            session.img.render_fx = None
                            pygame.event.clear()
                        
                        else: self.death_cooldown -= 1
                
                #########################################################
                # End the game
                else:
                    for event in pygame.event.get():
                        
                        # Restrict movement speed
                        session.mech.movement_speed(toggle=False, custom=2)
                        
                        # Menus
                        if event.type == KEYDOWN:
                            
                            # >>MAIN MENU<<
                            if event.key in session.pyg.key_BACK:
                                session.pyg.overlay = 'menu'
                                pygame.event.clear()
                                return
                        
                            # >>TOGGLE MESSAGES<<
                            elif event.key in session.pyg.key_PERIOD:
                                if session.pyg.msg_toggle: session.pyg.msg_toggle = False
                                else:
                                    if session.pyg.gui_toggle:
                                        session.pyg.gui_toggle = False
                                        session.pyg.msg_toggle = False
                                    else:
                                        session.pyg.msg_toggle = True
                                        session.pyg.gui_toggle = True
                            
                            # >>STATS<<
                            elif event.key in session.pyg.key_INFO:
                                if session.pyg.overlay != 'stats':
                                    session.stats_obj.dic = session.stats_obj.stats
                                    session.pyg.overlay = 'stats'
                                else:
                                    session.pyg.overlay = None
                                pygame.event.clear()
                            
                            # >>QUESTLOG<<
                            elif event.key in session.pyg.key_QUEST:
                                session.questlog_obj.update_questlog()
                                session.pyg.overlay = 'questlog'
                                pygame.event.clear()
                                return
                            
                            # Other
                            elif event.key in session.pyg.key_SPEED:  self.key_SPEED()
        
        #########################################################
        # Move AI controlled entities
        for entity in session.player_obj.ent.env.entities: entity.ai()
        
        session.pyg.game_state = 'play_game'

    def key_UP(self):
        session.player_obj.ent.move(0, -session.pyg.tile_height) # >>MOVE<<

    def key_DOWN(self):
        session.player_obj.ent.move(0, session.pyg.tile_height)  # >>MOVE<<

    def key_LEFT(self):
        session.player_obj.ent.move(-session.pyg.tile_width, 0)  # >>MOVE<<

    def key_RIGHT(self):
        session.player_obj.ent.move(session.pyg.tile_width, 0)   # >>MOVE<<

    def key_ENTER(self):

        #########################################################
        # Activate items
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            # >>PICKUP/STAIRS<<
            # Check if an item is under the player
            if session.player_obj.ent.tile.item:
                tile = session.player_obj.ent.tile
                
                # Activate entryway
                if tile.item.name == 'dungeon':     session.mech.enter_dungeon()
                elif tile.item.name == 'cave':      session.mech.enter_cave()
                elif tile.item.name == 'overworld': session.mech.enter_overworld()
                elif tile.item.name == 'home':      session.mech.enter_home()
                
                # Activate bed
                elif tile.item.name in ['red bed', 'purple bed']:
                    
                    # Check if it is the player's bed
                    if tile.room:
                        if tile.room.name == 'home room':
                            
                            # Go to sleep if it's not daytime
                            if session.player_obj.ent.env.env_time in [1, 2, 7, 8]:
                                session.player_obj.ent.env.env_time = (session.player_obj.ent.env.env_time + 3) % 8
                                session.mech.enter_dungeon(text="The evening dims to night... sleep trustly follows.")
                            else: session.pyg.update_gui("Time to face the day.", session.pyg.dark_gray)
                        
                        # No sleeping in owned beds
                        else: session.pyg.update_gui("This is not your bed.", session.pyg.dark_gray)
                    
                    else: session.pyg.update_gui("This is not your bed.", session.pyg.dark_gray)
                
                # Activate chair
                elif tile.item.name in ['red chair left', 'red chair right']:
                    session.player_obj.ent.env.weather.set_day_and_time(increment=True)
                    session.pyg.update_gui("You sit down to rest for a while.", session.pyg.dark_gray)
                
                # Pick up or activate
                else: session.player_obj.ent.tile.item.pick_up()

    def key_GUI(self):
        
        #########################################################
        # Change GUI setting
        self.gui_set = (self.gui_set + 1) % 4
        
        #########################################################
        # Apply setting
        ## Show all
        if self.gui_set == 0:
            session.pyg.gui_toggle = True
            session.pyg.msg_toggle = True
        
        ## Hide GUI
        elif self.gui_set == 1:
            session.pyg.gui_toggle = False
            session.pyg.msg_toggle = True
        
        ## Hide both
        elif self.gui_set == 2:
            session.pyg.gui_toggle = False
            session.pyg.msg_toggle = False

        ## Hide messages
        elif self.gui_set == 3:
            session.pyg.gui_toggle = True
            session.pyg.msg_toggle = False

    def key_PERIOD(self):
        
        #########################################################
        # Move down a level
        if session.player_obj.ent.tile.item:
            if session.player_obj.ent.tile.item.name in ['dungeon', 'cave']:
                if time.time()-session.pyg.last_press_time > self.cooldown_time:
                    session.pyg.last_press_time = float(time.time())
                
                    # Go up by one floor
                    if session.player_obj.ent.env.lvl_num > 1:
                        env = session.player_obj.envs.dict[session.player_obj.ent.env.name][session.player_obj.ent.env.lvl_num-2]
                        place_player(
                            ent = session.player_obj.ent,
                            env = env,
                            loc = env.player_coordinates)
                    
                    elif session.player_obj.ent.env.lvl_num == 1:
                        env = session.player_obj.ent.last_env
                        place_player(
                            ent = session.player_obj.ent,
                            env = env,
                            loc = env.player_coordinates)

    def key_PLUS(self):
        session.player_obj.ent.env.camera.zoom_in()  # >>ZOOM<<

    def key_MINUS(self):
        session.player_obj.ent.env.camera.zoom_out() # >>ZOOM<<

    def key_SPEED(self):
        
        #########################################################
        # Change speed
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = float(time.time())
            session.mech.movement_speed()

    def render(self):
        
        #########################################################
        # Imports
        from utilities import render_all

        #########################################################
        # Render typical game display
        session.pyg.msg_height = 4
        if not session.pyg.overlay: session.pyg.update_gui()
        render_all()
        
        #########################################################
        # Fade when entering new area
        if self.fadein:
            session.pyg.fadeout_screen(
                text     = self.fadein,
                fade_in  = True,
                duration = 3)
            self.fadein = False

class PlayGarden:

    def run(self):
        """ Hosts garden gamestate as a lightweight variant of PlayGame. """
        
        #########################################################
        # Initialize
        ## Update pet stats, mood, and effects
        session.pets_obj.update()
        
        ## Active AI when viewing the main menu
        if session.pyg.overlay == 'menu': session.player_obj.ent.role = 'NPC'
        else:                             session.player_obj.ent.role = 'player'
        
        ## Set camera and movement speed
        session.player_obj.envs.dict['garden'].camera.zoom_in(custom=1)
        session.mech.movement_speed(toggle=False, custom=2)
        
        #########################################################
        # Handle input
        if session.pyg.overlay in [None, 'stats']:
            for event in pygame.event.get():
                
                #########################################################
                # Quit
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                #########################################################
                # Keep playing
                if not session.player_obj.ent.dead:
                    if event.type == KEYDOWN:
                        
                        #########################################################
                        # Movement
                        if event.key in session.pyg.key_UP:       self.key_UP()
                        elif event.key in session.pyg.key_DOWN:   self.key_DOWN()
                        elif event.key in session.pyg.key_LEFT:   self.key_LEFT()
                        elif event.key in session.pyg.key_RIGHT:  self.key_RIGHT()
                        
                        #########################################################
                        # Actions
                        elif event.key in session.pyg.key_ENTER:  self.key_ENTER()
                        elif event.key in session.pyg.key_PERIOD: self.key_PERIOD()
                        
                        #########################################################
                        # Menus
                        elif event.key in session.pyg.key_SPEED:  self.key_SPEED()
                        
                        ## >>MAIN MENU<<
                        elif event.key in session.pyg.key_BACK:
                            
                            if session.pyg.overlay == 'stats':
                                session.pyg.overlay = None
                            
                            elif time.time()-session.pyg.last_press_time > self.cooldown_time:
                                session.pyg.last_press_time = float(time.time())
                                session.pyg.overlay = 'menu'
                                pygame.event.clear()
                                return
                        
                        ## >>COMBOS<<
                        elif event.key in session.pyg.key_HOLD:
                            session.hold_obj.sequence_toggle = True
                            session.pyg.overlay = 'hold'
                            pygame.event.clear()
                            return
                        
                        ## >>INVENTORY<<
                        elif event.key in session.pyg.key_INV:
                            session.pyg.overlay = 'inv'
                            pygame.event.clear()
                            return
                        
                        ## >>CONSTRUCTION<<
                        elif event.key in session.pyg.key_DEV:
                            session.pyg.overlay = 'dev'
                            pygame.event.clear()
                            return
                
                        ## >>STATS<<
                        elif event.key in session.pyg.key_INFO:
                            if session.pyg.overlay != 'stats':
                                session.stats_obj.dic = session.pets_obj.stats
                                session.pyg.overlay = 'stats'
                            else:
                                session.pyg.overlay = None
                            pygame.event.clear()
                            return
                
                        ## >>QUESTLOG<<
                        elif event.key in session.pyg.key_QUEST:
                            session.pyg.overlay = 'gardenlog'
                            pygame.event.clear()
                            return

                #########################################################
                # Return to main menu
                else:

                    # >>MAIN MENU<<
                    if event.type == KEYDOWN:
                        if event.key in session.pyg.key_BACK:
                            session.pyg.overlay = 'menu'
                            pygame.event.clear()
                            return
                            
                    # >>TOGGLE MESSAGES<<
                    elif event.key in session.pyg.key_PERIOD:
                        if session.pyg.msg_toggle: session.pyg.msg_toggle = False
                        else:
                            if session.pyg.gui_toggle:
                                session.pyg.gui_toggle = False
                                session.pyg.msg_toggle = False
                            else:
                                session.pyg.msg_toggle = True
                                session.pyg.gui_toggle = True
        
        #########################################################
        # Move AI controlled entities
        for entity in session.player_obj.ent.env.entities: entity.ai()
        session.player_obj.ent.ai()
        
        session.pyg.game_state = 'play_garden'

    def key_UP(self):
        session.player_obj.ent.move(0, -session.pyg.tile_height) # >>MOVE<<

    def key_DOWN(self):
        session.player_obj.ent.move(0, session.pyg.tile_height)  # >>MOVE<<

    def key_LEFT(self):
        session.player_obj.ent.move(-session.pyg.tile_width, 0)  # >>MOVE<<

    def key_RIGHT(self):
        session.player_obj.ent.move(session.pyg.tile_width, 0)   # >>MOVE<<

    def key_ENTER(self):

        #########################################################
        # Pick up items or activate stairs       
        if session.player_obj.ent.tile.item:
            session.player_obj.ent.tile.item.pick_up()

    def key_PERIOD(self):
        
        #########################################################
        # Toggle messages
        ## Hide messages
        if session.pyg.msg_toggle:
            session.pyg.msg_toggle = False
        
        else:

            ## Hide messages and GUI
            if session.pyg.gui_toggle:
                session.pyg.gui_toggle = False
                session.pyg.msg_toggle = False
            
            ## View messages and GUI
            else:
                session.pyg.gui_toggle = True
                session.pyg.msg_toggle = True

    def key_SPEED(self):

        #########################################################
        # Change speed
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = float(time.time())
            session.mech.movement_speed()

    def render(self):
        
        from utilities import render_all

        session.pyg.msg_toggle = False
        session.pyg.gui_toggle = False
        render_all()

########################################################################################################################################################
# Interactions
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
        
        #########################################################
        # Set parameters
        ## Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

        ## Other
        self.tile   = None
        self.X      = None
        self.Y      = None
        self.owner  = None
        
        # Seed a seed for individual adjustments
        self.rand_X  = random.randint(-self.rand_X, self.rand_X)
        self.rand_Y  = random.randint(0,            self.rand_Y)
        self.flipped = random.choice([0, self.rand_Y])
        
        # Notify code of big object
        self.big = False
        
        #########################################################
        # Initialize effect if passive
        if self.effect:
            if self.effect.trigger == 'passive':
                if self.role != 'weapons':
                    self.effect.function(self)

    def draw(self):
        """ Constructs (but does not render) surfaces for items and their positions. """
        
        #########################################################
        # Shorthand
        cam = session.player_obj.ent.env.camera
        pyg = session.pyg
        img = session.img

        #########################################################
        # Blit a tile
        if not self.big:
            
            # Set position
            X = self.X - cam.X
            Y = self.Y - cam.Y

            if self.img_names[0] == 'decor':
                X -= self.rand_X
                Y -= self.rand_Y
        
            # Add effects and draw
            if (self.img_names[1] in ['leafy']) and not self.rand_Y:
                surface = img.dict[self.img_names[0]][self.img_names[1]]
                X       -= 32
                Y       -= 32
            else:
                if self.flipped: surface = img.flipped.dict[self.img_names[0]][self.img_names[1]]
                else:            surface = img.dict[self.img_names[0]][self.img_names[1]]

            pos = (X, Y)
                
        #########################################################
        # Blit multiple tiles
        else:
            
            # Blit every tile in the image
            surface, pos = [], []
            for i in range(len(img.big)):
                for j in range(len(img.big[0])):

                    img = img.big[len(img.big)-j-1][len(img.big[0])-i-1]
                    X   = self.X - cam.X - pyg.tile_width * i
                    Y   = self.Y - cam.Y - pyg.tile_height * j

                    surface.append(img)
                    pos.append((X, Y))

        return surface, pos

    def pick_up(self, ent=None, silent=False):
        """ Adds an item to the player's inventory and removes it from the map.
        
            Parameters
            ----------
            ent    : Entity object; owner of the item
            silent : bool; updates GUI if False
        """

        #########################################################
        # Imports
        from utilities import sort_inventory
        if not ent: ent = session.player_obj.ent
        
        #########################################################
        # Pick up if possible
        ## Do not pick up item if inventory is full
        if (len(ent.inventory) >= 26) and not silent:
            session.pyg.update_gui("Your inventory is full, cannot pick up " + self.name + ".", session.pyg.dark_gray)
        
        ## Check if movable
        else:
            if self.movable:
                
                # Add to inventory
                self.owner = ent
                if self.effect and (self.effect.trigger == 'passive'):
                    ent.item_effects.append(self.effect)
                
                ent.inventory[self.role].append(self)
                sort_inventory(ent)
                
                # Remove from environment
                if ent.tile:
                    if ent.tile.item:
                        ent.tile.item = None
                        self.tile     = ent.tile
                
                if (ent.role == 'player') and not silent:
                    session.pyg.update_gui("Picked up " + self.name + ".", session.pyg.dark_gray)

    def drop(self, ent=None):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at
            the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home. """
        
        # Allow for NPC actions
        if not ent: ent = session.player_obj.ent
        
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
            session.pyg.update_gui("Not enough cash!", color=session.pyg.red)

    def use(self, ent=None):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        # Allow for NPC actions
        if not ent: ent = session.player_obj.ent
        
        # Handle equipment
        if self.equippable: self.toggle_equip(ent)
        
        # Handle items
        elif self.effect:
            
            # Add active effect
            if (self.role == 'player') and (self.role in ['potions', 'weapons', 'armor']):
                ent.effects.append(self.effect)
            
            # Activate the item
            else: self.effect.function(ent)
        
        elif self.role == 'player': session.pyg.update_gui("The " + self.name + " cannot be used.", session.pyg.dark_gray)

    def toggle_equip(self, ent, silent=False):
        """ Toggles the equip/unequip status. """
        
        # Assign entity
        if not ent:        ent = session.player_obj.ent
        if not self.owner: self.owner = ent
        
        # Equip or dequip
        if self.equipped:  self.dequip(ent, silent)
        else:              self.equip(ent,  silent)

    def equip(self, ent, silent=False):
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
            if not self.hidden and not silent:
                session.pyg.update_gui("Equipped " + self.name + " on " + self.slot + ".", session.pyg.dark_gray)

    def dequip(self, ent, silent=False):
        """ Unequips an object and shows a message about it. """
        
        #########################################################
        # Update stats
        ent.equipment[self.slot] = None
        ent.attack  -= self.attack_bonus
        ent.defense -= self.defense_bonus
        ent.max_hp  -= self.hp_bonus

        if ent.hp > ent.max_hp:
            ent.hp = ent.max_hp
        if self.effect:
            if self.effect in ent.effects:
                ent.effects.remove(self.effect)

        #########################################################
        # Notify change of status
        self.equipped = False
        if self.role == 'player':
            if not self.hidden and not silent:
                session.pyg.update_gui("Dequipped " + self.name + " from " + self.slot + ".", session.pyg.dark_gray)

    def move(self, direction):
        
        self.direction = direction
        
        if direction == 'up':      self.Y += 32
        elif direction == 'down':  self.Y -= 32
        elif direction == 'left':  self.X += 32
        elif direction == 'right': self.X -= 32
        
        if self.tile: self.tile.item = None
        place_object(self, [self.X//32, self.Y//32], session.player_obj.ent.env)

class Entity:
    """ Player, enemies, and NPCs. Manages stats, inventory, and basic mechanics. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            player_obj    : Player object

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
        
        #########################################################
        # Imports
        from items_entities import Effect

        #########################################################
        # Set parameters
        ## Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        ## Images
        self.img_names_backup = self.img_names
        self.direction        = self.img_names[1]
        self.handedness       = 'left'

        ## Location
        self.env        = None
        self.last_env   = None
        self.tile       = None
        self.prev_tile  = None
        self.X          = 0
        self.Y          = 0
        self.X0         = 0
        self.Y0         = 0
        self.vicinity   = []

        ## Movement
        self.cooldown_time = 0.25
        self.last_ai_time  = 0
        self.motions_log   = [] # list of lists of int; prescribed motions for ai
        
        ## Mechanics
        self.dead        = False
        self.dialogue    = None
        self.default_dialogue = []
        self.quest       = None
        self.wallet      = 100
        self.trade_times = None
        self.inventory   = {'weapons': [], 'armor': [],  'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
        self.equipment   = {'head': None,  'face': None, 'chest': None, 'body': None,  'dominant hand': None, 'non-dominant hand': None}
        
        ## Randomizer
        self.rand_X = random.randint(-session.pyg.tile_width,  session.pyg.tile_width)
        self.rand_Y = random.randint(-session.pyg.tile_height, session.pyg.tile_height)

        #########################################################
        # Initialize reactions and abilities
        self.garden_effects = [
            Effect(
                name          = 'scare',
                img_names     = ['bubbles', 'exclamation'],
                function      = session.mech.entity_scare,
                trigger       = 'active',
                sequence      = '⮟⮜⮟',
                cooldown_time = 1,
                other         = None),
            
            Effect(
                name          = 'comfort',
                img_names     = ['bubbles', 'heart'],
                function      = session.mech.entity_comfort,
                trigger       = 'active',
                sequence      = '⮟⮞⮜',
                cooldown_time = 1,
                other         = None),
            
            Effect(
                name          = 'clean',
                img_names     = ['bubbles', 'dots'],
                function      = session.mech.entity_clean,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None)]
        
        self.item_effects = [
            Effect(
                name          = 'suicide',
                img_names     = ['decor', 'bones'],
                function      = session.mech.suicide,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None),

            Effect(
                name          = 'scare',
                img_names     = ['bubbles', 'exclamation'],
                function      = session.mech.entity_scare,
                trigger       = 'active',
                sequence      = '⮟⮜⮟',
                cooldown_time = 1,
                other         = None),
                
            Effect(
                name          = 'capture',
                img_names     = ['bubbles', 'heart'],
                function      = session.mech.entity_capture,
                trigger       = 'active',
                sequence      = '⮟⮞⮟',
                cooldown_time = 1,
                other         = None)]
        self.effects    = []
        
    def ai(self):
        """ Preset movements. """
        
        #########################################################
        # Move if alive
        moved = False
        if not self.dead:
            if time.time()-self.last_ai_time > self.cooldown_time:
                self.last_ai_time = float(time.time())
                
                # Move or follow
                if not self.motions_log:
                    distance = self.distance_to(session.player_obj.ent)
                    
                    #########################################################
                    # Flee
                    if self.fear and (type(self.fear) == int):
                        if not random.randint(0, self.lethargy//10):
                            self.move_towards(self.X0, self.Y0)
                            self.fear -= 1
                            if self.fear < 0: self.fear = 0
                    
                    #########################################################
                    # Approach far, possibly attack
                    elif self.follow and (distance < 320):
                        if not random.randint(0, self.lethargy//2):
                            self.move_towards(session.player_obj.ent.X, session.player_obj.ent.Y)
                    
                        # Attack if close and aggressive; chance based on miss_rate
                        if self.aggression:
                            if (distance < 64) and not random.randint(0, self.miss_rate):
                                self.attack_target(session.player_obj.ent)
                    
                    #########################################################
                    # Approach near, possibly attack
                    elif self.aggression and (session.player_obj.ent.hp > 0):
                        
                        # Attack if close and aggressive; chance based on miss_rate
                        if (distance < 64) and not random.randint(0, self.miss_rate):
                            self.attack_target(session.player_obj.ent)
                        
                        # Move towards the player if distant; chance based on lethargy
                        elif (distance < self.aggression*session.pyg.tile_width) and not random.randint(0, self.lethargy//2) and not moved:
                            self.move_towards(session.player_obj.ent.X, session.player_obj.ent.Y)
                    
                    #########################################################
                    # Idle if not following or aggressive
                    else:
                        if self.role != 'player': self.idle()
                
                #########################################################
                # Continue a prescribed pattern
                else:
                    loc = self.motions_log[0]
                    self.move(loc[0], loc[1])
                    self.motions_log.remove(loc)

    def idle(self):
        """ Randomly walks around """
        
        # Choose direction
        if random.randint(0, 1):
            dX = random.randint(-1, 1) * session.pyg.tile_width
            dY = 0
        else:
            dX = 0
            dY = random.randint(-1, 1) * session.pyg.tile_width
        
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
        
        #########################################################
        # Imports
        from utilities import is_blocked

        #########################################################
        # Check if direction matches entity orientation
        ## Determine direction
        if   dY > 0: self.direction = 'front'
        elif dY < 0: self.direction = 'back'
        elif dX < 0: self.direction = 'left'
        elif dX > 0: self.direction = 'right'
        else:        self.direction = random.choice(['front', 'back', 'left', 'right'])
        
        ## Change orientation before moving
        if self.img_names[1] != self.direction:
            if self.img_names[1]:
                self.img_names[1] = self.direction

        #########################################################
        # Move to new position
        else:
            x = int((self.X + dX)/session.pyg.tile_width)
            y = int((self.Y + dY)/session.pyg.tile_height)
            
            #########################################################
            # Move player
            if self.role == 'player': self.move_player(x, y, dX, dY)
            
            #########################################################
            # Move pet
            pet_list = ['red radish', 'orange radish', 'purple radish']
            if self.img_names[0] in pet_list: self.move_pet(x, y, dX, dY)
            
            #########################################################
            # Move NPC, enemy, or projectile
            else:
                
                # Move NPC or enemy
                if not is_blocked(self.env, [x, y]):
                    
                    # Keep the entity in its native habitat
                    if self.env.map[x][y].biome in session.img.biomes[self.habitat]:
                        
                        if self.env.map[x][y].item and self.role == 'enemy':
                            if self.env.map[x][y].item.img_names[0] != 'stairs':
                                self.X          += dX
                                self.Y          += dY
                                self.tile.entity = None
                                session.player_obj.ent.env.map[x][y].entity = self
                                self.tile        = session.player_obj.ent.env.map[x][y]
                        
                        else:
                            self.X          += dX
                            self.Y          += dY
                            self.tile.entity = None
                            session.player_obj.ent.env.map[x][y].entity = self
                            self.tile        = session.player_obj.ent.env.map[x][y]
                
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

        #########################################################
        # Imports
        from utilities import check_tile, is_blocked

        #########################################################
        # Move forwards
        if not is_blocked(self.env, [x, y]):
            
            # Move player and update map
            self.prev_tile              = self.env.map[int(self.X/session.pyg.tile_width)][int(self.Y/session.pyg.tile_height)]
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
            if (session.mech.movement_speed_toggle == 1) and (self.stamina > 0):
                self.stamina -= 1/2
                session.pyg.update_gui()
        
        #########################################################
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
                    if ent.trade_times:
                        if session.player_obj.ent.env.env_time in ent.trade_times:
                            session.trade_obj.ent = ent
                            session.pyg.overlay = 'trade'
                
                # Play speech and update quests
                if time.time() - session.aud.last_press_time_speech > session.aud.speech_speed//100:
                    session.pyg.update_gui(dialogue)
                    session.aud.play_speech(dialogue)
                    if ent.dialogue:
                        ent.dialogue = ent.quest.dialogue(ent)
            
            # Make them flee
            elif type(ent.fear) == int: ent.fear += 30
            
            # Attack the entity
            elif (self.env.name != 'home') or (self.equipment['dominant hand'] in ['blood dagger', 'blood sword']):
                self.attack_target(ent)
        
        #########################################################
        # Dig a tunnel
        elif self.equipment['dominant hand'] is not None:
            if self.equipment['dominant hand'].name in ['shovel', 'super shovel']:
                
                # Move player and reveal tiles
                if self.X >= 64 and self.Y >= 64:
                    if self.super_dig or not self.env.map[x][y].unbreakable:
                        self.env.create_tunnel(x, y)
                        self.prev_tile                 = self.env.map[int(self.X/session.pyg.tile_width)][int(self.Y/session.pyg.tile_height)]
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
                        session.pyg.update_gui("The shovel strikes the barrier but does not break it.", session.pyg.dark_gray)
                    
                    # Update durability
                    if self.equipment['dominant hand'].durability <= 100:
                        self.equipment['dominant hand'].durability -= 1
                    if self.equipment['dominant hand'].durability <= 0:
                        session.pyg.update_gui(f"Broken {self.equipment['dominant hand'].name}!", color=session.pyg.dark_gray)
                        self.equipment['dominant hand'].drop()
                        self.tile.item = None # removes item from world
        
        self.env.camera.update() # omit this if you want to modulate when the camera focuses on the player

    def move_pet(self, x, y, dX, dY):

        from utilities import is_blocked

        # Move forwards
        if not is_blocked(self.env, [x, y]):
            
            # Move and update map
            self.X                      += dX
            self.Y                      += dY
            self.tile.entity            = None
            session.player_obj.ent.env.map[x][y].entity   = self
            self.tile                   = self.env.map[x][y]
            
        # Trigger floor effects
        if self.env.map[x][y].item:
            if self.env.map[x][y].item.effect:
                if self.env.map[x][y].item.effect.function == session.mech.entity_eat:
                    self.env.map[x][y].item.effect.function(self)

    def move_towards(self, target_X, target_Y):
        """ Moves object towards target. """
        
        dX       = target_X - self.X
        dY       = target_Y - self.Y
        distance = (dX ** 2 + dY ** 2)**(1/2)
        if distance:
            
            if dX and not dY:
                dX = round(dX/distance) * session.pyg.tile_width
                dY = 0
            
            elif dY and not dX:
                dX = 0
                dY = round(dX/distance) * session.pyg.tile_width
            
            elif dX and dY:
                if random.randint(0, 1):
                    dX = round(dX/distance) * session.pyg.tile_width
                    dY = 0
                else:
                    dX = 0
                    dY = round(dY/distance) * session.pyg.tile_width
            
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
                            session.pyg.update_gui(self.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points.", session.pyg.red)
                            target.take_damage(damage)
                    
                    # Regular attack
                    else:
                        session.pyg.update_gui(self.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points.", session.pyg.red)
                        target.take_damage(damage)
                else:
                    session.pyg.update_gui(self.name.capitalize() + " strikes " + target.name + " but it has no effect!", session.pyg.red)
        return

    def take_damage(self, damage):
        """ Applies damage if possible. """
        
        if damage > 0:
            
            # Apply damage
            self.hp -= damage
            
            # Damage animation
            session.img.flash_over(self)
            
            # Check for death
            if self.hp <= 0:
                self.hp = 0
                self.death()
                
                # Gain experience
                if self != session.player_obj.ent:
                    session.player_obj.ent.exp += self.exp
                    check_level_up()
                else:
                    session.pyg.update_gui()

    def death(self):
        
        #########################################################
        # Imports
        from items_entities import create_item

        #########################################################
        # Player death
        if self.role == 'player':
            session.pyg.update_gui("You died!", session.pyg.red)
            session.player_obj.ent.dead        = True
            session.player_obj.ent.tile.entity = None
            session.player_obj.ent.img_names   = session.player_obj.ent.img_names_backup
            
            item = create_item('skeleton')
            item.name = f"the corpse of {self.name}"
            place_object(item, [self.X//session.pyg.tile_width, self.Y//session.pyg.tile_height], self.env)
            pygame.event.clear()
        
        #########################################################
        # Entity or projectile death
        else:
            self.dead        = True
            self.tile.entity = None
            self.env.entities.remove(self)
            if self in session.player_obj.ent.env.entities: session.player_obj.ent.env.entities.remove(self)
            
            if self.role != 'projectile':
                session.pyg.update_gui("The " + self.name + " is dead! You gain " + str(self.exp) + " experience points.", session.pyg.red)
                
                if not self.tile.item:
                    item = create_item('bones')
                    item.name = f"the corpse of {self.name}"
                    place_object(item, [self.X//session.pyg.tile_width, self.Y//session.pyg.tile_height], self.env)
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
        session.pyg.update_gui("The " + self.name + " has been captured!", session.pyg.red)

        # Update entity
        self.dead        = True
        self.tile.entity = None
        self.env.entities.remove(self)
        if self in session.player_obj.ent.env.entities: session.player_obj.ent.env.entities.remove(self)
        
        session.player_obj.ent.discoveries['entities'][self.name] = self.img_names

    def draw(self, surface, loc=None):
        """ Draws the object at its position.

            Parameters
            ----------
            surface : pygame image
            loc     : list of int; screen coordinates """
        
        #########################################################
        # Set location
        if loc:
            X = loc[0]
            Y = loc[1]
        else:
            X = self.X - self.env.camera.X
            Y = self.Y - self.env.camera.Y
        
        #########################################################
        # Choose a variant to render
        ## Swimming
        if self.tile.biome in session.img.biomes['sea']: swimming = True
        else:                                            swimming = False

        ## Regular
        if self.handedness == 'left': 
            if swimming: surface.blit(session.img.halved([self.img_names[0], self.img_names[1]]), (X, Y))
            else:        surface.blit(session.img.dict[self.img_names[0]][self.img_names[1]],     (X, Y))
        
        ## Flipped
        else:
            if swimming: surface.blit(session.img.halved([self.img_names[0], self.img_names[1]], flipped=True), (X, Y))
            else:        surface.blit(session.img.flipped.dict[self.img_names[0]][self.img_names[1]],           (X, Y))
        
        #########################################################
        # Apply equipment to humans
        if self.img_names[0] in session.img.skin_options:
            
            # Blit chest
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'chest':
                        if self.handedness == 'left':
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]), (X, Y))
                            else:        surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],     (X, Y))
                        else:
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                            else:        surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                    else: pass

            # Blit armor
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'body':
                        if self.handedness == 'left':
                            if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]),        (X, Y))
                            elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]), (X, Y))
                            else:                 surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],            (X, Y))
                        else:
                            if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                            elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]),        (X, Y))
                            else:                 surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                    else: pass

            # Blit face
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'face':
                        if self.handedness == 'left':
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]), (X, Y))
                            else:        surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],     (X, Y))
                        else:
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                            else:        surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                    else: pass
            
            # Blit hair
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'head':
                        if self.handedness == 'left':
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]), (X, Y))
                            else:        surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],     (X, Y))
                        else:
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                            else:        surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                    else: pass
            
            # Blit weapons and shields
            for item in self.equipment.values():
                if item is not None:
                    if not item.hidden:
                        if item.role in ['weapons', 'armor']:
                            if item.slot in ['dominant hand', 'non-dominant hand']:
                                if self.handedness == 'left':
                                    if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]),               (X, Y))
                                    elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]),        (X, Y))
                                    else:                 surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],                   (X, Y))
                                else:
                                    if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (X, Y))
                                    elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]),        (X, Y))
                                    else:                 surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (X, Y))
                            else: pass
        
        # Blit dialogue bubble
        if self.dialogue: session.pyg.display.blit(session.img.dict['bubbles']['dots'], (X, Y-session.pyg.tile_height))
        
        # Blit trading bubble
        elif self.trade_times:
            if session.player_obj.ent.env.env_time in self.trade_times:
                session.pyg.display.blit(session.img.dict['bubbles']['cart'], (X, Y-session.pyg.tile_height))

class Mechanics:
    """ Game parameters. Does not need to be saved. """
    
    def __init__(self):
        
        #########################################################
        # Set parameters
        ## Utility
        self.cooldown_time     = 1

        ## Combat
        self.heal_amount       = 4
        self.lightning_damage  = 20
        self.lightning_range   = 5 * session.pyg.tile_width
        self.confuse_range     = 8 * session.pyg.tile_width
        self.confuse_num_turns = 10
        self.fireball_radius   = 3 * session.pyg.tile_width
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

    # Environments
    def enter_dungeon(self, text='', lvl_num=0):
        """ Advances player to the next level. """
        
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            # Fade in
            if text:
                session.pyg.fadeout_screen(text)
                session.play_game_obj.fadein = text
            
            #########################################################
            # Create and/or enter
            ## Create dungeon for new game
            if 'dungeon' not in session.player_obj.envs.dict.keys():
                session.player_obj.envs.dict['dungeon'] = []
                session.player_obj.envs.build_dungeon_level(lvl_num)
            
            ## Enter the first dungeon
            if session.player_obj.ent.env.name != 'dungeon':
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['dungeon'][0],
                    loc = session.player_obj.envs.dict['dungeon'][0].center)
            
            ## Enter the next saved dungeon
            elif session.player_obj.ent.env.lvl_num < len(session.player_obj.envs.dict['dungeon']):
                lvl_num = session.player_obj.ent.env.lvl_num
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['dungeon'][lvl_num],
                    loc = session.player_obj.envs.dict['dungeon'][lvl_num].center)
            
            ## Enter a new dungeon
            else:
                session.player_obj.envs.build_dungeon_level(lvl_num)
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['dungeon'][-1],
                    loc = session.player_obj.envs.dict['dungeon'][-1].center)

    def enter_hallucination(self, text=None):
        """ Advances player to the next level. """
        
        if text == None: text='. . . ! Your vision blurs as the substance seeps through your veins.'

        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            #########################################################
            # Create and/or enter
            ## Create environment
            if 'hallucination' not in session.player_obj.envs.dict.keys():
                session.player_obj.envs.dict['hallucination'] = []
                
                session.pyg.fadeout_screen(text)
                session.pyg.overlay = None
                session.player_obj.envs.build_hallucination_level()
                session.play_game_obj.fadein = text

            ## Enter the first hallucination
            if session.player_obj.ent.env.name != 'hallucination':
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['hallucination'][0],
                    loc = session.player_obj.envs.dict['hallucination'][0].center)
            
            ## Enter the next saved hallucination
            elif session.player_obj.ent.env.lvl_num < len(session.player_obj.envs.dict['hallucination']):
                lvl_num = session.player_obj.ent.env.lvl_num
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['hallucination'][lvl_num],
                    loc = session.player_obj.envs.dict['hallucination'][lvl_num].center)
            
            ## Enter a new hallucination
            else:
                session.player_obj.envs.build_hallucination_level()
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['hallucination'][-1],
                    loc = session.player_obj.envs.dict['hallucination'][-1].center)

    def enter_bitworld(self, text=None):
        """ Advances player to bitworld. """
        
        if text == None: text = '. . . ! Your vision blurs as the substance seeps through your veins.'

        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            #########################################################
            # Create and/or enter
            ## Create
            if 'bitworld' not in session.player_obj.envs.dict.keys():
                session.player_obj.envs.dict['bitworld'] = []
                
                session.pyg.fadeout_screen(text)
                session.pyg.overlay = None
                session.player_obj.envs.build_bitworld()
                session.play_game_obj.fadein = text

            ## Enter
            if session.player_obj.ent.env.name != 'bitworld':
                session.img.render_fx = 'bw_binary'
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['bitworld'],
                    loc = session.player_obj.envs.dict['bitworld'].center)
    
    def enter_cave(self):
        """ Advances player to the next level. """
        
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            #########################################################
            # Create and/or enter
            ## Create
            if 'cave' not in session.player_obj.envs.dict.keys(): 
                session.pyg.update_gui("The ground breaks beneath you and reveals a cave.", session.pyg.dark_gray)
                session.player_obj.envs.dict['cave'] = []
                session.player_obj.envs.build_cave_level()
            
            ## Enter the first cave
            if session.player_obj.ent.env.name != 'cave':
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['cave'][0],
                    loc = session.player_obj.envs.dict['cave'][0].center)
            
            ## Enter the next saved cave
            elif session.player_obj.ent.env.lvl_num < len(session.player_obj.envs.dict['cave']):
                lvl_num = session.player_obj.ent.env.lvl_num
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['cave'][lvl_num],
                    loc = session.player_obj.envs.dict['cave'][lvl_num].center)
            
            ## Enter a new cave
            else:
                session.player_obj.envs.build_cave_level()
                place_player(
                    ent = session.player_obj.ent,
                    env = session.player_obj.envs.dict['cave'][-1],
                    loc = session.player_obj.envs.dict['cave'][-1].center)

    def enter_overworld(self):
        
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            #########################################################
            # Create and/or enter
            ## Create
            if 'overworld' not in session.player_obj.envs.dict.keys():
                session.player_obj.envs.build_overworld()

            ## Enter
            loc = session.player_obj.envs.dict['overworld'].center
            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.dict['overworld'],
                loc = [loc[0], loc[1]])

    def enter_home(self):
        
        if time.time()-session.pyg.last_press_time > self.cooldown_time:
            session.pyg.last_press_time = time.time()
            pygame.event.clear()
            
            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.dict['home'],
                loc = session.player_obj.envs.dict['home'].player_coordinates)

    # Item effects
    def swing(self, ent=None):

        from utilities import get_vicinity

        # Set entity
        if not ent: ent = session.player_obj.ent
        
        # Check for remaining stamina
        if ent.stamina:
            
            # Send animation to queue
            image = session.img.dict[ent.equipment['dominant hand'].img_names[0]]['dropped']
            session.img.vicinity_flash(ent, image)
            
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
        session.pyg.update_gui()

    def lamp(self, item):
        """ Adds or removes a light to be rendered under the following conditions.
            1. The object is not owned by an entity.
            2. The object is equipped by an entity. """
        
        if hasattr(item, 'env'):
            lamp_list = item.env.weather.lamp_list
        else:
            lamp_list = session.player_obj.ent.env.weather.lamp_list
        
        if item.owner:
            if item.equipped:
                if item not in lamp_list: lamp_list.append(item)
            else:
                if item in lamp_list:     lamp_list.remove(item)
                    
        
        else:
            if item not in lamp_list: lamp_list.append(item)
            else:                     lamp_list.remove(item)

    def propagate(self, ent=None):
        
        from items_entities import create_entity

        # Set entity
        if not ent: ent = session.player_obj.ent
        
        # Note location and image names
        img_x, img_y = int(ent.X/session.pyg.tile_width), int(ent.Y/session.pyg.tile_height)
        
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
            'front': [0, session.pyg.tile_height],
            'back':  [0, -session.pyg.tile_height],
            'left':  [-session.pyg.tile_width, 0],
            'right': [session.pyg.tile_width, 0]}
        
        for _ in range(100):
            motions_log.append(directions[ent.direction])
        
        # Send directions to entity
        item.motions_log = motions_log

    # Gameplay
    def movement_speed(self, toggle=True, custom=None):
        """ Toggles and sets movement speed. """
        
        # Check stamina
        if session.player_obj.ent.stamina > 0:
        
            # Change speed
            if toggle:
                if self.movement_speed_toggle == len(self.speed_list)-1: 
                    self.movement_speed_toggle = 0
                else:
                    self.movement_speed_toggle += 1
                session.pyg.update_gui(f"Movement speed: {self.speed_list[self.movement_speed_toggle][0]}", session.pyg.dark_gray)
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
                session.pyg.update_gui(f"Movement speed: {self.slow_list[self.movement_speed_toggle][0]}", session.pyg.dark_gray)
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
        image = session.img.dict['decor']['bones']
        session.img.vicinity_flash(session.player_obj.ent, image)
        
        # Kill player
        session.player_obj.ent.death()
        return

    def spin(self, ent):
        
        # Prepare movements
        motions_log = []
        
        # Look forward first
        if ent.img_names[0] != 'front':
            motions_log.append([0, session.pyg.tile_height])
        motions_log.append([-session.pyg.tile_width, 0])
        
        # Spin around
        motions_log.append([0, -session.pyg.tile_height])
        motions_log.append([session.pyg.tile_width, 0])
        motions_log.append([0, session.pyg.tile_height])
        
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
                                dX = round(dX/distance) * session.pyg.tile_width
                                dY = 0
                            
                            elif dY and not dX:
                                dX = 0
                                dY = round(dX/distance) * session.pyg.tile_width
                            
                            elif dX and dY:
                                if random.randint(0, 1):
                                    dX = round(dX/distance) * session.pyg.tile_width
                                    dY = 0
                                else:
                                    dX = 0
                                    dY = round(dY/distance) * session.pyg.tile_width
                            
                            motions_log.append([dX, dY])
                            motions_log.append([dX, dY])
                            distance -= 32
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = session.img.dict['bubbles']['question']

        # Bathe
        else:
            if session.pets_obj.moods['anger']:
                session.pets_obj.moods['anger'] -= 1
                image = session.img.dict['bubbles']['water']
            
            else:
                session.pets_obj.moods['boredom'] += 1
                image = session.img.dict['bubbles']['dots']
            
        session.img.flash_above(ent, image)

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
                                        dX = round(dX/distance) * session.pyg.tile_width
                                        dY = 0
                                    
                                    elif dY and not dX:
                                        dX = 0
                                        dY = round(dX/distance) * session.pyg.tile_width
                                    
                                    elif dX and dY:
                                        if random.randint(0, 1):
                                            dX = round(dX/distance) * session.pyg.tile_width
                                            dY = 0
                                        else:
                                            dX = 0
                                            dY = round(dY/distance) * session.pyg.tile_width
                                    
                                    motions_log.append([dX, dY])
                                    motions_log.append([dX, dY])
                                    distance -= 32
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = session.img.dict['bubbles']['question']

        # Sleep
        else:
            image = session.img.dict['bubbles']['dots']
            
        session.img.flash_above(ent, image)

    # Entity interactions
    def entity_eat(self, ent):
        """ Dropped item effect. """
        
        session.pets_obj.moods['happiness'] += 1
        session.pets_obj.moods['boredom']   -= 1
        image = session.img.dict['bubbles']['heart']
        session.img.flash_above(ent, image)
        ent.tile.item = None

    def entity_scare(self):
        """ Combo effect. """

        from utilities import get_vicinity

        # Find entities in vicinity
        ent_list = []
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            
            if session.player_obj.ent.env.name == 'garden':
                session.pets_obj.moods['lethargy'] -= 1
                session.pets_obj.moods['boredom']  -= 1
            
            image = session.img.dict['bubbles']['exclamation']
            for ent in ent_list:
                for tile in get_vicinity(ent).values():
                    if not tile.blocked:
                        ent.move_towards(tile.X, tile.Y)
                session.img.flash_above(ent, image)
        
        else:
            session.pyg.update_gui("There are no entities in your vicinity.", session.pyg.dark_gray)

    def entity_capture(self):
        """ Combo effect. """

        from utilities import get_vicinity

        # Find entities in vicinity
        ent = None
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                if tile.entity.role != 'NPC':
                    ent = tile.entity
                    break
        
        # Activate effect if entities are found
        if ent:
            image = session.img.dict['bubbles']['heart']
            session.img.flash_above(ent, image)
            session.img.flash_on(ent, session.img.dict[ent.img_names[0]][ent.img_names[1]])
            
            if session.player_obj.ent.discoveries['entities'].values():
                for names in session.player_obj.ent.discoveries['entities'].values():
                    if ent.name not in names:
                        ent.capture()
                        break
                    else:
                        session.pyg.update_gui("The " + ent.name + " has already been logged.", session.pyg.dark_gray)
            else:
                ent.capture()
        else:
            session.pyg.update_gui("There are no entities in your vicinity.", session.pyg.dark_gray)

    def entity_comfort(self):
        """ Combo effect. """

        from utilities import get_vicinity

        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            session.pets_obj.moods['sadness'] -= 1
            if session.pets_obj.moods['sadness'] <= 0: session.pets_obj.moods['boredom'] += 1
            image = session.img.dict['bubbles']['heart']
            for ent in ent_list:
                session.img.flash_above(ent, image)
                self.spin(ent)

    def entity_clean(self):
        """ Combo effect. """

        from utilities import get_vicinity
        
        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            for ent in ent_list:
                self.find_water(ent)

    # Item interactions
    def skeleton(self):
        
        # Find location
        loc = session.player_obj.ent.env
        locs = ['garden', 'womb', 'home', 'dungeon', 'hallucination', 'overworld', 'bitworld', 'cave']
        
        # Define dialogue bank
        dead_log = {
            'garden': [
                "... this must be a dream."],
            
            'womb': [
                "... this must be a dream."],
            
            'home': [
                "A skeleton... in your home."],
            
            'dungeon': [
                "Skeleton. Looks like a Greg.",
                "Ow! Shouldn't poke around with bones.",
                "Wait... is this Jerry?",
                "The pile of bones lay motionless, thankfully.",
                "Decay is swift.",
                "..."],
            
            'hallucination': [
                "Bones? I must be seeing things.",
                "..."],
            
            'overworld': [
                "Should I be concerned about this?",
                "Looks human. Something bad happened here.",
                "..."],
            
            'bitworld': [
                "Are these dots inside of me too?",
                "What is...?",
                "..."
                ],
            
            'cave': [
                "Typical.",
                "Caves can kill in mysterious ways."]}
        
        if random.randint(0, 4): image = session.img.dict['bubbles']['skull']
        else:                    image = session.img.dict['bubbles']['exclamation']
        session.img.flash_above(session.player_obj.ent, image)

########################################################################################################################################################
# Side Menus
class InventoryMenu:
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """
        
        #########################################################
        # Parameters
        ## Positions
        self.cursor_pos  = [0, 32]
        self.img_x       = 0
        self.img_y       = 0

        ## Other
        self.dic_index   = 0
        self.dic_indices = [[0, 0]]
        self.img_names   = ['null', 'null']
        self.locked      = False
        self.detail      = True
        
        #########################################################
        # Surface initialization
        self.background_fade = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def run(self):
        
        #########################################################
        # Initialize
        ## Update dictionaries and create cursors
        self.update_data()

        ## Set navigation speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Define shorthand
        pyg = session.pyg

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
                # Switch section
                elif event.key in pyg.key_LEFT:
                    self.key_LEFT()
                elif event.key in pyg.key_RIGHT:
                    self.key_RIGHT()
                
                #########################################################
                # Activate or drop item
                elif event.key in session.pyg.key_ENTER:
                    self.key_ENTER()
                elif event.key in session.pyg.key_PERIOD:
                    self.key_PERIOD()
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_QUEST:
                    self.key_QUEST()
                
                #########################################################
                # Toggle selection lock
                elif event.key in pyg.key_INV:
                    self.key_INV()
                
                #########################################################
                # Open catalog
                elif event.key in session.pyg.key_DEV:
                    self.key_DEV()
                    return
                
                #########################################################
                # Return to game
                else:
                    self.key_BACK()
                    return

            # Save for later reference
            if self.dic_indices:
                index = self.dic_index%len(self.dic_indices)
                self.dic_indices[index][0] = self.offset
                self.dic_indices[index][1] = self.choice
        
        pyg.overlay = 'inv'
        return

    def render(self):

        #########################################################
        # Adjust GUI
        pyg = session.pyg
        pyg.msg_height = 1
        pyg.update_gui()

        #########################################################
        # Renders
        ## Background
        if not self.locked: pyg.screen.blit(self.background_fade, (0, 0))
        
        ## Cursor
        if self.cursor_pos[1] < 32: self.cursor_pos[1] = 32
        pyg.screen.blit(self.cursor_fill, self.cursor_pos)

        ## Color
        session.img.average()
        color = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
        
        ## Renders entries (up to 13 visible)
        Y = 32
        visible_count = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if visible_count <= 12:
                
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
                visible_count += 1                
                
            else: break
        
        pyg.screen.blit(self.cursor_border, self.cursor_pos)

    # Keys
    def key_UP(self):

        if not self.locked:
            self.choice -= 1
            if self.cursor_pos[1] == 32: self.offset -= 1
            else: self.cursor_pos[1] -= session.pyg.tile_height

        else:
            session.player_obj.ent.move(0, -session.pyg.tile_height)
                
    def key_DOWN(self):

        if not self.locked:
            self.choice += 1
            if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
            else: self.cursor_pos[1] += session.pyg.tile_height

        else:
            session.player_obj.ent.move(0, session.pyg.tile_height)

    def key_LEFT(self):
        if len(self.dic_categories) > 1:
            
            if not self.locked:
                self.dic_index -= 1
                self.dic    = self.inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
                self.choice = self.cursor_pos[1]//32 + self.offset - 1
                
                # Move cursor to the highest spot in the dictionary
                if self.cursor_pos[1] > 32*len(self.dic):
                    self.cursor_pos[1] = 32*len(self.dic)
                    self.choice = len(self.dic) - self.offset - 1

            else:
                session.player_obj.ent.move(-session.pyg.tile_height, 0)

    def key_RIGHT(self):
        if len(self.dic_categories) > 1:
            
            if not self.locked:
                self.dic_index += 1
                self.dic    = self.inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]
                self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
                self.choice = self.cursor_pos[1]//32 + self.offset - 1
                
                # Move cursor to the highest spot in the dictionary
                if self.cursor_pos[1] > 32*len(self.dic):
                    self.cursor_pos[1] = 32*len(self.dic)
                    self.choice = len(self.dic) - self.offset - 1
            
            else:
                session.player_obj.ent.move(session.pyg.tile_width, 0)

    def key_BACK(self):
        session.pyg.last_press_time = float(time.time())
        session.pyg.overlay         = None

    def key_QUEST(self):
        if not self.detail: self.detail = True
        else:               self.detail = False

    def key_INV(self):
        session.pyg.last_press_time = float(time.time())
        self.cursor_border = pygame.Surface((32, 32)).convert()
        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))

        # Thin cursor
        if not self.locked:
            self.locked   = True
            cursor_points = [(0, 0), (30, 0), (30, 30), (0, 30)]
            cursor_width  = 2
        
        # Thick cursor
        else:
            self.locked   = False
            cursor_points = [(0, 0), (31, 0), (31, 31), (0, 31)]
            cursor_width  = 1
        
        pygame.draw.polygon(self.cursor_border, session.pyg.white, cursor_points, cursor_width)

    def key_DEV(self):
        session.pyg.overlay = 'dev'
        pygame.event.clear()

    def key_ENTER(self):
        self.find_item().use()
        self.update_data()

    def key_PERIOD(self):
        self.find_item().drop()
        if self.cursor_pos[1] >= 32*len(self.dic):
            self.cursor_pos[1] = 32*(len(self.dic)-1)
            self.choice = len(self.dic) - self.offset - 2

    # Tools
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
        for key, value in session.player_obj.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics[key][item.name] = session.img.dict[item.img_names[0]][item.img_names[1]]
        for key, value in self.inventory_dics.items():
            if not value: self.dic_categories.remove(key)
        
        # Restore last selection
        if len(self.dic_indices) != len(self.dic_categories):
            self.dic_indices = [[0, 0] for _ in self.dic_categories] # offset, choice
        if self.dic_indices:
            self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
            self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
            self.dic    = self.inventory_dics[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        else: session.pyg.overlay = None

    def find_item(self, offset=None):
        
        # Retrieve inventory list
        outer_list = list(session.player_obj.ent.inventory.items())
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

class CatalogMenu:
    
    # Core
    def __init__(self):
        """ Manages catalog menu on the side of the screen. Allows item placemennt. """
        
        #########################################################
        # Parameters
        ## Positions
        self.cursor_pos = [session.pyg.screen_width-session.pyg.tile_width, 32]
        self.img_x      = 0
        self.img_y      = 0

        ## Other
        self.img_names = ['null', 'null']
        self.locked    = False

        #########################################################
        # Surface initialization
        self.background_fade = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def run(self):  
        
        #########################################################
        # Initialize
        ## Update dictionaries and create cursors
        self.update_data()
        
        ## Restrict movement speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Define shorthand
        pyg = session.pyg

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
                # Switch section
                elif event.key in pyg.key_LEFT:
                    self.key_LEFT()
                
                elif event.key in pyg.key_RIGHT:
                    self.key_RIGHT()
                
                #########################################################
                # Activate item
                elif event.key in pyg.key_ENTER:
                    self.key_ENTER()
                
                #########################################################
                # Toggle selection lock
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                
                #########################################################
                # Open inventory
                elif event.key in pyg.key_INV:
                    self.key_INV()
                    return

                #########################################################
                # Return to game
                else:
                    self.key_BACK()
                    return

            # Save for later reference
            self.dic_indices[self.dic_index%len(self.dic_indices)][0] = self.offset
            self.dic_indices[self.dic_index%len(self.dic_indices)][1] = self.choice
        
        pyg.overlay = 'dev'
        return

    def render(self):
        if not self.locked: session.pyg.screen.blit(self.background_fade, (0, 0))
        
        session.pyg.msg_height = 1
        session.pyg.update_gui()
        
        session.pyg.screen.blit(self.cursor_fill, self.cursor_pos)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                img_names = self.dic[list(self.dic.keys())[(i+self.offset)%len(self.dic)]]
                session.pyg.screen.blit(session.img.dict[img_names[0]][img_names[1]], (session.pyg.screen_width-session.pyg.tile_width, Y))
                Y += session.pyg.tile_height
                counter += 1
            else: break
        session.pyg.screen.blit(self.cursor_border, self.cursor_pos)

    # Keys
    def key_UP(self):

        if not self.locked:
            self.choice -= 1
            if self.cursor_pos[1] == 32: self.offset -= 1
            else: self.cursor_pos[1] -= session.pyg.tile_height
        
        else:
            session.player_obj.ent.move(0, -session.pyg.tile_height)
                
    def key_DOWN(self):

        if not self.locked:
            self.choice += 1
            if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
            else: self.cursor_pos[1] += session.pyg.tile_height
            
        else:
            session.player_obj.ent.move(0, session.pyg.tile_height)

    def key_LEFT(self):

        if not self.locked:
            self.dic_index -= 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
            while not len(self.dic):
                self.dic_index -= 1
                self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        
        else:
            session.player_obj.ent.move(-session.pyg.tile_height, 0)

        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
        self.choice = self.cursor_pos[1]//32 + self.offset - 1
    
        # Move cursor to the highest spot in the dictionary
        if self.cursor_pos[1] > 32*len(self.dic):
            self.cursor_pos[1] = 32*len(self.dic)
            self.choice = len(self.dic) - self.offset - 1

    def key_RIGHT(self):

        if not self.locked:
            self.dic_index += 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
            while not len(self.dic):
                self.dic_index += 1
                self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        
        else:
            session.player_obj.ent.move(session.pyg.tile_width, 0)
        
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
        self.choice = self.cursor_pos[1]//32 + self.offset - 1
    
        # Move cursor to the highest spot in the dictionary
        if self.cursor_pos[1] > 32*len(self.dic):
            self.cursor_pos[1] = 32*len(self.dic)
            self.choice = len(self.dic) - self.offset - 1

    def key_ENTER(self):

        from items_entities import create_item, create_entity

        # Note location and image names
        self.img_x, self.img_y = int(session.player_obj.ent.X/session.pyg.tile_width), int(session.player_obj.ent.Y/session.pyg.tile_height)
        self.img_names[0] = self.dic_categories[self.dic_index%len(self.dic_categories)]
        self.img_names[1] = list(self.dic.keys())[(self.choice)%len(self.dic)]
        
        # Set location for drop
        if session.player_obj.ent.direction == 'front':   self.img_y += 1
        elif session.player_obj.ent.direction == 'back':  self.img_y -= 1
        elif session.player_obj.ent.direction == 'right': self.img_x += 1
        elif session.player_obj.ent.direction == 'left':  self.img_x -= 1
        
        # Place tile
        if self.img_names[0] in ['floors', 'walls', 'roofs']:
            obj = session.player_obj.ent.env.map[self.img_x][self.img_y]
            obj.placed = True
            place_object(
                obj = obj,
                loc = [self.img_x, self.img_y],
                env = session.player_obj.ent.env,
                names = self.img_names.copy())

            # Check if it completes a room
            if self.img_names[0] == 'walls':
                session.player_obj.ent.env.build_room(obj)
        
        # Place entity
        elif self.img_names[0] in session.img.ent_names:
            item = create_entity(
                names = self.img_names.copy())
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_names.copy())
        
        # Place item
        elif self.img_names[1] not in session.img.ent_names:
            item = create_item(
                names = self.img_names)
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_names.copy())
            if item.img_names[0] == 'stairs':
                item.tile.blocked = False
        
        else:
            ent = create_entity(
                names = self.img_names[1])
            place_object(
                obj   = ent,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_names.copy())
        
        self.img_x, self.img_y = None, None
        session.pyg.overlay = None

    def key_DEV(self):
        session.pyg.last_press_time = float(time.time())
        self.cursor_border = pygame.Surface((32, 32)).convert()
        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))

        # Thin cursor
        if not self.locked:
            self.locked   = True
            cursor_points = [(0, 0), (30, 0), (30, 30), (0, 30)]
            cursor_width  = 2
        
        # Thick cursor
        else:
            self.locked   = False
            cursor_points = [(0, 0), (31, 0), (31, 31), (0, 31)]
            cursor_width  = 1
        
        pygame.draw.polygon(self.cursor_border, session.pyg.white, cursor_points, cursor_width)

    def key_INV(self):
        session.pyg.overlay = 'inv'
        pygame.event.clear()

    def key_BACK(self):
        session.pyg.last_press_time = float(time.time())
        session.pyg.overlay         = None

    # Tools
    def update_data(self):

        # Update cursor
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
        self.dic    = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
        
    def update_dict(self):
        
        # Dictionary management
        self.dic_categories = list(session.player_obj.ent.discoveries.keys())
        self.dic_index = 0
        self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]] # {first name: {second name: surface}}
        while not len(self.dic):
            self.dic_index += 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        self.dic_indices = [[0, 0] for _ in self.dic_categories]

    def export_env(self):
        with open(f"Data/File_{session.player_obj.file_num}/env.pkl", 'wb') as file:
            pickle.dump(session.player_obj.ent.env, file)

    def import_env(self):

        from data_management import Camera

        try:
            with open(f"Data/File_{session.player_obj.file_num}/env.pkl", "rb") as file:
                env = pickle.load(file)
            env.camera = Camera(session.player_obj.ent)
            env.camera.update()
            place_player(
                ent = session.player_obj.ent,
                env = env,
                loc = env.player_coordinates)
        except: print("No file found!")

class AbilitiesMenu:
    
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
        self.keys            = session.pyg.key_LEFT + session.pyg.key_DOWN + session.pyg.key_RIGHT
        self.key_sequence    = []
        self.cooldown_time   = 0.5
        self.last_combo_time = 0
        
        # GUI
        self.detail = True

    def run(self):
        """ Processes input sequences while a key is held down. """
        
        # Restrict movement speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        # Generate cursor and dictionaries
        self.update_data()

        # Define shorthand
        pyg = session.pyg
        
        # Handle keystrokes
        for event in pygame.event.get():
            
            # Clear sequence after some time
            if time.time()-self.last_combo_time > self.cooldown_time:
                self.last_combo_time = time.time()
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
            if len(self.key_sequence) == 3:
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
        for effect in session.player_obj.ent.effects:
            if effect.sequence:
                inventory_dics['effects'][effect.name] = session.img.dict[effect.img_names[0]][effect.img_names[1]]
                self.sequences[effect.name] = effect.sequence
        
        # Restore last selection
        if len(self.dic_indices) != len(self.dic_categories):
            self.dic_indices = [[0, 0] for _ in self.dic_categories]
        self.dic = inventory_dics[self.dic_categories[0]]

    def check_sequence(self, sequence_string):
        
        # Look through item effects
        for effect in session.player_obj.ent.effects:
            if effect.sequence == sequence_string:
                if time.time()-effect.last_use_time > effect.cooldown_time:
                    effect.last_use_time = float(time.time())
                    effect.function()
                    return

    def render(self):
        session.pyg.msg_height = 1
        session.pyg.update_gui()
        
        session.img.average()
        color = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
        
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
                            session.pyg.minifont.render(self.menu_choices[i], True, color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        session.pyg.screen.blit(menu_choice_surface, (40, Y_cache))
                        Y_cache += 12
                
                # Render image
                session.pyg.screen.blit(self.dic[effect_name], (0, Y))
                Y += session.pyg.tile_height
                counter += 1
            
            else: break

class ExchangeMenu:

    def __init__(self):
        
        # Data for select_item and locked_item
        self.cursor_pos_bnm = [session.pyg.screen_width-session.pyg.tile_width, 32]
        self.dic_index_bnm = 0
        self.dic_categories_bnm = session.img.other_names[:-1]
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

        self.background_fade = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def run(self):
        
        # Restrict movement speed
        session.mech.movement_speed(toggle=False, custom=2)
        
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
            self.recipient         = session.player_obj.ent
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
            self.recipient         = session.player_obj.ent
            self.cursor_fill_jkl   = self.cursor_fill
            self.cursor_border_jkl = self.cursor_border
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                ## >>PLAY GAME<<
                if (event.key in session.pyg.key_BACK) or (event.key in session.pyg.key_HOLD):
                    if time.time()-session.pyg.last_press_time > self.cooldown_time:
                        session.pyg.last_press_time = float(time.time())
                        session.pyg.overlay = None
                        return
                
                ## >>SWITCH<<
                elif event.key in session.pyg.key_INV: self.menu_toggle = 'left'
                elif event.key in session.pyg.key_DEV: self.menu_toggle = 'right'    
                
                ## >>NAVIGATE DICTIONARY<<
                elif event.key in session.pyg.key_UP:
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        self.choice_bnm = (self.choice_bnm - 1)%len(self.dic_bnm)
                        if self.cursor_pos_bnm[1] == 32: self.offset_bnm -= 1
                        else: self.cursor_pos_bnm[1] -= session.pyg.tile_height
                    
                    # Navigate player's inventory
                    else:
                        self.choice = (self.choice - 1)%len(self.dic)
                        if self.cursor_pos[1] == 32: self.offset -= 1
                        else: self.cursor_pos[1] -= session.pyg.tile_height
                
                elif event.key in session.pyg.key_DOWN:
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        self.choice_bnm = (self.choice_bnm + 1)%len(self.dic_bnm)
                        if self.cursor_pos_bnm[1] >= (min(len(self.dic_bnm), 12) * 32): self.offset_bnm += 1
                        else: self.cursor_pos_bnm[1] += session.pyg.tile_height
                    
                    # Navigate player's inventory
                    else:
                        self.choice = (self.choice + 1)%len(self.dic)
                        if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
                        else: self.cursor_pos[1] += session.pyg.tile_height
                
                ## >>CHANGE DICTIONARY<<
                elif (event.key in session.pyg.key_LEFT) or (event.key in session.pyg.key_RIGHT):
                
                    if event.key in session.pyg.key_LEFT:
                        if self.menu_toggle == 'right': self.dic_index_bnm = (self.dic_index_bnm - 1)%len(self.dic_indices_bnm)
                        else:                           self.dic_index     = (self.dic_index - 1)%len(self.dic_indices)
                    
                    elif event.key in session.pyg.key_RIGHT:
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
                            session.pyg.overlay = None
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
                            session.pyg.overlay = None
                            return
                
                ## >>DETAILS<<
                elif event.key in session.pyg.key_QUEST:
                    if not self.detail: self.detail = True
                    else:               self.detail = False
                
                ## >>SELECT<<
                elif event.key in session.pyg.key_ENTER:
                    self.select()
            
            # Save for later reference
            if self.menu_toggle == 'right':
                if self.dic_indices_bnm:
                    self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0] = self.offset_bnm
                    self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1] = self.choice_bnm
                else:
                    session.pyg.overlay = None
                    return
            else:
                if self.dic_indices:
                    self.dic_indices[self.dic_index%len(self.dic_indices)][0] = self.offset
                    self.dic_indices[self.dic_index%len(self.dic_indices)][1] = self.choice
                else:
                    session.pyg.overlay = None
                    return
        
        session.pyg.overlay = 'trade'
        return

    def update_data(self):
        
        # Restrict movement speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Dictionaries
        # Left dictionary
        self.inventory_dics = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        for key, value in session.player_obj.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics[key][item.name] = [session.img.dict[item.img_names[0]][item.img_names[1]], item]
        self.inv_dics = {}
        for key, value in self.inventory_dics.items():
            if value: self.inv_dics[key] = value
        
        # Right dictionary
        self.inventory_dics_bnm = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        for key, value in self.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics_bnm[key][item.name] = [session.img.dict[item.img_names[0]][item.img_names[1]], item]
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
            session.pyg.overlay = None
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
            session.pyg.overlay = None
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
            recipient = session.player_obj.ent
            index     = self.dic_indices_bnm[self.dic_index_bnm%len(self.inv_dics_bnm)][1]
            item      = list(self.dic_bnm.values())[index][1]
        else:
            owner     = session.player_obj.ent
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
        session.pyg.screen.blit(self.background_fade, (0, 0))
        
        # Basics
        session.pyg.msg_height = 1
        session.pyg.update_gui()
        
        # Cursor background and font colors
        session.img.average()
        if self.menu_toggle == 'right':
            left_color  = pygame.Color(session.img.left_correct - 20, session.img.left_correct - 20, session.img.left_correct - 20)
            right_color = pygame.Color(session.img.right_correct, session.img.right_correct, session.img.right_correct)
            session.pyg.screen.blit(self.cursor_fill_bnm, self.cursor_pos_bnm)
        else:
            left_color  = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
            right_color = pygame.Color(session.img.right_correct - 20, session.img.right_correct - 20, session.img.right_correct - 20)
            session.pyg.screen.blit(self.cursor_fill, self.cursor_pos)
        
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
                        self.menu_choices_surfaces.append(session.pyg.minifont.render(self.menu_choices[i], True, left_color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        session.pyg.screen.blit(menu_choice_surface, (40, Y_detail))
                        Y_detail += 12
                
                # Render image
                session.pyg.screen.blit(self.dic[item_name][0], (0, Y))
                Y += session.pyg.tile_height
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
                        self.menu_choices_surfaces.append(session.pyg.minifont.render(self.menu_choices[i], True, right_color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        X = session.pyg.screen_width - session.pyg.tile_width - menu_choice_surface.get_width() - 8
                        session.pyg.screen.blit(menu_choice_surface,  (X, Y_detail))
                        Y_detail += 12
                
                # Render image
                session.pyg.screen.blit(self.dic_bnm[item_name][0],  (session.pyg.screen_width-session.pyg.tile_width, Y))
                Y += session.pyg.tile_height
                counter += 1                
            else: break
        
        if self.menu_toggle == 'right': session.pyg.screen.blit(self.cursor_border_bnm, self.cursor_pos_bnm)
        else:                           session.pyg.screen.blit(self.cursor_border,     self.cursor_pos)

########################################################################################################################################################
# Environments
def place_objects(env, items, entities):
    """ Places entities and items according to probability and biome.

        Parameters
        ----------
        env      : Environment object; location to be placed
        items    : list of lists; [[<biome str>, <object str>, <unlikelihood int>], ...]
        entities :  """
    
    from utilities import is_blocked
    from items_entities import create_item, create_entity

    # Sort through each tile
    for y in range(len(env.map[0])):
        for x in range(len(env.map)):
            
            # Check that the space is not already occupied
            if not is_blocked(env, [x, y]):

                ## Randomly select and place an item
                selection = random.choice(items)
                
                # Check that the object matches the biome
                if env.map[x][y].biome in session.img.biomes[selection[0]]:
                    if not random.randint(0, selection[2]) and not env.map[x][y].item:
                        
                        ## Place object
                        item = create_item(selection[1])
                        place_object(item, [x, y], env)
                
                ## Randomly select and place an entity
                selection = random.choice(entities)
                
                # Check that the entity matches the biome
                if env.map[x][y].biome in session.img.biomes[selection[0]]:
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

def place_object(obj, loc, env, names=None):
    """ Places a single object in the given location.

        Parameters
        ----------
        obj   : class object in [Tile, Item, Entity]; object to be placed
        loc   : list of int; tile coordinates
        env   : Environment object; desired location
        names : list of str; Image dictionary names """  
      
    from environments import Tile

    # Place tile
    if type(obj) == Tile:
        env.map[loc[0]][loc[1]].img_names = names
        
        # Set properties
        if names[1] in session.img.biomes['sea']:
            env.map[loc[0]][loc[1]].biome   = 'water'
        elif names[0] in ['walls']:
            env.map[loc[0]][loc[1]].blocked = True
            env.map[loc[0]][loc[1]].item    = None
        else:
            env.map[loc[0]][loc[1]].blocked = False
    
    # Place item
    elif type(obj) == Item:
        obj.X    = loc[0] * session.pyg.tile_width
        obj.X0   = loc[0] * session.pyg.tile_width
        obj.Y    = loc[1] * session.pyg.tile_height
        obj.Y0   = loc[1] * session.pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].item = obj
        if obj.blocked:
            env.map[loc[0]][loc[1]].blocked = True
    
    # Place entity
    elif type(obj) == Entity:
        obj.X    = loc[0] * session.pyg.tile_width
        obj.X0   = loc[0] * session.pyg.tile_width
        obj.Y    = loc[1] * session.pyg.tile_height
        obj.Y0   = loc[1] * session.pyg.tile_height
        obj.env  = env
        obj.tile = env.map[loc[0]][loc[1]]
        env.map[loc[0]][loc[1]].entity = obj
        env.entities.append(obj)

def place_player(ent, env, loc):
    """ Sets player in a new position.

        Parameters
        ----------
        env : Environment object; new environment of player
        loc : list of integers; new location of player in tile coordinates """
    
    from utilities import check_tile

    if not ent.dead:
        
        # Remove extra motions and animations
        pygame.event.clear()
        session.img.render_log = []
        
        # Remove from current location
        if ent.env:
            if ent.env.name != env.name:
                ent.last_env = ent.env
            ent.env.player_coordinates = [ent.X//32, ent.Y//32]
            ent.env.entities.remove(ent)
            ent.tile.entity = None
            ent.tile = None

        # Set current environment and tile
        ent.env  = env
        ent.tile = ent.env.map[loc[0]][loc[1]]
        ent.X    = loc[0] * session.pyg.tile_width
        ent.X0   = loc[0] * session.pyg.tile_width
        ent.Y    = loc[1] * session.pyg.tile_height
        ent.Y0   = loc[1] * session.pyg.tile_height
        ent.toggle_effects()
        
        # Set time and date
        if ent.env.name in ['home', 'overworld', 'cave']:
            if ent.last_env.name in ['home', 'overworld', 'cave']:
                ent.env.env_date = ent.last_env.env_date
                ent.env.env_time = ent.last_env.env_time

        # Notify environment of player position
        ent.env.entities.append(ent)
        ent.tile.entity = ent
        check_tile(loc[0], loc[1], ent=ent, startup=True)
        
        # Update camera
        if not env.camera.fixed:
            env.camera.update()
            ent.env.camera.zoom_in()
            ent.env.camera.zoom_out()
        
        # Render
        time.sleep(0.5)
        session.pyg.update_gui(ent=ent)
        
        # Change song
        if ent.env.name != ent.last_env.name:
            session.aud.control(soundtrack=env.soundtrack)

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
    
    from items_entities import create_item

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

########################################################################################################################################################
# Other
def floor_effects(floor_effect):
    if floor_effect:
        if floor_effect == 'damage':
            session.player_obj.ent.take_damage(10)

def active_effects():
    """ Applies effects from items and equipment. Runs constantly. """
    
    ent = session.player_obj.ent

    # Check for equipment
    if ent.equipment['dominant hand']:     hand_1 = session.player_obj.ent.equipment['dominant hand']
    else:                                  hand_1 = None
    if ent.equipment['non-dominant hand']: hand_2 = session.player_obj.ent.equipment['non-dominant hand']
    else:                                  hand_2 = None
    
    # Apply dominant hand function
    if hand_1:
        if hand_1.name == 'super shovel': ent.super_dig = True
        else:                             ent.super_dig = False
    
    # Apply non-dominant hand function
    if hand_2:
        if hand_2.effect.name == 'lamp':
            hand_2.effect.function(hand_2)

def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    
    level_up_exp = session.mech.level_up_base + session.player_obj.ent.rank * session.mech.level_up_factor
    if session.player_obj.ent.exp >= level_up_exp:
        session.player_obj.ent.rank += 1
        session.player_obj.ent.exp -= level_up_exp
        
        dialogue = [
            "You feel stronger.",
            "Flow state!",
            "Resilience flows through you."]
        session.pyg.update_gui(random.choice(dialogue), session.pyg.gray)

        session.player_obj.ent.rank += 1
        session.player_obj.ent.max_hp += 20
        session.player_obj.ent.hp += 20
        session.player_obj.ent.attack += 1
        session.player_obj.ent.defense += 1
        session.pyg.update_gui()

########################################################################################################################################################