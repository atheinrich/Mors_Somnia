########################################################################################################################################################
# Imports
## Standard
import csv
import os
import time
import json

## Specific
import pygame
from   pypresence import Presence

## Local
import session

########################################################################################################################################################
# Backend tools
def find_path(target, folder=None, start_dir='/'):
    """ Search for a file starting from the root directory.
        - If 'target' is an existing relative or absolute path, return it directly.
        - If 'target' is a name (no slashes), search for it as a file or directory.
        - If 'folder' is given, only search inside that folder name.
    
        Parameters
        ----------
        filename : str; name of the file to find
        folder : str; name of the folder the file is in; if None, search all folders
        start_dir : str; directory to start search from (default: root '/')
        
        Returns
        -------
        str or None : absolute path to the file if found, otherwise None
        
        Examples
        -------
        file_path   = find_path(target='Data/.Databases/items.json') # fast
        file_path   = find_path(target='items.tsv')                  # slow but general
        file_path   = find_path(target='envs.pkl', folder='File_1')  # slow but accurate
        folder_path = find_path(target='Databases')                  # fast
        folder_path = find_path(target='Dev/Databases')        # fast
        
    """
    if folder:
        guessed_path = os.path.join(start_dir, folder, target)
    else:
        guessed_path = os.path.join(start_dir, target)

    if os.path.exists(guessed_path):
        return os.path.abspath(guessed_path)

    # Brute force search for a file
    if folder is None:
        
        # Direct path check
        if os.path.exists(target):
            return os.path.abspath(target)

        # Search for file or directory by name
        for root, dirs, files in os.walk(start_dir):
            if target in files or target in dirs:
                return os.path.abspath(os.path.join(root, target))
        
        return None
    
    # Find the folder
    folder_path = find_path(target=folder, start_dir=start_dir)
    if folder_path:
        
        # Check if target is a file inside the folder
        candidate = os.path.join(folder_path, target)
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
        
        # Search recursively if needed
        for root, dirs, files in os.walk(folder_path):
            if target in files or target in dirs:
                return os.path.abspath(os.path.join(root, target))
    
    return None

def load_json(filename):
    """ Loads a JSON file and returns python-readable data.

        Parameters
        ----------
        filename : str; path of the JSON file to create (including extension)
    """

    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

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

########################################################################################################################################################
# Gameplay tools
class Camera:
    """ Defines a camera to follow the player. """
    
    def __init__(self, ent):
        """ Defines a camera and its parameters. 
            
            Parameters
            ----------
            ent             : Entity object; focus of camera
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
            
            fix_position    : bool; prevents adjustment of parameters
        """
        
        self.ent             = ent
        self.width           = session.pyg.screen_width
        self.height          = session.pyg.screen_height + session.pyg.tile_height
        self.tile_map_width  = int(self.width / session.pyg.tile_width)
        self.tile_map_height = int(self.height / session.pyg.tile_height)
        
        self.X               = int(self.ent.X - int(self.width / 2))
        self.Y               = int(self.ent.Y - int(self.height / 2))
        self.tile_map_x      = int(self.X / session.pyg.tile_width)
        self.tile_map_y      = int(self.Y / session.pyg.tile_height)
        
        self.right           = self.X + self.width
        self.bottom          = self.Y + self.height
        self.x_range         = self.tile_map_x + self.tile_map_width
        self.y_range         = self.tile_map_y + self.tile_map_height
        
        self.center_X        = int(self.X + int(self.width / 2))
        self.center_Y        = int(self.Y + int(self.height / 2))
        
        self.zoom            = 1
        self.fixed           = False
        self.fix_position()

    def update(self):
        """ ? """
        
        if not self.fixed:
            X_move          = int(self.ent.X - self.center_X)
            self.X          = int(self.X + X_move)
            self.center_X   = int(self.center_X + X_move)
            self.right      = int(self.right + X_move)
            self.tile_map_x = int(self.X / session.pyg.tile_width)
            self.x_range    = int(self.tile_map_x + self.tile_map_width)

            Y_move          = int(self.ent.Y - self.center_Y)
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
            self.tile_map_x = int(self.X / (session.pyg.tile_width / self.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        elif self.right > (len(self.ent.env.map)-1) * session.pyg.tile_width:
            self.right      = (len(self.ent.env.map)) * session.pyg.tile_width
            self.X          = self.right - self.width
            self.center_X   = self.X + int(self.width / 2)
            self.tile_map_x = int(self.X / (session.pyg.tile_width / self.zoom))
            self.x_range    = self.tile_map_x + self.tile_map_width
        
        if self.Y < 0:
            self.Y          = 0
            self.center_Y   = self.Y + int(self.height / 2)
            self.bottom     = (self.Y + self.height + 320) / self.zoom
            self.tile_map_y = int(self.Y / (session.pyg.tile_height / self.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height
        
        elif self.bottom > (len(self.ent.env.map[0])) * session.pyg.tile_height:
            self.bottom     = (len(self.ent.env.map[0])) * session.pyg.tile_height
            self.Y          = self.bottom - self.height
            self.center_Y   = self.Y + int(self.height / 2)
            self.tile_map_y = int(self.Y / (session.pyg.tile_height / self.zoom))
            self.y_range    = self.tile_map_y + self.tile_map_height

    def zoom_in(self, factor=0.1, custom=None):
        """ Zoom in by reducing the camera's width and height. """
        
        # Set to a specific value
        if custom and (self.zoom != custom):
            self.zoom = custom
            session.pyg.update_gui()
            self.width  = int(session.pyg.screen_width / self.zoom)
            self.height = int(session.pyg.screen_height / self.zoom)
            session.pyg.display = pygame.Surface((self.width, self.height))
            self._recalculate_bounds()
        
        elif not custom and not self.fixed:
            self.zoom += factor
            session.pyg.update_gui()
            self.width  = int(session.pyg.screen_width / self.zoom)
            self.height = int(session.pyg.screen_height / self.zoom)
            session.pyg.display = pygame.Surface((self.width, self.height))
            self._recalculate_bounds()

    def zoom_out(self, factor=0.1, custom=None):
        """ Zoom out by increasing the camera's width and height. """
        
        if not self.fixed:
            if round(self.zoom, 2) > factor:  # Ensure zoom level stays positive
                if custom:
                    self.zoom = custom
                else:
                    self.zoom -= factor
                session.pyg.update_gui()
                self.width = int(session.pyg.screen_width / self.zoom)
                self.height = int(session.pyg.screen_height / self.zoom)
                session.pyg.display = pygame.Surface((self.width, self.height))
                self._recalculate_bounds()

    def _recalculate_bounds(self):
        """ Recalculate dependent properties after zooming. """
        self.X               = self.ent.X - int(self.width / 2)
        self.Y               = self.ent.Y - int(self.height / 2)
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
# Development tools
def debug_call(func):
    """ Just a print statement for debugging. Shows which function is called alongside variable details. """

    def wrapped_function(*args, **kwargs):
        print(f"{func.__name__:<30}{time.strftime('%M:%S', time.localtime())}")
        return func(*args, **kwargs)
    
    return wrapped_function

def load_tsv(path):
    """ Load TSV data into a nested dictionary of dictionaries, automatically detecting types.
    
        Parameters
        ----------
        path : str; file path, such as one returned by find_path

        Returns
        -------
        items : dict; container for all rows in the file
    """
    
    def parse_value(val):
        val = val.strip()
        if val   == 'None':   return None
        elif val == 'True':   return True
        elif val == 'False':  return False
        elif val.startswith('[') and val.endswith(']'):
            return [x.strip("'\" ") for x in val[1:-1].split(';') if x.strip()]
        elif val.startswith('(') and val.endswith(')'):
            return [int(x.strip("'\" ")) for x in val[1:-1].split(';') if x.strip()]
        else:
            try:               return int(val)
            except ValueError: return val.strip("'\"")
    
    items = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            category = row['category']
            key = row['key']

            entry = {col: parse_value(val) for col, val in row.items() if col not in ('category', 'key')}

            items[key] = entry

    return items

def save_json(data, filename):
    """ Saves data as a JSON file.

        Parameters
        ----------
        data     : dict; data to save.
        filename : str; path of the JSON file to create (including extension)
    """

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def rebuild_databases():
    """ Converts convenient file types (ex. TSV) to efficient types (ex. JSON).
        Run this after changing the convenient files.
    """

    for file in ['items', 'item_effects', 'ents', 'NPCs']:
        print(f"Converting {file}...")
        load_path = find_path(target=f'{file}.tsv', folder='Databases')
        load_data = load_tsv(load_path)
        save_path = os.path.join(find_path(target='.Databases'), f'{file}.json')
        save_json(load_data, save_path)
    print("Databases rebuilt!")

########################################################################################################################################################
# Initializations
#rebuild_databases()
item_dict   = load_json(find_path('Data/.Databases/items.json'))
ent_dict    = load_json(find_path('Data/.Databases/ents.json'))
effect_dict = load_json(find_path('Data/.Databases/item_effects.json'))
NPC_dict    = load_json(find_path('Data/.Databases/NPCs.json'))

########################################################################################################################################################