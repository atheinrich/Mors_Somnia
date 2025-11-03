########################################################################################################################################################
# Local mechanics
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random
import time
import sys

## Specific
import pygame
from   pygame.locals import *

## Local
import session

########################################################################################################################################################
# Core
class PlayGame:

    # Core
    def __init__(self):

        self.last_press_time = 0
        self.cooldown_time   = 1
        self.gui_set         = 0
        self.death_cooldown  = 1

        self.death_checked = False

    def run(self):
        pyg = session.pyg
        ent = session.player_obj.ent

        #########################################################
        # Initialize
        active_effects()

        ## Reset from last death
        if (not ent.dead) and self.death_checked:
            self.death_checked = False

        ## Set navigation speed
        session.effects.movement_speed(toggle=False)
        
        ## Wait for input
        if (not pyg.pause) and (pyg.overlay_state is None):
            
            #########################################################
            # Play game if alive
            for event in pygame.event.get():

                if event.type == KEYDOWN:

                    if not ent.dead:
                            
                        #########################################################
                        # Move player
                        if event.key in pyg.key_UP:
                            self.key_UP()
                        elif event.key in pyg.key_DOWN:
                            self.key_DOWN()
                        elif event.key in pyg.key_LEFT:
                            self.key_LEFT()
                        elif event.key in pyg.key_RIGHT:
                            self.key_RIGHT()

                        #########################################################
                        # Activate objects below
                        elif event.key in pyg.key_ENTER:
                            self.key_ENTER()
                        elif event.key in pyg.key_PERIOD:
                            self.key_PERIOD()
                        
                        #########################################################
                        # Enter combo sequence
                        elif event.key in pyg.key_HOLD:
                            self.key_HOLD()
                            return
            
                        #########################################################
                        # Zoom camera
                        elif event.key in pyg.key_PLUS:
                            self.key_PLUS()
                        elif event.key in pyg.key_MINUS:
                            self.key_MINUS()
                        
                        print((ent.X, ent.Y))

                elif event.type == pygame.KEYUP:

                    if not ent.dead:
                        
                        #########################################################
                        # Adjust speed
                        if event.key in pyg.key_SPEED:
                            self.key_SPEED()

                        #########################################################
                        # Open side menu
                        elif event.key in pyg.key_INV:
                            self.key_INV()
                            return
                        elif event.key in pyg.key_DEV:
                            self.key_DEV()
                            return

                    #########################################################
                    # View stats
                    if event.key in pyg.key_INFO:
                        self.key_INFO()
                        return
                        
                    #########################################################
                    # Open questlog
                    elif event.key in pyg.key_QUEST:
                        self.key_QUEST()
                        return
                    
                    #########################################################
                    # Toggle GUI
                    elif event.key in pyg.key_GUI:
                        self.key_GUI()
                        
                    #########################################################
                    # Open main menu
                    elif event.key in pyg.key_BACK:
                        self.key_BACK()
                        return

                # Quit
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
            #########################################################
            # Handle player death
            if ent.dead:
                self.handle_death()

        #########################################################
        # Move AI controlled entities
        if not pyg.pause:
            for ent in ent.env.entities:
                session.movement.ai(ent)
        
        pyg.game_state = 'play_game'
        return

    def render(self):
        pyg = session.pyg

        pyg.msg_height = 4
        if not pyg.overlay_state: pyg.update_gui()

    # Navigation
    def key_UP(self):
        session.movement.move(session.player_obj.ent, 0, -session.pyg.tile_height)

    def key_DOWN(self):
        session.movement.move(session.player_obj.ent, 0, session.pyg.tile_height)

    def key_LEFT(self):
        session.movement.move(session.player_obj.ent, -session.pyg.tile_width, 0)

    def key_RIGHT(self):
        session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)

    # Action
    def key_ENTER(self):
        pyg = session.pyg

        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            # Check if an item is under the player
            if session.player_obj.ent.tile.item:
                tile = session.player_obj.ent.tile
                
                #########################################################
                # Entryway
                if tile.item.name == 'dungeon':     session.effects.enter_dungeon()
                elif tile.item.name == 'cave':      session.effects.enter_cave()
                elif tile.item.name == 'overworld': session.effects.enter_overworld()
                elif tile.item.name == 'home':      session.effects.enter_home()
                
                
                #########################################################
                # Furniture
                ## Bed
                elif tile.item.name in ['red bed', 'purple bed']:
                    
                    # Check if it is the player's bed
                    if tile.room:
                        if tile.room.name == 'home room':
                            
                            # Go to sleep if it's not daytime
                            if session.player_obj.ent.env.env_time in [1, 2, 7, 8]:
                                session.player_obj.ent.env.env_time = (session.player_obj.ent.env.env_time + 3) % 8
                                session.effects.enter_dungeon(text="The evening dims to night... sleep trustly follows.")
                            else: pyg.update_gui("Time to face the day.", pyg.dark_gray)
                        
                        # No sleeping in owned beds
                        else: pyg.update_gui("This is not your bed.", pyg.dark_gray)
                    
                    else: pyg.update_gui("This is not your bed.", pyg.dark_gray)
                
                ## Chair
                elif tile.item.name in ['red chair left', 'red chair right']:
                    session.player_obj.ent.env.weather.set_day_and_time(increment=True)
                    pyg.update_gui("You sit down to rest for a while.", pyg.dark_gray)
                
                #########################################################
                # Items
                else: session.items.pick_up(session.player_obj.ent.tile.item)

    def key_PERIOD(self):
        
        #########################################################
        # Move down a level
        if session.player_obj.ent.tile.item:
            if session.player_obj.ent.tile.item.name in ['dungeon', 'cave']:
                if time.time()-self.last_press_time > self.cooldown_time:
                    self.last_press_time = float(time.time())
                
                    # Go up by one floor
                    if session.player_obj.ent.env.lvl_num > 1:
                        env = session.player_obj.envs.areas[session.player_obj.ent.env.name][session.player_obj.ent.env.lvl_num-2]
                        place_player(
                            ent = session.player_obj.ent,
                            env = env,
                            loc = env.player_coordinates)
                    
                    elif session.player_obj.ent.env.lvl_num == 1:
                        env = session.player_obj.ent.last_env
                        place_player(
                            ent = session.player_obj.ent,
                            env = env,
                            loc = env.player_coordinates)

    def key_SPEED(self):
        session.effects.movement_speed()

    def key_BACK(self):
        pyg = session.pyg

        pyg.overlay_state = 'menu'
        pyg.hud_state     = 'off'

    # Menus
    def key_HOLD(self):
        session.pyg.overlay_state = 'hold'

    def key_INFO(self):
        session.pyg.overlay_state = 'ent_stats'

    def key_INV(self):
        session.pyg.overlay_state = 'inv'

    def key_DEV(self):
        session.pyg.overlay_state = 'dev'

    def key_QUEST(self):
        pyg = session.pyg

        pyg.overlay_state = 'questlog'
        pyg.hud_state     = 'off'

    # GUI
    def key_GUI(self):
        
        pyg = session.pyg

        #########################################################
        # Change GUI setting
        self.gui_set = (self.gui_set + 1) % 4
        
        #########################################################
        # Apply setting
        ## Show all
        if self.gui_set == 0:
            pyg.gui_toggle = True
            pyg.msg_toggle = True
        
        ## Hide GUI
        elif self.gui_set == 1:
            pyg.gui_toggle = False
            pyg.msg_toggle = True
        
        ## Hide both
        elif self.gui_set == 2:
            pyg.gui_toggle = False
            pyg.msg_toggle = False

        ## Hide messages
        elif self.gui_set == 3:
            pyg.gui_toggle = True
            pyg.msg_toggle = False

    def key_PLUS(self):
        session.player_obj.ent.env.camera.zoom_in()

    def key_MINUS(self):
        session.player_obj.ent.env.camera.zoom_out()

    # Tools
    def handle_death(self):
        """ Overwrite save files for permadeath or revive the player. """

        pyg = session.pyg
        ent = session.player_obj.ent

        # End the game
        if ent.env.area.permadeath:
            if (not session.img.render_log) and (not self.death_checked):
                session.file_menu.check_player_id(ent.player_id)
                self.death_checked = True
        
        # Revive player
        else:
            drug_locs  = ['hallucination', 'bitworld']
            dream_locs = ['dungeon']

            # Regain consciousness
            if ent.env.name in drug_locs:
                text = "Delirium passes, but nausea remains."
            
            # Wake up at home
            elif ent.env.name in dream_locs:
                text = "Your cling to life has slipped, yet you wake unscarred in bed."
            
            else:
                text = "???"

            pyg.add_intertitle(text)
            pyg.fn_queue.append([self.revive_player,  {}])
            pyg.fade_delay = 500
            pyg.fade_state = 'out'

            ent.dead = False

    def revive_player(self):
        pyg = session.pyg
        ent = session.player_obj.ent

        last_env = session.player_obj.envs.areas['overworld'].last_env

        # Restore player state
        ent.hp          = ent.max_hp
        pyg.gui         = {}
        pyg.msg         = []
        pyg.msg_history = {}
        session.effects.movement_speed(toggle=False, custom=0)
        
        pyg.overlay_state = None
        place_player(
            ent = ent,
            env = last_env,
            loc = last_env.player_coordinates)
        session.img.render_fx = None
        pygame.event.clear()

class PlayGarden:

    # Core
    def run(self):
        """ Hosts garden gamestate as a lightweight variant of PlayGame. """
        
        pyg = session.pyg
        ent = session.player_obj.ent

        #########################################################
        # Initialize
        ## Update pet stats, mood, and effects
        session.stats_obj.pet_update()
        
        ## Active AI when viewing the main menu
        print('--------------')
        if pyg.overlay_state == 'menu': session.player_obj.ent.role = 'NPC'
        else:                           session.player_obj.ent.role = 'player'
        
        ## Set camera (?)
        session.player_obj.envs.areas['underworld']['garden'].camera.zoom_in(custom=1)
        
        ## Set navigation speed
        session.effects.movement_speed(toggle=False, custom=2)
        
        ## Wait for input
        if pyg.overlay_state is None:
            for event in pygame.event.get():
                
                #########################################################
                # Keep playing
                if event.type == KEYDOWN:

                    if not ent.dead:
                            
                        #########################################################
                        # Move player
                        if event.key in pyg.key_UP:
                            self.key_UP()
                        elif event.key in pyg.key_DOWN:
                            self.key_DOWN()
                        elif event.key in pyg.key_LEFT:
                            self.key_LEFT()
                        elif event.key in pyg.key_RIGHT:
                            self.key_RIGHT()

                        #########################################################
                        # Activate objects below
                        elif event.key in pyg.key_ENTER:
                            self.key_ENTER()
                        
                        #########################################################
                        # Enter combo sequence
                        elif event.key in pyg.key_HOLD:
                            self.key_HOLD()
                            return

                        print((ent.X, ent.Y))

                elif event.type == pygame.KEYUP:

                    if not ent.dead:
                        
                        #########################################################
                        # Open side menu
                        if event.key in pyg.key_INV:
                            self.key_INV()
                            return
                        elif event.key in pyg.key_DEV:
                            self.key_DEV()
                            return

                    #########################################################
                    # View stats
                    if event.key in pyg.key_INFO:
                        self.key_INFO()
                        return
                    
                    #########################################################
                    # Open questlog
                    elif event.key in pyg.key_QUEST:
                        self.key_QUEST()
                        return
                    
                    #########################################################
                    # Open main menu
                    elif event.key in pyg.key_BACK:
                        self.key_BACK()
                        return

                # Quit
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()

        #########################################################
        # Move AI controlled entities
        if not pyg.pause:

            for ent in ent.env.entities:
                session.movement.ai(ent)

            session.movement.ai(session.player_obj.ent)
        
        pyg.game_state = 'play_garden'
        return

    def render(self):
        pass

    # Navigation
    def key_UP(self):
        session.movement.move(session.player_obj.ent, 0, -session.pyg.tile_height)

    def key_DOWN(self):
        session.movement.move(session.player_obj.ent, 0, session.pyg.tile_height)

    def key_LEFT(self):
        session.movement.move(session.player_obj.ent, -session.pyg.tile_width, 0)

    def key_RIGHT(self):
        session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)

    # Action
    def key_ENTER(self):
        if session.player_obj.ent.tile.item:
            session.items.pick_up(session.player_obj.ent.tile.item)

    def key_BACK(self):
        pyg = session.pyg

        pyg.overlay_state = 'menu'
        pyg.hud_state     = 'off'

    # Menus
    def key_HOLD(self):
        session.pyg.overlay_state = 'hold'

    def key_INFO(self):
        session.pyg.overlay_state = 'pet_stats'

    def key_INV(self):
        session.pyg.overlay_state = 'inv'

    def key_DEV(self):
        session.pyg.overlay_state = 'dev'

    def key_QUEST(self):
        pyg = session.pyg

        pyg.overlay_state = 'questlog'
        pyg.hud_state     = 'off'

########################################################################################################################################################
# Interactions
class MovementSystem:

    def ai(self, ent):
        """ Preset movements. """
        
        #########################################################
        # Move if alive
        moved = False
        if not ent.dead:
            if time.time()-ent.last_press > ent.cooldown:
                ent.last_press = float(time.time())
                
                # Move or follow
                if not ent.motions_log:
                    distance = self.distance_to(ent, session.player_obj.ent)
                    
                    #########################################################
                    # Flee
                    if ent.fear and (type(ent.fear) == int):
                        if not random.randint(0, ent.lethargy//10):
                            self.move_towards(ent, ent.X0, ent.Y0)
                            ent.fear -= 1
                            if ent.fear < 0: ent.fear = 0
                    
                    #########################################################
                    # Approach far, possibly attack
                    elif ent.follow and (distance < 320):
                        if not random.randint(0, ent.lethargy//2):
                            self.move_towards(ent, session.player_obj.ent.X, session.player_obj.ent.Y)
                    
                        # Attack if close and aggressive; chance based on miss_rate
                        if ent.aggression:
                            if (distance < 64) and not random.randint(0, ent.miss_rate):
                                session.interact.attack_target(ent, session.player_obj.ent)
                    
                    #########################################################
                    # Approach near, possibly attack
                    elif ent.aggression and (session.player_obj.ent.hp > 0):
                        
                        # Attack if close and aggressive; chance based on miss_rate
                        if (distance < 64) and not random.randint(0, ent.miss_rate):
                            session.interact.attack_target(ent, session.player_obj.ent)
                        
                        # Move towards the player if distant; chance based on lethargy
                        elif (distance < ent.aggression*session.pyg.tile_width) and not random.randint(0, ent.lethargy//2) and not moved:
                            self.move_towards(ent, session.player_obj.ent.X, session.player_obj.ent.Y)
                    
                    #########################################################
                    # Idle if not following or aggressive
                    else:
                        if ent.role != 'player':
                            self.idle(ent)
                
                #########################################################
                # Continue a prescribed pattern
                else:
                    loc = ent.motions_log[0]
                    self.move(ent, loc[0], loc[1])
                    ent.motions_log.remove(loc)

    def idle(self, ent):
        """ Randomly walks around """
        
        pyg = session.pyg

        # Choose direction
        if random.randint(0, 1):
            dX = random.randint(-1, 1) * pyg.tile_width
            dY = 0
        else:
            dX = 0
            dY = random.randint(-1, 1) * pyg.tile_width
        
        # Move
        if self.distance_new(ent, [ent.X+dX, ent.Y+dY], [ent.X0, ent.Y0]) <= ent.reach:
            if   (dX < 0) and (ent.img_names[1] == 'left'):  chance = 5
            elif (dX > 0) and (ent.img_names[1] == 'right'): chance = 5
            elif (dY < 0) and (ent.img_names[1] == 'back'):  chance = 5
            elif (dY > 0) and (ent.img_names[1] == 'front'): chance = 5
            else:                                             chance = 1
            if not random.randint(0, ent.lethargy//chance):
                self.move(ent, dX, dY)

    def move(self, ent, dX, dY):
        """ Moves the player by the given amount if the destination is not blocked.
            May activate any of the following:
            - motion
            - floor effects
            - dialogue
            - combat
            - digging """
        
        pyg = session.pyg

        #########################################################
        # Orientation
        ## Determine direction
        if   dY > 0: ent.direction = 'front'
        elif dY < 0: ent.direction = 'back'
        elif dX < 0: ent.direction = 'left'
        elif dX > 0: ent.direction = 'right'
        
        ## Change orientation before moving
        if ent.img_names[1] != ent.direction:
            ent.img_names[1] = ent.direction

        #########################################################
        # Move to new position
        else:

            # Find new position in tile units
            x = int((ent.X + dX)/pyg.tile_width)
            y = int((ent.Y + dY)/pyg.tile_height)
                
            #########################################################
            # Move forward in allowed biome
            if (not is_blocked(ent.env, [x, y])) and (ent.env.map[x][y].biome in session.img.biomes[ent.habitat]):
                    
                    # Prevent non-player entities from standing in entryways
                    if (ent.name != "player") and (ent.env.map[x][y].item):
                        if ent.env.map[x][y].item.img_names[0] in session.img.other['stairs']:
                            return
                    
                    # Player-specific
                    elif ent.name == 'player':
                        ent.env.player_coordinates = [x, y]
                        check_tile(x, y)

                        # Check stamina
                        if (session.effects.movement_speed_toggle == 1) and (ent.stamina > 0):
                            ent.stamina -= 1/2
                            pyg.update_gui()

                    # Move player and update map
                    ent.prev_tile              = ent.env.map[int(ent.X/pyg.tile_width)][int(ent.Y/pyg.tile_height)]
                    ent.X                      += dX
                    ent.Y                      += dY
                    ent.tile.entity            = None
                    ent.env.map[x][y].entity   = ent
                    ent.tile                   = ent.env.map[x][y]

                    # Activate effects
                    session.effects.check_tile(ent)
                
            #########################################################
            # Interact with an entity
            elif ent.env.map[x][y].entity:
                session.interact.interact(ent, ent.env.map[x][y].entity)
            
            elif ent.equipment['dominant hand'] is not None:
                self.dig_tunnel(ent, x, y, dX, dY)
                session.effects.check_tile(ent)

        ent.env.camera.update() # omit this if you want to modulate when the camera focuses on the player

    def dig_tunnel(self, ent, x, y, dX, dY):

        #########################################################
        # Dig a tunnel
        pyg = session.pyg
        if ent.equipment['dominant hand'].name in ['shovel', 'super shovel']:
            
            # Move player and reveal tiles
            if ent.X >= 64 and ent.Y >= 64:
                if ent.super_dig or not ent.env.map[x][y].unbreakable:
                    ent.env.create_tunnel(x, y)
                    ent.prev_tile                 = ent.env.map[int(ent.X/pyg.tile_width)][int(ent.Y/pyg.tile_height)]
                    ent.X                         += dX
                    ent.Y                         += dY
                    ent.tile.entity               = None
                    ent.env.map[x][y].blocked     = False
                    ent.env.map[x][y].unbreakable = False
                    ent.env.map[x][y].img_names   = ent.env.floors
                    ent.env.map[x][y].entity      = ent
                    ent.tile                      = ent.env.map[x][y]
                    ent.env.player_coordinates    = [x, y]
                    check_tile(x, y)
                else:
                    pyg.update_gui("The shovel strikes the barrier but does not break it.", pyg.dark_gray)
                
                # Update durability
                if ent.equipment['dominant hand'].durability <= 100:
                    ent.equipment['dominant hand'].durability -= 1
                if ent.equipment['dominant hand'].durability <= 0:
                    pyg.update_gui(f"Broken {ent.equipment['dominant hand'].name}!", color=pyg.dark_gray)
                    session.items.drop(ent.equipment['dominant hand'])
                    ent.tile.item = None # removes item from world
    
    def move_towards(self, ent, target_X, target_Y):
        """ Moves object towards target. """
        
        pyg = session.pyg

        dX       = target_X - ent.X
        dY       = target_Y - ent.Y
        distance = (dX ** 2 + dY ** 2)**(1/2)
        if distance:
            
            if dX and not dY:
                dX = round(dX/distance) * pyg.tile_width
                dY = 0
            
            elif dY and not dX:
                dX = 0
                dY = round(dX/distance) * pyg.tile_width
            
            elif dX and dY:
                if random.randint(0, 1):
                    dX = round(dX/distance) * pyg.tile_width
                    dY = 0
                else:
                    dX = 0
                    dY = round(dY/distance) * pyg.tile_width
            
            self.move(ent, dX, dY)

    def distance_to(self, ent, other):
        """ Returns the distance to another object. """
        
        if type(other) in [tuple, list]:
            dX = other[0] - ent.X
            dY = other[1] - ent.Y
        else:
            dX = other.X - ent.X
            dY = other.Y - ent.Y
        return (dX ** 2 + dY ** 2)**(1/2)

    def distance_new(self, ent, loc_1, loc_2):
        return ((loc_2[0] - loc_1[0]) ** 2 + (loc_2[1] - loc_1[1]) ** 2)**(1/2)

class InteractionSystem:

    def interact(self, ent, target):
        """ Routes the interaction to the proper channel based on entities and location. """

        # Player specific
        if ent.role == 'player':

            if target.role == 'NPC':

                # Trading
                if target.trade_active and not target.quest_active:
                    session.trade_obj.ent = target
                    session.pyg.overlay_state = 'trade'
            
                # Dialogue
                session.player_obj.dialogue.emit_dialogue(target.name)
        
            # Make them flee
            elif type(target.fear) == int:
                target.fear += 30
            
            # Attack
            elif session.pyg.game_state != 'play_garden':
                self.attack_target(ent, target)
        
            # Emit interaction
            session.bus.emit(
                event_id      = 'entity_interacted',
                ent_id        = ent.name,
                target_ent_id = target.name)
        
        # General
        elif session.pyg.game_state != 'play_garden':

            if ent.role == 'NPC':
                if target.role != 'player':
                    self.attack_target(ent, target)
            
            else:
                self.attack_target(ent, target)
    
    def attack_target(self, ent, target, effect_check=True):
        """ Calculates and applies attack damage. """
        
        pyg = session.pyg
        gui = ""

        # Only attack living targets
        if not target.dead:
            
            # No attacking yourself
            if ent.name != target.name:
                
                # Default damage calculation
                damage = ent.attack - target.defense
                
                # Deal damage
                if damage > 0:
                    
                    # Apply an effect
                    if effect_check and not random.randint(0, 1):
                        if ent.equipment['dominant hand']:
                            if ent.equipment['dominant hand'].effect:
                                if ent.equipment['dominant hand'].effect.trigger == 'passive':
                                    ent.equipment['dominant hand'].effect.effect_fn(ent)
                        
                        # Regular attack
                        else:
                            gui = ent.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points."
                            self.take_damage(target, damage)
                    
                    # Regular attack
                    else:
                        gui = ent.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points."
                        self.take_damage(target, damage)
                else:
                    gui = ent.name.capitalize() + " strikes " + target.name + " but it has no effect!"
        
        # Update gui
        if gui and (ent.role == 'player') or (target.role == 'player'):
            pyg.update_gui(gui, pyg.red)

        return

    def take_damage(self, ent, damage):
        """ Applies damage if possible. """
        
        if damage > 0:
            
            # Apply damage
            ent.hp -= damage
            
            # Damage animation
            session.img.flash_over(ent)
            
            # Check for death
            if ent.hp <= 0:
                ent.hp = 0
                session.interact.death(ent)
                
                # Gain experience
                if ent != session.player_obj.ent:
                    session.player_obj.ent.exp += ent.exp
                    check_level_up()
                else:
                    session.pyg.update_gui()

    def death(self, ent):
        
        pyg = session.pyg

        #########################################################
        # Imports
        from items_entities import create_item
        from environments import place_object

        #########################################################
        # Player death
        if ent.role == 'player':
            pyg.update_gui("You died!", pyg.red)
            session.player_obj.ent.dead        = True
            session.player_obj.ent.tile.entity = None
            session.player_obj.ent.img_names   = session.player_obj.ent.img_names_backup
            
            item = create_item('skeleton')
            item.name = f"the corpse of {ent.name}"
            place_object(item, [ent.X//pyg.tile_width, ent.Y//pyg.tile_height], ent.env)
            pygame.event.clear()
        
        #########################################################
        # Entity or projectile death
        else:
            ent.dead        = True
            ent.tile.entity = None
            ent.env.entities.remove(ent)
            if ent in session.player_obj.ent.env.entities: session.player_obj.ent.env.entities.remove(ent)
            
            if ent.role != 'projectile':
                pyg.update_gui("The " + ent.name + " is dead! You gain " + str(ent.exp) + " experience points.", pyg.red)
                
                if not ent.tile.item:
                    item = create_item('bones')
                    item.name = f"the corpse of {ent.name}"
                    place_object(item, [ent.X//pyg.tile_width, ent.Y//pyg.tile_height], ent.env)
                    ent.role = 'corpse'

            del ent

            pygame.event.get()
        pygame.event.clear()

class ItemSystem:

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
                    ent.item_effects.append(item.effect)
                
                ent.inventory[item.role].append(item)
                sort_inventory(ent)
                
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
                if item.effect in ent.effects: ent.effects.remove(item.effect)
            ent.inventory[item.role].remove(item)
            ent.tile.item = item

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
            session.items.pick_up(item, ent=recipient)
            recipient.wallet -= item.cost
        
        else:
            pyg.update_gui("Not enough cash!", color=pyg.red)

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
                ent.effects.append(item.effect)
            
            # Activate the item
            else: item.effect.effect_fn(ent)
        
        elif ent.role == 'player':
            pyg.update_gui("The " + item.name + " cannot be used.", pyg.dark_gray)

    def toggle_equip(self ,item, ent, silent=False):
        """ Toggles the equip/unequip status. """
        
        # Assign entity
        if not ent:        ent = session.player_obj.ent
        if not item.owner: item.owner = ent
        
        # Equip or dequip
        if item.equipped: self.dequip(item, ent, silent)
        else:             self.equip(item, ent, silent)

    def equip(self, item, ent, silent=False):
        """ Unequips object if the slot is already being used. """
        
        pyg = session.pyg

        # Check if anything is already equipped
        if ent.equipment[item.slot] is not None:
            self.dequip(ent.equipment[item.slot], ent)
        
        # Apply stat adjustments
        ent.equipment[item.slot] = item
        ent.max_hp  += item.hp_bonus
        ent.attack  += item.attack_bonus
        ent.defense += item.defense_bonus
        if item.effect:
            if item.effect.trigger == 'active': ent.effects.append(item.effect)
        item.equipped = True

        if ent.role == 'player':
            if not item.hidden and not silent:
                pyg.update_gui("Equipped " + item.name + " on " + item.slot + ".", pyg.dark_gray)

    def dequip(self, item, ent, silent=False):
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
            if item.effect in ent.effects:
                ent.effects.remove(item.effect)

        #########################################################
        # Notify change of status
        item.equipped = False
        if ent.role == 'player':
            if not item.hidden and not silent:
                pyg.update_gui("Dequipped " + item.name + " from " + item.slot + ".", pyg.dark_gray)

class EffectsSystem:

    def __init__(self):
        
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

    def check_tile(self, ent):
        if ent.tile.item:
            if ent.tile.item.effect:
                ent.tile.item.effect.effect_fn(ent)

    def heal(self, ent, amount):
        """ Heals player by the given amount without going over the maximum. """
        
        ent.hp += amount
        if ent.hp > ent.max_hp:
            ent.hp = ent.max_hp

    def jug_of_blood(self, ent, amount):
        """ Heals player by the given amount without going over the maximum. """
        
        ent.hp -= amount
        if ent.hp <= 0:
            ent.hp = 0
            ent.dead = True
        else:
            ent.attack += 1

    def toggle_effects(self, ent):
        """ Switches between different sets of effects. """
        
        if ent.env.name == 'garden': ent.effects = ent.garden_effects
        else:                         ent.effects = ent.item_effects

    def capture(self, ent):
        pyg = session.pyg

        pyg.update_gui("The " + ent.name + " has been captured!", pyg.red)

        # Update entity
        ent.dead        = True
        ent.tile.entity = None
        ent.env.entities.remove(ent)
        if ent in session.player_obj.ent.env.entities: session.player_obj.ent.env.entities.remove(ent)
        
        session.player_obj.ent.discoveries['entities'][ent.name] = ent.img_names

    # Environments
    def enter_dungeon(self, text, lvl_num=0):
        pyg = session.pyg

        pyg.add_intertitle(text)
        pyg.fn_queue.append([self.enter_dungeon_queue, {'lvl_num': lvl_num}])
        pyg.fade_state = 'out'

    def enter_dungeon_queue(self, lvl_num):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
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

    def enter_home(self):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.areas['overworld']['home'],
                loc = session.player_obj.envs.areas['overworld']['home'].player_coordinates)

    def enter_overworld(self):
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()

            place_player(
                ent = session.player_obj.ent,
                env = session.player_obj.envs.areas['overworld']['overworld'],
                loc = session.player_obj.envs.areas['overworld']['overworld'].center)

    def enter_cave(self):
        pyg = session.pyg

        pyg.add_intertitle("The ground breaks beneath you and reveals a cave.")
        pyg.fn_queue.append([self.enter_cave_queue,  {}])
        pyg.fade_state = 'out'

    def enter_cave_queue(self):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()

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

    def enter_hallucination(self):
        pyg = session.pyg

        pyg.add_intertitle(". . . ! Your vision blurs as the substance seeps through your veins.")
        pyg.fn_queue.append([self.enter_hallucination_queue,  {}])
        pyg.fade_state = 'out'

    def enter_hallucination_queue(self):
        """ Advances player to the next level. """
        
        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
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

    def enter_bitworld(self, text=None):
        """ Advances player to bitworld. """
        
        if text == None: text = '. . . ! Your vision blurs as the substance seeps through your veins.'

        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
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
    def swing(self, ent=None):

        # Set entity
        if not ent: ent = session.player_obj.ent
        
        # Check for remaining stamina
        if ent.stamina:
            
            # Send animation to queue
            image = session.img.dict[ent.equipment['dominant hand'].img_names[0]]['dropped']
            session.img.vicinity_flash(ent, image)
            
            # Apply attack to enemies
            for tile in get_vicinity(ent).values():
                if tile.entity:
                    ent.attack += 5
                    session.interact.attack_target(ent, tile.entity, effect_check=False)
                    ent.attack -= 5
            
            # Decrease stamina
            ent.stamina -= 5

    def boost_stamina(self, ent):
        ent.stamina += 50
        if ent.stamina > 100: ent.stamina = 100
        session.pyg.update_gui()

    def lamp(self, item):
        """ Adds or removes a light to be rendered under the following conditions.
            1. The object is not owned by an entity.
            2. The object is equipped by an entity. """
        
        if hasattr(item, 'env'):
            lamp_list = item.env.weather.lamp_list
        else:
            lamp_list = session.player_obj.ent.env.weather.lamp_list
        
        if item.owner:
            if item.equipped:
                if item not in lamp_list: lamp_list.append(item)
            else:
                if item in lamp_list:     lamp_list.remove(item)
        
        else:
            if item not in lamp_list: lamp_list.append(item)
            else:                     lamp_list.remove(item)

    def propagate(self, ent=None):
        
        pyg = session.pyg

        from items_entities import create_entity
        from environments import place_object

        # Set entity
        if not ent: ent = session.player_obj.ent
        
        # Note location and image names
        img_x, img_y = int(ent.X/pyg.tile_width), int(ent.Y/pyg.tile_height)
        
        # Set location for drop
        if ent.direction == 'front':   img_y += 1
        elif ent.direction == 'back':  img_y -= 1
        elif ent.direction == 'right': img_x += 1
        elif ent.direction == 'left':  img_x -= 1
        
        # Place item
        item = create_entity('green blob')
        item.lethargy = 0
        item.cooldown = 0.1
        item.direction = None
        place_object(
            obj   = item,
            loc   = [img_x, img_y],
            env   = ent.env,
            names = item.img_names)
        
        # Prepare movements
        motions_log = []
        directions = {
            'front': [0, pyg.tile_height],
            'back':  [0, -pyg.tile_height],
            'left':  [-pyg.tile_width, 0],
            'right': [pyg.tile_width, 0]}
        
        for _ in range(100):
            motions_log.append(directions[ent.direction])
        
        # Send directions to entity
        item.motions_log = motions_log

    # Gameplay
    def movement_speed(self, toggle=True, custom=None):
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

    def suicide(self, ent=None):
        
        # Activate animation
        image = session.img.dict['decor']['bones']
        session.img.vicinity_flash(session.player_obj.ent, image)
        
        # Kill player
        session.interact.death(session.player_obj.ent)
        return

    def spin(self, ent):
        
        pyg = session.pyg

        # Prepare movements
        motions_log = []
        
        # Look forward first
        if ent.img_names[0] != 'front':
            motions_log.append([0, pyg.tile_height])
        motions_log.append([-pyg.tile_width, 0])
        
        # Spin around
        motions_log.append([0, -pyg.tile_height])
        motions_log.append([pyg.tile_width, 0])
        motions_log.append([0, pyg.tile_height])
        
        # Send directions to entity
        ent.motions_log = motions_log

    def find_water(self, ent):
        """ Moves entity towards water. """
        
        pyg = session.pyg

        # Look for water
        if ent.tile.img_names[1] != 'water':
            
            # Prepare movements
            motions_log = []
            
            # Look for water
            for y in range(len(ent.env.map[0])):
                for x in range(len(ent.env.map)):
                    if ent.env.map[x][y].img_names[1] == 'water':
                        
                        # Construct a path
                        dX       = int(x*32) - ent.X
                        dY       = int(y*32) - ent.Y
                        distance = (dX ** 2 + dY ** 2)**(1/2)
                        while distance > 0:
                            
                            if dX and not dY:
                                dX = round(dX/distance) * pyg.tile_width
                                dY = 0
                            
                            elif dY and not dX:
                                dX = 0
                                dY = round(dX/distance) * pyg.tile_width
                            
                            elif dX and dY:
                                if random.randint(0, 1):
                                    dX = round(dX/distance) * pyg.tile_width
                                    dY = 0
                                else:
                                    dX = 0
                                    dY = round(dY/distance) * pyg.tile_width
                            
                            motions_log.append([dX, dY])
                            motions_log.append([dX, dY])
                            distance -= 32
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = session.img.dict['bubbles']['question bubble']

        # Bathe
        else:
            if session.stats_obj.pet_moods['anger']:
                session.stats_obj.pet_moods['anger'] -= 1
                image = session.img.dict['bubbles']['water bubble']
            
            else:
                session.stats_obj.pet_moods['boredom'] += 1
                image = session.img.dict['bubbles']['dots bubble']
            
        session.img.flash_above(ent, image)

    def find_bed(self, ent):
        """ Moves entity towards water. """
        
        pyg = session.pyg

        # Look for a bed
        item = bool(ent.tile.item)
        if item: bed = bool(ent.tile.item.name == 'bed')
        else:    bed = False
        if not item and not bed:
            
            # Prepare movements
            motions_log = []
            
            # Look for a bed
            for y in range(len(ent.env.map[0])):
                for x in range(len(ent.env.map)):
                    if ent.env.map[x][y].item:
                        if ent.env.map[x][y].item.name == 'bed':
                            if not ent.env.map[x][y].item.occupied:
                                ent.env.map[x][y].item.occupied = True
                                
                                # Construct a path
                                dX       = int(x*32) - ent.X
                                dY       = int(y*32) - ent.Y
                                distance = (dX ** 2 + dY ** 2)**(1/2)
                                while distance > 0:
                                    
                                    if dX and not dY:
                                        dX = round(dX/distance) * pyg.tile_width
                                        dY = 0
                                    
                                    elif dY and not dX:
                                        dX = 0
                                        dY = round(dX/distance) * pyg.tile_width
                                    
                                    elif dX and dY:
                                        if random.randint(0, 1):
                                            dX = round(dX/distance) * pyg.tile_width
                                            dY = 0
                                        else:
                                            dX = 0
                                            dY = round(dY/distance) * pyg.tile_width
                                    
                                    motions_log.append([dX, dY])
                                    motions_log.append([dX, dY])
                                    distance -= 32
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = session.img.dict['bubbles']['question bubble']

        # Sleep
        else:
            image = session.img.dict['bubbles']['dots bubble']
            
        session.img.flash_above(ent, image)

    # Entity interactions
    def entity_eat(self, ent):
        """ Dropped item effect. """
        
        session.stats_obj.pet_moods['happiness'] += 1
        session.stats_obj.pet_moods['boredom']   -= 1
        image = session.img.dict['bubbles']['heart bubble']
        session.img.flash_above(ent, image)
        ent.tile.item = None

    def entity_scare(self, ent=None):
        """ Combo effect. """

        pyg = session.pyg

        # Find entities in vicinity
        ent_list = []
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            
            if session.player_obj.ent.env.name == 'garden':
                session.stats_obj.pet_moods['lethargy'] -= 1
                session.stats_obj.pet_moods['boredom']  -= 1
            
            image = session.img.dict['bubbles']['exclamation bubble']
            for ent in ent_list:
                for tile in get_vicinity(ent).values():
                    if not tile.blocked:
                        self.move_towards(ent, tile.X, tile.Y)
                session.img.flash_above(ent, image)
        
        else:
            pyg.update_gui("There are no entities in your vicinity.", pyg.dark_gray)

    def entity_capture(self, ent=None):
        """ Combo effect. """

        pyg = session.pyg

        # Find entities in vicinity
        ent = None
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                if tile.entity.role != 'NPC':
                    ent = tile.entity
                    break
        
        # Activate effect if entities are found
        if ent:
            image = session.img.dict['bubbles']['heart bubble']
            session.img.flash_above(ent, image)
            session.img.flash_on(ent, session.img.dict[ent.img_names[0]][ent.img_names[1]])
            
            if session.player_obj.ent.discoveries['entities'].values():
                for names in session.player_obj.ent.discoveries['entities'].values():
                    if ent.name not in names:
                        session.effects.capture(ent)
                        break
                    else:
                        pyg.update_gui("The " + ent.name + " has already been logged.", pyg.dark_gray)
            else:
                session.effects.capture(ent)
        else:
            pyg.update_gui("There are no entities in your vicinity.", pyg.dark_gray)

    def entity_comfort(self, ent=None):
        """ Combo effect. """

        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            session.stats_obj.pet_moods['sadness'] -= 1
            if session.stats_obj.pet_moods['sadness'] <= 0: session.stats_obj.pet_moods['boredom'] += 1
            image = session.img.dict['bubbles'][' bubble']
            for ent in ent_list:
                session.img.flash_above(ent, image)
                self.spin(ent)

    def entity_clean(self, ent=None):
        """ Combo effect. """
        
        # Find pets in vicinity
        ent_list = []
        for tile in get_vicinity(session.player_obj.ent).values():
            if tile.entity:
                ent_list.append(tile.entity)
        
        # Activate effect if entities are found
        if ent_list:
            for ent in ent_list:
                self.find_water(ent)

    # Item interactions
    def skeleton(self, ent=None):
        
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

########################################################################################################################################################
# Environments
def place_player(ent, env, loc):
    """ Sets player in a new position.

        Parameters
        ----------
        env : Environment object; new environment of player
        loc : list of integers; new location of player in tile coordinates """
    
    pyg = session.pyg

    if not ent.dead:
        
        # Remove extra motions and animations
        pygame.event.clear()
        session.img.render_log = []
        
        # Remove from current location
        if ent.env:
            ent.env.player_coordinates = [ent.X//32, ent.Y//32]
            ent.env.entities.remove(ent)
            ent.tile.entity = None
            ent.tile        = None
            
            ent.last_env          = ent.env
            ent.env.area.last_env = ent.env

        # Set current environment and tile
        ent.env  = env
        ent.tile = ent.env.map[loc[0]][loc[1]]
        ent.X    = loc[0] * pyg.tile_width
        ent.X0   = loc[0] * pyg.tile_width
        ent.Y    = loc[1] * pyg.tile_height
        ent.Y0   = loc[1] * pyg.tile_height
        session.effects.toggle_effects(ent)

        # Set time and date
        if ent.env.name in ['home', 'overworld', 'cave']:
            if ent.last_env.name in ['home', 'overworld', 'cave']:
                ent.env.env_date = ent.last_env.env_date
                ent.env.env_time = ent.last_env.env_time

        # Notify environment of player position
        ent.env.entities.append(ent)
        ent.tile.entity = ent
        check_tile(loc[0], loc[1], ent=ent, startup=True)
        
        # Update camera
        if not env.camera.fixed:
            env.camera.update()
            ent.env.camera.zoom_in()
            ent.env.camera.zoom_out()
        
        # Render
        time.sleep(0.5)
        pyg.update_gui(ent=ent)
        
        # Change song
        if ent.env.name != ent.last_env.name:
            session.aud.control(soundtrack=env.soundtrack)
        
        # Update event bus
        session.bus.clear()
        pyg.subscribe_events()
        env.area.questlog.subscribe_events()
        if session.player_obj.dialogue:
            session.player_obj.dialogue.subscribe_events()

def get_vicinity(obj):
    """ Returns a list of tiles surrounding the given location.
    
        Returns
        -------
        obj.vicinity : dict of Tile objects
    """

    pyg = session.pyg

    (x, y) = obj.X//pyg.tile_width, obj.Y//pyg.tile_width
    obj.vicinity = {
        'top middle'    : session.player_obj.ent.env.map[x][y-1],
        'top right'     : session.player_obj.ent.env.map[x+1][y-1],
        'right'         : session.player_obj.ent.env.map[x+1][y],
        'bottom right'  : session.player_obj.ent.env.map[x+1][y+1],
        'bottom middle' : session.player_obj.ent.env.map[x][y+1],
        'bottom left'   : session.player_obj.ent.env.map[x-1][y+1],
        'middle left'   : session.player_obj.ent.env.map[x-1][y],
        'top left'      : session.player_obj.ent.env.map[x-1][y-1]}
    return obj.vicinity

def check_tile(x, y, ent=None, startup=False):
    """ Reveals newly explored regions with respect to the player's position. """
    
    # Select entity
    if not ent: ent = session.player_obj.ent

    # Define some shorthand
    tile = ent.env.map[x][y]
    
    # Reveal a square around the player
    for u in range(x-1, x+2):
        for v in range(y-1, y+2):
            ent.env.map[u][v].hidden = False
    
    # Reveal a hidden room
    if tile.room:
        
        if tile.room.hidden:
            tile.room.hidden = False
            for room_tile in tile.room.tiles_list:
                room_tile.hidden = False
        
        # Check if the player enters or leaves a room
        if ent.prev_tile:
            if (tile.room != ent.prev_tile.room) or (startup == True):
                
                # Hide the roof if the player enters a room
                if tile.room and tile.room.roof:
                    for spot in tile.room.tiles_list:
                        if spot not in tile.room.walls_list:
                            spot.img_names = tile.room.floor
    
    # Reveal the roof if the player leaves the room
    if ent.prev_tile:
        prev_tile = ent.prev_tile
        if prev_tile.room and not tile.room:
            if prev_tile.room.roof:
                for spot in prev_tile.room.tiles_list:
                    if spot not in prev_tile.room.walls_list:
                        spot.img_names = prev_tile.room.roof

def is_blocked(env, loc):
    """ Checks for barriers. """
    
    try:
        # Check for barriers
        if env.map[loc[0]][loc[1]].blocked:
            return True
        
        # Check for monsters
        if env.map[loc[0]][loc[1]].entity: 
            return True
        
        # Triggers message for hidden passages
        if env.map[loc[0]][loc[1]].unbreakable:
            #session.pyg.update_gui("A mysterious breeze seeps through the cracks.", session.pyg.dark_gray)
            pygame.event.clear()
            return True
    
    except: return False
    
    return False

########################################################################################################################################################
# Other
def active_effects():
    """ Applies effects from items and equipment. Runs constantly. """
    
    ent = session.player_obj.ent

    # Check for equipment
    if ent.equipment['dominant hand']:     hand_1 = session.player_obj.ent.equipment['dominant hand']
    else:                                  hand_1 = None
    if ent.equipment['non-dominant hand']: hand_2 = session.player_obj.ent.equipment['non-dominant hand']
    else:                                  hand_2 = None
    
    # Apply dominant hand function
    if hand_1:
        if hand_1.name == 'super shovel': ent.super_dig = True
        else:                             ent.super_dig = False
    
    # Apply non-dominant hand function
    if hand_2:
        if hand_2.effect.name == 'lamp':
            hand_2.effect.effect_fn(hand_2)

def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    
    pyg = session.pyg

    level_up_exp = session.effects.level_up_base + session.player_obj.ent.rank * session.effects.level_up_factor
    if session.player_obj.ent.exp >= level_up_exp:
        session.player_obj.ent.rank += 1
        session.player_obj.ent.exp -= level_up_exp
        
        notification = [
            "You feel stronger.",
            "Flow state!",
            "Resilience flows through you."]
        pyg.update_gui(random.choice(notification), pyg.gray)

        session.player_obj.ent.rank += 1
        session.player_obj.ent.max_hp += 20
        session.player_obj.ent.hp += 20
        session.player_obj.ent.attack += 1
        session.player_obj.ent.defense += 1
        pyg.update_gui()

def sort_inventory(ent=None):
    
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

########################################################################################################################################################