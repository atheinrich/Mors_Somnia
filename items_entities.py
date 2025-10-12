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
            temp     : something to do with NewGame """
        
        # Gameplay
        self.ent      = None
        self.ents     = {}
        self.envs     = None
        
        # File management
        self.file_num = 0
        
        # Debugging
        self.temp     = False

    def create_player(self):

        from mechanics import Entity
        
        # Remove from environment
        if self.ent: self.clear_prior()
        
        # Create default entity
        self.ent = Entity(
            name       = 'Player',
            role       = 'player',
            img_names  = ['white', 'front'],

            exp        = 0,
            rank       = 1,
            hp         = 10,
            max_hp     = 10,
            attack     = 0,
            defense    = 1,
            sanity     = 1,
            stamina    = 100,
            
            X          = 0,
            Y          = 0,
            habitat    = 'any',

            follow     = False,
            lethargy   = 5,
            miss_rate  = 10,
            aggression = 0,
            fear       = None,
            reach      = 1000)
        
        # Initialize player-specific attributes
        self.ent.questlog = {}
        self.ent.garden_questlog = {}
        self.ent.discoveries = {}
        
        # Set default discoveries
        self.ent.discoveries = {
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
        
        # Set default items
        hair   = create_item('bald')
        face   = create_item('clean')
        chest  = create_item('flat')
        dagger = create_item('dagger')
        
        hair.pick_up(ent=self.ent)
        face.pick_up(ent=self.ent)
        chest.pick_up(ent=self.ent)
        dagger.pick_up(ent=self.ent)
        
        hair.toggle_equip(self.ent)
        face.toggle_equip(self.ent)
        chest.toggle_equip(self.ent)
        dagger.toggle_equip(self.ent)

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

s = {

    'Kyrio': {
        'name': 'Kyrio',
        'model': 'black',
        'reach': 1000,
        'hair': 'bald',
        'chest': 'flat',
        'clothes': 'exotic clothes',
        'beard': 'white beard',
        'weapon': 'blood dagger',
        'armor': None,
        'dialogue': [
            "Kyrio: *furrows his brow*",
            "Kyrio: Talk to my brother, Kapno. I know little of mercantile.",
            "Kyrio: *seems not to notice*",
            "Kyrio: Is there something you need?"],
        'trade_times': None,
        'inv': None
    },

    'Kapno': {
        'name': 'Kapno',
        'model': 'black',
        'reach': 2,
        'hair': 'bald',
        'chest': 'flat',
        'clothes': 'exotic clothes',
        'beard': 'white beard',
        'weapon': 'blood dagger',
        'armor': None,
        'dialogue': [
            "Kapno: Huh?",
            "Kapno: Too many dry days, it seems. The lake is rather shallow.",
            "Kapno: Have you seen my brother? He seems distracted as of late.",
            "Kapno: My bones may be brittle, but I know good products when I see them.",
            "Kapno: *mumbles*"],
        'trade_times': (
            3,
            4,
            5,
            6),
        'inv': [
            'shovel',
            'sword',
            'iron shield',
            'orange clothes',
            'exotic clothes',
            'jug of blood',
            'jug of grapes',
            'jug of water',
            'jug of cement',
            'boxes',
            'fire',
            'shrooms',
            'cup shroom']
    },

    'Blodo': {
        'name': 'Blodo',
        'model': 'black',
        'reach': 2,
        'hair': 'bald',
        'chest': 'flat',
        'clothes': 'exotic clothes',
        'beard': 'white beard',
        'weapon': 'blood dagger',
        'armor': None,
        'dialogue': [
            "Blodo: Huh?",
            "Blodo: Too many dry days, it seems. The lake is rather shallow.",
            "Blodo: Have you seen my brother? He seems distracted as of late.",
            "Blodo: My bones may be brittle, but I know good products when I see them.",
            "Blodo: *mumbles*"],
        'trade_times': (
            3,
            4,
            5,
            6),
        'inv': [
            'shovel',
            'sword',
            'iron shield',
            'orange clothes',
            'exotic clothes',
            'jug of blood',
            'jug of grapes',
            'jug of water',
            'jug of cement',
            'boxes',
            'fire',
            'shrooms',
            'cup shroom']
    },

    'Erasti': {
        'name': 'Erasti',
        'model': 'black',
        'reach': 10,
        'hair': 'brown hair',
        'chest': 'bra',
        'clothes': 'yellow dress',
        'beard': None,
        'weapon': 'shovel',
        'armor': None,
        'dialogue': [
            "Erasti: ...",
            "Erasti: Are you new to the region? Sorry, my memory is terrible!",
            "Erasti: I know... the town needs work. I guess we should all pitch in.",
            "Erasti: Sorry, I have a lot on my mind.",
            "Erasti: Good to see you!",
            "Erasti: Rumor has it that Kapno stashes a jar of herbs under his bed."],
        'trade_times': None,
        'inv': None
    },

    'Merci': {
        'name': 'Merci',
        'model': 'white',
        'reach': 4,
        'hair': 'blue hair',
        'chest': 'bra',
        'clothes': 'chain dress',
        'beard': None,
        'weapon': 'shovel',
        'armor': None,
        'dialogue': [
            "Merci: Are you looking to buy anything in particular? Please, take a look at my stock.",
            "Merci: We specialize in exotic goods, but the basics are available as well.",
            "Merci: I prefer coins, but I could use the sale. Are you looking to trade?",
            "Merci: Your purchase is free if you can find my keys. I can't sell my blades without them!",
            "Merci: We have many items for sale.",
            "Merci: ... Oh, welcome in!"],
        'trade_times': (
            3,
            4,
            5,
            6),
        'inv': [
            'shovel',
            'chain dress',
            'green clothes',
            'yellow dress',
            'bubbles',
            'plant']
    },

    'Oxi': {
        'name': 'Oxi',
        'model': 'white',
        'reach': 25,
        'hair': 'blue hair',
        'chest': 'flat',
        'clothes': 'orange clothes',
        'beard': 'blue beard',
        'weapon': None,
        'armor': None,
        'dialogue': [
            "Oxi: Yeah, I got it... talk to me later. You'd be surprised by what I can find.",
            "Oxi: Don't run your mouth about this. Just buy and leave.",
            "Oxi: Weren't you just here? Buy what you need, I guess.",
            "Oxi: ..."],
        'trade_times': (
            1,
            2,
            7,
            8),
        'inv': [
            'needle',
            'skin',
            'teeth',
            'bowl',
            'plant',
            'bubbles']
    },

    'Aya': {
        'name': 'Aya',
        'model': 'white',
        'reach': 50,
        'hair': 'brown hair',
        'chest': 'bra',
        'clothes': 'chain dress',
        'beard': None,
        'weapon': 'sword',
        'armor': 'iron shield',
        'dialogue': [
            "Aya: ...",
            "Aya: I chop trees, vines, grass -- whatever needs to be cut.",
            "Aya: Huh, haven't seen you around. Been busy clearing paths.",
            "Aya: Careful! My blades are sharp.",
            "Aya: I can only dream of what's out there, beyond the town.",
            "Aya: The trickle of the lake lulls me to sleep.",
            "Aya: You don't talk much, huh? Just like Kyrio... what a curious old man."],
        'trade_times': None,
        'inv': None
    },

    'Zung': {
        'name': 'Zung',
        'model': 'white',
        'reach': 6,
        'hair': 'bald',
        'chest': 'flat',
        'clothes': 'green clothes',
        'beard': None,
        'weapon': None,
        'armor': None,
        'dialogue': [
            "Zung: ...",
            "Zung: Have you seen my sister, Aya? She's scary, right?",
            "Zung: No, I deal in rumors. If you want goods, ask Merci or Kapno.",
            "Zung: I always thought we were the only town... until recently.",
            "Zung: The jail also houses the bank. Secure? You bet.",
            "Zung: *mumbles something about Erasti and Oxi*",
            "Zung: Kyrio is fit for his age, but he hides it well."],
        'trade_times': None,
        'inv': None
    },

    'Lilao': {
        'name': 'Lilao',
        'model': 'black',
        'reach': 6,
        'hair': 'blue hair',
        'chest': 'bra',
        'clothes': 'yellow dress',
        'beard': None,
        'weapon': None,
        'armor': None,
        'dialogue': [
            "Lilao: ..."],
        'trade_times': None,
        'inv': None
    }

}

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
                item.pick_up(ent=ent)
                item.toggle_equip(ent)
                if NPC['trade_times']: item.hidden = True

        # Trading
        ent.trade_times = NPC['trade_times']
        if NPC['trade_times']:
            for item in NPC['inv']:
                item = create_item(item)
                item.pick_up(ent=ent)
    
    elif name == 'random':
        
        # Basics
        ent       = create_entity(str(random.choice(session.img.skin_options)))
        ent.name  = random.choice(['Traveler', 'Settler', 'Stranger'])
        ent.reach = 20
        
        # Equipment
        hair    = create_item(str(random.choice(session.img.hair_options)))
        bra     = create_item(str(random.choice(session.img.chest_options)))
        clothes = create_item(str(random.choice(session.img.armor_names)))
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        
        if bra.name == 'flat':
            face = create_item(str(random.choice(session.img.face_options)))
            face.pick_up(ent=ent)
            face.toggle_equip(ent)
        
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