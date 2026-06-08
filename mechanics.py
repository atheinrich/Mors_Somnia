########################################################################################################################################################
# Local mechanics
# Contains core gameplay mechanisms, then routes special actions to other modules.
#
# MovementSystem usage (session.movement):
# - move: move entity, face new direction, activate effects, or interact with another entity
#
# General usage:
# - place_player: move player to a new location, remove from current location, and update map and time
# - get_vicinity: return a dict of tiles in the vicinity of an entity
# - is_blocked: return whether a tile is blocked for movement
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
                            self._key_UP()
                        elif event.key in pyg.key_DOWN:
                            self._key_DOWN()
                        elif event.key in pyg.key_LEFT:
                            self._key_LEFT()
                        elif event.key in pyg.key_RIGHT:
                            self._key_RIGHT()

                        #########################################################
                        # Enter combo sequence
                        elif event.key in pyg.key_HOLD:
                            self._key_HOLD()
                            return
            
                        #########################################################
                        # Zoom camera
                        elif event.key in pyg.key_PLUS:
                            self._key_PLUS()
                        elif event.key in pyg.key_MINUS:
                            self._key_MINUS()
                        
                        print((ent.X, ent.Y))

                elif event.type == pygame.KEYUP:

                    if not ent.dead:
                        
                        #########################################################
                        # Activate objects below
                        if event.key in pyg.key_ENTER:
                            self._key_ENTER()
                        elif event.key in pyg.key_PERIOD:
                            self._key_PERIOD()
                        
                        #########################################################
                        # Adjust speed
                        elif event.key in pyg.key_SPEED:
                            self._key_SPEED()

                        #########################################################
                        # Open side menu
                        elif event.key in pyg.key_INV:
                            self._key_INV()
                            return
                        elif event.key in pyg.key_DEV:
                            self._key_DEV()
                            return

                    #########################################################
                    # View stats
                    if event.key in pyg.key_INFO:
                        self._key_INFO()
                        return
                        
                    #########################################################
                    # Open questlog
                    elif event.key in pyg.key_QUEST:
                        self._key_QUEST()
                        return
                    
                    #########################################################
                    # Toggle GUI
                    elif event.key in pyg.key_GUI:
                        self._key_GUI()
                        
                    #########################################################
                    # Open main menu
                    elif event.key in pyg.key_BACK:
                        self._key_BACK()
                        return

                # Quit
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
            #########################################################
            # Handle player death
            if ent.dead:
                self._handle_death()

        #########################################################
        # Move AI controlled entities
        if not pyg.pause:
            for ent in ent.env.ents:
                session.movement.ai(ent)
        
        pyg.game_state = 'play_game'
        return

    def render(self):
        pyg = session.pyg

        pyg.msg_height = 4
        if not pyg.overlay_state: pyg.update_gui()

    # Navigation
    def _key_UP(self):
        session.movement.move(session.player_obj.ent, 0, -session.pyg.tile_height)

    def _key_DOWN(self):
        session.movement.move(session.player_obj.ent, 0, session.pyg.tile_height)

    def _key_LEFT(self):
        session.movement.move(session.player_obj.ent, -session.pyg.tile_width, 0)

    def _key_RIGHT(self):
        session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)

    # Action
    def _key_ENTER(self):
        pyg = session.pyg
        ent = session.player_obj.ent

        if time.time()-self.last_press_time > self.cooldown_time:
            self.last_press_time = time.time()
            pygame.event.clear()
            
            # Check if an item is under the player
            if ent.tile.item is not None:

                tile = ent.tile
                item = tile.item
                
                #########################################################
                # Effects (doors)
                if item.effect:
                    if (item.effect.trigger == 'on_use') and (not item.movable):
                        item.effect.activate()

                ## Chair
                if tile.item.item_id in ['red_chair_left', 'red_chair_right']:
                    ent.env.weather.set_day_and_time(increment=True)
                    pyg.update_gui("You sit down to rest for a while.", pyg.dark_gray)
                
                #########################################################
                # Items
                else:
                    session.items.pick_up(ent, item)

    def _key_PERIOD(self):
        
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

    def _key_SPEED(self):
        session.effects.movement_speed()

    def _key_BACK(self):
        pyg = session.pyg

        pyg.overlay_state = 'menu'
        pyg.hud_state     = 'off'

    # Menus
    def _key_HOLD(self):
        session.pyg.overlay_state = 'hold'

    def _key_INFO(self):
        session.pyg.overlay_state = 'stats'

    def _key_INV(self):
        session.pyg.overlay_state = 'inv'

    def _key_DEV(self):
        session.pyg.overlay_state = 'dev'

    def _key_QUEST(self):
        pyg = session.pyg

        pyg.overlay_state = 'questlog'
        pyg.hud_state     = 'off'

    # GUI
    def _key_GUI(self):
        
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

    def _key_PLUS(self):
        session.player_obj.ent.env.camera.zoom_in()

    def _key_MINUS(self):
        session.player_obj.ent.env.camera.zoom_out()

    # Tools
    def _handle_death(self):
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
            pyg.fn_queue.append([self._revive_player,  {}])
            pyg.fade_delay = 500
            pyg.fade_state = 'out'

            ent.dead = False

    def _revive_player(self):
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
        session.pets.update()
        
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
                            self._key_UP()
                        elif event.key in pyg.key_DOWN:
                            self._key_DOWN()
                        elif event.key in pyg.key_LEFT:
                            self._key_LEFT()
                        elif event.key in pyg.key_RIGHT:
                            self._key_RIGHT()

                        #########################################################
                        # Activate objects below
                        elif event.key in pyg.key_ENTER:
                            self._key_ENTER()
                        
                        #########################################################
                        # Enter combo sequence
                        elif event.key in pyg.key_HOLD:
                            self._key_HOLD()
                            return

                        print((ent.X, ent.Y))

                elif event.type == pygame.KEYUP:

                    if not ent.dead:
                        
                        #########################################################
                        # Open side menu
                        if event.key in pyg.key_INV:
                            self._key_INV()
                            return
                        elif event.key in pyg.key_DEV:
                            self._key_DEV()
                            return

                    #########################################################
                    # View stats
                    if event.key in pyg.key_INFO:
                        self._key_INFO()
                        return
                    
                    #########################################################
                    # Open questlog
                    elif event.key in pyg.key_QUEST:
                        self._key_QUEST()
                        return
                    
                    #########################################################
                    # Open main menu
                    elif event.key in pyg.key_BACK:
                        self._key_BACK()
                        return

                # Quit
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    pyg.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        #########################################################
        # Move AI controlled entities
        if not pyg.pause:

            for ent in ent.env.ents:
                session.movement.ai(ent)

            session.movement.ai(session.player_obj.ent)
        
        pyg.game_state = 'play_garden'
        return

    def render(self):
        pass

    # Navigation
    def _key_UP(self):
        session.movement.move(session.player_obj.ent, 0, -session.pyg.tile_height)

    def _key_DOWN(self):
        session.movement.move(session.player_obj.ent, 0, session.pyg.tile_height)

    def _key_LEFT(self):
        session.movement.move(session.player_obj.ent, -session.pyg.tile_width, 0)

    def _key_RIGHT(self):
        session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)

    # Action
    def _key_ENTER(self):
        ent = session.player_obj.ent

        if ent.tile.item:
            session.items.pick_up(ent, ent.tile.item)

    def _key_BACK(self):
        pyg = session.pyg

        pyg.overlay_state = 'menu'
        pyg.hud_state     = 'off'

    # Menus
    def _key_HOLD(self):
        session.pyg.overlay_state = 'hold'

    def _key_INFO(self):
        session.pyg.overlay_state = 'stats'

    def _key_INV(self):
        session.pyg.overlay_state = 'inv'

    def _key_DEV(self):
        session.pyg.overlay_state = 'dev'

    def _key_QUEST(self):
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
        map = ent.env.map

        # Orientation
        if   dY > 0: ent.direction = 'front'
        elif dY < 0: ent.direction = 'back'
        elif dX < 0: ent.direction = 'left'
        elif dX > 0: ent.direction = 'right'
        
        # New position in tile units
        x = int((ent.X + dX)/pyg.tile_width)
        y = int((ent.Y + dY)/pyg.tile_height)

        self._effect_on_move(ent, x, y, dX, dY)

        # Move forward
        if self._movement_allowed(ent, x, y):
            
            # Player-specific
            if ent.name == 'player':
                ent.env.player_coordinates = [x, y]
                check_tile(x, y)

                # Check stamina
                if (session.effects.movement_speed_toggle == 1) and (ent.stamina > 0):
                    ent.stamina -= 0.5
                    pyg.update_gui()

            # Move entity and update map
            ent.X         += dX
            ent.Y         += dY
            ent.prev_tile = map[int(ent.X/pyg.tile_width)][int(ent.Y/pyg.tile_height)]
            ent.tile.ent  = None
            ent.tile      = map[x][y]
            ent.tile.ent  = ent

            session.bus.emit(
                event_id = 'tile_occupied',
                ent_id   = ent.ent_id,
                tile_id  = ent.tile.img_IDs[1])
            
        # Interact with an entity
        elif map[x][y].ent:
            session.interact.interact_with_target(ent, map[x][y].ent)

        ent.env.camera.update()

    def _effect_on_move(self, ent, x, y, dX, dY):
        if ent.active_effects:
            for effect in ent.active_effects.values():
                if effect.trigger == 'on_move':
                    effect.activate(x=x, y=y, dX=dX, dY=dY)
                    break

    def _movement_allowed(self, ent, x, y):
        map = ent.env.map
        success = True

        ## Change orientation before moving
        if ent.img_IDs[1] != ent.direction:
            ent.img_IDs[1] = ent.direction
            success = False

        ## Check for the edge of the map
        elif (x==0) or (x==len(map)-1) or (y==0) or (y==len(map[0])-1):
            success = False
        
        # Verify the tile is available
        elif is_blocked(map[x][y]):
            success = False
        
        # Check if the entity has biome restrictions
        elif map[x][y].biome not in session.img.biomes[ent.habitat]:
            success = False

        # Prevent non-player entities from standing in entryways
        elif (ent.ent_id != 'player') and (map[x][y].item):
            if map[x][y].item.img_IDs[0] in session.img.other['stairs']:
                success = False
        
        return success

    def ai(self, ent):
        """ Preset movements. """
        
        #########################################################
        # Move if alive
        moved = False
        if not ent.dead:
            if time.time() - ent.last_press > ent.cooldown:
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
                            self._idle(ent)
                
                #########################################################
                # Continue a prescribed pattern
                else:
                    loc = ent.motions_log[0]
                    self.move(ent, loc[0], loc[1])
                    ent.motions_log.remove(loc)

    # Preset sequence
    def _idle(self, ent):
        """ Randomly walk around. """
        
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

            # High chance to move in the faced direction
            if   (dX < 0) and (ent.img_IDs[1] == 'left'):  chance = 5
            elif (dX > 0) and (ent.img_IDs[1] == 'right'): chance = 5
            elif (dY < 0) and (ent.img_IDs[1] == 'back'):  chance = 5
            elif (dY > 0) and (ent.img_IDs[1] == 'front'): chance = 5

            # Low chance to face a new direction
            else:                                          chance = 1

            # Move, chance weighed by lethargy
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
        nearby_tiles = [tile.img_IDs[1] for tile in get_vicinity(ent).values()]
        if ('water' not in nearby_tiles) and ('water' not in ent.tile.img_IDs[1]):
            
            # Prepare movements
            motions_log = []
            
            # Look for water
            distance_list = []
            for y in range(len(ent.env.map[0])):
                for x in range(len(ent.env.map)):
                    if ent.env.map[x][y].img_IDs[1] == 'water':
                        
                        # Find distance
                        dX_total = int(x*32) - ent.X
                        dY_total = int(y*32) - ent.Y

                        distance_list.append([dX_total, dY_total])
            
            # Move to the nearest location
            if distance_list:
                dX_total, dY_total = min(distance_list, key=lambda p: p[0]**2 + p[1]**2)
                motions_log = self.build_path(dX_total, dY_total)
                                        
            # Send directions to entity
            ent.motions_log = motions_log
            image = session.img.dict['bubbles']['question_bubble']

        # Bathe
        else:

            session.bus.emit(
                event_id = 'tile_occupied',
                ent_id   = ent.ent_id,
                tile_id  = 'water')
        
            env = session.player_obj.envs.areas['underworld']['garden']

            session.stats_obj.pet_moods['anger'] -= 1
            image = session.img.dict['bubbles']['water_bubble']
            
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
                                
                                dX = int(x*32) - ent.X
                                dY = int(y*32) - ent.Y

                                motions_log = self.build_path(dX, dY)
            
            # Send directions to entity
            ent.motions_log = motions_log
            image = session.img.dict['bubbles']['question_bubble']

        # Sleep
        else:
            image = session.img.dict['bubbles']['dots_bubble']
            
        session.img.flash_above(ent, image)

    def spin(self, ent):
        
        pyg = session.pyg

        # Prepare movements
        motions_log = []
        
        # Look forward first
        if ent.img_IDs[0] != 'front':
            motions_log.append([0, pyg.tile_height])
        motions_log.append([-pyg.tile_width, 0])
        
        # Spin around
        motions_log.append([0, -pyg.tile_height])
        motions_log.append([pyg.tile_width, 0])
        motions_log.append([0, pyg.tile_height])
        
        # Send directions to entity
        ent.motions_log = motions_log

    def build_path(self, dX_total, dY_total):
        step = session.pyg.tile_width
        motions_log = []

        # Find total number of steps in each direction
        if dX_total: sign_dX = int(dX_total / abs(dX_total))
        else:        sign_dX = 0

        if dY_total: sign_dY = int(dY_total / abs(dY_total))
        else:        sign_dY = 0

        # Make one step in each direction until destination is reached
        while dX_total or dY_total:

            # Only horizontal movement left
            if dX_total and not dY_total:
                dX = step * sign_dX
                dY = 0

            # Only vertical movement left
            elif dY_total and not dX_total:
                dX = 0
                dY = step * sign_dY

            # Both directions available
            else:
                if random.randint(0, 1):
                    dX = step * sign_dX
                    dY = 0
                else:
                    dX = 0
                    dY = step * sign_dY

            motions_log.append([dX, dY])

            dX_total -= dX
            dY_total -= dY

        return motions_log

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

    def interact_with_target(self, ent, target):
        """ Routes the interaction to the proper channel based on entities and location.
        
            Trade menu: player -> NPC with active trade
            Dialogue: player -> NPC with dialogue
            Attack: player -> aggressive target or any entity
            Flee: player -> fearful target
        """

        # Player specific
        if ent.role == 'player':

            if target.role == 'NPC':

                # Trading
                if target.trade_active() and not target.quest_active():
                    session.trade_obj.columns[1].ent = target
                    session.pyg.overlay_state = 'trade'
            
                # Dialogue
                current_time = time.time()
                if current_time - target.last_dialogue_time > 1:
                    target.last_dialogue_time = current_time
                    session.dialogue.emit_dialogue(target.ent_id)

                    # Emit event
                    states      = session.player_obj.dialogue_states
                    dialogue_id = states.get(target.ent_id)['dialogue_id']
                    session.bus.emit(
                        event_id      = 'entity_dialogue',
                        ent_id        = ent.ent_id,
                        target_ent_id = target.ent_id,
                        dialogue_id   = dialogue_id)

            # Attack
            elif target.aggression:
                self.attack_target(ent, target)
            
            # Make them flee
            elif type(target.fear) == int:
                target.fear += 30
            
        # General
        elif session.pyg.game_state != 'play_garden':

            if ent.role == 'NPC':
                if target.role != 'player':
                    self.attack_target(ent, target)            
            else:
                self.attack_target(ent, target)        
    
    def attack_target(self, ent, target):
        """ Calculates and applies attack damage. Used for player and entities.
        
            Parameters
            ----------
            ent    : entity instance; the one attacking
            target : entity instance; the one being attacked
        """
        
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
                            self.take_damage(ent, target, damage)
                    
                    else:
                        msg = ent.name.capitalize() + " strikes " + target.name + " for " + str(damage) + " hit points."
                        self.take_damage(ent, target, damage)
                
                # Do nothing
                else:
                    msg = ent.name.capitalize() + " strikes " + target.name + " but it has no effect!"
        
        # Update gui
        if msg and (ent.role == 'player') or (target.role == 'player'):
            pyg.update_gui(msg, pyg.red)

    def take_damage(self, ent, target, damage):
        """ Applies damage if possible. """
    
        # Apply damage
        target.hp -= damage
        
        # Damage animation
        session.img.flash_over(target)
        
        # Check for death
        if target.hp <= 0:
            target.hp = 0
            session.interact.ent_death(target)
            
            # Gain experience
            if ent.role == 'player':
                session.player_obj.ent.exp += ent.exp
                check_level_up()
            else:
                session.pyg.update_gui()

    def ent_death(self, ent):
        
        pyg = session.pyg

        #########################################################
        # Imports
        from environments import place_object
        from items import create_item

        session.bus.emit(
            event_id = 'entity_death',
            ent_id   = ent.ent_id)
        
        #########################################################
        # Player death
        if ent.role == 'player':
            pyg.update_gui("You died!", pyg.red)
            session.player_obj.ent.dead        = True
            session.player_obj.ent.tile.ent = None
            session.player_obj.ent.img_IDs   = session.player_obj.ent.img_names_backup
            
            item = create_item('skeleton')
            item.name = f"the corpse of {ent.name}"
            place_object(item, [ent.X//pyg.tile_width, ent.Y//pyg.tile_height], ent.env)
            pygame.event.clear()
        
        #########################################################
        # Entity or projectile death
        else:
            ent.dead     = True
            ent.tile.ent = None
            ent.env.ents.remove(ent)
            if ent in session.player_obj.ent.env.ents: session.player_obj.ent.env.ents.remove(ent)

            if ent.role != 'projectile':
                pyg.update_gui(ent.name.upper() + " is dead! You gain " + str(ent.exp) + " experience points.", pyg.red)
                
                if not ent.tile.item:
                    item = create_item('bones')
                    item.name = f"the corpse of {ent.name}"
                    place_object(item, [ent.X//pyg.tile_width, ent.Y//pyg.tile_height], ent.env)
                    ent.role = 'corpse'

            del ent

            pygame.event.get()
        pygame.event.clear()

class PetsSystem:
    """ Manager pet mood for stats menu. """

    def __init__(self):

        # Passed to stat menu
        self.mood = None

        # Time to lose happiness and gain something else
        self.happiness_cooldown = 10
        self.happiness_press    = 0
        
        # Time between mood switches if tied
        self.emoji_cooldown     = 10
        self.emoji_press        = 0

    def update(self):
        """ Decreases happiness over time, sets mood to current highest stat, handles mood effects, and updates stat display. """
        
        pet_moods = session.stats_obj.pet_moods

        #######################################################
        # Change stats
        if pet_moods['happiness']:
            if time.time() - self.happiness_press > self.happiness_cooldown:
                self.happiness_press = time.time()
                
                # Random chance to lose happiness and gain something else
                if not random.randint(0, 2):
                    pet_moods['happiness'] -= 1
                    pet_moods[random.choice(list(pet_moods.keys()))] += 1
        
                # Keep stats to [0, 9]
                self._stat_limiter(pet_moods)
        
        #######################################################
        # Set mood
        max_val       = max(pet_moods.values())
        current_moods = [mood for mood, val in pet_moods.items() if val == max_val]
        
        ## Alternate between tied moods
        if len(current_moods) > 1:
            if time.time() - self.emoji_press > self.emoji_cooldown:
                self.emoji_press = time.time()

                # Random chance to switch mood
                self.mood = random.choice(current_moods)
        
        else:
            self.mood = current_moods[0]
        
        #######################################################
        # Change color
        ent = session.player_obj.ent
        happiness = pet_moods['happiness']

        if happiness >= 6:   target_img = 'orange_radish'
        elif happiness >= 3: target_img = 'red_radish'
        else:                target_img = 'purple_radish'

        if ent.env.ents[-1].img_IDs[0] == target_img:
            return

        for pet in ent.env.ents:
            if pet is not ent:
                pet.img_IDs[0] = target_img

    def _stat_limiter(self, dic):
        for key, value in dic.items():
            if value > 9:   dic[key] = 9
            elif value < 0: dic[key] = 0

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
            ent.env.ents.remove(ent)
            ent.tile.ent = None
            ent.tile     = None
            
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
        if ent.env.area == ent.last_env.area:
            ent.env.env_date = ent.last_env.env_date
            ent.env.env_time = ent.last_env.env_time

        # Notify environment of player position
        ent.env.ents.append(ent)
        ent.tile.ent = ent
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

def get_vicinity(obj):
    """ Returns a list of tiles surrounding the given location.
    
        Returns
        -------
        obj.vicinity : dict of tile objects
    """

    pyg = session.pyg
    map = session.player_obj.ent.env.map

    (x, y) = obj.X//pyg.tile_width, obj.Y//pyg.tile_width
    
    obj.vicinity = {
        'top middle'    : (x,   y-1),
        'top right'     : (x+1, y-1),
        'right'         : (x+1, y),
        'bottom right'  : (x+1, y+1),
        'bottom middle' : (x,   y+1),
        'bottom left'   : (x-1, y+1),
        'middle left'   : (x-1, y),
        'top left'      : (x-1, y-1)}
    
    for key, val in obj.vicinity.items():
        x, y = val[0], val[1]
        if (x >= 0) and (x < len(map)) and (y >= 0) and (y < len(map[0])):
            obj.vicinity[key] = map[x][y]
        else:
            obj.vicinity[key] = None
    
    return obj.vicinity

def check_tile(x, y, ent=None, startup=False):
    """ Reveals newly explored regions with respect to the player's position and reveals/hides roof. """
    
    # Select entity
    if not ent: ent = session.player_obj.ent

    # Define some shorthand
    tile = ent.env.map[x][y]
    
    # Reveal a square around the player
    for u in range(x-1, x+2):
        for v in range(y-1, y+2):
            if (u < len(ent.env.map)) and (v < len(ent.env.map[0])):
                ent.env.map[u][v].hidden = False
    
    # Reveal room and hide roof
    if tile.room:
        
        # Reveal room
        if tile.room.hidden:
            tile.room.hidden = False
            for loc in tile.room.tile_locs:
                room_tile = ent.env.map[loc[0]][loc[1]]
                room_tile.hidden = False
        
        # Check if the player enters or leaves a room
        if ent.prev_tile:
            if (tile.room != ent.prev_tile.room) or (startup == True):
                
                # Hide the roof if the player enters a room
                if tile.room and tile.room.roof_img_IDs:
                    for loc in tile.room.floor_locs:
                        room_tile = ent.env.map[loc[0]][loc[1]]
                        room_tile.img_IDs = tile.room.floor_img_IDs
    
    # Reveal roof if the player leaves the room
    if ent.prev_tile:
        prev_tile = ent.prev_tile
        if prev_tile.room and not tile.room:
            if prev_tile.room.roof_img_IDs:
                for loc in prev_tile.room.floor_locs:
                    room_tile = ent.env.map[loc[0]][loc[1]]
                    room_tile.img_IDs = prev_tile.room.roof_img_IDs

def is_blocked(tile):
    """ Checks for barriers. """
    
    # Check for barriers
    if tile.blocked:
        return True
    
    # Check for monsters
    if tile.ent: 
        return True
    
    return False

########################################################################################################################################################
# Other
def check_level_up():
    """ Checks if the player's experience is enough to level-up. """
    
    print('The player gained experience, but this has not been implemented.')

########################################################################################################################################################