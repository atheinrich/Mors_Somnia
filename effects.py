########################################################################################################################################################
# Effects creation and management
# No items are managed here -- only mechanics for predefined effects.
#
# Like abilities, effects are owned by entities and items.
# Unlike abilities, effects can be also be owned by tiles.
# Unlike abilities, effects have various trigger mechanisms.
# - on_idle:  applies when not in an inventory;               includes lights
# - on_hover: applies when stepped on by an entity;           includes pet food and traps
# - on_hold:  applies continuously when wielded by an entity; includes weapon strikes
# - on_use:   applies when activated manually by the player;  includes drugs
########################################################################################################################################################

########################################################################################################################################################
# Imports
import pygame
import random

import session
from mechanics import place_player
from data_management import load_json

########################################################################################################################################################
# Core
_registry = {}
def register(function_id):
    def decorator(function):
        _registry[function_id] = function
        return function
    return decorator

class Effect:

    def __init__(self, owner, item, **kwargs):

        # Load general details from JSON
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Other
        self.effect_fn       = session.effects._registry[self.function_id]
        self.owner           = owner
        self.item            = item
        self.last_press_time = 0

    def activate(self, **kwargs):
        self.effect_fn(self, self, **kwargs)

class EffectsSystem:

    # Core
    def __init__(self, registry):
        self._data     = load_json(f'Data/.Databases/effects.json')
        self._registry = registry
        self.speed_list = [
            ['Default', (250, 200)],
            ['Fast',    (1,   150)],
            ['Fixed',   (0,   0)]]
        self.slow_list = [
            ['Fixed',   (0,   0)],
            ['Default', (250, 200)]]
        self.movement_speed_toggle = 0

    def create_effect(self, owner, effect_id, item=None):
        return Effect(owner, item, **self._data[effect_id])

    def toggle_effect(self, ent, effect_obj):
        """ Adds or removes ability for a given entity. """

        if effect_obj.trigger != 'on_use':

            # Add effect
            if effect_obj.name not in ent.active_effects.keys():
                ent.active_effects[effect_obj.name] = effect_obj
                effect_obj.owner = ent
            
            # Remove effect
            else:
                del ent.active_effects[effect_obj.name]
                effect_obj.owner = None
        
            effect_obj.activate(on_toggle=True)

    def check_tile(self, ent):
        #if ent.tile.item:
        #    if ent.tile.item.effect:
        #        ent.tile.item.effect.effect_fn(ent)
        pass

    # Working
    @register("dig_tunnel")
    def dig_tunnel(self, effect_obj, **kwargs):
        pyg = session.pyg
        ent = effect_obj.owner

        if not kwargs.get('on_toggle'):
            x  = kwargs.get('x')
            y  = kwargs.get('y')
            dX = kwargs.get('dX')
            dY = kwargs.get('dY')

            if ent.X >= 64 and ent.Y >= 64:

                # Dig
                if not ent.env.map[x][y].unbreakable:
                    ent.env.map[x][y].blocked     = False
                    ent.env.map[x][y].unbreakable = False
                    ent.env.map[x][y].img_names   = ent.env.floors
                    session.movement.move(ent, dX, dY)
                
                    # Decrease condition
                    if ent.equipment['dominant hand'].durability <= 100:
                        ent.equipment['dominant hand'].durability -= 1

                    # Break item
                    if ent.equipment['dominant hand'].durability <= 0:
                        pyg.update_gui(f"Broken {ent.equipment['dominant hand'].name}!", color=pyg.dark_gray)
                        session.items.destroy(ent.equipment['dominant hand'])
                
                # Do not dig
                else:
                    pyg.update_gui("You strike the barrier but cannot break it.", pyg.dark_gray)

    @register("lamp")
    def lamp(self, effect_obj, **kwargs):
        """ Adds or removes a light to be rendered. """

        light_list = session.player_obj.ent.env.weather.light_list

        if kwargs.get('on_toggle'):
            if effect_obj not in light_list: light_list.append(effect_obj)
            else:                            light_list.remove(effect_obj)

        elif effect_obj not in light_list:   light_list.append(effect_obj)

    # Queue
    @register("jug_of_water")
    def jug_of_water(self, effect_obj, **kwargs):

        if not kwargs.get('on_toggle'):

            # Update tile
            tile            = effect_obj.owner.tile
            tile.img_names  = ['floors', 'water']
            tile.biome      = 'water'

            # Update effect
            effect_obj.uses -= 1

            # Destroy if no more uses
            if effect_obj.uses:
                effect_obj.item.img_names = ['potions', f'blue potion {4-effect_obj.uses}']
            else:
                session.items.destroy(effect_obj.item)

    # Potions
    @register("heal")
    def heal(self, effect_obj):
        """ Heals player by the given amount without going over the maximum. """
        
        owner = effect_obj.owner

        owner.hp += 5
        if owner.hp > owner.max_hp:
            owner.hp = owner.max_hp

    @register("jug_of_blood")
    def jug_of_blood(self, effect_obj):
        owner = effect_obj.owner
        
        owner.hp -= 5
        if owner.hp <= 0:
            owner.hp = 0
            owner.dead = True
        else:
            owner.attack += 1

    # Environments
    @register("enter_home")
    def enter_home(self, effect_obj=None):
        if effect_obj: owner = effect_obj.owner
        
        place_player(
            ent = session.player_obj.ent,
            env = session.player_obj.envs.areas['overworld']['home'],
            loc = session.player_obj.envs.areas['overworld']['home'].player_coordinates)

    @register("enter_overworld")
    def enter_overworld(self, effect_obj=None):
        
        place_player(
            ent = session.player_obj.ent,
            env = session.player_obj.envs.areas['overworld']['overworld'],
            loc = session.player_obj.envs.areas['overworld']['overworld'].center)

    @register("enter_dungeon")
    def enter_dungeon(self, effect_obj=None, text=None, lvl_num=0):
        pyg = session.pyg

        pyg.add_intertitle(text)
        pyg.fn_queue.append([self.enter_dungeon_queue, {'lvl_num': lvl_num}])
        pyg.fade_state = 'out'

    def enter_dungeon_queue(self, effect_obj=None, lvl_num=0):
        """ Advances player to the next level. """


        
        #########################################################
        # Create and/or enter
        ## Enter the first dungeon
        if session.player_obj.ent.env.name != 'dungeon':
            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.areas['dungeon'][0],
                loc = session.player_obj.envs.areas['dungeon'][0].center)
        
        ## Enter the next saved dungeon
        elif session.player_obj.ent.env.lvl_num < len(session.player_obj.envs.areas['dungeon'].levels):
            lvl_num = session.player_obj.ent.env.lvl_num
            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.areas['dungeon'][lvl_num],
                loc = session.player_obj.envs.areas['dungeon'][lvl_num].center)
        
        ## Enter a new dungeon
        else:
            session.player_obj.envs.build_dungeon_level(lvl_num)
            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.areas['dungeon'][-1],
                loc = session.player_obj.envs.areas['dungeon'][-1].center)

    @register("enter_cave")
    def enter_cave(self, effect_obj=None):
        pyg = session.pyg

        pyg.add_intertitle("The ground breaks beneath you and reveals a cave.")
        pyg.fn_queue.append([self.enter_cave_queue,  {}])
        pyg.fade_state = 'out'

    def enter_cave_queue(self, effect_obj=None):
        """ Advances player to the next level. """
    
        ## Shorthand
        envs = session.player_obj.envs
        ent  = session.player_obj.ent
        pyg  = session.pyg
        
        #########################################################
        # Create and/or enter
        ## Create
        if 'cave' not in envs.areas.keys():
            envs.add_area('cave')
            envs.areas['cave'].add_level('cave')
        
        ## Enter the first cave
        if ent.env.name != 'cave':
            pyg.update_gui("The ground breaks beneath you and reveals a cave.", pyg.dark_gray)
            place_player(
                ent = ent,
                env = envs.areas['cave'][0],
                loc = envs.areas['cave'][0].center)
        
        ## Enter the next saved cave
        elif ent.env.lvl_num < len(envs.areas['cave'].levels):
            pyg.update_gui("You descend deeper into the cave.", pyg.dark_gray)
            lvl_num = ent.env.lvl_num
            place_player(
                ent = ent,
                env = envs.areas['cave'][lvl_num],
                loc = envs.areas['cave'][lvl_num].center)
        
        ## Enter a new cave
        else:
            envs.areas['cave'].add_level('cave')
            place_player(
                ent = ent,
                env = envs.areas['cave'][-1],
                loc = envs.areas['cave'][-1].center)

    @register("enter_hallucination")
    def enter_hallucination(self, effect_obj=None):
        pyg = session.pyg

        pyg.add_intertitle(". . . ! Your vision blurs as the substance seeps through your veins.")
        pyg.fn_queue.append([self.enter_hallucination_queue,  {}])
        pyg.fade_state = 'out'

    def enter_hallucination_queue(self):
        """ Advances player to the next level. """
    
        ## Shorthand
        envs = session.player_obj.envs
        ent  = session.player_obj.ent
        pyg  = session.pyg
        
        #########################################################
        # Create and/or enter
        ## Create environment
        if 'hallucination' not in envs.areas.keys():
            envs.add_area('hallucination')
            envs.areas['hallucination'].add_level('hallucination')
            pyg.overlay_state = None
            envs.build_hallucination_level()

        ## Enter the first hallucination
        if ent.env.name != 'hallucination':
            place_player(
                ent = ent,
                env = envs.areas['hallucination'][0],
                loc = envs.areas['hallucination'][0].center)
        
        ## Enter the next saved hallucination
        elif ent.env.lvl_num < len(envs.areas['hallucination'].levels):
            lvl_num = ent.env.lvl_num
            place_player(
                ent = ent,
                env = envs.areas['hallucination'][lvl_num],
                loc = envs.areas['hallucination'][lvl_num].center)
        
        ## Enter a new hallucination
        else:
            envs['hallucination'].add_level('hallucination')
            place_player(
                ent = ent,
                env = envs.areas['hallucination'][-1],
                loc = envs.areas['hallucination'][-1].center)

    @register("enter_bitworld")
    def enter_bitworld(self, effect_obj=None, text=None):
        """ Advances player to bitworld. """
        
        if text == None: text = '. . . ! Your vision blurs as the substance seeps through your veins.'

        ## Shorthand
        envs = session.player_obj.envs
        ent  = session.player_obj.ent
        pyg  = session.pyg

        #########################################################
        # Create and/or enter
        ## Create
        if 'bitworld' not in envs.areas.keys():
            envs.add_area('bitworld')
            envs['bitworld'].add_level['overworld']
            
            pyg.overlay_state = None
            envs.build_bitworld()

        ## Enter
        if ent.env.name != 'bitworld':
            session.img.render_fx = 'bw_binary'
            place_player(
                ent = ent,
                env = envs.areas['bitworld']['overworld'],
                loc = envs.areas['bitworld']['overworld'].center)

    # Item effects
    @register("boost_stamina")
    def boost_stamina(self, effect_obj):
        owner = effect_obj.owner

        owner.stamina += 50
        if owner.stamina > 100:
            owner.stamina = 100

        session.pyg.update_gui()

    @register("entity_eat")
    def entity_eat(self, effect_obj=None, target=None):
        """ Dropped item effect. """
        
        session.stats_obj.pet_moods['happiness'] += 1
        session.stats_obj.pet_moods['boredom']   -= 1
        image = session.img.dict['bubbles']['heart bubble']
        session.img.flash_above(target, image)
        target.tile.item = None

    # Gameplay
    @register("movement_speed")
    def movement_speed(self, effect_obj=None, toggle=True, custom=None):
        """ Toggles and sets movement speed. """
        
        pyg = session.pyg

        # Check stamina
        if session.player_obj.ent.stamina > 0:
        
            # Change speed
            if toggle:
                if self.movement_speed_toggle == len(self.speed_list)-1: 
                    self.movement_speed_toggle = 0
                else:
                    self.movement_speed_toggle += 1
                pyg.update_gui(f"Movement speed: {self.speed_list[self.movement_speed_toggle][0]}", pyg.dark_gray)
                (hold_time, repeat_time) = self.speed_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Set custom speed
            elif custom is not None:
                (hold_time, repeat_time) = self.speed_list[custom][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Restore previous speed
            else:
                (hold_time, repeat_time) = self.speed_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
        else:            
            
            # Change speed
            if toggle:
                if self.movement_speed_toggle == len(self.slow_list)-1: 
                    self.movement_speed_toggle = 0
                else:
                    self.movement_speed_toggle += 1
                pyg.update_gui(f"Movement speed: {self.slow_list[self.movement_speed_toggle][0]}", pyg.dark_gray)
                (hold_time, repeat_time) = self.slow_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Set custom speed
            elif custom is not None:
                custom = custom % 2
                (hold_time, repeat_time) = self.slow_list[custom][1]
                pygame.key.set_repeat(hold_time, repeat_time)
            
            # Restore previous speed
            else:
                (hold_time, repeat_time) = self.slow_list[self.movement_speed_toggle][1]
                pygame.key.set_repeat(hold_time, repeat_time)

    # Item interactions
    @register("death_note")
    def death_note(self, effect_obj=None, ent=None):
        
        # Find location
        loc = session.player_obj.ent.env
        locs = ['garden', 'womb', 'home', 'dungeon', 'hallucination', 'overworld', 'bitworld', 'cave']
        
        # Define notification bank
        dead_log = {
            'garden': [
                "... this must be a dream."],
            
            'womb': [
                "... this must be a dream."],
            
            'home': [
                "A skeleton... in your home."],
            
            'dungeon': [
                "Skeleton. Looks like a Greg.",
                "Ow! Shouldn't poke around with bones.",
                "Wait... is this Jerry?",
                "The pile of bones lay motionless, thankfully.",
                "Decay is swift.",
                "..."],
            
            'hallucination': [
                "Bones? I must be seeing things.",
                "..."],
            
            'overworld': [
                "Should I be concerned about this?",
                "Looks human. Something bad happened here.",
                "..."],
            
            'bitworld': [
                "Are these dots inside of me too?",
                "What is...?",
                "..."
                ],
            
            'cave': [
                "Typical.",
                "Caves can kill in mysterious ways."]}
        
        if random.randint(0, 4): image = session.img.dict['bubbles']['skull bubble']
        else:                    image = session.img.dict['bubbles']['exclamation bubble']
        session.img.flash_above(session.player_obj.ent, image)

_effects = EffectsSystem(_registry)

########################################################################################################################################################