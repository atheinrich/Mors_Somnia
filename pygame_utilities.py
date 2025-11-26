########################################################################################################################################################
# Utilities
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import time
import copy

## Specific
import pygame
from   pygame.locals import *
from   PIL import Image, ImageFilter, ImageOps

## Local
import session
from data_management import img_dicts, biome_dicts, find_path

########################################################################################################################################################
# Classes
class Pygame:

    def __init__(self):
        """ Manages pygame parameters, GUI details, and display transitions. Nothing here is saved elsewhere.
            
            There are four main surfaces that render in order.
                1) Display: Tiles, entities, items, etc.
                2) Overlay: Menus, inventories, questlogs, etc.
                3) Fade:    Black screen, narrative, logos, etc.
                5) Screen:  Final output of all prior surfaces.
        """

        #########################################################
        # Start pygame
        pygame.init()
        pygame.key.set_repeat(250, 150)
        pygame.display.set_caption("Mors Somnia")

        #########################################################
        # Shorthand and gameplay parameters
        self.set_graphics()
        self.set_controls('numpad 1')
        self.set_colors()
        
        #########################################################
        # Screens
        self.init_screen()
        self.init_display()
        self.init_hud()
        self.init_overlay()
        self.init_fade()

        #########################################################
        # Utility
        self._subscribe_events()
        self.pause = False
        self.startup_toggle  = True
        self.cooldown_time   = 0.2
        self.last_press_time = 0

    # Screens
    def init_screen(self):
        """ Final window that everything is shown on. """
        
        self.screen   = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        self.windowed = False
        self.font     = pygame.font.SysFont('segoeuisymbol', 16, bold=True)
        self.minifont = pygame.font.SysFont('segoeuisymbol', 14, bold=True)
        self.clock    = pygame.time.Clock()

    def init_display(self):
        """ World pieces, like environment tiles and entities. """
        
        self.display       = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.game_state    = 'startup'
        self.display_queue = []

    def init_hud(self):
        """ Status bars, time, and messages/dialogue. """
        
        self.hud       = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.hud_state = 'off'
        self.hud_queue = []
        
        self.msg = []  # list of font objects; messages to be rendered
        self.gui = {
            'health':   self.font.render('', True, self.red),
            'stamina':  self.font.render('', True, self.green),
            'location': self.font.render('', True, self.gray)}
        
        self.msg_toggle  = True  # bool; shows or hides messages
        self.gui_toggle  = True  # bool; shows or hides GUI
        self.msg_height  = 4     # number of lines shown
        self.msg_width   = int(self.screen_width / 6)
        self.msg_history = {}

    def init_overlay(self):
        """ Menus and action bars. """
        
        self.overlays      = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.overlay_state = 'menu'
        self.overlay_queue = []

    def init_fade(self):
        """ Black surface of variable opacity, overlaid text, and background functions. """
        
        self.fade          = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.fade_surface  = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.fade_state    = 'in'
        self.fade_queue    = []
        self.fade_cache    = []
        self.fn_queue      = []

        self.fade_speed    = 5
        self.fade_delay    = 0
        self.max_alpha     = 255
        self.min_alpha     = 0
        self.fade_alpha    = 255

    # Gameplay settings and shorthand
    def set_controls(self, controls):
        
        #########################################################
        # Change control scheme
        self.controls_preset = controls
        
        #########################################################
        # Define control schemes
        ## Extended
        if controls == 'arrows':
            
            # Movement
            self.key_UP       = ['↑', K_UP,    K_w]
            self.key_DOWN     = ['↓', K_DOWN,  K_s]
            self.key_LEFT     = ['←', K_LEFT,  K_a]
            self.key_RIGHT    = ['→', K_RIGHT, K_d]
            
            # Actions
            self.key_BACK     = ['/', K_BACKSPACE, K_ESCAPE,  K_SLASH, K_KP_DIVIDE]
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY, K_a]
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]
            self.key_PERIOD   = ['.', K_KP_PERIOD, K_DELETE]
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS, K_EQUALS]
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]
            self.key_HOLD     = ['0', K_0, K_KP0]
            
            # Menus
            self.key_INV      = ['4', K_4, K_KP4]
            self.key_DEV      = ['6', K_6, K_KP6]
            self.key_INFO     = ['7', K_7, K_KP7]
            self.key_SPEED    = ['8', K_8, K_KP8]
            self.key_QUEST    = ['9', K_9, K_KP9]
            
            # Other
            self.key_EQUIP    = ['2', K_2, K_KP2]
            self.key_DROP     = ['3', K_3, K_KP3]

        ## Alternate 1
        elif controls == 'numpad 1':
            
            # Movement
            self.key_UP       = ['5', K_5, K_KP5,  K_UP]
            self.key_DOWN     = ['2', K_2, K_KP2,  K_DOWN]
            self.key_LEFT     = ['1', K_1, K_KP1,  K_LEFT]
            self.key_RIGHT    = ['3', K_3, K_KP3,  K_RIGHT]

            # Actions
            self.key_BACK     = ['/', K_SLASH,     K_KP_DIVIDE]
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY, K_a]
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]
            self.key_PERIOD   = ['.', K_KP_PERIOD, K_DELETE]
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS, K_EQUALS]
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]
            self.key_HOLD     = ['0', K_0, K_KP0]
            
            # Menus
            self.key_INV      = ['4', K_4, K_KP4]
            self.key_DEV      = ['6', K_6, K_KP6]
            self.key_INFO     = ['7', K_7, K_KP7]
            self.key_SPEED    = ['8', K_8, K_KP8]
            self.key_QUEST    = ['9', K_9, K_KP9]
            
            # Unused
            self.key_EQUIP    = []
            self.key_DROP     = []

        # Alternate 2
        elif controls == 'numpad 2':
            
            # Movement
            self.key_UP       = ['8', K_8, K_KP8,  K_UP]
            self.key_DOWN     = ['5', K_5, K_KP5,  K_DOWN]
            self.key_LEFT     = ['4', K_4, K_KP4,  K_LEFT]
            self.key_RIGHT    = ['6', K_6, K_KP6,  K_RIGHT]

            # Actions
            self.key_BACK     = ['/', K_SLASH,     K_KP_DIVIDE]
            self.key_GUI      = ['*', K_ASTERISK,  K_KP_MULTIPLY, K_a]
            self.key_ENTER    = ['↲', K_RETURN,    K_KP_ENTER]
            self.key_PERIOD   = ['.', K_KP_PERIOD, K_DELETE]
            self.key_PLUS     = ['+', K_PLUS,      K_KP_PLUS, K_EQUALS]
            self.key_MINUS    = ['-', K_MINUS,     K_KP_MINUS]
            self.key_HOLD     = ['0', K_0, K_KP0]
            
            # Menus
            self.key_INV      = ['7', K_7, K_KP7]
            self.key_DEV      = ['9', K_9, K_KP9]
            self.key_INFO     = ['1', K_1, K_KP1]
            self.key_SPEED    = ['2', K_2, K_KP2]
            self.key_QUEST    = ['3', K_3, K_KP3]
            
            # Unused
            self.key_EQUIP    = []
            self.key_DROP     = []

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

    # HUD tools
    def textwrap(self, text, width):
        """ Separates long chunks of text into consecutive lines. """
        
        #########################################################
        # Initialize
        words        = text.split()
        lines        = []
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

    def update_gui(self, text=None, color=None, ent=None):
        """ Constructs (but does not render) messages in the top GUI and stats in the bottom GUI.

            Parameters
            ----------
            text  : str; text added to top GUI
            color : pygame Color; color of new message
            ent   : Entity object; only specified at startup

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
        if text:
            for line in pyg.textwrap(text, pyg.msg_width):

                # Only show a message once
                if line in self.msg_history.keys():
                    del self.msg_history[line]
                self.msg_history[line] = color

        ## Find which messages to display
        index               = len(self.msg_history) - self.msg_height
        if index < 0: index = 0
        lines  = list(self.msg_history.keys())[index:]
        colors = list(self.msg_history.values())[index:]

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
        time = ent.env.weather.symbols[ent.env.env_time]
        
        ## Construct dictionary for display
        if pyg.overlay_state:
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

    def _subscribe_events(self):
        session.bus.subscribe('emit_message', self.update_gui)

    # Fade tools
    def update_fade(self):
        """ Update the fade's alpha each frame and queues the intertitle with effects.
            Pauses the game while the fade is ongoing.
            
            A fadein/fadeout is triggered by setting fade_state. Intertitles are held in fade_cache and
            sent to fade_queue until the fadeout is complete. Functions to be delayed are held in fn_queue
            and run in main after the fadein is complete.

            Example
            -------
            pyg.add_intertitle("This is shown over a black screen.")
            pyg.fn_queue.append([function_in_background,  {}])
            pyg.fn_queue.append([function_with_arguments, {'parameter_name': value}])
            pyg.fade_delay = 400
            pyg.fade_state = 'out'
        """

        # Update alpha
        if self.fade_state != 'off':
            self.pause = True
            self.fade_surface.fill((0, 0, 0))
            
            #########################################################
            # Fade in from black
            if self.fade_state == 'in':

                # Change alpha
                if self.fade_delay >= 0: self.fade_delay -= self.fade_speed
                else:                    self.fade_alpha -= self.fade_speed

                # End fade
                if self.fade_alpha <= self.min_alpha:
                    self.fade_alpha = self.min_alpha

                    self.fade_cache = []
                    self.pause      = False
                    self.fade_state = 'off'
            
            #########################################################
            # Fade out to black
            elif self.fade_state == 'out':

                # Change alpha
                if self.fade_delay >= 0: self.fade_delay -= self.fade_speed
                else:                    self.fade_alpha += self.fade_speed

                # End fade
                if self.fade_alpha >= self.max_alpha:
                    self.fade_alpha = self.max_alpha

                    self.fade_state = 'on'

            #########################################################
            # Run functions while holding a black screen
            elif self.fade_state == 'on':
                
                # Check current time
                start_time = time.time()

                # Process functions in queue
                while self.fn_queue:
                    function, kwargs = self.fn_queue.pop(0)
                    function(**kwargs)
                self.fade_state = 'in'

                # Hold text for at least 3 seconds, including run time
                remaining_time = 4 - (time.time() - start_time)
                if remaining_time > 0: time.sleep(remaining_time)

            #########################################################
            # Update surfaces
            self.fade_surface.set_alpha(self.fade_alpha)
            self.fade_queue.append([self.fade_surface, (0, 0)])

            #if self.fade_alpha >= self.max_alpha * 0.8:
            for (surface, loc) in self.fade_cache:

                # Set flicker effect
                flicker_low  = max(self.fade_alpha-100, self.min_alpha)
                flicker_high = min(self.fade_alpha,     self.max_alpha-100)

                surface.set_alpha(random.randint(flicker_low, flicker_high))
                self.fade_queue.append([surface, loc])

    def add_intertitle(self, text=None, surface=None, loc='centered'):
        
        if text: surface = self.font.render(text, True, self.white)
        else:    surface = copy.copy(surface)

        if loc == 'centered':
            X = int((self.screen_width - surface.get_width())/2)
            Y = int((self.screen_height - surface.get_height())/2)
            loc = (X, Y)
        
        self.fade_cache.append([surface, loc])

# Needs updating
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
            
            biomes       : dict; set of biome names and associated region_id list 

            Alternates
            ----------
            flipped.<>   : flipped version of the parameters """

        pyg = session.pyg

        # Create entity dictionary
        self.ent, self.ent_data, skin_options = self.load_entities(flipped)
        self.skin_options  = skin_options
        
        # Create equipment dictionary
        self.equip, self.equip_names, equipment_options = self.load_equipment(flipped)
        self.hair_options  = equipment_options['hair']
        self.face_options  = equipment_options['face']
        self.chest_options = equipment_options['chest']
        self.armor_names   = equipment_options['armor']
        
        # Create other dictionary
        self.other, self.other_names = self.load_other(flipped)
        self.other_alt, _            = self.load_other(flipped, alt=True)
        
        # Create combined dictionary
        self.dict = self.ent | self.equip | self.other
        
        self.big = self.big_img()

        # Assign tiles to biomes
        self.biomes = self.load_biomes()

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
        path       = find_path(f'Data/.Images/tileset_ent.png')
        ent_matrix = self.import_tiles(path, flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        entity_options = ['front', 'back', 'left', 'right']

        # Identify character creation options
        img_ents_dict = copy.deepcopy(img_dicts['img_ents'])
        ent_data      = {}
        skin_options  = []

        for key, dict in img_ents_dict.items():
            if dict['slot'] != None:
                skin_options.append(key)
            ent_data[key] = {keys: dict[keys] for keys in dict.keys() if keys != 'slot'}

        # Create image dictionary
        ent_images = {key: None for key in ent_data.keys()}
        index = 0
        for entity_name in ent_images:
            ent_images[entity_name] = {option: image for (option, image) in zip(entity_options, ent_matrix[index])}
            if flipped:
                cache = ent_images[entity_name]['right']
                ent_images[entity_name]['right'] = ent_images[entity_name]['left']
                ent_images[entity_name]['left'] = cache
            index += 1

        return ent_images, ent_data, skin_options

    def load_equipment(self, flipped):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """

        # Import tiles
        path         = find_path(f'Data/.Images/tileset_equip.png')
        equip_matrix = self.import_tiles(path, flipped=flipped, effects=['posterize'])
        
        # Define tile names and options
        equip_options = ['dropped', 'front', 'back', 'left', 'right']
        equip_aliases = {
            'clean': 'null',
            'flat':  'null',
            'bald':  'null'}

        # Identify character creation options
        img_equipment_dict = copy.deepcopy(img_dicts['img_equipment'])
        equip_names        = []
        equipment_options  = {
            'hair':  ['bald'],
            'face':  ['clean'],
            'chest': ['flat'],
            'armor': []}

        for key, dict in img_equipment_dict.items():
            if dict['slot'] is not None:
                equipment_options[dict['slot']].append(key)
            equip_names.append(key)

        # Create image dictionary
        equip = {key: None for key in equip_names}
        index = 0
        for _ in equip_names:
            equip[equip_names[index]] = {option: image for (option, image) in zip(equip_options, equip_matrix[index])}
            if flipped:
                cache = equip[equip_names[index]]['right']
                equip[equip_names[index]]['right'] = equip[equip_names[index]]['left']
                equip[equip_names[index]]['left'] = cache
            index += 1
        
        for key, val in equip_aliases.items():
            equip[key] = equip[val]

        return equip, equip_names, equipment_options
        
    def load_other(self, flipped=False, alt=False):
        """ Imports tiles, defines tile names, creates image dictionary, and provides image count. """
        
        # Choose tileset
        if alt: path = find_path(f'Data/.Images/tileset_other_alt.png')
        else:   path = find_path(f'Data/.Images/tileset_other.png')
        
        # Import tiles
        other_matrix = self.import_tiles(path, flipped=flipped, effects=['posterize'])

        # Identify character creation options
        img_other_dict = copy.deepcopy(img_dicts['img_other'])
        other = {}

        for key, dict in img_other_dict.items():
            if dict['group'] not in other.keys():
                other[dict['group']] = []
            other[dict['group']].append(key)
        other_names = list(other.keys())

        decor_options     = other['decor']
        bubbles_options   = other['bubbles']
        furniture_options = other['furniture']
        drugs_options     = other['drugs']
        potions_options   = other['potions']
        scrolls_options   = other['scrolls']
        stairs_options    = other['stairs']
        floors_options    = other['floors']
        walls_options     = other['walls']
        roofs_options     = other['roofs']
        paths_options     = other['paths']
        concrete_options  = other['concrete']
        null_options      = other['null']

        other_options = [
            decor_options,  bubbles_options, furniture_options,
            drugs_options,  potions_options, scrolls_options,
            stairs_options, floors_options,  walls_options,
            roofs_options,  paths_options,   concrete_options, 
            null_options]
        
        # Create image dictionary
        for i in range(len(other_names)):
            other[other_names[i]] = {option: image for (option, image) in zip(other_options[i], other_matrix[i])}

        return other, other_names

    def big_img(self):
    
        # Import tiles
        path = find_path(f'Data/.Images/logo.png')
        big  = self.import_tiles(path, flipped=False, effects=['posterize'])
        return big

    def load_biomes(self):
        
        biomes = {}

        for key, dict in biome_dicts.items():
            if dict['habitats'] is not None:
                biomes[key] = copy.deepcopy(dict['habitats'])
        
        return biomes

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

    def halved(self, img_IDs, flipped=False):
        
        if flipped: image = self.flipped.dict[img_IDs[0]][img_IDs[1]]
        else:       image = self.dict[img_IDs[0]][img_IDs[1]]
        
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

        from mechanics import get_vicinity
        
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

        shift = 32 - self.ent_data[ent.img_IDs[0]]['height']
        
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

# Needs updating/fixing
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

class EventBus:

    def __init__(self):
        """ Accepts event information, holds functions tied to events, and calls the functions if events match. """
        self.listeners = {}

    def subscribe(self, event_id, function):
        """ Adds a new function to be called when the given event type occurs. """
        self.listeners.setdefault(event_id, []).append(function)

    def emit(self, event_id, **kwargs):
        """ Accepts an event flag and calls any functions with a matching event. """
        for function in self.listeners.get(event_id, []):
            function(**kwargs)

    def clear(self):
        self.listeners = {}

########################################################################################################################################################
# Tools
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
    pyg = session.pyg
    
    for (surface, pos) in pyg.display_queue:
        pyg.display.blit(surface, pos)
    display = pygame.transform.scale(
        pyg.display, (pyg.screen_width, pyg.screen_height))
    
    # Extract screen as image
    raw_str = pygame.image.tostring(display, 'RGB')
    image   = Image.frombytes('RGB', display.get_size(), raw_str)
    
    # Apply PIL effects
    image = image.convert('L')
    
    # Apply numpy effects
    image = np.array(image)
    image = np.where(image > 50, 255, 0)
    image = image.T
    image = np.stack([image] * 3, axis=-1)
    image = pygame.surfarray.make_surface(image)
    
    session.pyg.display_queue = [[image, (0, 0)]]

def render_display():
    """ Adds tiles, entities, items, etc to the queue for rendering. """
    
    pyg = session.pyg

    #########################################################
    # Initialize
    ## Select entity to focus on
    if pyg.overlay_state == 'new_game':
        ent = session.new_game_obj.temp_obj.ent
        session.player_obj.ent.env.camera.zoom_in(custom=1)
    
    else:
        ent = session.player_obj.ent

    ## Shorthand
    camera = ent.env.camera

    #########################################################
    # Draw visible tiles
    for y in range(int(camera.Y/32), int(camera.bottom/pyg.tile_height + 1)):
        for x in range(int(camera.X/32), int(camera.right/pyg.tile_width + 1)):
            try:    tile = ent.env.map[x][y]
            except: continue
            if not tile.hidden:
                
                # First tier (floor or walls)
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
                if tile.ent:
                    tile.ent.draw()
                    
                    # Effects
                    if tile.ent.active_effects:
                        for effect in tile.ent.active_effects.values():
                            if effect.trigger == 'on_render':
                                effect.activate()
                
                # Fourth tier (effects)
                if tile.active_effects:
                    for effect in tile.active_effects.values():
                        if effect.trigger == 'on_render':
                            effect.activate()
                
                # Fifth tier (roof)
                if tile.room:
                    if tile.room.roof_img_IDs == tile.img_IDs:
                        image, (X, Y) = tile.draw()
                        pyg.display_queue.append([image, (X, Y)])

    
    ent.env.weather.render()

    if session.img.render_fx == 'bw_binary': bw_binary()

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