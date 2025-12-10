########################################################################################################################################################
# Ability creation and management
# No items are managed here -- only functions for predefined abilities.
#
# Abilities may be added to an entity directly, or they may be available upon equipping an item.
# They be assigned to anything but are only owned by entities and tiles.
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
    """ Holds a function, owner, and other details for one instance of an ability. """

    def __init__(self, owner, **kwargs):
        """ Parameters
            ----------
            name            : str; descriptor to be displayed in ability list
            img_IDs         : list of str; sets image to be displayed in ability list
            sequence        : str; three-key combo for ability activation (ex. ⮜⮟⮞)
            cooldown        : float; time required between activations
            function_id     : str; sets the ability function on initialization (not used after)

            ability_fn      : ability function; see AbilitiesSystem
            owner           : entity object; used in ability function
            last_press_time : float; time of last activation
        """

        # Load general details from JSON
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Other
        self.ability_fn      = session.abilities._registry[self.function_id]
        self.owner           = owner
        self.last_press_time = 0

    def activate(self):
        self.ability_fn(self, self)

class AbilitiesSystem:
    """ Holds all ability functions, as well as ability creation and toggling. """

    # Core
    def __init__(self, registry):
        self._data     = load_json(f'Data/.Databases/abilities.json')
        self._registry = registry

    def create_ability(self, owner, ability_id):
        return Ability(owner, **self._data[ability_id])

    def toggle_ability(self, ent, ability_obj):
        """ Adds or removes ability for a given entity. Called when equipping/dequipping items. """

        if session.pyg.game_state not in ['startup', 'play_garden']:
            
            # Add ability
            if ability_obj.name not in ent.game_abilities.keys():
                ent.game_abilities[ability_obj.name] = ability_obj
                ability_obj.owner = ent
            
            # Remove ability
            else:
                del ent.game_abilities[ability_obj.name]
                ability_obj.owner = None

    def toggle_abilities(self, ent):
        """ Switches ability list for the garden and game. """
        
        if session.pyg.game_state in ['startup', 'play_garden']:
            ent.active_abilities = ent.garden_abilities
        else:
            ent.active_abilities = ent.game_abilities

    # Entity interactions
    @register("entity_scare")
    def entity_scare(self, ability_obj):
        """ Combo effect. Should be updated. """

        pyg   = session.pyg
        owner = ability_obj.owner

        # Find entities in vicinity
        ent_list = []
        for tile in get_vicinity(owner).values():
            if tile.ent:
                ent_list.append(tile.ent)
        
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
        """ Combo effect. Should be updated. """

        pyg   = session.pyg
        owner = ability_obj.owner

        # Find entities in vicinity
        target = None
        for tile in get_vicinity(owner).values():
            if tile.ent:
                if tile.ent.role != 'NPC':
                    target = tile.ent
                    break
        
        # Activate effect if entities are found
        if target:
            image = session.img.dict['bubbles']['heart bubble']
            session.img.flash_above(target, image)
            session.img.flash_on(target, session.img.dict[target.img_IDs[0]][target.img_IDs[1]])
            
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
        target.dead     = True
        target.tile.ent = None
        target.env.entities.remove(target)
        
        owner.discoveries['entities'][target.name] = target.img_IDs

    @register("entity_comfort")
    def entity_comfort(self, ability_obj):
        """ Combo effect. Should be updated. """

        owner = ability_obj.owner

        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(owner).values():
            if tile.ent:
                ent_list.append(tile.ent)
        
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
        """ Combo effect. Should be updated. """
        
        owner = ability_obj.owner

        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(owner).values():
            if tile.ent:
                ent_list.append(tile.ent)
        
        # Activate effect if entities are found
        if ent_list:
            for ent in ent_list:
                session.movement.find_water(ent)

    # Attacks
    @register("swing")
    def swing(self, ability_obj):
        """ Renders attack cinematic and damages enemies with a small stat boost. """

        owner = ability_obj.owner
        
        # Check for remaining stamina
        if owner.stamina:
            
            # Send animation to queue
            if owner.equipment['dominant hand']:
                image = session.img.dict[owner.equipment['dominant hand'].img_IDs[0]]['dropped']
            else:
                image = session.img.dict[ability_obj.img_IDs[0]][ability_obj.img_IDs[1]]
            
            session.img.vicinity_flash(owner, image)
            
            # Apply attack to enemies
            for tile in get_vicinity(owner).values():
                if tile.ent:
                    owner.attack += 5
                    session.interact.attack_target(owner, tile.ent)
                    owner.attack -= 5
            
            # Decrease stamina
            owner.stamina -= 5

    @register("propagate")
    def propagate(self, ability_obj):
        """ Throws projectile that damages entity upon contact. Needs updating. """
        
        pyg   = session.pyg
        owner = ability_obj.owner

        from entities import create_entity
        from environments import place_object

        # Note location and image names
        img_x, img_y = int(owner.X/pyg.tile_width), int(owner.Y/pyg.tile_height)
        
        # Set location for drop
        if owner.direction == 'front':   img_y += 1
        elif owner.direction == 'back':  img_y -= 1
        elif owner.direction == 'right': img_x += 1
        elif owner.direction == 'left':  img_x -= 1
        
        # Place blob
        blob = create_entity('green blob')
        blob.lethargy = 0
        blob.cooldown = 0.1
        blob.direction = None
        place_object(
            obj   = blob,
            loc   = [img_x, img_y],
            env   = owner.env,
            names = blob.img_IDs)
        
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
        blob.motions_log = motions_log

    @register("suicide")
    def suicide(self, ability_obj):
        """ Instant death for the activating entity. """

        owner = ability_obj.owner

        # Activate animation
        image = session.img.dict['decor']['bones']
        session.img.vicinity_flash(owner, image)
        
        # Kill player
        session.interact.death(owner)
        return

_abilities = AbilitiesSystem(_registry)

########################################################################################################################################################