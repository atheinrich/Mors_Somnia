########################################################################################################################################################
# Utilities
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import pygame
from   pygame.locals import *
import time
import pickle
import copy
from PIL import Image, ImageFilter, ImageOps
from pypresence import Presence
import sys

## Modules
import session
from main import render_all
from items_entities import Player
from mechanics import place_player

########################################################################################################################################################
# Classes
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
        self.blank_surface     = pygame.Surface((session.pyg.tile_width, session.pyg.tile_height)).convert()
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
        num_rows     = tileset.get_height() // session.pyg.tile_height
        num_columns  = tileset.get_width() // session.pyg.tile_width
        tile_matrix  = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
        for row in range(num_rows):
            for col in range(num_columns):
                
                # Find location of image in tileset
                X = col * session.pyg.tile_width
                Y = row * session.pyg.tile_height
                if flipped:
                    image = pygame.transform.flip(tileset.subsurface(X, Y, session.pyg.tile_width, session.pyg.tile_height).convert_alpha() , True, False)
                else:
                    image = tileset.subsurface(X, Y, session.pyg.tile_width, session.pyg.tile_height).convert_alpha()
                
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
        top_rect     = pygame.Rect(0, 0, session.pyg.screen_width, 50)
        bottom_rect  = pygame.Rect(0, session.pyg.screen_height-50, session.pyg.screen_width, 50)
        left_rect    = pygame.Rect(50, 50, 50, 50)
        right_rect   = pygame.Rect(session.pyg.screen_width-100, 50, 50, 50)
        menu_rect    = pygame.Rect(100, session.pyg.screen_height-100, 50, 50)
        
        self.top_color    = pygame.transform.average_color(session.pyg.screen, rect=top_rect,    consider_alpha=False)
        self.bottom_color = pygame.transform.average_color(session.pyg.screen, rect=bottom_rect, consider_alpha=False)
        self.left_color   = pygame.transform.average_color(session.pyg.screen, rect=left_rect,   consider_alpha=False)
        self.right_color  = pygame.transform.average_color(session.pyg.screen, rect=right_rect,  consider_alpha=False)
        self.menu_color   = pygame.transform.average_color(session.pyg.screen, rect=menu_rect,   consider_alpha=False)
        
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
        
        color = (230, 230, 230)
        self.impact_image = pygame.Surface((session.pyg.tile_width, session.pyg.tile_width)).convert()
        self.impact_image.set_colorkey(self.impact_image.get_at((0,0)))
        image = pygame.Surface((int(session.pyg.tile_width/2), int(session.pyg.tile_height/3))).convert()
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
        
        short_list = ['red radish', 'orange radish', 'purple radish']
        if ent.name in short_list: shift = 12
        else:                      shift = 0
        
        self.impact = True
        
        image     = image
        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - session.pyg.tile_height - session.player_obj.ent.env.camera.Y + shift
        image_pos = (x, y)
        duration  = 0.8
        delay     = 0
        last_time = time.time()
        self.render_log.append([image, image_pos, duration, last_time, delay])

        x         = lambda: ent.X - session.player_obj.ent.env.camera.X
        y         = lambda: ent.Y - session.pyg.tile_height - session.player_obj.ent.env.camera.Y + shift
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
                        session.pyg.display.blit(image, position)
                        
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

class FileMenu:

    def __init__(self, name, header, options, options_categories=None, position='top left', backgrounds=None):
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
        self.backgrounds        = backgrounds
        
        # Temporary data containers
        self.choice                   = 0                   # holds index of option pointed at by cursor
        self.choices_length           = len(self.options)-1 # number of choices
        self.options_categories_cache = ''                  # holds current category
        self.options_render           = self.options.copy()
        
        # Cursor and text positions
        self.set_positions()
        self.tab_x = 0
        self.tab_y = 0
        
        # Cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0,0)))
        pygame.draw.polygon(self.cursor_img, session.pyg.green, [(0, 0), (16, 8), (0, 16)], 0)
        
        # Menu options
        self.header_render = session.pyg.font.render(self.header, True, session.pyg.white)
        for i in range(len(self.options)):
            color = session.pyg.gray
            self.options_render[i] = session.pyg.font.render(options[i], True, color)
        
        # Backgrounds
        if self.backgrounds:
            self.backgrounds_render = copy.copy(self.backgrounds)
            for i in range(len(self.backgrounds)):
                self.backgrounds_render[i] = pygame.image.load(self.backgrounds[i]).convert()

    def set_positions(self):
        
        # Alter layout if categories are present
        if self.options_categories: 
            self.tab_x, self.tab_y = 70, 10
            self.options_categories_cache_2 = self.options_categories[0]
        else:
            self.tab_x, self.tab_y = 0, 0

        # Set initial position of each text type
        self.header_position = {
            'top left':     [5, 10],
            'center':       [int((session.pyg.screen_width - session.main_menu_obj.game_title.get_width())/2), 85],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        
        self.cursor_position = {
            'top left':     [50+self.tab_x, 38+self.tab_y],
            'center':       [50, 300],
            'bottom left':  [50+self.tab_x, 65-self.tab_y],
            'bottom right': [60 ,70]}
        
        self.options_positions = {
            'top left':     [80+self.tab_x, 34],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        
        self.category_positions = {
            'top left':     [5,  34],
            'center':       [80, 300],
            'bottom left':  [5,  10],
            'bottom right': [60, 70]}

        # Set mutable copies of text positions
        self.cursor_position_mutable    = self.cursor_position[self.position].copy()
        self.options_positions_mutable  = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()

    def reset(self, name, header, options, options_categories, position, backgrounds):
        self.__init__(self.name, self.header, self.options, self.options_categories, self.position, self.backgrounds)

    def run(self):
        
        session.mech.movement_speed(toggle=False, custom=2)
        session.mech.zoom_cache = 1
        
        # Called when the user inputs a command
        for event in pygame.event.get():
            
            if event.type == KEYDOWN:
                
                # Navigation
                if event.key in session.pyg.key_UP:       self.key_UP()
                elif event.key in session.pyg.key_DOWN:   self.key_DOWN()
                elif event.key in session.pyg.key_LEFT:
                    if self.name == 'session.ctrl_menu':  self.set_controls('left')
                elif event.key in session.pyg.key_RIGHT:
                    if self.name == 'session.ctrl_menu':  self.set_controls('right')
                
                # Process selection or return to main menu
                elif event.key in session.pyg.key_ENTER:
                    
                    if self.name == 'save':
                        self.save_account()
                    elif self.name == 'load':
                        self.load_account()
                    
                    session.pyg.overlay = 'menu'
                    return

                # >>RESUME<<
                else:
                    if time.time()-session.pyg.last_press_time > session.pyg.cooldown_time:
                        session.pyg.last_press_time = float(time.time())
                        session.pyg.overlay = 'menu'
                        return None
                
        session.pyg.overlay = copy.copy(self.name)
        return

    def key_UP(self):
        
        # Move cursor up
        self.cursor_position_mutable[1] -= 24
        self.choice                     -= 1
        
        # Move to lowest option
        if self.choice < 0:
            self.choice                     = self.choices_length
            self.cursor_position_mutable[1] = self.cursor_position[self.position][1] + (len(self.options)-1) * 24
            if self.options_categories:
                self.cursor_position_mutable[1] += self.tab_y * (len(set(self.options_categories)) - 1)
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] -= self.tab_y

    def key_DOWN(self):
        
        # Move cursor down
        self.cursor_position_mutable[1] += 24
        self.choice                     += 1
        
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

    def save_account(self):    
        """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen.
            
            Structures
            ----------
            = session.player_obj
            == envs
            === garden
            === home
            === dungeon
            == ent
            == ents 
            == questlog """
        
        # Update file menu
        if session.player_obj.file_num: self.options[session.player_obj.file_num - 1] += ' *'
        
        # Save data or return to main menu
        if type(self.choice) != int:
            session.pyg.overlay = 'main_menu'
            return
        else:
            self.choice += 1
            
            # Update Player object
            session.player_obj.file_num = self.choice
            
            # Save everything
            with open(f"Data/File_{self.choice}/session.player_obj.pkl", 'wb') as file: pickle.dump(session.player_obj, file)
            
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
            session.load_account_obj.reset(
                session.load_account_obj.name,
                session.load_account_obj.header,
                session.load_account_obj.options,
                session.load_account_obj.options_categories,
                session.load_account_obj.position,
                session.load_account_obj.backgrounds)
            session.pyg.overlay = 'main_menu'

    def load_account(self):    
        """ Shows a menu with each item of the inventory as an option, then returns an item if it is chosen.
            Structures
            ----------
            = session.player_obj
            == envs
            === garden
            === home
            === dungeon
            == ent 
            == ents 
            == questlog """
                
        # Update file menu
        if session.player_obj.file_num: self.options[session.player_obj.file_num - 1] += ' *'
        
        # Load data or return to main menu
        if self.choice is not None:
            
            if type(self.choice) != int:
                session.pyg.overlay = 'main_menu'
                return
            else:
                self.choice += 1
                session.pyg.startup_toggle = False
            
            # Load data onto fresh player
            session.player_obj = Player()
            with open(f"Data/File_{self.choice}/session.player_obj.pkl", "rb") as file:
                session.player_obj = pickle.load(file)

            # Load cameras
            for env in session.player_obj.envs.values():
                if type(env) == list:
                    for sub_env in env: sub_env.camera = Camera(session.player_obj.ent)
                else:                   env.camera     = Camera(session.player_obj.ent)
            
            self.reset(self.name, self.header, self.options, self.options_categories, self.position, self.backgrounds)
            session.pyg.game_state = 'play_game'
            session.play_game_obj.fadein = None
            session.pyg.overlay = 'main_menu'

        # Turn on gui
        session.pyg.gui_toggle, session.pyg.msg_toggle = True, True

    def set_controls(self, direction):
        if session.pyg.controls_preset == 'numpad 1':
            if direction == 'right': session.pyg.set_controls('numpad 2')
            else:                    session.pyg.set_controls('arrows')
        elif session.pyg.controls_preset == 'numpad 2':
            if direction == 'right': session.pyg.set_controls('arrows')
            else:                    session.pyg.set_controls('numpad 1')
        elif session.pyg.controls_preset == 'arrows':
            if direction == 'right': session.pyg.set_controls('numpad 1')
            else:                    session.pyg.set_controls('numpad 2')
    
        self.options = [
            f"Move up:                                {session.pyg.key_UP[0]}                     Exit:                                         {session.pyg.key_BACK[0]}",
            f"Move down:                           {session.pyg.key_DOWN[0]}                     Activate 1:                             {session.pyg.key_ENTER[0]}",
            f"Move left:                               {session.pyg.key_LEFT[0]}                     Activate 2:                               {session.pyg.key_PERIOD[0]}",
            f"Move right:                            {session.pyg.key_RIGHT[0]}",
            "",
            
            f"Toggle inventory:                  {session.pyg.key_INV[0]}                     Enter combo:                         {session.pyg.key_HOLD[0]}",
            f"Toggle Catalog:                   {session.pyg.key_DEV[0]}                     Change speed:                      {session.pyg.key_SPEED[0]}",
            f"Toggle GUI:                            {session.pyg.key_GUI[0]}                     Zoom in:                                {session.pyg.key_PLUS[0]}",
            f"View stats:                             {session.pyg.key_INFO[0]}                     Zoom out:                              {session.pyg.key_MINUS[0]}",
            f"View questlog:                      {session.pyg.key_QUEST[0]}"]
    
        for i in range(len(self.options)):
            self.options_render[i] = session.pyg.font.render(self.options[i], True, session.pyg.gray)
    
    def render(self):
        
        # Render menu background
        if self.backgrounds:
            session.pyg.screen.fill(session.pyg.black)
            session.pyg.screen.blit(self.backgrounds_render[self.choice], (0, 0))
        else:
            session.pyg.screen.fill(session.pyg.black)
        
        # Render header and cursor
        session.pyg.screen.blit(self.header_render, self.header_position[self.position])
        session.pyg.screen.blit(self.cursor_img, self.cursor_position_mutable)
        
        # Render categories and options
        for i in range(len(self.options_render)):
            
            # Render category text if it is not present 
            if self.options_categories:
                if self.options_categories[i] != self.options_categories_cache:
                    self.options_categories_cache = self.options_categories[i]
                    text = session.pyg.font.render(f'{self.options_categories_cache.upper()}:', True, session.pyg.gray)
                    self.options_positions_mutable[1] += self.tab_y
                    session.pyg.screen.blit(text, (self.category_positions_mutable[0], self.options_positions_mutable[1]))
                
            # Render option text
            session.pyg.screen.blit(self.options_render[i], self.options_positions_mutable)
            self.options_positions_mutable[1] += 24
        self.options_positions_mutable = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()
        pygame.display.flip()

class Info:
    """ Manages stats in the Garden. """

    def __init__(self):

        self.stats = {
            'Character Information': None,
            '': None,
            'rank':       None,
            'rigor':      None,
            'attack':     None,
            'defense':    None,
            'sanity':     None}

    def update(self):
        
        self.stats['rank']  = '★' * int(session.player_obj.ent.rank)
        if len(self.stats['rank']) < 5:
            while len(self.stats['rank']) < 5:
                self.stats['rank'] += '☆'
            
        self.stats['rigor']   = '★' * int(session.player_obj.ent.max_hp // 10)
        if len(self.stats['rigor']) < 5:
            while len(self.stats['rigor']) < 5:
                self.stats['rigor'] += '☆'
        
        self.stats['attack']   = '★' * int(session.player_obj.ent.attack // 10)
        if len(self.stats['attack']) < 5:
            while len(self.stats['attack']) < 5:
                self.stats['attack'] += '☆'
        
        self.stats['defense']   = '★' * int(session.player_obj.ent.defense // 10)
        if len(self.stats['defense']) < 5:
            while len(self.stats['defense']) < 5:
                self.stats['defense'] += '☆'

        self.stats['sanity']   = '★' * int(session.player_obj.ent.sanity // 10)
        if len(self.stats['sanity']) < 5:
            while len(self.stats['sanity']) < 5:
                self.stats['sanity'] += '☆'

class Pets:
    """ Manages stats in the Garden. """

    def __init__(self):
        
        # General
        self.ents = session.player_obj.envs['garden'].entities
        
        self.stats = {
            '      RADIX ATRIUM': None,
            '':         None,
            'mood':     None,
            'stamina':  None,
            'strength': None,
            'appeal':   None}
        
        # Numerical stats
        self.levels = {
            'stamina':   1,
            'strength':  1,
            'appeal':    1}
        
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
        
        # Time to lose happiness and gain something else
        self.happiness_cooldown = 10
        self.happiness_press    = 0
        
        # Time between mood switches if tied
        self.emoji_cooldown     = 10
        self.emoji_press        = 0

    def import_pets(self):
        self.ents = session.player_obj.envs['garden'].entities

    def stat_check(self, dic):
        for key, value in dic.items():
            if value > 10:  dic[key] = 10
            elif value < 0: dic[key] = 0

    def update(self):
        
        # Lose happiness
        if self.moods['happiness']:
            if time.time() - self.happiness_press > self.happiness_cooldown:
                self.happiness_press = time.time()
                
                # Random chance to lose happiness and gain something else
                if not random.randint(0, 1):
                    self.moods['happiness'] -= 1
                    self.moods[random.choice(list(self.moods.keys()))] += 1
        
        ## Keep stats to [0, 10]
        self.stat_check(self.levels)
        self.stat_check(self.moods)
        
        # Set mood to those with the highest value
        max_val = max(self.moods.values())
        current_moods = [mood for mood, val in self.moods.items() if val == max_val]
        
        ## Alternate between tied moods
        if len(current_moods) > 1:
            if time.time() - self.emoji_press > self.emoji_cooldown:
                self.emoji_press = time.time()
                self.stats['mood'] = self.faces[random.choice(current_moods)]        
        
        ## Set the current mood
        else:
            self.stats['mood'] = self.faces[current_moods[0]]
        
        ## Apply mood effects
        if self.moods['happiness'] <= 2:
            if self.ents[-1].img_names[0] != 'purple radish':
                for ent in self.ents:
                    if ent != session.player_obj.ent:
                        if ent.img_names[0] != 'purple radish':
                            ent.img_names[0] = 'purple radish'
        elif self.moods['happiness'] >= 8:
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
        self.stats['stamina']  = '★' * self.levels['stamina']
        while len(self.stats['stamina']) < 5:
            self.stats['stamina'] += '☆'
        self.stats['strength'] = '★' * self.levels['strength']
        while len(self.stats['strength']) < 5:
            self.stats['strength'] += '☆'
        self.stats['appeal']   = '★' * self.levels['appeal']
        while len(self.stats['appeal']) < 5:
            self.stats['appeal'] += '☆'

class MainMenu:
    
    def __init__(self):
        
        # Initialize title
        self.title_font     = pygame.font.SysFont('segoeuisymbol', 40, bold=True)
        self.game_title     = self.title_font.render("MORS SOMNIA", True, session.pyg.gray)
        self.game_title_pos = (int((session.pyg.screen_width - self.game_title.get_width())/2), 85)
        
        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, session.pyg.gray, [(5, 3), (10, 7), (5, 11)], 0)
        self.cursor_pos = [32, 320]
        
        # Initialize menu options
        self.menu_choices = ["NEW GAME", "LOAD", "SAVE", "CONTROLS", "QUIT"]
        self.menu_choices_surfaces = []
        
        session.img.average()
        self.color = pygame.Color(session.img.menu_correct, session.img.menu_correct, session.img.menu_correct)
        for i in range(len(self.menu_choices)):
            self.menu_choices_surfaces.append(session.pyg.font.render(self.menu_choices[i], True, self.color))
        self.choice, self.choices_length = 0, len(self.menu_choices) - 1
        
        # Allows access to garden
        self.menu_toggle = True
        
        # Other
        self.last_press_time, self.cooldown_time = 0, 0.5
        self.background_fade = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def startup(self):
        
        # Startup background
        background_image = pygame.image.load("Data/.Images/garden.png").convert()
        background_image = pygame.transform.scale(background_image, (session.pyg.screen_width, session.pyg.screen_height))

        # Fade details
        alpha = 0
        fade_speed = 10
        fade_surface = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height))
        fade_surface.fill(session.pyg.black)
        
        # Apply fade
        while alpha < 255:
            session.pyg.clock.tick(30)
            fade_surface.set_alpha(255 - alpha)
            
            # Set menu background to the custom image
            session.pyg.screen.blit(background_image, (0, 0))
            
            # Draw the menu elements during the fade
            session.pyg.screen.blit(self.game_title, self.game_title_pos)

            # Apply the fade effect
            session.pyg.screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
            
            # Increase alpha for the next frame
            alpha += fade_speed
        session.pyg.game_state = 'play_garden'
        session.pyg.overlay = 'menu'
        return

    def run(self):
        
        # Restrict keystroke speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        # Prevent saving before a game is started or loaded
        if session.pyg.startup_toggle:
            self.menu_choices_surfaces[2] = session.pyg.font.render(self.menu_choices[2], True, session.pyg.dark_gray)
        else:
            self.menu_choices_surfaces[2] = session.pyg.font.render(self.menu_choices[2], True, self.color)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                # Navigation
                if event.key in session.pyg.key_UP:       self.key_UP()
                elif event.key in session.pyg.key_DOWN:   self.key_DOWN()
                
                # Music
                elif event.key in session.pyg.key_PLUS:   self.key_PLUS()
                elif event.key in session.pyg.key_MINUS:  self.key_MINUS()
                elif event.key in session.pyg.key_DEV:    self.key_DEV()
                
                # Garden
                elif event.key in session.pyg.key_PERIOD: self.key_PERIOD()
        
                # Unused
                elif event.key in session.pyg.key_HOLD:   self.key_HOLD()
                elif event.key in session.pyg.key_INFO:   self.key_INFO()
                
                # >>RESUME<<
                elif event.key in session.pyg.key_BACK:
                    if time.time()-session.pyg.last_press_time > session.pyg.cooldown_time:
                        session.pyg.last_press_time = float(time.time())
                        session.pyg.overlay = None
                        return
                
                # Select option
                elif event.key in session.pyg.key_ENTER:
                    
                    # >>NEW GAME<<
                    if self.choice == 0:
                        session.pyg.game_state = 'new_game'
                        session.pyg.overlay = None
                        return
                    
                    # >>LOAD<<
                    elif self.choice == 1:
                        session.pyg.overlay = 'load'
                        return
                    
                    # >>SAVE<<
                    elif self.choice == 2:
                        
                        # Prevent saving before a game is started or loaded
                        if not session.pyg.startup_toggle:
                            session.pyg.overlay = 'save'
                            return
                    
                    # >>CONTROLS<<
                    elif self.choice == 3:
                        session.pyg.overlay = 'session.ctrl_menu'
                        return
                    
                    # >>QUIT<<
                    elif self.choice == 4:
                        pygame.quit()
                        sys.exit()
        
        session.pyg.overlay = 'menu'
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
            if session.player_obj.ent.env.name != 'garden':
                place_player(
                    env = session.player_obj.envs['garden'],
                    loc = session.player_obj.envs['garden'].player_coordinates)
                session.pyg.game_state = 'play_garden'
            elif not session.pyg.startup_toggle:
                place_player(
                    env = session.player_obj.ent.last_env,
                    loc = session.player_obj.ent.last_env.player_coordinates)
                session.pyg.game_state = 'play_game'

    def key_HOLD(self):
        pass

    def key_PLUS(self):
        session.aud.pause(paused=False)

    def key_MINUS(self):
        session.aud.pause(paused=True)

    def key_INFO(self):
        if session.pyg.frame:
            pygame.display.set_mode((session.pyg.screen_width, session.pyg.screen_height), pygame.NOFRAME)
            session.pyg.frame = False
        else:
            pygame.display.set_mode((session.pyg.screen_width, session.pyg.screen_height))
            session.pyg.frame = True

    def key_DEV(self):
        session.aud.play_track()

    def render(self):
        
        # Apply background fade
        session.pyg.screen.blit(self.background_fade, (0, 0))
        
        # Blit menu options
        Y = 316
        
        self.menu_choices_surfaces = []
        
        session.img.average()
        #self.color = pygame.Color(session.img.menu_correct, session.img.menu_correct, session.img.menu_correct)
        self.color = pygame.Color(255-session.img.bottom_color[0], 255-session.img.bottom_color[1], 255-session.img.bottom_color[2])
        for i in range(len(self.menu_choices)):
            if (i == 2) and session.pyg.startup_toggle:
                color = session.pyg.dark_gray
            else: color = self.color
            self.menu_choices_surfaces.append(session.pyg.font.render(self.menu_choices[i], True, color))
        for menu_choice_surface in self.menu_choices_surfaces:
            session.pyg.screen.blit(menu_choice_surface, (48, Y))
            Y += 24
        
        # Blit cursor
        pygame.draw.polygon(self.cursor_img, self.color, [(5, 3), (10, 7), (5, 11)], 0)
        session.pyg.screen.blit(self.cursor_img, self.cursor_pos)

        # Blit logo
        if session.pyg.startup_toggle:
            session.pyg.screen.blit(self.game_title, self.game_title_pos)
        else:
            for i in range(len(session.img.big)):
                for j in range(len(session.img.big[0])):
                    X = session.pyg.screen_width - session.pyg.tile_width * (i+2)
                    Y = session.pyg.screen_height - session.pyg.tile_height * (j+2)
                    session.pyg.screen.blit(session.img.big[len(session.img.big)-j-1][len(session.img.big[0])-i-1], (X, Y))

class SmallMenu:
    
    def render(self):
        session.pyg.msg_height = 1
        session.pyg.update_gui()
        render_all()
        if session.player_obj.ent.env.name != 'garden':
            for image, (X, Y) in session.player_obj.ent.env.weather.render():
                session.pyg.display.blit(image, (X, Y))
        
        # Render background
        fill_width  = session.pyg.tile_width  * 5 + session.pyg.tile_width // 2
        fill_height = session.pyg.tile_height * 4 + session.pyg.tile_height // 2
        self.cursor_fill   = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.cursor_fill.fill((0, 0, 0, 128))
        session.pyg.screen.blit(self.cursor_fill, (32, 32))
        
        # Render border
        self.cursor_border = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.cursor_fill.fill((0, 0, 0, 128))
        pygame.draw.polygon(
            self.cursor_border, 
            session.pyg.gray, 
            [(0, 0),
             (fill_width-1, 0),
             (fill_width-1, fill_height-1),
             (0, fill_height-1)], 1)
        session.pyg.screen.blit(self.cursor_border, (32, 32))
        
        # Render items
        Y = 32
        for i in range(len(list(self.dic))):
            X1 = session.pyg.tile_height + session.pyg.tile_height // 4
            X2 = session.pyg.tile_height * 4
            key, val = list(self.dic.items())[i]
            key = session.pyg.font.render(key, True, session.pyg.gray)
            val = session.pyg.font.render(val, True, session.pyg.gray)
            session.pyg.screen.blit(key, (X1, Y))
            session.pyg.screen.blit(val, (X2, Y))
            Y += session.pyg.tile_height//2

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
        self.width           = int(session.pyg.screen_width / session.pyg.zoom)
        self.height          = int((session.pyg.screen_height + session.pyg.tile_height) / session.pyg.zoom)
        self.tile_map_width  = int(self.width / session.pyg.tile_width)
        self.tile_map_height = int(self.height / session.pyg.tile_height)
        
        self.X               = int((self.target.X * session.pyg.zoom) - int(self.width / 2))
        self.Y               = int((self.target.Y * session.pyg.zoom) - int(self.height / 2))
        self.tile_map_x      = int(self.X / session.pyg.tile_width)
        self.tile_map_y      = int(self.Y / session.pyg.tile_height)
        
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
            self.tile_map_x = int(self.X / session.pyg.tile_width)
            self.x_range    = int(self.tile_map_x + self.tile_map_width)

            Y_move          = int(self.target.Y - self.center_Y)
            self.Y          = int(self.Y + Y_move)
            self.center_Y   = int(self.center_Y + Y_move)
            self.bottom     = int(self.bottom + Y_move)
            self.tile_map_y = int(self.Y / session.pyg.tile_height)
            self.y_range    = int(self.tile_map_y + self.tile_map_height)
            
            self.fix_position()

    def fix_position(self):
        """ ? """
        if self.X < 0:
            self.X          = 0
            self.center_X   = self.X + int(self.width / 2)
            self.right      = self.X + self.width
            self.tile_map_x = int(self.X / (session.pyg.tile_width / session.pyg.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        elif self.right > (len(session.player_obj.ent.env.map)-1) * session.pyg.tile_width:
            self.right      = (len(session.player_obj.ent.env.map)) * session.pyg.tile_width
            self.X          = self.right - self.width
            self.center_X   = self.X + int(self.width / 2)
            self.tile_map_x = int(self.X / (session.pyg.tile_width / session.pyg.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        if self.Y < 0:
            self.Y          = 0
            self.center_Y   = self.Y + int(self.height / 2)
            self.bottom     = (self.Y + self.height + 320) / session.pyg.zoom
            self.tile_map_y = int(self.Y / (session.pyg.tile_height / session.pyg.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height
        
        elif self.bottom > (len(session.player_obj.ent.env.map[0])) * session.pyg.tile_height:
            self.bottom     = (len(session.player_obj.ent.env.map[0])) * session.pyg.tile_height
            self.Y          = self.bottom - self.height
            self.center_Y   = self.Y + int(self.height / 2)
            self.tile_map_y = int(self.Y / (session.pyg.tile_height / session.pyg.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height

    def zoom_in(self, factor=0.1, custom=None):
        """ Zoom in by reducing the camera's width and height. """
        
        # Set to a specific value
        if custom and (session.pyg.zoom != custom):
            session.pyg.zoom = custom
            session.pyg.zoom_cache = session.pyg.zoom
            session.pyg.update_gui()
            self.width  = int(session.pyg.screen_width / session.pyg.zoom)
            self.height = int(session.pyg.screen_height / session.pyg.zoom)
            session.pyg.display = pygame.Surface((self.width, self.height))
            self._recalculate_bounds()
        
        elif not custom and not self.fixed:
            session.pyg.zoom += factor
            session.pyg.zoom_cache = session.pyg.zoom
            session.pyg.update_gui()
            self.width  = int(session.pyg.screen_width / session.pyg.zoom)
            self.height = int(session.pyg.screen_height / session.pyg.zoom)
            session.pyg.display = pygame.Surface((self.width, self.height))
            self._recalculate_bounds()

    def zoom_out(self, factor=0.1, custom=None):
        """ Zoom out by increasing the camera's width and height. """
        
        if not self.fixed:
            if round(session.pyg.zoom, 2) > factor:  # Ensure zoom level stays positive
                if custom:
                    session.pyg.zoom = custom
                else:
                    session.pyg.zoom -= factor
                    session.pyg.zoom_cache = session.pyg.zoom
                session.pyg.update_gui()
                self.width = int(session.pyg.screen_width / session.pyg.zoom)
                self.height = int(session.pyg.screen_height / session.pyg.zoom)
                session.pyg.display = pygame.Surface((self.width, self.height))
                self._recalculate_bounds()

    def _recalculate_bounds(self):
        """ Recalculate dependent properties after zooming. """
        self.X               = self.target.X - int(self.width / 2)
        self.Y               = self.target.Y - int(self.height / 2)
        self.center_X        = self.X + int(self.width / 2)
        self.center_Y        = self.Y + int(self.height / 2)
        self.right           = self.X + self.width
        self.bottom          = self.Y + self.height
        self.tile_map_width  = int(self.width / session.pyg.tile_width)
        self.tile_map_height = int(self.height / session.pyg.tile_height)
        self.tile_map_x      = int(self.X / session.pyg.tile_width)
        self.tile_map_y      = int(self.Y / session.pyg.tile_height)
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        self.fix_position()

########################################################################################################################################################
# Tools
def check_tile(x, y, startup=False):
    """ Reveals newly explored regions with respect to the player's position. """
    
    # Define some shorthand
    tile = session.session.player_obj.ent.env.map[x][y]
    
    # Reveal a square around the player
    for u in range(x-1, x+2):
        for v in range(y-1, y+2):
            session.session.player_obj.ent.env.map[u][v].hidden = False
    
    # Reveal a hidden room
    if tile.room:
        
        if tile.room.hidden:
            tile.room.hidden = False
            for room_tile in tile.room.tiles_list:
                room_tile.hidden = False
        
        # Check if the player enters or leaves a room
        if session.session.player_obj.ent.prev_tile:
            if (tile.room != session.session.player_obj.ent.prev_tile.room) or (startup == True):
                
                # Hide the roof if the player enters a room
                if tile.room and tile.room.roof:
                    for spot in tile.room.tiles_list:
                        if spot not in tile.room.walls_list:
                            spot.img_names = tile.room.floor
    
    # Reveal the roof if the player leaves the room
    if session.session.player_obj.ent.prev_tile:
        prev_tile = session.session.player_obj.ent.prev_tile
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
            #session.session.pyg.update_gui("A mysterious breeze seeps through the cracks.", session.session.pyg.dark_gray)
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
    
    (x, y) = obj.X//session.pyg.tile_width, obj.Y//session.pyg.tile_width
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
    if not ent: ent = session.session.player_obj.ent
        
    inventory_cache = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
    other_cache     = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}

    # Sort by category
    for item_list in session.session.player_obj.ent.inventory.values():
        for item in item_list:
            inventory_cache[item.role].append(item)
    
    # Sort by stats:
    sorted(inventory_cache['weapons'], key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
    sorted(inventory_cache['armor'],  key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
    sorted(inventory_cache['potions'], key=lambda obj: obj.name)
    sorted(inventory_cache['scrolls'], key=lambda obj: obj.name)
    sorted(inventory_cache['other'],  key=lambda obj: obj.name)

    session.session.player_obj.ent.inventory = inventory_cache

def screenshot(size='display', visible=False, folder="Data/.Cache", filename="screenshot.png", blur=False):
    """ Takes a screenshot.
        cache:  saves a regular screenshot under Data/.Cache/screenshot.png
        save:   moves regular cached screenshot to Data/File_#/screenshot.png 
        blur:   adds a blur effect """
    
    # Turn off gui
    gui_cache, msg_cache = copy.copy(session.pyg.gui_toggle), copy.copy(session.pyg.msg_toggle)
    session.pyg.gui_toggle, session.pyg.msg_toggle = False, False
    
    # Select display size
    if size == 'full':
        camera_cache = [session.player_obj.ent.env.camera.X, session.player_obj.ent.env.camera.Y]
        session.pyg.screen = pygame.display.set_mode((len(session.player_obj.ent.env.map[0])*16, len(session.player_obj.ent.env.map)*16),)
        session.player_obj.ent.env.camera.X = 0
        session.player_obj.ent.env.camera.Y = 0
        session.player_obj.ent.env.camera.update()
        render_all(size=size, visible=visible)
    
    # Save image
    path = folder + '/' + filename
    session.pyg.gui_toggle, session.pyg.msg_toggle = False, False
    pygame.image.save(session.pyg.screen, path)
    
    # Add effects
    if blur:
        image_before = Image.open(folder + '/' + filename)
        image_after  = image_before.filter(ImageFilter.BLUR)
        image_after.save(folder + '/' + filename)
    
    # Reset everthing to normal
    if size == 'full':
        session.pyg.screen = pygame.display.set_mode((session.pyg.screen_width, session.pyg.screen_height),)
        session.player_obj.ent.env.camera.X = camera_cache[0]
        session.player_obj.ent.env.camera.Y = camera_cache[1]
        session.player_obj.ent.env.camera.update()
    
    session.pyg.gui_toggle, session.pyg.msg_toggle = gui_cache, msg_cache
    render_all()

def API(state, details, init=False):
    global RPC
    
    if init:
        RPC = Presence(1384311591662780586)
        RPC.connect()
    
    else:
        RPC.update(
            state       = state,
            details     = details,
            large_image = "logo",
            start       = time.time())
    
def debug_call(func):
    """ Just a print statement for debugging. Shows which function is called alongside variable details. """
    def wrapped_function(*args, **kwargs):
        print(f"{func.__name__:<30}{time.strftime('%M:%S', time.localtime())}")
        return func(*args, **kwargs)
    return wrapped_function

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
        session.pyg.screen.blit(image, (0, 0))
    
    session.pyg.display.fill(session.pyg.black)
    
    # Set tiles to render
    if size == 'full':
        y_range_1, y_range_2 = 0, len(session.player_obj.ent.env.map[0])
        x_range_1, x_range_2 = 0, len(session.player_obj.ent.env.map)
    
    else:        
        camera = session.player_obj.ent.env.camera

        y_range_1 = max(0, camera.tile_map_y)
        y_range_2 = min(len(session.player_obj.ent.env.map[0])-1, camera.tile_map_y + camera.tile_map_height+2)
        
        x_range_1 = max(0, camera.tile_map_x)
        x_range_2 = min(len(session.player_obj.ent.env.map)-1, camera.tile_map_x + camera.tile_map_width+2)
    
    # Draw visible tiles
    for y in range(int(camera.Y/32), int(camera.bottom/session.pyg.tile_height + 1)):
        for x in range(int(camera.X/32), int(camera.right/session.pyg.tile_width + 1)):
            try:    tile = session.player_obj.ent.env.map[x][y]
            except: continue
            
            if visible or not tile.hidden:
                
                # Lowest tier (floor and walls)
                image, (X, Y) = tile.draw()
                session.pyg.display.blit(image, (X, Y))

                # Second tier (decor and items)
                if tile.item:
                    tile.item.draw(session.pyg.display)
                
                # Third tier (entity)
                if tile.entity:
                    tile.entity.draw(session.pyg.display)
                
                # Fourth tier (roof)
                if tile.room:
                    if tile.room.roof:
                        if tile.img_names == tile.room.roof:
                            image, (X, Y) = tile.draw()
                            session.pyg.display.blit(image, (X, Y))
    
    # Apply effects
    if session.img.render_fx == 'bw_binary': bw_binary()
    
    # Render GUI
    if (size == 'display') and (session.pyg.overlay != 'menu'):
        if bool(session.img.impact):
            for i in range(len(session.img.impact_images)):
                session.pyg.screen.blit(session.img.impact_images[i], session.img.impact_image_pos[i])
        
        # Print messages
        if session.pyg.msg_toggle: 
            Y = 3
            
            # Find how many messages to write
            for message in session.pyg.msg:
                session.pyg.screen.blit(message, (5, Y))
                Y += 16
        
        # Print status bars and time
        if session.pyg.gui_toggle:
            gui = list(session.pyg.gui.values())
            for i in range(len(session.pyg.gui)):
                
                # Left
                if i == 0:   x = 16
                
                # Central
                elif i == 1: x = session.pyg.screen_width//2 - gui[2].get_width()//2 - gui[1].get_width()
                elif i == 2: x = session.pyg.screen_width//2 - gui[2].get_width()//2
                elif i == 3: x = session.pyg.screen_width//2 + gui[2].get_width()//2
                
                # Right
                elif i == 4: x = session.pyg.screen_width - gui[i].get_width() - 16
                
                y = session.pyg.screen_height - 27
                session.pyg.screen.blit(gui[i], (x, y))
    
    session.aud.shuffle()

########################################################################################################################################################