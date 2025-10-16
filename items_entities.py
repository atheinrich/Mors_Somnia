########################################################################################################################################################
# Item creation and management
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random

## Local
import session
from data_management import item_dict, effect_dict, ent_dict, NPC_dict

########################################################################################################################################################

########################################################################################################################################################
# Classes
class Player:
    """ Manages player file. One save for each file. """

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
        
        # Mechanics
        self.ent        = None
        self.ents       = {}
        self.envs       = None
        self.file_num   = 0
        self.temp       = False

        # Default entity parameters
        self.name       = 'Player'
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

        # Default player parameters
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
    
    from mechanics import Item

    # Look for item
    item = None
    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if val['img_names'] == names:
                item = Item(**val)
    else:       item = Item(**item_dict[names])
    
    # Add effect
    if item:
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

    from mechanics import Entity

    # Look for entity
    item = None
    if type(names) in [tuple, list]:
        for val in ent_dict.values():
            if val.img_names == names:
                ent = Entity(**val)
                ent.handedness = random.choice(['left', 'right'])
    else:       ent = Entity(**ent_dict[names])
    
    # Return if found
    if not ent: raise Exception(names)
    else:        return ent

def create_NPC(name):
    """ A more specific version of create_entity. """
    
    # Look for entity
    ent = None
    if name in NPC_dict.keys():
        NPC = NPC_dict[name]

        # Basics
        ent                  = create_entity(NPC['model'])
        ent.name             = NPC['name']
        ent.reach            = NPC['reach']
        ent.default_dialogue = NPC['dialogue']
        
        # Equipment
        for item_type in ['clothes', 'chest', 'hair', 'beard', 'weapon', 'armor']:
            if NPC[item_type]: 
                item = create_item(NPC[item_type])
                item.pick_up(ent, silent=True)
                item.toggle_equip(ent, silent=True)
                if NPC['trade_times']: item.hidden = True

        # Trading
        ent.trade_times = NPC['trade_times']
        if NPC['trade_times']:
            for item in NPC['inv']:
                item = create_item(item)
                item.pick_up(ent, silent=True)
    
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
            item.pick_up(ent,      silent=True)
            item.toggle_equip(ent, silent=True)
        
        if items['chest'] == 'flat':
            face = create_item(str(random.choice(session.img.face_options)))
            face.pick_up(ent,      silent=True)
            face.toggle_equip(ent, silent=True)
        
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

        ent.default_dialogue = random.choice(dialogue_options)
    
    return ent

########################################################################################################################################################