########################################################################################################################################################
# Item creation and management
# There are no effects here -- only generic tools.
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import copy

## Local
import session
from data_management import item_dicts

########################################################################################################################################################

########################################################################################################################################################
# Classes
class Item:
    
    def __init__(self, item_id, **kwargs):
        """ Parameters
            ----------
            name          : string
            role          : string in ['weapons', 'armor', 'potions', 'scrolls', 'other']
            slot          : string in ['non-dominant hand', 'dominant hand', 'body', 'head', 'face']
            
            X             :
            Y             : 
            
            img_IDs[0]  : string
            img_IDs[1]  : string
            
            uses          : int; item breaks at 0
            equippable    : Boolean; lets item be equipped by entity
            equipped      : Boolean; notes if the item is equipped
            hidden        : Boolean; hides from inventory menu
            
            hp_bonus      : int
            attack_bonus  : int
            defense_bonus : int
            effects       : """
        
        # Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.item_id = item_id

        # Set abilities and effects
        if self.ability_id:
            self.ability = session.abilities.create_ability(
                owner      = None,
                ability_id = self.ability_id)
        
        if self.effect_id:
            effect = session.effects.create_effect(
                owner     = None,
                effect_id = self.effect_id,
                item      = self)
            self.effect = effect

        # Seed a seed for individual adjustments
        self.rand_X  = random.randint(-self.rand_X, self.rand_X)
        self.rand_Y  = random.randint(0,            self.rand_Y)
        self.flipped = random.choice([0, self.rand_Y])

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

            if self.img_IDs[0] == 'decor':
                X -= self.rand_X
                Y -= self.rand_Y
        
            # Add effects and draw
            if self.flipped: surface = img.flipped.dict[self.img_IDs[0]][self.img_IDs[1]]
            else:            surface = img.dict[self.img_IDs[0]][self.img_IDs[1]]

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

class ItemSystem:

    # Core
    def __init__(self):
        session.bus.subscribe('drop_item', self.find_and_drop)

    def sort_inventory(self, ent=None):
        
        # Allow for NPC actions
        if not ent: ent = session.player_obj.ent
            
        inventory_cache = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}
        other_cache     = {'weapons': [], 'armor': [], 'potions': [], 'scrolls': [], 'drugs': [], 'other': []}

        # Sort by category
        for item_list in ent.inventory.values():
            for item in item_list:
                inventory_cache[item.role].append(item)
        
        # Sort by stats:
        sorted(inventory_cache['weapons'], key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
        sorted(inventory_cache['armor'],  key=lambda obj: obj.attack_bonus + obj.defense_bonus + obj.hp_bonus)
        sorted(inventory_cache['potions'], key=lambda obj: obj.name)
        sorted(inventory_cache['scrolls'], key=lambda obj: obj.name)
        sorted(inventory_cache['other'],  key=lambda obj: obj.name)

        ent.inventory = inventory_cache

    # Events
    def find_and_drop(self, ent_id, item_id, **kwargs):
        for ent in session.player_obj.ent.env.ents:
            if ent.ent_id == ent_id:
                for category in ent.inventory.values():
                    for item in category:
                        if item.item_id == item_id:
                            self.drop(item, kwargs.get('vicinity', None))

    # Activation
    def pick_up(self, ent, item, silent=False):
        """ Adds an item to the player's inventory and removes it from the map. Assigns owner to item.
        
            Parameters
            ----------
            ent    : Entity instance; new owner of the item
            item   : item instance; item picked up
            silent : bool; updates GUI if False
        """

        pyg = session.pyg
        
        # Do not pick up item if inventory is full
        if (ent.role == 'player') and (len(ent.inventory) >= 26) and (not silent):
            pyg.update_gui("Your inventory is full, cannot pick up " + item.name + ".", pyg.dark_gray)
        
        # Pick up if movable
        elif item.movable:
            
            # Update owner
            ent.inventory[item.role].append(item)
            self.sort_inventory(ent)

            if item.effect and (item.effect.trigger == 'passive'):
                ent.active_effects.append(item.effect)
            
            # Update item
            item.owner = ent
            item.tile  = ent.tile
            if item.effect:
                item.effect.owner = ent

            # Update tile (if needed)
            if ent.tile:
                if ent.tile.item:
                    ent.tile.item = None
            
            # Notify GUI
            if (ent.role == 'player') and (not silent):
                pyg.update_gui("Picked up " + item.name + ".", pyg.dark_gray)

    def drop(self, item, vicinity=False):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at
            the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home.
        """

        # Set location
        tile = None

        ## Place under entity
        if not vicinity and not item.owner.tile.item:
                tile = item.owner.tile
        
        ## Place near entity
        else:
            from mechanics import get_vicinity, is_blocked

            # Select random location
            vicinity = list(get_vicinity(item.owner).values())
            tile     = random.choice(vicinity)
            vicinity.remove(tile)

            # Check if location is blocked
            while is_blocked(tile=tile) or tile.item:
                tile = random.choice(vicinity)
                vicinity.remove(tile)

                # Place under entity if no other locations are free
                if not vicinity:
                    tile = item.owner.tile
                    break

        # Prevent dropping items over other items
        if tile:

            # Update tile
            tile.item = item
            
            # Update owner
            if item in item.owner.equipment.values():
                self.toggle_equip(item)
            item.owner.inventory[item.role].remove(item)

            if item.effect and (item.effect.trigger == 'passive'):
                item.owner.active_effects.remove(item.effect)

            # Update item
            item.X     = tile.X
            item.Y     = tile.Y
            item.tile  = tile
            item.owner = tile
            if item.effect:
                item.effect.owner = tile

    def destroy(self, item):
        self.drop(item)
        item.tile.item = None

    def toggle_equip(self, item, silent=False):
        """ Toggles the equip/unequip status. """
        
        if item.equipped: self._dequip(item, silent)
        else:             self._equip(item, silent)

    def _equip(self, item, silent=False):
        """ Unequips object if the slot is already being used. """
        
        pyg = session.pyg
        ent = item.owner

        # Check if anything is already equipped
        if ent.equipment[item.slot] is not None:
            self._dequip(ent.equipment[item.slot], ent)
        
        # Effects and abilities
        ## Apply stat adjustments
        ent.equipment[item.slot] = item
        ent.max_hp  += item.hp_bonus
        ent.attack  += item.attack_bonus
        ent.defense += item.defense_bonus

        if item.effect:
            session.effects.toggle_effect(ent, item.effect)
        if item.ability:
            session.abilities.toggle_ability(ent, item.ability)

        item.equipped = True

        if ent.role == 'player':
            if not item.hidden and not silent:
                pyg.update_gui("Equipped " + item.name + " on " + item.slot + ".", pyg.dark_gray)

    def _dequip(self, item, silent=False):
        """ Unequips an object and shows a message about it. """
        
        pyg = session.pyg
        ent = item.owner

        #########################################################
        # Update stats
        ent.equipment[item.slot] = None
        ent.attack  -= item.attack_bonus
        ent.defense -= item.defense_bonus
        ent.max_hp  -= item.hp_bonus

        if ent.hp > ent.max_hp:
            ent.hp = ent.max_hp

        if item.effect:
            session.effects.toggle_effect(ent, item.effect)
        if item.ability:
            session.abilities.toggle_ability(ent, item.ability)
        
        #########################################################
        # Notify change of status
        item.equipped = False
        if ent.role == 'player':
            if not item.hidden and not silent:
                pyg.update_gui("Dequipped " + item.name + " from " + item.slot + ".", pyg.dark_gray)

    def use(self, item, silent=False):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        pyg = session.pyg
        ent = item.owner

        session.bus.emit(
            event_id = 'item_used',
            ent_id   = ent.ent_id,
            item_id  = item.item_id)
        
        # Equip
        if item.equippable:
            self.toggle_equip(item)
        
        # Effects
        elif item.effect:
            
            # Use item
            if item.effect.trigger == 'on_use':
                item.effect.activate()
        
        elif (ent.role == 'player') and not silent:
            pyg.update_gui("The " + item.name + " cannot be used.", pyg.dark_gray)

    def trade(self, item, owner, recipient):
        
        pyg = session.pyg

        # Dequip before trading
        if item in owner.equipment.values():
            self.toggle_equip(item)
        
        # Check wallet for cash
        if (owner.wallet - item.cost) >= 0:
            
            # Remove from owner
            owner.inventory[item.role].remove(item)
            owner.wallet += item.cost
            
            # Give to recipient
            self.pick_up(recipient, item)
            recipient.wallet -= item.cost

            # Emit event
            session.bus.emit(
                event_id      = 'item_traded',
                ent_id        = recipient.ent_id,
                target_ent_id = owner.ent_id,
                item_id       = item.item_id)
        
        else:
            pyg.update_gui("Not enough cash!", color=pyg.red)

def create_item(item_id):
    """ Creates and returns an object.
    
        Parameters
        ----------
        names  : string or list of strings; name of object
        effect : bool or Effect object; True=default, False=None, effect=custom """
    
    # Create object
    json_data = copy.deepcopy(item_dicts[item_id])
    item      = Item(item_id, **json_data)

    return item

########################################################################################################################################################