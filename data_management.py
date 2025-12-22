########################################################################################################################################################
# Imports
## Standard
import csv
import json
import os
import time
import json
import copy

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
        folder_path = find_path(target='Dev/Databases')              # fast
        
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

    path = find_path(filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def merge_json(group, names):
    """ Imports all category-specific json data, then fills in the gaps with default parameters. """

    _defaults = load_json(f'Data/.{group}/_defaults.json')
    dicts     = {}

    for category in names:
        category_dict  = load_json(f'Data/.{group}/{category}.json')
        _defaults_dict = _defaults[category]

        for item_id, attrs in category_dict.items():
            full_attrs = copy.deepcopy(_defaults_dict)
            full_attrs.update(attrs)
            dicts[item_id] = full_attrs

    return dicts

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
    
        Syntax
        ------
        category    : meta data, not used anywhere
        key         : used to locate a given row in the output dictionary
        lists       : () for integers and [] for strings with entries separated by semicolons
        blank lines : ignored

        Parameters
        ----------
        path : str; file path, such as one returned by find_path

        Returns
        -------
        items : dict; container for all rows in the file
    """
    
    def parse_value(val):
        val = val.strip()

        # Keywords
        if val.upper()   == 'NONE':   return None
        elif val.upper() == 'TRUE':   return True
        elif val.upper() == 'FALSE':  return False

        # Lists of strings; semicolon separated entries
        elif val.startswith('[') and val.endswith(']'):
            return [x.strip("'\" ") for x in val[1:-1].split(';') if x.strip()]
        
        # Lists of integers; semicolon separated entries
        elif val.startswith('(') and val.endswith(')'):
            return [int(x.strip("'\" ")) for x in val[1:-1].split(';') if x.strip()]
        
        else:
            
            # Integers
            try:
                return int(val)

            # Strings
            except ValueError:
                return val.strip("'\"")
    
    # Initialize data container
    items = {}

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            key = row['key']

            # Skip blank lines
            if key:
                
                # Convert one row of data to a dictionary entry
                entry = {col: parse_value(val) for col, val in row.items() if col not in ['category', 'key']}
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

def rebuild_databases(filename_list):
    """ Converts convenient file types (ex. TSV) to efficient types (ex. JSON).
        Run this after changing the convenient files.
    """

    for file in filename_list:

        print(f"Converting {file}.tsv...")
        load_path = find_path(target=f'{file}.tsv', folder='Databases')
        load_data = load_tsv(load_path)
        save_path = os.path.join(find_path(target='.Databases'), f'{file}.json')
        save_json(load_data, save_path)

    print("Databases rebuilt!")

########################################################################################################################################################
# Startup
########################################################################################################################################################
# Initializations
## Group database files
img_IDs     = ['img_ents', 'img_equipment', 'img_other']
obj_names   = ['item_effects', 'NPCs']
other_names = ['biomes']

entities    = ['humanoids', 'monsters']
items       = ['accessories', 'armor', 'decor', 'drugs', 'furniture', 'offhands', 'potions', 'scrolls', 'stairs', 'structures', 'weapons']
tiles       = ['walls', 'floors']

## Build JSON files
#rebuild_databases(['ents']) # img_IDs + obj_names + other_names

## Load JSON files
item_dicts   = merge_json('Items',    items)
ent_dicts    = merge_json('Entities', entities)
tile_dicts   = merge_json('Tiles',    tiles)
NPC_dicts    = load_json(f'Data/.Entities/NPCs.json')
biome_dicts  = load_json(f'Data/.Databases/biomes.json')
img_dicts    = {name: load_json(f'Data/.Images/{name}.json') for name in img_IDs}

########################################################################################################################################################