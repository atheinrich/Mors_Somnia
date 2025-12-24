########################################################################################################################################################
# Entity creation and management
#
# The player is stored as session.player_obj.ent; all others are stored in a list (env.ents).
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import time
import copy

## Specific
import pygame

## Local
import session
from data_management import ent_dicts, NPC_dicts, load_json
from items import create_item

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
        self.envs       = None
        self.dialogue   = None

        # Utility
        self.file_num = 0

    # Startup
    def new_player_ent(self):
        from mechanics import place_player

        # Initialize entity, womb, and garden
        self.ent  = self._new_entity()
        self.envs = self._new_environments()

        # Dialogue
        self.dialogue_cache  = {}
        self.dialogue_states = {}

        self.ent.last_env = self.envs.areas['underworld']['womb']
        place_player(
            ent = self.ent,
            env = self.envs.areas['underworld']['womb'],
            loc = self.envs.areas['underworld']['womb'].center)

    def _new_entity(self):
        
        #############################################
        # Entity
        ent = create_entity('white_skin')

        ent.name        = "player"
        ent.ent_id      = 'player'
        ent.role        = 'player'

        ent.hp          = 10
        ent.max_hp      = 10
        ent.attack      = 0
        ent.defense     = 1

        ent.player_id   = random.randint(100_000_000, 999_999_999)

        #############################################
        # Abilities
        ent.garden_abilities = {
            'entity_scare':   session.abilities.create_ability(ent, 'entity_scare'),
            'entity_comfort': session.abilities.create_ability(ent, 'entity_comfort'),
            'entity_clean':   session.abilities.create_ability(ent, 'entity_clean')}
        
        ent.game_abilities = {
            'entity_scare':   session.abilities.create_ability(ent, 'entity_scare'),
            'entity_capture': session.abilities.create_ability(ent, 'entity_capture'),
            'suicide':        session.abilities.create_ability(ent, 'suicide')}

        #############################################
        # Items
        for item_name in ['bald', 'clean', 'flat', 'dagger']:
            item = create_item(item_name)
            session.items.pick_up(ent, item, silent=True)
            session.items.toggle_equip(item, silent=True)

        #############################################
        # Discoveries
        ent.discoveries = Discoveries()
        
        walls     = ['gray', 'green']
        floors    = ['grass4', 'wood', 'water']
        stairs    = ['door']
        decor     = ['blades', 'lights']
        furniture = ['table', 'red_chair_left', 'red_chair_right']
        starter_disc = walls + floors + stairs + decor + furniture

        for object_ID in starter_disc:
            ent.discoveries.add_discovery(object_ID)
        
        return ent

    def _new_environments(self):
        from environments import Environments

        envs = Environments(self)

        # Womb and garden
        envs.add_area('underworld', permadeath=True)
        envs.areas['underworld'].add_level('womb')
        envs.areas['underworld'].add_level('garden')

        return envs

    def finalize_player_ent(self):
        from mechanics import place_player

        # Create and equip items
        self._finalize_entity()

        # Add additional environments
        self._finalize_environments()

        place_player(
            ent = self.ent,
            env = self.envs.areas['overworld']['home'],
            loc = self.envs.areas['overworld']['home'].center)
    
    def _finalize_entity(self):

        # Shovel
        item = create_item('shovel')
        item.uses = 25
        session.items.pick_up(self.ent, item, silent=True)
        session.items.toggle_equip(item, silent=True)

        # Clothes
        clothes = None
        if self.ent.equipment['chest'].img_IDs[0] == 'bra': clothes = 'yellow_dress'
        else:                                               clothes = 'green_clothes'
        item = create_item(clothes)
        session.items.pick_up(self.ent, item, silent=True)
        session.items.toggle_equip(item, silent=True)

        # Lamp and debugging
        apparel = ['lamp', 'orange_clothes', 'exotic_clothes', 'yellow_dress', 'chain_dress', 'iron_armor']
        for ID in apparel:
            item = create_item(ID)
            session.items.pick_up(self.ent, item, silent=True)

        # Debugging
        furniture = ["red_bed", "table", "red_chair_left", "red_chair_right"]
        for ID in furniture:
            item = create_item(ID)
            session.items.pick_up(self.ent, item, silent=True)

        # Debugging
        decor = ['tree', 'bones', 'boxes', 'fire', 'leafy', 'skeleton', 'shrooms', 'cup_shroom', 'frond', 'blades', 'purple_bulbs', 'lights']
        for ID in decor:
            item = create_item(ID)
            session.items.pick_up(self.ent, item, silent=True)

        # Debugging
        weapons = ['super_shovel', 'sword', 'blood_sword', 'blood_dagger']
        for ID in weapons:
            item = create_item(ID)
            session.items.pick_up(self.ent, item, silent=True)

    def _finalize_environments(self):

        self.envs.add_area('overworld', permadeath=True)
        self.envs.areas['overworld'].add_level('home')
        self.envs.areas['overworld'].add_level('overworld')

class Entity:
    """ Player, enemies, and NPCs. Manages stats, inventory, and basic mechanics. """
    
    # Core
    def __init__(self, ent_id, **kwargs):
        """ Parameters
            ----------
            player_obj     : PlayerData object

            name           : string
            role           : string in ['player', 'enemy', 'NPC']
            img_IDs        : list of strings
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

            inventory      : dict of categories with lists of item instances
            equipment      : dict of categories with lists of item instances
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

        self.ent_id = ent_id
        
        ## Images
        self.img_names_backup = self.img_IDs
        self.direction        = self.img_IDs[1]
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
        self.last_dialogue_time = 0

        ## Randomizer
        self.rand_X = random.randint(-pyg.tile_width,  pyg.tile_width)
        self.rand_Y = random.randint(-pyg.tile_height, pyg.tile_height)

        #########################################################
        # Initialize effects and abilities
        self.game_abilities = {}
        for ability_id in self.ability_ids:
            self.game_abilities[ability_id] = session.abilities.create_ability(self, ability_id)
        self.active_abilities = self.game_abilities

        self.active_effects   = {}

    # Utility
    def quest_active(self):
        """ Returns True if the current dialogue is related to a quest.
            Assumes quest IDs start with 'quest_'.
        """

        state = session.player_obj.dialogue_states.get(self.name)
        if state:
            dialogue_id = state.get("dialogue_id", "")
            return dialogue_id.startswith("quest_")
        return False

    def trade_active(self):
        """ Returns True if the entity is a trader and if the current time matches their shop hours. """

        if self.trade_times:
            if session.player_obj.ent.env.env_time in self.trade_times:
                return True
        return False

    def get_pos(self, pixels=False):
        pyg = session.pyg
        if pixels: return (self.X, self.Y)
        else:      return (self.X//pyg.tile_width, self.Y//pyg.tile_height)

    # Rendering
    def _find_body(self, swimming):
        
        ## Left handed
        if self.handedness == 'left': 

            if swimming: img = session.img.halved([self.img_IDs[0], self.img_IDs[1]])
            else:        img = session.img.dict[self.img_IDs[0]][self.img_IDs[1]]
        
        ## Right handed
        else:

            if swimming: img = session.img.halved([self.img_IDs[0], self.img_IDs[1]], flipped=True)
            else:        img = session.img.flipped.dict[self.img_IDs[0]][self.img_IDs[1]]

        return img
    
    def _find_chest(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'chest':

                    if self.handedness == 'left':
                        if swimming: img = session.img.halved([item.img_IDs[0], self.img_IDs[1]])
                        else:        img = session.img.dict[item.img_IDs[0]][self.img_IDs[1]]

                    else:
                        if swimming: img = session.img.halved([item.img_IDs[0], self.img_IDs[1]], flipped=True)
                        else:        img = session.img.flipped.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    return img

    def _find_armor(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'body':

                    if self.handedness == 'left':
                        if swimming:          img = session.img.halved([item.img_IDs[0], self.img_IDs[1]])
                        elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_IDs[0]][self.img_IDs[1]])
                        else:                 img = session.img.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    else:
                        if swimming:          img = session.img.halved([item.img_IDs[0], self.img_IDs[1]], flipped=True)
                        elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_IDs[0]][self.img_IDs[1]])
                        else:                 img = session.img.flipped.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    return img

    def _find_face(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'face':

                    if self.handedness == 'left':
                        if swimming: img = session.img.halved([item.img_IDs[0], self.img_IDs[1]])
                        else:        img = session.img.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    else:
                        if swimming: img = session.img.halved([item.img_IDs[0], self.img_IDs[1]], flipped=True)
                        else:        img = session.img.flipped.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    return img
        
    def _find_hair(self, swimming):

        for item in self.equipment.values():
            if item is not None:
                if item.slot == 'head':
                    
                    if self.handedness == 'left':
                        if swimming: img = session.img.halved([item.img_IDs[0], self.img_IDs[1]])
                        else:        img = session.img.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    else:
                        if swimming: img = session.img.halved([item.img_IDs[0], self.img_IDs[1]], flipped=True)
                        else:        img = session.img.flipped.dict[item.img_IDs[0]][self.img_IDs[1]]
                    
                    return img
        
    def _find_holdables(self, swimming):

        img_list = []
        for item in self.equipment.values():
            if item is not None:
                if not item.hidden:
                    if item.role in ['weapons', 'armor']:
                        if item.slot in ['dominant hand', 'non-dominant hand']:
                            
                            if self.handedness == 'left':
                                if swimming:          img = session.img.halved([item.img_IDs[0], self.img_IDs[1]])
                                elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_IDs[0]][self.img_IDs[1]])
                                else:                 img = session.img.dict[item.img_IDs[0]][self.img_IDs[1]]
                            
                            else:
                                if swimming:          img = session.img.halved([item.img_IDs[0], self.img_IDs[1]], flipped=True)
                                elif not self.rand_Y: img = session.img.scale(session.img.dict[self.img_IDs[0]][self.img_IDs[1]])
                                else:                 img = session.img.flipped.dict[item.img_IDs[0]][self.img_IDs[1]]
                            
                            img_list.append(img)
        return img_list
    
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
        if self.img_IDs[0] in session.img.skin_options:
            img_finders = [
                self._find_chest,
                self._find_armor,
                self._find_face,
                self._find_hair,
                self._find_holdables]
            
            for img_finder in img_finders:
                img = img_finder(swimming)
                if img is not None:
                    if isinstance(img, list):
                        for item in img:
                            surface.blit(item, (0, 0))
                    else:
                        surface.blit(img, (0, 0))
        
        pyg.display_queue.append([surface, (X, Y)])

        #########################################################
        # Bubbles
        bubble = None
        shift  = 32 - session.img.ent_data[self.img_IDs[0]]['height']

        if self.quest_active():                bubble = 'dots_bubble'
        if self.trade_active() and not bubble: bubble = 'cart_bubble'
        
        if bubble:
            loc = (X, Y - pyg.tile_height + shift)
            pyg.display_queue.append([session.img.dict['bubbles'][bubble], loc])

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
            dialogue_cache  : dict; all dialogue
                (key) NPC name → (key) dialogue ID → (value) list of dialogue strings
            dialogue_states : dict; current ID;
                (key) NPC name → (value) current quest ID, current dialogue ID, or dict of dialogue IDs in queue
        
            Schematic
            ---------
            load quest: {"event_id": "unlock_dialogue", "ent_id": <>, "dialogue_id": <>, "owner_id": <>}
            trigger:    dialogue.emit_dialogue(target.ent_id)
            end quest:  {"event_id": "release_dialogue", "ent_id": <>, "owner_id": <>}]}
        """

        session.bus.subscribe('unlock_dialogue',  self.unlock_dialogue)
        session.bus.subscribe('emit_dialogue',    self.emit_dialogue)
        session.bus.subscribe('release_dialogue', self.release_dialogue)

    def _load_npc(self, ent_id):
        """ Sends all dialogue to dialogue_cache. """

        cache  = session.player_obj.dialogue_cache
        states = session.player_obj.dialogue_states

        if ent_id not in cache:
            
            cache[ent_id]  = load_json(f'Data/.Dialogue/{ent_id}.json')
            states[ent_id] = {
                'dialogue_id': 'default', # ex. 'quest_1_dialogue_1'
                'owner_id':    None,      # ex. 'quest_1'
                'queue':       {}}        # ex. {'quest_2': 'quest_2_dialogue_1'}

    def _get_dialogue(self, ent_id):
        """ Return a random dialogue string from the character's current set of available options. """
        
        cache  = session.player_obj.dialogue_cache
        states = session.player_obj.dialogue_states

        self._load_npc(ent_id)
        key   = states[ent_id]["dialogue_id"]
        lines = cache[ent_id].get(key, [])
        return random.choice(lines) if lines else ""

    # Events
    def unlock_dialogue(self, ent_id, dialogue_id, owner_id):
        """ Changes current set of available options.
            Keeps the current quest at the top, and adds new quests to the queue.
        """

        # Handle more than one entity
        if isinstance(ent_id, str): ent_id = [ent_id]
        for id in ent_id:

            self._load_npc(id)
            state = session.player_obj.dialogue_states[id]

            # Make quest the current owner
            if state['owner_id'] is None:
                state['owner_id']    = owner_id
                state['dialogue_id'] = dialogue_id
            
            # Update dialogue for current owner
            elif state['owner_id'] == owner_id:
                state['dialogue_id'] = dialogue_id

            # Defer new quest dialogue to the queue
            elif owner_id in state['queue']:

                # Update existing queue entry without changing its position
                state['queue'][owner_id] = dialogue_id
            else:

                # Add new entry to the end
                state['queue'][owner_id] = dialogue_id

    def release_dialogue(self, ent_id, owner_id):
        """ Release dialogue ownership and hand off to the next queued quest if present. """

        # Handle more than one entity
        if isinstance(ent_id, str): ent_id = [ent_id]
        for id in ent_id:
            state = session.player_obj.dialogue_states[id]

            # Remove current owner
            if state['owner_id'] == owner_id:
                state['owner_id'] = None

                # Add new owner and remove it from the queue
                if state['queue']:
                    next_owner_id        = next(iter(state['queue']))
                    state['owner_id']    = next_owner_id
                    state['dialogue_id'] = state['queue'].pop(next_owner_id)
                
                # Return to default dialogue
                else:
                    state['dialogue_id'] = "default"

            # Remove from the queue
            elif owner_id in state['queue']:
                state['queue'].pop(owner_id)

    def emit_dialogue(self, ent_id):
        """ Loads dialogue, sends it to the GUI, and plays some audio. """

        dialogue = self._get_dialogue(ent_id)
        session.pyg.update_gui(dialogue)

        if time.time() - session.aud.last_press_time_speech > session.aud.speech_speed//100:
            session.aud.last_press_time_speech = time.time()
            session.aud.play_speech(dialogue)

class Discoveries:
    
    # Core
    def __init__(self):
        self.discoveries = {
            'walls':     [],
            'floors':    [],
            'stairs':    [],
            'decor':     [],
            'furniture': [],
            'paths':     [],
            'entities':  []}

    def add_discovery(self, object_ID):
        from environments import create_tile
        from entities import create_entity

        try:
            obj = create_item(object_ID)
            self.discoveries[obj.img_IDs[0]].append(obj)
        
        except:
            try:
                obj = create_tile(object_ID)
                self.discoveries[obj.img_IDs[0]].append(obj)
            
            except:
                obj = create_entity(object_ID)
                self.discoveries['entities'].append(obj)

    # Dictionary methods
    def __getitem__(self, key):
        return self.discoveries[key]

    def __setitem__(self, key, value):
        self.discoveries[key] = value

    def __delitem__(self, key):
        del self.discoveries[key]

    def __iter__(self):
        return iter(self.discoveries)

    def items(self):
        return self.discoveries.items()

########################################################################################################################################################
# Tools
def create_entity(ent_id):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names : str; name of object """

    json_data = copy.deepcopy(ent_dicts[ent_id])
    ent       = Entity(ent_id, **json_data)
    
    # Return if found
    if not ent: raise Exception(ent_id)
    else:       return ent

def create_NPC(NPC_id):
    """ A more specific version of create_entity. """
    
    ent = None

    #########################################################
    # Custom
    if NPC_id in NPC_dicts.keys():
        NPC = copy.deepcopy(NPC_dicts[NPC_id])

        # Basics
        ent        = create_entity(NPC['model'])
        ent.role   = 'NPC'
        ent.name   = NPC['name']
        ent.reach  = NPC['reach']
        ent.ent_id = NPC_id
        
        # Equipment
        for item_type in ['clothes', 'chest', 'hair', 'beard', 'weapon', 'armor']:
            if NPC[item_type]: 
                item = create_item(NPC[item_type])
                session.items.pick_up(ent, item, silent=True)
                session.items.toggle_equip(item, silent=True)
                if NPC['trade_times']: item.hidden = True

        # Trading
        ent.trade_times = NPC['trade_times']
        if NPC['trade_times']:
            for item in NPC['inv']:
                item = create_item(item)
                session.items.pick_up(ent, item, silent=True)
    
    #########################################################
    # Randomly generated
    elif NPC_id == 'random':
        
        # Basics
        ent        = create_entity(str(random.choice(session.img.skin_options)))
        ent.name   = random.choice(['traveler', 'settler', 'stranger'])
        ent.reach  = 20
        ent.ent_id = ent.name
        
        # Equipment
        items = {
            'hair':  str(random.choice(session.img.hair_options)),
            'chest': str(random.choice(session.img.chest_options)),
            'armor': str(random.choice(session.img.armor_names))}
        
        for name in items.values():
            item = create_item(name)
            session.items.pick_up(ent, item, silent=True)
            session.items.toggle_equip(item, silent=True)
        
        if items['chest'] == 'flat':
            face = create_item(str(random.choice(session.img.face_options)))
            session.items.pick_up(ent, face, silent=True)
            session.items.toggle_equip(face, silent=True)
        
        ent.lethargy = random.randint(1, 10)
    
    return ent

########################################################################################################################################################