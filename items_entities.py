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
from data_management import item_dict, ent_dict

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
        self.function        = function # set as a function in Mechanics
        
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

    effect_dict = {
        'skeleton': Effect(
            name          = 'info',
            img_names     = ['bubbles', 'exclamation'],
            function      = session.mech.skeleton,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'lights': Effect(
            name          = 'lamp',
            img_names     = ['lights', 'dropped'],
            function      = session.mech.lamp,
            trigger       = 'passive',
            sequence      = None,
            cooldown_time = 0,
            other         = 5),

        'needle': Effect(
            name          = 'bowl',
            img_names     = ['drugs', 'bowl'],
            function      = session.mech.enter_hallucination,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'skin': Effect(
            name          = 'bowl',
            img_names     = ['drugs', 'bowl'],
            function      = session.mech.enter_hallucination,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'teeth': Effect(
            name          = 'bowl',
            img_names     = ['drugs', 'bowl'],
            function      = session.mech.enter_bitworld,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'bowl': Effect(
            name          = 'bowl',
            img_names     = ['drugs', 'bowl'],
            function      = session.mech.enter_hallucination,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'plant': Effect(
            name          = 'food',
            img_names     = ['drugs', 'plant'],
            function      = session.mech.boost_stamina,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'bubbles': Effect(
            name          = 'food',
            img_names     = ['drugs', 'bubbles'],
            function      = session.mech.entity_eat,
            trigger       = 'active',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'shovel': Effect(
            name          = 'dirtball',
            img_names     = ['green blob', 'right'],
            function      = session.mech.propagate,
            trigger       = 'active',
            sequence      = '⮞⮜⮞',
            cooldown_time = 1,
            other         = None),

        'super shovel': Effect(
            name          = 'the way of the spade',
            img_names     = ['shovel', 'dropped'],
            function      = session.mech.suicide,
            trigger       = 'active',
            sequence      = '⮟⮟⮟',
            cooldown_time = 1,
            other         = None),

        'dagger': Effect(
            name          = 'swing',
            img_names     = ['dagger', 'dropped'],
            function      = session.mech.swing,
            trigger       = 'active',
            sequence      = '⮜⮟⮞',
            cooldown_time = 0.1,
            other         = None),

        'eye': Effect(
            name          = 'swing',
            img_names     = ['null', 'null'],
            function      = session.mech.swing,
            trigger       = 'passive',
            sequence      = None,
            cooldown_time = 0.1,
            other         = None),

        'lamp': Effect(
            name          = 'lamp',
            img_names     = ['iron shield', 'dropped'],
            function      = session.mech.lamp,
            trigger       = 'passive',
            sequence      = None,
            cooldown_time = 0,
            other         = 5)}

    # Look for item
    item = None
    if type(names) in [tuple, list]:
        for val in item_dict.values():
            if val['img_names'] == names:
                item = Item(**val)
    else:       item = Item(**item_dict[names])
    
    # Add effect
    if item:
        if effect:                     item.effect = effect
        elif item.name in effect_dict: item.effect = effect_dict[item.name]
        else:                          item.effect = None
    
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
    
    if name == 'Kyrio':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Kyrio'
        ent.reach = 1000
        
        # Equipment
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        
        clothes.pick_up(ent=ent)
        beard.pick_up(ent=ent)
        dagger.pick_up(ent=ent)

        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Kyrio: *furrows his brow*",
            "Kyrio: Talk to my brother, Kapno. I know little of mercantile.",
            "Kyrio: *seems not to notice*",
            "Kyrio: Is there something you need?"]
    
    elif name == 'Kapno':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Kapno'
        ent.reach = 2

        # Equipment
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        
        clothes.pick_up(ent=ent)
        beard.pick_up(ent=ent)
        dagger.pick_up(ent=ent)
        
        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Inventory
        ent.trader = [3, 4, 5, 6]
        inv = ['shovel', 'sword', 'iron shield',
               'orange clothes', 'exotic clothes',
               'jug of blood', 'jug of grapes', 'jug of water', 'jug of cement',
               'boxes', 'fire', 'shrooms', 'cup shroom']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Kapno: Huh?",
            "Kapno: Too many dry days, it seems. The lake is rather shallow.",
            "Kapno: Have you seen my brother? He seems distracted as of late.",
            "Kapno: My bones may be brittle, but I know good products when I see them.",
            "Kapno: *mumbles*"]
    
    elif name == 'Blodo':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Blodo'
        ent.reach = 2

        # Equipment
        clothes = create_item('exotic clothes')
        beard   = create_item('white beard')
        dagger  = create_item('blood dagger')
        
        clothes.pick_up(ent=ent)
        beard.pick_up(ent=ent)
        dagger.pick_up(ent=ent)
        
        clothes.toggle_equip(ent)
        beard.toggle_equip(ent)
        dagger.toggle_equip(ent)
        
        # Inventory
        ent.trader = [3, 4, 5, 6]
        inv = ['shovel', 'sword', 'iron shield',
               'orange clothes', 'exotic clothes',
               'jug of blood', 'jug of grapes', 'jug of water', 'jug of cement',
               'boxes', 'fire', 'shrooms', 'cup shroom']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Blodo: Huh?",
            "Blodo: Too many dry days, it seems. The lake is rather shallow.",
            "Blodo: Have you seen my brother? He seems distracted as of late.",
            "Blodo: My bones may be brittle, but I know good products when I see them.",
            "Blodo: *mumbles*"]
    
    elif name == 'Erasti':
        
        # Basics
        ent       = create_entity('black')
        ent.name  = 'Erasti'
        ent.reach = 10
        
        # Equipment
        hair    = create_item('brown hair')
        bra     = create_item('bra')
        clothes = create_item('yellow dress')
        shovel  = create_item('shovel')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        shovel.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        shovel.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Erasti: ...",
            "Erasti: Are you new to the region? Sorry, my memory is terrible!",
            "Erasti: I know... the town needs work. I guess we should all pitch in.",
            "Erasti: Sorry, I have a lot on my mind.",
            "Erasti: Good to see you!",
            "Erasti: Rumor has it that Kapno stashes a jar of herbs under his bed."]
    
    elif name == 'Merci':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Merci'
        ent.reach = 4
        
        # Equipment
        hair    = create_item('blue hair')
        bra     = create_item('bra')
        clothes = create_item('chain dress')
        shovel  = create_item('shovel')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        shovel.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        shovel.toggle_equip(ent)
        
        # Inventory
        ent.trader = [3, 4, 5, 6]
        inv = ['shovel',
               'chain dress', 'green clothes', 'yellow dress',
               'bubbles', 'plant']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Merci: Are you looking to buy anything in particular? Please, take a look at my stock.",
            "Merci: We specialize in exotic goods, but the basics are available as well.",
            "Merci: I prefer coins, but I could use the sale. Are you looking to trade?",
            "Merci: Your purchase is free if you can find my keys. I can't sell my blades without them!",
            "Merci: We have many items for sale.",
            "Merci: ... Oh, welcome in!"]
    
    elif name == 'Oxi':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Oxi'
        ent.reach = 25
        
        # Equipment
        hair    = create_item('blue hair')
        face    = create_item('blue beard')
        clothes = create_item('orange clothes')
        
        hair.pick_up(ent=ent)
        face.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        face.toggle_equip(ent)
        clothes.toggle_equip(ent)
        clothes.hidden = True
        
        # Inventory
        ent.trader = [1, 2, 7, 8]
        inv = ['needle', 'skin', 'teeth', 'bowl', 'plant', 'bubbles']
        for item in inv:
            item = create_item(item)
            item.pick_up(ent=ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Oxi: Yeah, I got it... talk to me later. You'd be surprised by what I can find.",
            "Oxi: Don't run your mouth about this. Just buy and leave.",
            "Oxi: Weren't you just here? Buy what you need, I guess.",
            "Oxi: ..."]
    
    elif name == 'Aya':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Aya'
        ent.reach = 50
        
        # Equipment
        hair    = create_item('brown hair')
        bra     = create_item('bra')
        clothes = create_item('chain dress')
        sword  = create_item('sword')
        shield  = create_item('iron shield')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        sword.pick_up(ent=ent)
        shield.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        sword.toggle_equip(ent)
        shield.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Aya: ...",
            "Aya: I chop trees, vines, grass -- whatever needs to be cut.",
            "Aya: Huh, haven't seen you around. Been busy clearing paths.",
            "Aya: Careful! My blades are sharp.",
            "Aya: I can only dream of what's out there, beyond the town.",
            "Aya: The trickle of the lake lulls me to sleep.",
            "Aya: You don't talk much, huh? Just like Kyrio... what a curious old man."]
    
    elif name == 'Zung':
        
        # Basics
        ent       = create_entity('white')
        ent.name  = 'Zung'
        ent.reach = 6
        
        # Equipment
        hair    = create_item('bald')
        clothes = create_item('green clothes')
        
        hair.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        clothes.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Zung: ...",
            "Zung: Have you seen my sister, Aya? She's scary, right?",
            "Zung: No, I deal in rumors. If you want goods, ask Merci or Kapno.",
            "Zung: I always thought we were the only town... until recently.",
            "Zung: The jail also houses the bank. Secure? You bet.",
            "Zung: *mumbles something about Erasti and Oxi*",
            "Zung: Kyrio is fit for his age, but he hides it well."]
    
    elif name == 'Lilao':
        
        # Basics
        ent     = create_entity('black')
        ent.name  = 'Lilao'
        ent.reach = 15
        
        # Equipment
        hair    = create_item('blue hair')
        bra     = create_item('bra')
        clothes = create_item('yellow dress')
        
        hair.pick_up(ent=ent)
        bra.pick_up(ent=ent)
        clothes.pick_up(ent=ent)
        
        hair.toggle_equip(ent)
        bra.toggle_equip(ent)
        clothes.toggle_equip(ent)
        
        # Dialogue
        ent.default_dialogue = [
            "Lilao: ..."]
    
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
            ["NPC: ...",
            "NPC: I had the strangest dream last night... Huh? Just talking to myself.",
            "NPC: *seems busy*"],
            ["NPC: Howdy!",
            "NPC: Have you seen those cracks in the sand? My neighbor fell right through one!",
            "NPC: Yeah, Merci is good. I always go to her for clothes and everyday items.",
            "NPC: Grapes are great for health, but you can't build without concrete!"],
            ["NPC: Oxi can get whatever you need, but he only sells at night.",
            "NPC: Sometimes, I just pick weeds for fun. The ground looks nice without them.",
            "NPC: ...Did you see that? Maybe I should spend less time with Oxi..."]]

        ent.default_dialogue = random.choice(dialogue_options)
    
    return ent

########################################################################################################################################################