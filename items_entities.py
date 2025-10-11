########################################################################################################################################################
# Item creation and management
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random

## Modules
import session

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
item_dict = {

## Decor (decor_options)

    'tree': {
        'name':           'tree',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'tree'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        True,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'bones': {
        'name':           'bones',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'bones'],

        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           5,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'boxes': {
        'name':           'boxes',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'boxes'],

        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           5,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'fire': {
        'name':           'fire',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'fire'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'leafy': {
        'name':           'leafy tree',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'leafy'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        True,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         2,
        'cost':           25,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'skeleton': {
        'name':           'skeleton',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'skeleton'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'shrooms': {
        'name':           'shrooms',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'shrooms'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        False,
        'rand_X':         10,
        'rand_Y':         10,
        'cost':           15,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red plant left': {
        'name':           'red plant left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'red plant left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           15,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red plant right': {
        'name':           'red plant right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'red plant right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           15,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'cup shroom': {
        'name':           'cup shroom',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'cup shroom'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           15,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'frond': {
        'name':           'frond',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'frond'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           15,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'blades': {
        'name':           'blades',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'blades'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         10,
        'rand_Y':         10,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'purple bulbs': {
        'name':           'purple bulbs',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'purple bulbs'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         10,
        'rand_Y':         10,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'lights': {
        'name':           'lights',
        'role':           'other',
        'slot':           None,
        'img_names':      ['decor', 'lights'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         5,
        'rand_Y':         5,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Dialogue bubbles (bubbles_options)

    'dots': {
        'name':           'dots',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'dots'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'exclamation': {
        'name':           'exclamation',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'exclamation'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'dollar': {
        'name':           'dollar',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'dollar'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'cart': {
        'name':           'cart',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'cart'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'question': {
        'name':           'question',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'question'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'skull': {
        'name':           'skull',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'skull'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'heart': {
        'name':           'heart',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'heart'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'water': {
        'name':           'water',
        'role':           'other',
        'slot':           None,
        'img_names':      ['bubbles', 'water'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Furniture

    'purple bed': {
        'name':           'purple bed',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'purple bed'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red bed': {
        'name':           'red bed',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red bed'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'shelf left': {
        'name':           'shelf left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'shelf left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'shelf right': {
        'name':           'shelf right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'shelf right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'long table left': {
        'name':           'long table left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'long table left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'long table right': {
        'name':           'long table right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'long table right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'table': {
        'name':           'table',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'table'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red chair left': {
        'name':           'red chair left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red chair left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red chair right': {
        'name':           'red chair right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red chair right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug bottom left': {
        'name':           'red rug bottom left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug bottom left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug bottom middle': {
        'name':           'red rug bottom middle',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug bottom middle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug bottom right': {
        'name':           'red rug bottom right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug bottom right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug middle left': {
        'name':           'red rug middle left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug middle left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug middle middle': {
        'name':           'red rug middle middle',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug middle middle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug middle right': {
        'name':           'red rug middle right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug middle right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug top left': {
        'name':           'red rug top left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug top left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug top middle': {
        'name':           'red rug top middle',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug top middle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'red rug top right': {
        'name':           'red rug top right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'red rug top right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug bottom left': {
        'name':           'green rug bottom left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug bottom left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug bottom middle': {
        'name':           'green rug bottom middle',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug bottom middle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug bottom right': {
        'name':           'green rug bottom right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug bottom right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug middle left': {
        'name':           'green rug middle left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug middle left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug middle middle': {
        'name':           'green rug middle middle',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug middle middle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug middle right': {
        'name':           'green rug middle right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug middle right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug top left': {
        'name':           'green rug top left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug top left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug top middle': {
        'name':           'green rug top middle',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug top middle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'green rug top right': {
        'name':           'green rug top right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['furniture', 'green rug top right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

## Drugs (drugs_options)

    'needle': {
        'name':           'needle',
        'role':           'drugs',
        'slot':           None,
        'img_names':      ['drugs', 'needle'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           25,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'skin': {
        'name':           'skin',
        'role':           'drugs',
        'slot':           None,
        'img_names':      ['drugs', 'skin'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'teeth': {
        'name':           'teeth',
        'role':           'drugs',
        'slot':           None,
        'img_names':      ['drugs', 'teeth'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'bowl': {
        'name':           'bowl',
        'role':           'drugs',
        'slot':           None,
        'img_names':      ['drugs', 'bowl'],

        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           30,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'plant': {
        'name':           'plant',
        'role':           'drugs',
        'slot':           None,
        'img_names':      ['drugs', 'plant'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'bubbles': {
        'name':           'bubbles',
        'role':           'drugs',
        'slot':           None,
        'img_names':      ['drugs', 'bubbles'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           50,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Potions and scrolls (potions_options, scrolls_options)

    'jug of blood': {
        'name':          'jug of blood',
        'role':          'potions',
        'slot':          None,
        'img_names':     ['potions', 'red'],

        'durability':    101,
        'equippable':    False,
        'equipped':      False,
        'hidden':        False,
        'blocked':       False,
        'movable':       True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':          10,
        
        'hp_bonus':      0,
        'attack_bonus':  0,
        'defense_bonus': 0,
        'effect':        None},

    'jug of grapes': {
        'name':          'jug of grapes',
        'role':          'potions',
        'slot':          None,
        'img_names':     ['potions', 'purple'],

        'durability':    101,
        'equippable':    False,
        'equipped':      False,
        'hidden':        False,
        'blocked':       False,
        'movable':       True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':          10,
        
        'hp_bonus':      0,
        'attack_bonus':  0,
        'defense_bonus': 0,
        'effect':        None},

    'jug of water': {
        'name':          'jug of water',
        'role':          'potions',
        'slot':          None,
        'img_names':     ['potions', 'blue'],

        'durability':    101,
        'equippable':    False,
        'equipped':      False,
        'hidden':        False,
        'blocked':       False,
        'movable':       True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':          10,
        
        'hp_bonus':      0,
        'attack_bonus':  0,
        'defense_bonus': 0,
        'effect':        None},

    'jug of cement': {
        'name':           'jug of cement',
        'role':           'potions',
        'slot':           None,
        'img_names':      ['potions', 'gray'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'scroll of lightning bolt': {
        'name':           'scroll of lightning bolt',
        'role':           'scrolls',
        'slot':           None,
        'img_names':      ['scrolls', 'closed'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'scroll of fireball': {
        'name':           'scroll of fireball',
        'role':           'scrolls',
        'slot':           None,
        'img_names':      ['scrolls', 'closed'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'scroll of confusion': {
        'name':           'scroll of confusion',
        'role':           'scrolls',
        'slot':           None,
        'img_names':      ['scrolls', 'closed'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'scroll of death': {
        'name':           'scroll of death',
        'role':           'scrolls',
        'slot':           None,
        'img_names':      ['scrolls', 'open'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           1000,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Structures (stairs_options, floors_options)

    'door': {
        'name':           'door',
        'role':           'other',
        'slot':           None,
        'img_names':      ['stairs', 'door'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'portal': {
        'name':           'portal',
        'role':           'other',
        'slot':           None,
        'img_names':      ['stairs', 'portal'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'cave': {
        'name':           'cave',
        'role':           'other',
        'slot':           None,
        'img_names':      ['floors', 'sand2'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'path left right': {
        'name':           'path',
        'role':           'other',
        'slot':           None,
        'img_names':      ['paths', 'left right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'path up down': {
        'name':           'path',
        'role':           'other',
        'slot':           None,
        'img_names':      ['paths', 'up down'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'path down right': {
        'name':           'path',
        'role':           'other',
        'slot':           None,
        'img_names':      ['paths', 'down right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'path down left': {
        'name':           'path',
        'role':           'other',
        'slot':           None,
        'img_names':      ['paths', 'down left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'paths up right': {
        'name':           'path',
        'role':           'other',
        'slot':           None,
        'img_names':      ['paths', 'up right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'paths up left': {
        'name':           'path',
        'role':           'other',
        'slot':           None,
        'img_names':      ['paths', 'up left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Concrete structures (concrete_options)

    'gray window': {
        'name':           'gray window',
        'role':           'other',
        'slot':           None,
        'img_names':      ['concrete', 'gray window'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'gray door': {
        'name':           'gray door',
        'role':           'other',
        'slot':           None,
        'img_names':      ['concrete', 'gray door'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'gray wall left': {
        'name':           'gray wall left',
        'role':           'other',
        'slot':           None,
        'img_names':      ['concrete', 'gray wall left'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'gray wall': {
        'name':           'gray wall',
        'role':           'other',
        'slot':           None,
        'img_names':      ['concrete', 'gray wall'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'gray wall right': {
        'name':           'gray wall right',
        'role':           'other',
        'slot':           None,
        'img_names':      ['concrete', 'gray wall right'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        True,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'gray floor': {
        'name':           'gray floor',
        'role':           'other',
        'slot':           None,
        'img_names':      ['concrete', 'gray floor'],
        
        'durability':     101,
        'equippable':     False,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Weapons (equip_names)

    'shovel': {
        'name':           'shovel',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['shovel', 'dropped'],

        'durability':     100,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           15,
        
        'hp_bonus':       0,
        'attack_bonus':   2,
        'defense_bonus':  10,
        'effect':         None},

    'super shovel': {
        'name':           'super shovel',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['super shovel', 'dropped'],

        'durability':     1000,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   100,
        'defense_bonus':  0,
        'effect':         None},

    'dagger': {
        'name':           'dagger',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['dagger', 'dropped'],
        
        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           25,
        
        'hp_bonus':       0,
        'attack_bonus':   2,
        'defense_bonus':  0,
        'effect':         None},

    'sword': {
        'name':           'sword',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['sword', 'dropped'],
        
        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           75,
        
        'hp_bonus':       0,
        'attack_bonus':   5,
        'defense_bonus':  0,
        'effect':         None},

    'blood dagger': {
        'name':           'blood dagger',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['blood dagger', 'dropped'],
        
        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           500,
        
        'hp_bonus':       0,
        'attack_bonus':   10,
        'defense_bonus':  0,
        'effect':         None},

    'blood sword': {
        'name':           'blood sword',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['blood sword', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           1000,
        
        'hp_bonus':       0,
        'attack_bonus':   15,
        'defense_bonus':  0,
        'effect':         None},

# Effects

    'eye': {
        'name':           'eye',
        'role':           'weapons',
        'slot':           'dominant hand',
        'img_names':      ['blood dagger', 'dropped'],
        
        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

# Armor (equip_names)

    'green clothes': {
        'name':           'green clothes',
        'role':           'armor',
        'slot':           'body',
        'img_names':      ['green clothes', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  1,
        'effect':         None},

    'orange clothes': {
        'name':           'orange clothes',
        'role':           'armor',
        'slot':           'body',
        'img_names':      ['orange clothes', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  1,
        'effect':         None},

    'exotic clothes': {
        'name':           'exotic clothes',
        'role':           'armor',
        'slot':           'body',
        'img_names':      ['exotic clothes', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       1,
        'attack_bonus':   0,
        'defense_bonus':  1,
        'effect':         None},

    'yellow dress': {
        'name':           'yellow dress',
        'role':           'armor',
        'slot':           'body',
        'img_names':      ['yellow dress', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           10,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  1,
        'effect':         None},

    'chain dress': {
        'name':           'chain dress',
        'role':           'armor',
        'slot':           'body',
        'img_names':      ['chain dress', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           20,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  2,
        'effect':         None},

    'iron armor': {
        'name':           'iron armor',
        'role':           'armor',
        'slot':           'body',
        'img_names':      ['iron armor', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           100,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  10,
        'effect':         None},

    'lamp': {
        'name':           'lamp',
        'role':           'armor',
        'slot':           'non-dominant hand',
        'img_names':      ['lamp', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           100,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'bald': {
        'name':           'bald',
        'role':           'armor',
        'slot':           'head',
        'img_names':      ['bald', 'front'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        False,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'brown hair': {
        'name':           'brown hair',
        'role':           'armor',
        'slot':           'head',
        'img_names':      ['brown hair', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'blue hair': {
        'name':           'blue hair',
        'role':           'armor',
        'slot':           'head',
        'img_names':      ['blue hair', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'short brown hair': {
        'name':           'short brown hair',
        'role':           'armor',
        'slot':           'head',
        'img_names':      ['short brown hair', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'clean': {
        'name':           'clean',
        'role':           'armor',
        'slot':           'face',
        'img_names':      ['clean', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'brown beard': {
        'name':           'brown beard',
        'role':           'armor',
        'slot':           'face',
        'img_names':      ['brown beard', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'blue beard': {
        'name':           'blue beard',
        'role':           'armor',
        'slot':           'face',
        'img_names':      ['blue beard', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'white beard': {
        'name':           'white beard',
        'role':           'armor',
        'slot':           'face',
        'img_names':      ['white beard', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'flat': {
        'name':           'flat',
        'role':           'armor',
        'slot':           'chest',
        'img_names':      ['flat', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'bra': {
        'name':           'bra',
        'role':           'armor',
        'slot':           'chest',
        'img_names':      ['bra', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'glasses': {
        'name':           'glasses',
        'role':           'armor',
        'slot':           'face',
        'img_names':      ['glasses', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         True,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  0,
        'effect':         None},

    'iron shield': {
        'name':           'iron shield',
        'role':           'armor',
        'slot':           'non-dominant hand',
        'img_names':      ['iron shield', 'dropped'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           50,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  10,
        'effect':         None},

# Big objects
        'logo': {
        'name':           'logo',
        'role':           'decor',
        'img_names':      ['top', 'left'],

        'durability':     101,
        'equippable':     True,
        'equipped':       False,
        'hidden':         False,
        'blocked':        False,
        'movable':        True,
        'rand_X':         0,
        'rand_Y':         0,
        'cost':           0,
        
        'hp_bonus':       0,
        'attack_bonus':   0,
        'defense_bonus':  10,
        'effect':         None}}

ent_dict = {

## Actual entities

    'white': {
        'name':        'white NPC',
        'role':        'NPC',
        'img_names':   ['white', 'front'],
        'habitat':     'any',
        
        'exp':         0,
        'rank':        1,
        'sanity':      100,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        
        'follow':      False,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

    'black': {
        'name':        'black NPC',
        'role':        'NPC',
        'img_names':   ['black', 'front'],
        'habitat':     'any',
        
        'exp':         0,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

    'fat': {
        'name':        'fat NPC',
        'role':        'NPC',
        'img_names':   ['fat', 'front'],
        'habitat':     'any',
        
        'exp':         0,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

    'friend': {
        'name':        'friend',
        'role':        'NPC',
        'img_names':   ['friend', 'front'],
        'habitat':     'land',

        'exp':         0,
        'rank':        100,
        'hp':          100,
        'max_hp':      100,
        'attack':      0,
        'defense':     100,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  0,
        'fear':        None,
        'reach':       640},

    'eye': {
        'name':        'eye',
        'role':        'enemy',
        'img_names':   ['eye', 'front'],
        'habitat':     'land',
        
        'exp':         35,
        'rank':        1,
        'hp':          100,
        'max_hp':      100,
        'attack':      20,
        'defense':     20,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   20,
        'aggression':  50,
        'fear':        None,
        'reach':       1000},

    'eyes': {
        'name':        'eyes',
        'role':        'enemy',
        'img_names':   ['eyes', 'front'],
        'habitat':     'land',
        
        'exp':         35,
        'rank':        1,
        'hp':          20,
        'max_hp':      20,
        'attack':      4,
        'defense':     0,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  10,
        'fear':        None,
        'reach':       1000},

    'troll': {
        'name':        'troll',
        'role':        'enemy',
        'img_names':   ['troll', 'front'],
        'habitat':     'land',

        'exp':         100,
        'rank':        1,
        'hp':          30,
        'max_hp':      30,
        'attack':      8,
        'defense':     2,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  10,
        'fear':        None,
        'reach':       1000},

    'triangle': {
        'name':        'triangle',
        'role':        'enemy',
        'img_names':   ['triangle', 'front'],
        'habitat':     'land',

        'exp':         100,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      15,
        'defense':     10,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    1,
        'miss_rate':   5,
        'aggression':  100,
        'fear':        None,
        'reach':       1000},

    'purple': {
        'name':        'purple',
        'role':        'enemy',
        'img_names':   ['purple', 'front'],
        'habitat':     'land',
        
        'exp':         500,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  10,
        'fear':        None,
        'reach':       1000},

    'tentacles': {
        'name':        'tentacles',
        'role':        'enemy',
        'img_names':   ['tentacles', 'front'],
        'habitat':     'any',

        'exp':         50,
        'rank':        1,
        'hp':          35,
        'max_hp':      35,
        'attack':      10,
        'defense':     10,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    2,
        'miss_rate':   1,
        'aggression':  100,
        'fear':        None,
        'reach':       1000},

    'round1': {
        'name':        'round1',
        'role':        'enemy',
        'img_names':   ['round1', 'front'],
        'habitat':     'land',
        
        'exp':         50,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    0,
        'miss_rate':   5,
        'aggression':  100,
        'fear':        None,
        'reach':       1000},

    'round2': {
        'name':        'round2',
        'role':        'enemy',
        'img_names':   ['round2', 'front'],
        'habitat':     'land',
        
        'exp':         500,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  10,
        'fear':        None,
        'reach':       1000},

    'grass': {
        'name':        'grass',
        'role':        'enemy',
        'img_names':   ['grass', 'front'],
        'habitat':     'forest',
        
        'exp':         500,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   40,
        'aggression':  20,
        'fear':        None,
        'reach':       1000},

    'round3': {
        'name':        'round3',
        'role':        'enemy',
        'img_names':   ['round3', 'front'],
        'habitat':     'any',
        
        'exp':         500,
        'rank':        1,
        'hp':          1,
        'max_hp':      1,
        'attack':      0,
        'defense':     0,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    10,
        'miss_rate':   10,
        'aggression':  0,
        'fear':        None,
        'reach':       64},

    'lizard': {
        'name':        'lizard',
        'role':        'enemy',
        'img_names':   ['lizard', 'front'],
        'habitat':     'desert',
        
        'exp':         500,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    5,
        'miss_rate':   10,
        'aggression':  10,
        'fear':        None,
        'reach':       1000},

    'red': {
        'name':        'red',
        'role':        'enemy',
        'img_names':   ['red', 'front'],
        'habitat':     'land',
        
        'exp':         500,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      15,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    100,
        'miss_rate':   10,
        'aggression':  1,
        'fear':        None,
        'reach':       0},

    'rock': {
        'name':        'rock',
        'role':        'enemy',
        'img_names':   ['rock', 'front'],
        'habitat':     'desert',
        
        'exp':         500,
        'rank':        1,
        'hp':          10,
        'max_hp':      10,
        'attack':      0,
        'defense':     500,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    2,
        'miss_rate':   0,
        'aggression':  0,
        'fear':        None,
        'reach':       0},

    'frog': {
        'name':        'frog',
        'role':        'enemy',
        'img_names':   ['frog', 'front'],
        'habitat':     'any',
        
        'exp':         15,
        'rank':        1,
        'hp':          50,
        'max_hp':      50,
        'attack':      1,
        'defense':     5,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      False,
        'lethargy':    10,
        'miss_rate':   10,
        'aggression':  10,
        'fear':        None,
        'reach':       32},

    'red radish': {
        'name':        'red radish',
        'role':        'enemy',
        'img_names':   ['red radish', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        0,
        'reach':       1000},

    'orange radish': {
        'name':        'orange radish',
        'role':        'enemy',
        'img_names':   ['orange radish', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        0,
        'reach':       1000},

    'purple radish': {
        'name':        'purple radish',
        'role':        'enemy',
        'img_names':   ['purple radish', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        0,
        'reach':       1000},

    'snake': {
        'name':        'snake',
        'role':        'enemy',
        'img_names':   ['snake', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

    'buzz': {
        'name':        'buzz',
        'role':        'enemy',
        'img_names':   ['buzz', 'front'],
        'habitat':     'city',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

    'egg': {
        'name':        'egg',
        'role':        'enemy',
        'img_names':   ['egg', 'front'],
        'habitat':     'any',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

    'star': {
        'name':        'star',
        'role':        'enemy',
        'img_names':   ['star', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    20,
        'miss_rate':   20,
        'aggression':  10,
        'fear':        None,
        'reach':       1000},

    'plant': {
        'name':        'plant',
        'role':        'enemy',
        'img_names':   ['plant', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        None,
        'reach':       1000},

## Projectiles

    'green blob': {
        'name':        'green blob',
        'role':        'projectile',
        'img_names':   ['green blob', 'front'],
        'habitat':     'forest',
        
        'exp':         0,
        'rank':        1,
        'hp':          25,
        'max_hp':      25,
        'attack':      0,
        'defense':     25,
        'stamina':     100,
        'sanity':      100,
        
        'follow':      True,
        'lethargy':    6,
        'miss_rate':   6,
        'aggression':  0,
        'fear':        None,
        'reach':       1000}}

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