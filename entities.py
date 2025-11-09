########################################################################################################################################################
# Entity creation and management
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
    
    # Core
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
        self.wallet      = 100
        self.trade_times = None
        self.inventory   = {'weapons': [], 'armor': [],  'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
        self.equipment   = {'head': None,  'face': None, 'chest': None, 'body': None,  'dominant hand': None, 'non-dominant hand': None}
        
        ## Randomizer
        self.rand_X = random.randint(-pyg.tile_width,  pyg.tile_width)
        self.rand_Y = random.randint(-pyg.tile_height, pyg.tile_height)

        #########################################################
        # Initialize reactions and abilities
        self.garden_abilities = {
            'entity_scare':   session.abilities.create_ability(self, 'entity_scare'),
            'entity_comfort': session.abilities.create_ability(self, 'entity_comfort'),
            'entity_clean':   session.abilities.create_ability(self, 'entity_clean')}
        
        self.game_abilities = {
            'entity_scare':   session.abilities.create_ability(self, 'entity_scare'),
            'entity_capture': session.abilities.create_ability(self, 'entity_capture'),
            'suicide':        session.abilities.create_ability(self, 'suicide')}
        
        self.active_effects   = {}
        self.active_abilities = {}

    # Utility
    def quest_active(self):
        """ Returns True if the current dialogue set is related to a quest.
            For this to work, set quest_ as a prefix for all quest IDs.    
        """

        if self.name in session.player_obj.dialogue.npc_states.keys():
            if session.player_obj.dialogue.npc_states[self.name][:5] == 'quest_':
                return True
        return False

    def trade_active(self):
        """ Returns True if the entity is a trader and if the current time matches their shop hours. """

        if self.trade_times:
            if session.player_obj.ent.env.env_time in self.trade_times:
                return True
        return False

    # Rendering
    def _find_body(self, swimming):
        
        ## Left handed
        if self.handedness == 'left': 

            if swimming: img = session.img.halved([self.img_names[0], self.img_names[1]])
            else:        img = session.img.dict[self.img_names[0]][self.img_names[1]]
        
        ## Right handed
        else:

            if swimming: img = session.img.halved([self.img_names[0], self.img_names[1]], flipped=True)
            else:        img = session.img.flipped.dict[self.img_names[0]][self.img_names[1]]

        return img
    
    def _find_chest(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'chest':

                    if self.handedness == 'left':
                        if swimming: img = session.img.halved([item.img_names[0], self.img_names[1]])
                        else:        img = session.img.dict[item.img_names[0]][self.img_names[1]]

                    else:
                        if swimming: img = session.img.halved([item.img_names[0], self.img_names[1]], flipped=True)
                        else:        img = session.img.flipped.dict[item.img_names[0]][self.img_names[1]]
                    
                    return img

    def _find_armor(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'body':

                    if self.handedness == 'left':
                        if swimming:          img = session.img.halved([item.img_names[0], self.img_names[1]])
                        elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]])
                        else:                 img = session.img.dict[item.img_names[0]][self.img_names[1]]
                    
                    else:
                        if swimming:          img = session.img.halved([item.img_names[0], self.img_names[1]], flipped=True)
                        elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]])
                        else:                 img = session.img.flipped.dict[item.img_names[0]][self.img_names[1]]
                    
                    return img

    def _find_face(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'face':

                    if self.handedness == 'left':
                        if swimming: img = session.img.halved([item.img_names[0], self.img_names[1]])
                        else:        img = session.img.dict[item.img_names[0]][self.img_names[1]]
                    
                    else:
                        if swimming: img = session.img.halved([item.img_names[0], self.img_names[1]], flipped=True)
                        else:        img = session.img.flipped.dict[item.img_names[0]][self.img_names[1]]
                    
                    return img
        
    def _find_hair(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'head':
                    
                    if self.handedness == 'left':
                        if swimming: img = session.img.halved([item.img_names[0], self.img_names[1]])
                        else:        img = session.img.dict[item.img_names[0]][self.img_names[1]]
                    
                    else:
                        if swimming: img = session.img.halved([item.img_names[0], self.img_names[1]], flipped=True)
                        else:        img = session.img.flipped.dict[item.img_names[0]][self.img_names[1]]
                    
                    return img
        
    def _find_holdables(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if not item.hidden:
                    if item.role in ['weapons', 'armor']:
                        if item.slot in ['dominant hand', 'non-dominant hand']:
                            
                            if self.handedness == 'left':
                                if swimming:          img = session.img.halved([item.img_names[0], self.img_names[1]])
                                elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]])
                                else:                 img = session.img.dict[item.img_names[0]][self.img_names[1]]
                            
                            else:
                                if swimming:          img = session.img.halved([item.img_names[0], self.img_names[1]], flipped=True)
                                elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_names[0]][self.img_names[1]])
                                else:                 img = session.img.flipped.dict[item.img_names[0]][self.img_names[1]]
                            
                            return img
    
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
        ## Toggle lower half
        if self.tile.biome in session.img.biomes['sea']: swimming = True
        else:                                            swimming = False

        ## Body
        img = self._find_body(swimming)
        surface.blit(img, (0, 0))
    
        ## Equipment for humanoids
        if self.img_names[0] in session.img.skin_options:
            img_finders = [
                self._find_chest,
                self._find_armor,
                self._find_face,
                self._find_hair,
                self._find_holdables]
            
            for img_finder in img_finders:
                img = img_finder(swimming)
                if img is not None: surface.blit(img, (0, 0))
        
        pyg.display_queue.append([surface, (X, Y)])

        #########################################################
        # Bubbles
        bubble = None
        shift = 32 - session.img.ent_data[self.img_names[0]]['height']

        if self.quest_active():                bubble = 'dots bubble'
        if self.trade_active() and not bubble: bubble = 'cart bubble'
        
        if bubble:
            pyg.display_queue.append([session.img.dict['bubbles'][bubble], (X, Y - pyg.tile_height + shift)])

class Dialogue:
    """ Imports and stores dialogue from JSON files, and returns a random piece of accessible dialogue.
        Handled automatically in the InteractionSystem and in Quest objects via event subscription.
    """

    # Core
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

        self._subscribe_events()

    def _load_npc(self, ent_id):
        """ Sends all dialogue to dialogue_cache. """

        if ent_id not in self.dialogue_cache:
            
            self.dialogue_cache[ent_id] = load_json(f'Data/.Dialogue/{ent_id}.json')
            self.npc_states[ent_id]     = "default"

    def _get_dialogue(self, ent_id):
        """ Return a random dialogue string from the character's current set of available options. """

        self._load_npc(ent_id)
        key   = self.npc_states.get(ent_id)
        lines = self.dialogue_cache[ent_id].get(key)
        return random.choice(lines)

    def _subscribe_events(self):
        session.bus.subscribe('unlock_dialogue', self.unlock_dialogue)
        session.bus.subscribe('emit_dialogue',   self.emit_dialogue)

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._subscribe_events()

    # Actions
    def unlock_dialogue(self, ent_id, dialogue_id):
        """ Changes current set of available options. """

        self._load_npc(ent_id)
        self.npc_states[ent_id] = dialogue_id

    def emit_dialogue(self, ent_id, dialogue_id=None):
        """ Loads dialogue, sends it to the GUI, and plays some audio. """

        if dialogue_id:
            self.unlock_dialogue(ent_id, dialogue_id)

        dialogue = self._get_dialogue(ent_id)
        session.pyg.update_gui(dialogue)
        if time.time() - session.aud.last_press_time_speech > session.aud.speech_speed//100:
            session.aud.last_press_time_speech = time.time()
            session.aud.play_speech(dialogue)

########################################################################################################################################################
# Tools
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
                item = session.items.create_item(NPC[item_type])
                session.items.pick_up(ent, item, silent=True)
                session.items.toggle_equip(item, silent=True)
                if NPC['trade_times']: item.hidden = True

        # Trading
        ent.trade_times = NPC['trade_times']
        if NPC['trade_times']:
            for item in NPC['inv']:
                item = session.items.create_item(item)
                session.items.pick_up(ent, item, silent=True)
    
    #########################################################
    # Randomly generated
    elif name == 'random':
        
        # Basics
        ent       = create_entity(str(random.choice(session.img.skin_options)))
        ent.name  = random.choice(['traveler', 'settler', 'stranger'])
        ent.reach = 20
        
        # Equipment
        items = {
            'hair':  str(random.choice(session.img.hair_options)),
            'chest': str(random.choice(session.img.chest_options)),
            'armor': str(random.choice(session.img.armor_names))}
        
        for name in items.values():
            item = session.items.create_item(name)
            session.items.pick_up(ent, item, silent=True)
            session.items.toggle_equip(item, silent=True)
        
        if items['chest'] == 'flat':
            face = session.items.create_item(str(random.choice(session.img.face_options)))
            session.items.pick_up(ent, face, silent=True)
            session.items.toggle_equip(face, silent=True)
        
        ent.lethargy = random.randint(1, 10)
    
    return ent

########################################################################################################################################################