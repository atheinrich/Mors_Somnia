########################################################################################################################################################
# Abilities
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
import session
from mechanics import get_vicinity
from data_management import load_json

########################################################################################################################################################
# Core
_registry = {}
def register(function_id):
    def decorator(function):
        _registry[function_id] = function
        return function
    return decorator

class Ability:

    def __init__(self, owner, ability_id):

        # Load general details from JSON
        self.data       = session.abilities._data[ability_id]
        self.ability_fn = session.abilities._registry[self.data['function_id']]

        self.name          = self.data['name']
        self.img_names     = self.data['img_names']
        self.sequence      = self.data['sequence']
        self.cooldown_time = float(self.data['cooldown_time'])

        # Other
        self.owner           = owner
        self.last_press_time = 0

    def activate(self):
        self.ability_fn(self, self)

class AbilitiesSystem:

    # Core
    def __init__(self, registry):
        self._data     = load_json(f'Data/.Databases/abilities.json')
        self._registry = registry
        print(self._data)

        #########################################################
        # Set parameters
        ## Utility
        self.last_press_time   = 0
        self.cooldown_time     = 1

        ## Combat
        self.heal_amount       = 4
        self.lightning_damage  = 20
        self.lightning_range   = 5 * 32
        self.confuse_range     = 8 * 32
        self.confuse_num_turns = 10
        self.fireball_radius   = 3 * 32
        self.fireball_damage   = 12

        self.level_up_base     = 200
        self.level_up_factor   = 150
        
        self.torch_radius      = 10
        
        self.movement_speed_toggle = 0
        self.speed_list = [
            ['Default', (250, 200)],
            ['Fast',    (1,   150)],
            ['Fixed',   (0,   0)]]
        self.slow_list = [
            ['Fixed',   (0,   0)],
            ['Default', (250, 200)]]

    def add_ability(self, owner, ability_id):
        return Ability(owner, ability_id)

    # Entity interactions
    @register("entity_scare")
    def entity_scare(self, ability_obj):
        """ Combo effect. """

        pyg   = session.pyg
        owner = ability_obj.owner

        # Find entities in vicinity
        ent_list = []
        for tile in get_vicinity(owner).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            
            if owner.name == 'garden':
                session.stats_obj.pet_moods['lethargy'] -= 1
                session.stats_obj.pet_moods['boredom']  -= 1
            
            image = session.img.dict['bubbles']['exclamation bubble']
            for ent in ent_list:
                for tile in get_vicinity(ent).values():
                    if not tile.blocked:
                        session.movement.move_towards(ent, tile.X, tile.Y)
                session.img.flash_above(ent, image)
        
        else:
            pyg.update_gui("There are no entities in your vicinity.", pyg.dark_gray)

    @register("entity_capture")
    def entity_capture(self, ability_obj):
        """ Combo effect. """

        pyg   = session.pyg
        owner = ability_obj.owner

        # Find entities in vicinity
        target = None
        for tile in get_vicinity(owner).values():
            if tile.entity:
                if tile.entity.role != 'NPC':
                    target = tile.entity
                    break
        
        # Activate effect if entities are found
        if target:
            image = session.img.dict['bubbles']['heart bubble']
            session.img.flash_above(target, image)
            session.img.flash_on(target, session.img.dict[target.img_names[0]][target.img_names[1]])
            
            if owner.discoveries['entities'].values():
                for names in owner.discoveries['entities'].values():
                    if target.name not in names:
                        self._capture(owner, target)
                        break
                    else:
                        pyg.update_gui("The " + target.name + " has already been logged.", pyg.dark_gray)
            else:
                self._capture(owner, target)
        else:
            pyg.update_gui("There are no entities in your vicinity.", pyg.dark_gray)

    def _capture(self, owner, target):
        pyg = session.pyg

        pyg.update_gui("The " + target.name + " has been captured!", pyg.red)

        # Update entity
        target.dead        = True
        target.tile.entity = None
        target.env.entities.remove(target)
        
        owner.discoveries['entities'][target.name] = target.img_names

    @register("entity_comfort")
    def entity_comfort(self, ability_obj):
        """ Combo effect. """

        owner = ability_obj.owner

        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(owner).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            session.stats_obj.pet_moods['sadness'] -= 1
            if session.stats_obj.pet_moods['sadness'] <= 0: session.stats_obj.pet_moods['boredom'] += 1
            image = session.img.dict['bubbles'][' bubble']
            for ent in ent_list:
                session.img.flash_above(ent, image)
                session.movement.spin(ent)

    @register("entity_clean")
    def entity_clean(self, ability_obj):
        """ Combo effect. """
        
        owner = ability_obj.owner

        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(owner).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            for ent in ent_list:
                session.movement.find_water(ent)

    # Attacks
    @register("swing")
    def swing(self, ability_obj):

        owner = ability_obj.owner
        
        # Check for remaining stamina
        if owner.stamina:
            
            # Send animation to queue
            image = session.img.dict[owner.equipment['dominant hand'].img_names[0]]['dropped']
            session.img.vicinity_flash(owner, image)
            
            # Apply attack to enemies
            for tile in get_vicinity(owner).values():
                if tile.entity:
                    owner.attack += 5
                    session.interact.attack_target(owner, tile.entity, effect_check=False)
                    owner.attack -= 5
            
            # Decrease stamina
            owner.stamina -= 5

    @register("propagate")
    def propagate(self, ability_obj):
        
        pyg   = session.pyg
        owner = ability_obj.owner

        from items_entities import create_entity
        from environments import place_object

        # Note location and image names
        img_x, img_y = int(owner.X/pyg.tile_width), int(owner.Y/pyg.tile_height)
        
        # Set location for drop
        if owner.direction == 'front':   img_y += 1
        elif owner.direction == 'back':  img_y -= 1
        elif owner.direction == 'right': img_x += 1
        elif owner.direction == 'left':  img_x -= 1
        
        # Place item
        item = create_entity('green blob')
        item.lethargy = 0
        item.cooldown = 0.1
        item.direction = None
        place_object(
            obj   = item,
            loc   = [img_x, img_y],
            env   = owner.env,
            names = item.img_names)
        
        # Prepare movements
        motions_log = []
        directions = {
            'front': [0, pyg.tile_height],
            'back':  [0, -pyg.tile_height],
            'left':  [-pyg.tile_width, 0],
            'right': [pyg.tile_width, 0]}
        
        for _ in range(100):
            motions_log.append(directions[owner.direction])
        
        # Send directions to entity
        item.motions_log = motions_log

    @register("suicide")
    def suicide(self, ability_obj):
        
        owner = ability_obj.owner

        # Activate animation
        image = session.img.dict['decor']['bones']
        session.img.vicinity_flash(owner, image)
        
        # Kill player
        session.interact.death(owner)
        return

_abilities = AbilitiesSystem(_registry)

########################################################################################################################################################