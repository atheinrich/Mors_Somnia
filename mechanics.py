########################################################################################################################################################
# Local mechanics
# Contains core gameplay mechanisms, then routes special actions to other modules.
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
        ent = session.player_obj.ent

        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            # Check if an item is under the player
            if ent.tile.item:
                tile = ent.tile
                
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
                            if ent.env.env_time in [1, 2, 7, 8]:
                                ent.env.env_time = (ent.env.env_time + 3) % 8
                                session.effects.enter_dungeon(text="The evening dims to night... sleep trustly follows.")
                            else: pyg.update_gui("Time to face the day.", pyg.dark_gray)
                        
                        # No sleeping in owned beds
                        else: pyg.update_gui("This is not your bed.", pyg.dark_gray)
                    
                    else: pyg.update_gui("This is not your bed.", pyg.dark_gray)
                
                ## Chair
                elif tile.item.name in ['red chair left', 'red chair right']:
                    ent.env.weather.set_day_and_time(increment=True)
                    pyg.update_gui("You sit down to rest for a while.", pyg.dark_gray)
                
                #########################################################
                # Items
                else: session.items.pick_up(ent, ent.tile.item)

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
        ent = session.player_obj.ent

        if ent.tile.item:
            session.items.pick_up(ent, ent.tile.item)

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

    # Core
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
            
            elif 'dig_tunnel' in ent.active_effects.keys():
                ent.active_effects['dig_tunnel'].activate(x=x, y=y, dX=dX, dY=dY)
                session.effects.check_tile(ent)

        ent.env.camera.update() # omit this if you want to modulate when the camera focuses on the player

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

    # Preset sequence
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

    # Utility
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
                if target.trade_active() and not target.quest_active():
                    session.trade_obj.ent     = target
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
    
    def attack_target(self, ent, target):
        """ Calculates and applies attack damage. Used for player and entities. """
        
        pyg = session.pyg
        msg = None

        # Only attack living targets
        if not target.dead:
            
            # No attacking yourself
            if ent.name != target.name:
                
                # Default damage calculation
                damage = ent.attack - target.defense
                
                # Deal damage
                if damage > 0:
                    
                    # Apply an ability for non-player entities
                    if (ent.role != 'player') and ent.active_abilities:
                        
                        # Use ability
                        if not random.randint(0, 1):
                            random.choice(list(ent.active_abilities.values())).activate()
                            
                        # Regular attack
                        else:
                            msg = ent.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points."
                            self.take_damage(target, damage)
                    
                    # Regular attack
                    else:
                        msg = ent.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points."
                        self.take_damage(target, damage)
                else:
                    msg = ent.name.capitalize() + " strikes " + target.name + " but it has no effect!"
        
        # Update gui
        if msg and (ent.role == 'player') or (target.role == 'player'):
            pyg.update_gui(msg, pyg.red)

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
        from environments import place_object

        #########################################################
        # Player death
        if ent.role == 'player':
            pyg.update_gui("You died!", pyg.red)
            session.player_obj.ent.dead        = True
            session.player_obj.ent.tile.entity = None
            session.player_obj.ent.img_names   = session.player_obj.ent.img_names_backup
            
            item = session.items.create_item('skeleton')
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
                    item = session.items.create_item('bones')
                    item.name = f"the corpse of {ent.name}"
                    place_object(item, [ent.X//pyg.tile_width, ent.Y//pyg.tile_height], ent.env)
                    ent.role = 'corpse'

            del ent

            pygame.event.get()
        pygame.event.clear()

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
        session.abilities.toggle_abilities(ent)

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
        pyg._subscribe_events()
        env.area.questlog._subscribe_events()
        if session.player_obj.dialogue:
            session.player_obj.dialogue._subscribe_events()

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
    """ Applies effects from items and equipment. Runs constantly. 
    
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
            hand_2.effect.effect_fn(hand_2) """
    pass

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

########################################################################################################################################################