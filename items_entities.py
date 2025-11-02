########################################################################################################################################################
# Item creation and management
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import time

## Specific
import pygame

## Local
import session
from data_management import obj_dicts, load_json

########################################################################################################################################################

########################################################################################################################################################
# Classes
class PlayerData:
    """ Manages player file. One save for each file.

        Objects saved:
            - Entity:       stats, location, current and previous environment, inventory, equipment
            - Entities:     Entity instances for recurring characters for ease of access
            - Environments: all initialized environments, including all objects and entities therein
            - Dialogue:     all dialogue that has been loaded, as well as the current state for each
    """

    def __init__(self):
        """ Holds everything regarding the player.

            Details
            -------
            ent      : Entity object; player
            ents     : dict of Entity objects; NPCs, such as Kyrio
            envs     : dict of Environment objects; worlds, such as overworld
            file_num : int in [0, 1, 2, 3, 4]; index for data management
            temp     : something to do with NewGameMenu
        """
        
        # Class instances
        self.ent        = None
        self.ents       = {}
        self.envs       = None
        self.dialogue   = None

        # Utility
        self.file_num   = 0

        # Entity attributes
        self.default_values()

    def default_values(self):

        self.name       = "player"
        self.role       = 'player'
        self.img_names  = ['white', 'front']

        self.exp        = 0
        self.rank       = 1

        self.hp         = 10
        self.max_hp     = 10
        self.attack     = 0
        self.defense    = 1
        self.sanity     = 1
        self.stamina    = 100

        self.X          = 0
        self.Y          = 0

        self.habitat    = 'any'
        self.follow     = False
        self.lethargy   = 5
        self.miss_rate  = 10
        self.aggression = 0
        self.fear       = None
        self.reach      = 1000

        self.discoveries = {
            'walls': {
                'gray':            ['walls',     'gray'],
                'green':           ['walls',     'green']},
            'floors': {
                'grass4':          ['floors',    'grass4'],
                'wood':            ['floors',    'wood'],
                'water':           ['floors',    'water']},
            'stairs': {
                'door':            ['stairs',    'door']},
            'decor': {
                'blades':          ['decor',     'blades'],
                'lights':          ['decor',     'lights']},
            'furniture': {
                'table':           ['furniture', 'table'],
                'red chair left':  ['furniture', 'red chair left'],
                'red chair right': ['furniture', 'red chair right']},
            'paths': {},
            'entities': {}}

class Entity:
    """ Player, enemies, and NPCs. Manages stats, inventory, and basic mechanics. """
    
    def __init__(self, **kwargs):
        """ Parameters
            ----------
            player_obj     : PlayerData object

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
        
        pyg = session.pyg

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
        self.cooldown   = 0.25
        self.last_press = 0
        self.motions_log = [] # list of lists of int; prescribed motions for ai
        
        ## Mechanics
        self.dead        = False
        self.quest       = False
        self.wallet      = 100
        self.trade_times = None
        self.inventory   = {'weapons': [], 'armor': [],  'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
        self.equipment   = {'head': None,  'face': None, 'chest': None, 'body': None,  'dominant hand': None, 'non-dominant hand': None}
        
        ## Randomizer
        self.rand_X = random.randint(-pyg.tile_width,  pyg.tile_width)
        self.rand_Y = random.randint(-pyg.tile_height, pyg.tile_height)

        #########################################################
        # Initialize reactions and abilities
        self.garden_effects = [
            Effect(
                name          = 'scare',
                img_names     = ['bubbles', 'exclamation bubble'],
                function      = session.effects.entity_scare,
                trigger       = 'active',
                sequence      = '⮟⮜⮟',
                cooldown_time = 1,
                other         = None),
            
            Effect(
                name          = 'comfort',
                img_names     = ['bubbles', 'heart bubble'],
                function      = session.effects.entity_comfort,
                trigger       = 'active',
                sequence      = '⮟⮞⮜',
                cooldown_time = 1,
                other         = None),
            
            Effect(
                name          = 'clean',
                img_names     = ['bubbles', 'dots bubble'],
                function      = session.effects.entity_clean,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None)]
        
        self.item_effects = [
            Effect(
                name          = 'suicide',
                img_names     = ['decor', 'bones'],
                function      = session.effects.suicide,
                trigger       = 'active',
                sequence      = '⮟⮟⮟',
                cooldown_time = 1,
                other         = None),

            Effect(
                name          = 'scare',
                img_names     = ['bubbles', 'exclamation bubble'],
                function      = session.effects.entity_scare,
                trigger       = 'active',
                sequence      = '⮟⮜⮟',
                cooldown_time = 1,
                other         = None),
                
            Effect(
                name          = 'capture',
                img_names     = ['bubbles', 'heart bubble'],
                function      = session.effects.entity_capture,
                trigger       = 'active',
                sequence      = '⮟⮞⮟',
                cooldown_time = 1,
                other         = None)]
        self.effects    = []

    def draw(self, loc=None):
        """ Adds skin and equipment layers to a fresh surface.

            Parameters
            ----------
            surface : pygame image
            loc     : list of int; screen coordinates """
        
        pyg = session.pyg
        
        surface = pygame.Surface((64, 64), pygame.SRCALPHA)

        #########################################################
        # Set location
        if loc:
            X = loc[0]
            Y = loc[1]
        else:
            X = self.X - self.env.camera.X
            Y = self.Y - self.env.camera.Y
        
        #########################################################
        # Body
        ## Swimming
        if self.tile.biome in session.img.biomes['sea']: swimming = True
        else:                                            swimming = False

        ## Regular
        if self.handedness == 'left': 
            if swimming: surface.blit(session.img.halved([self.img_names[0], self.img_names[1]]), (0, 0))
            else:        surface.blit(session.img.dict[self.img_names[0]][self.img_names[1]],     (0, 0))
        
        ## Flipped
        else:
            if swimming: surface.blit(session.img.halved([self.img_names[0], self.img_names[1]], flipped=True), (0, 0))
            else:        surface.blit(session.img.flipped.dict[self.img_names[0]][self.img_names[1]],           (0, 0))
        
        #########################################################
        # Equipment
        if self.img_names[0] in session.img.skin_options:
            
            # Chest
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'chest':
                        if self.handedness == 'left':
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]), (0, 0))
                            else:        surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],     (0, 0))
                        else:
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (0, 0))
                            else:        surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (0, 0))
                    else: pass

            # Armor
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'body':
                        if self.handedness == 'left':
                            if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]),        (0, 0))
                            elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]), (0, 0))
                            else:                 surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],            (0, 0))
                        else:
                            if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (0, 0))
                            elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]),        (0, 0))
                            else:                 surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (0, 0))
                    else: pass

            # Face
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'face':
                        if self.handedness == 'left':
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]), (0, 0))
                            else:        surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],     (0, 0))
                        else:
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (0, 0))
                            else:        surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (0, 0))
                    else: pass
            
            # Hair
            for item in self.equipment.values():
                if item is not None:
                    if item.slot == 'head':
                        if self.handedness == 'left':
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]), (0, 0))
                            else:        surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],     (0, 0))
                        else:
                            if swimming: surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (0, 0))
                            else:        surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (0, 0))
                    else: pass
            
            # Holdables
            for item in self.equipment.values():
                if item is not None:
                    if not item.hidden:
                        if item.role in ['weapons', 'armor']:
                            if item.slot in ['dominant hand', 'non-dominant hand']:
                                if self.handedness == 'left':
                                    if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]]),               (0, 0))
                                    elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]),        (0, 0))
                                    else:                 surface.blit(session.img.dict[item.img_names[0]][self.img_names[1]],                   (0, 0))
                                else:
                                    if swimming:          surface.blit(session.img.halved([item.img_names[0], self.img_names[1]], flipped=True), (0, 0))
                                    elif not self.rand_Y: surface.blit(session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]]),        (0, 0))
                                    else:                 surface.blit(session.img.flipped.dict[item.img_names[0]][self.img_names[1]],           (0, 0))
                            else: pass
        
        pyg.display_queue.append([surface, (X, Y)])

        #########################################################
        # Bubbles
        ## Dialogue
        shift = 32 - session.img.ent_data[self.img_names[0]]['height']
        if self.quest:
            pyg.display_queue.append([session.img.dict['bubbles']['dots bubble'], (X, Y - pyg.tile_height + shift)])
        
        ## Trading
        if self.trade_times:
            if session.player_obj.ent.env.env_time in self.trade_times:
                pyg.display_queue.append([session.img.dict['bubbles']['cart bubble'], (X, Y - pyg.tile_height + shift)])

class Dialogue:
    """ Imports and stores dialogue from JSON files, and returns a random piece of accessible dialogue. """

    def __init__(self):
        """ Initialize dialogue and state containers. The cache dictionary holds all dialogue for all loaded NPCs.
            The states dictionary identifies the current set of dialogue for all loaded NPCs.

            Parameters
            ----------
            dialogue_cache : dict; (key) NPC names → (key) dialogue set identifier → (value) dialogue string
            npc_states     : dict; (key) NPC names → (value) dialogue set identifier
        """

        self.dialogue_cache = {}
        self.npc_states     = {}

        self.subscribe_events()
    
    def load_npc(self, ent_id):
        """ Sends all dialogue to dialogue_cache. """

        if ent_id not in self.dialogue_cache:
            
            self.dialogue_cache[ent_id] = load_json(f'Data/.Dialogue/{ent_id}.json')
            self.npc_states[ent_id]     = "default"

    def unlock_dialogue(self, ent_id, dialogue_id):
        """ Changes current set of available options. """

        self.load_npc(ent_id)
        self.npc_states[ent_id] = dialogue_id

    def get_dialogue(self, ent_id):
        """ Return a random dialogue string from the character's current set of available options. """

        self.load_npc(ent_id)
        key   = self.npc_states.get(ent_id)
        lines = self.dialogue_cache[ent_id].get(key)
        return random.choice(lines)

    def emit_dialogue(self, ent_id, dialogue_id=None):
        """ Loads dialogue, sends it to the GUI, and plays some audio. """

        if dialogue_id:
            self.unlock_dialogue(ent_id, dialogue_id)

        dialogue = self.get_dialogue(ent_id)
        session.pyg.update_gui(dialogue)
        if time.time() - session.aud.last_press_time_speech > session.aud.speech_speed//100:
            session.aud.play_speech(dialogue)

    def subscribe_events(self):
        session.bus.subscribe('unlock_dialogue', self.unlock_dialogue)
        session.bus.subscribe('emit_dialogue',   self.emit_dialogue)

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.subscribe_events()

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

class Effect:

    def __init__(self, name, img_names, function, trigger, sequence, cooldown_time, other):
        
        self.name            = name
        self.img_names       = img_names
        self.function        = function
        
        self.trigger         = trigger
        self.sequence        = sequence
        
        self.cooldown_time   = cooldown_time
        self.last_press_time = 0
        
        self.other           = other

########################################################################################################################################################
# Tools
def create_item(names, effect=False):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names  : string or list of strings; name of object
        effect : bool or Effect object; True=default, False=None, effect=custom """
    
    # Look for item
    item      = None
    item_dict = obj_dicts['items']

    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if val['img_names'] == names:
                item = Item(**val)
    else:       item = Item(**item_dict[names])
    
    # Add effect
    if item:
        effect_dict = obj_dicts['item_effects']

        if effect:
            item.effect = effect

        elif item.name in effect_dict:
            effect = effect_dict[item.name]
            item.effect = Effect(
                name          = effect['name'],
                img_names     = effect['img_names'],
                function      = eval(effect['function']),
                trigger       = effect['trigger'],
                sequence      = effect['sequence'],
                cooldown_time = effect['cooldown_time'],
                other         = effect['other'])
            
        else:
            item.effect = None
    
    # Return if found
    if not item: raise Exception(names)
    else:        return item

def create_entity(names):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names : str; name of object """

    # Look for entity
    ent_dict = obj_dicts['ents']

    if type(names) in [tuple, list]:
        for val in ent_dict.values():
            if val.img_names == names:
                ent            = Entity(**val)
                ent.handedness = random.choice(['left', 'right'])
    else:       ent            = Entity(**ent_dict[names])
    
    # Return if found
    if not ent: raise Exception(names)
    else:        return ent

def create_NPC(name):
    """ A more specific version of create_entity. """
    
    # Look for entity
    ent      = None
    NPC_dict = obj_dicts['NPCs']

    #########################################################
    # Custom
    if name in NPC_dict.keys():
        NPC = NPC_dict[name]

        # Basics
        ent                  = create_entity(NPC['model'])
        ent.name             = NPC['name']
        ent.reach            = NPC['reach']
        
        # Equipment
        for item_type in ['clothes', 'chest', 'hair', 'beard', 'weapon', 'armor']:
            if NPC[item_type]: 
                item = create_item(NPC[item_type])
                session.items.pick_up(item, ent, silent=True)
                session.items.toggle_equip(item, ent, silent=True)
                if NPC['trade_times']: item.hidden = True

        # Trading
        ent.trade_times = NPC['trade_times']
        if NPC['trade_times']:
            for item in NPC['inv']:
                item = create_item(item)
                session.items.pick_up(item, ent, silent=True)
    
    #########################################################
    # Randomly generated
    elif name == 'random':
        
        # Basics
        ent       = create_entity(str(random.choice(session.img.skin_options)))
        ent.name  = random.choice(['Traveler', 'Settler', 'Stranger'])
        ent.reach = 20
        
        # Equipment
        items = {
            'hair':  str(random.choice(session.img.hair_options)),
            'chest': str(random.choice(session.img.chest_options)),
            'armor': str(random.choice(session.img.armor_names))}
        
        for name in items.values():
            item = create_item(name)
            session.items.pick_up(item, ent, silent=True)
            session.items.toggle_equip(item, ent, silent=True)
        
        if items['chest'] == 'flat':
            face = create_item(str(random.choice(session.img.face_options)))
            session.items.pick_up(face, ent, silent=True)
            session.items.toggle_equip(face, ent, silent=True)
        
        ent.lethargy = random.randint(1, 10)

        dialogue_options = [
            [f"{ent.name}: ...",
            f"{ent.name}: I had the strangest dream last night... Huh? Just talking to myself.",
            f"{ent.name}: *seems busy*"],
            [f"{ent.name}: Howdy!",
            f"{ent.name}: Have you seen those cracks in the sand? My neighbor fell right through one!",
            f"{ent.name}: Yeah, Merci is good. I always go to her for clothes and everyday items.",
            f"{ent.name}: Grapes are great for health, but you can't build without concrete!"],
            [f"{ent.name}: Oxi can get whatever you need, but he only sells at night.",
            f"{ent.name}: Sometimes, I just pick weeds for fun. The ground looks nice without them.",
            f"{ent.name}: ...Did you see that? Maybe I should spend less time with Oxi..."]]
    
    return ent

########################################################################################################################################################