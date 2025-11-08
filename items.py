########################################################################################################################################################
# Item creation and management
# There are no effects here -- only generic tools.
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random

## Local
import session
from data_management import item_dicts

########################################################################################################################################################

########################################################################################################################################################
# Classes
class ItemSystem:

    # Core
    def create_item(self, item_id, effect=False):
        """ Creates and returns an object.
        
            Parameters
            ----------
            names  : string or list of strings; name of object
            effect : bool or Effect object; True=default, False=None, effect=custom """
        
        # Create object
        item_id = item_id.replace(" ", "_")
        item = Item(**item_dicts[item_id])
        
        # Add effect
        #effect_dict = obj_dicts['item_effects']

        #if effect:
        #    item.effect = effect

        #elif item.name in effect_dict:
        #    effect = effect_dict[item.name]
        #    item.effect = session.effects.add_effect(
        #        name          = effect['name'],
        #        img_names     = effect['img_names'],
        #        effect_fn     = eval(effect['effect_fn']),
        #        trigger       = effect['trigger'],
        #        sequence      = effect['sequence'],
        #        cooldown_time = effect['cooldown_time'],
        #        other         = effect['other'])
            
        #else:
        #    item.effect = None

        return item

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

    # Mechanics
    def pick_up(self, item, ent=None, silent=False):
        """ Adds an item to the player's inventory and removes it from the map.
        
            Parameters
            ----------
            ent    : Entity object; owner of the item
            silent : bool; updates GUI if False
        """

        pyg = session.pyg

        if not ent: ent = session.player_obj.ent
        
        #########################################################
        # Pick up if possible
        ## Do not pick up item if inventory is full
        if (len(ent.inventory) >= 26) and not silent:
            pyg.update_gui("Your inventory is full, cannot pick up " + item.name + ".", pyg.dark_gray)
        
        ## Check if movable
        else:
            if item.movable:
                
                # Add to inventory
                item.owner = ent
                if item.effect and (item.effect.trigger == 'passive'):
                    ent.active_effects.append(item.effect)
                
                ent.inventory[item.role].append(item)
                self.sort_inventory(ent)
                
                # Remove from environment
                if ent.tile:
                    if ent.tile.item:
                        ent.tile.item = None
                        item.tile     = ent.tile
                
                if (ent.role == 'player') and not silent:
                    pyg.update_gui("Picked up " + item.name + ".", pyg.dark_gray)

    def drop(self, item, ent=None):
        """ Unequips item before dropping if the object has the Equipment component, then adds it to the map at
            the player's coordinates and removes it from their inventory.
            Dropped items are only saved if dropped in home. """
        
        # Allow for NPC actions
        if not ent: ent = session.player_obj.ent
        
        # Prevent dropping items over other items
        if not ent.tile.item:
        
            # Dequip before dropping
            if item in ent.equipment.values():
                self.toggle_equip(item, ent)
            
            item.owner = None
            item.X     = ent.X
            item.Y     = ent.Y

            if item.effect:
                if item.effect.name in ent.active_effects.keys():
                    del ent.active_effects[item.effect.name]
            if item.ability:
                if item.ability.name in ent.active_abilities.keys():
                    del ent.active_abilities[item.ability.name]
            
            ent.inventory[item.role].remove(item)
            ent.tile.item = item

    def toggle_equip(self, item, ent, silent=False):
        """ Toggles the equip/unequip status. """
        
        # Assign entity
        if not ent:        ent = session.player_obj.ent
        if not item.owner: item.owner = ent
        
        # Equip or dequip
        if item.equipped: self._dequip(item, ent, silent)
        else:             self._equip(item, ent, silent)

    def _equip(self, item, ent, silent=False):
        """ Unequips object if the slot is already being used. """
        
        pyg = session.pyg

        try:
            # Check if anything is already equipped
            if ent.equipment[item.slot] is not None:
                self.dequip(ent.equipment[item.slot], ent)
        except:
            print(item.name, item.slot)
        
        # Apply stat adjustments
        ent.equipment[item.slot] = item
        ent.max_hp  += item.hp_bonus
        ent.attack  += item.attack_bonus
        ent.defense += item.defense_bonus

        if item.effect:
            if item.effect.name in ent.active_effects.keys():
                ent.active_effects[item.effect.name] = item.effect
        if item.ability:
            if item.ability.name in ent.active_abilities.keys():
                ent.active_abilities[item.ability.name] = item.ability

        item.equipped = True

        if ent.role == 'player':
            if not item.hidden and not silent:
                pyg.update_gui("Equipped " + item.name + " on " + item.slot + ".", pyg.dark_gray)

    def _dequip(self, item, ent, silent=False):
        """ Unequips an object and shows a message about it. """
        
        pyg = session.pyg

        #########################################################
        # Update stats
        ent.equipment[item.slot] = None
        ent.attack  -= item.attack_bonus
        ent.defense -= item.defense_bonus
        ent.max_hp  -= item.hp_bonus

        if ent.hp > ent.max_hp:
            ent.hp = ent.max_hp

        if item.effect:
            if item.effect.name in ent.active_effects.keys():
                del ent.active_effects[item.effect.name]
        if item.ability:
            if item.ability.name in ent.active_abilities.keys():
                del ent.active_abilities[item.ability.name]
        
        #########################################################
        # Notify change of status
        item.equipped = False
        if ent.role == 'player':
            if not item.hidden and not silent:
                pyg.update_gui("Dequipped " + item.name + " from " + item.slot + ".", pyg.dark_gray)

    def use(self, item, ent=None):
        """ Equips of unequips an item if the object has the Equipment component. """
        
        pyg = session.pyg

        # Allow for NPC actions
        if not ent: ent = session.player_obj.ent

        # Declare event
        session.bus.emit(
            event_id = 'item_used',
            ent_id   = ent.name,
            item_id  = item.name)
        
        # Handle equipment
        if item.equippable:
            self.toggle_equip(item, ent)
        
        # Handle items
        elif item.effect:
            
            # Add active effect
            if (ent.role == 'player') and (item.role in ['potions', 'weapons', 'armor']):
                ent.active_effects.append(item.effect)
                print(1234567, item.name, item.effect)
            
            # Activate the item
            else: item.effect.effect_fn(ent)
        
        elif ent.role == 'player':
            pyg.update_gui("The " + item.name + " cannot be used.", pyg.dark_gray)

    def trade(self, item, owner, recipient):
        
        pyg = session.pyg

        # Dequip before trading
        if item in owner.equipment.values():
            self.toggle_equip(item, owner)
        
        # Check wallet for cash
        if (owner.wallet - item.cost) >= 0:
            
            # Remove from owner
            owner.inventory[item.role].remove(item)
            owner.wallet += item.cost
            
            # Give to recipient
            self.pick_up(item, ent=recipient)
            recipient.wallet -= item.cost
        
        else:
            pyg.update_gui("Not enough cash!", color=pyg.red)

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
        
        ## Import parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

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

########################################################################################################################################################
# Tools
########################################################################################################################################################