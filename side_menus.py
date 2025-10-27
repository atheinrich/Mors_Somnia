########################################################################################################################################################
# Local mechanics
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import time

## Specific
import pygame
from   pygame.locals import *

## Local
import session

########################################################################################################################################################
# Classes
class InventoryMenu:
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """
        
        pyg = session.pyg

        #########################################################
        # Parameters
        ## Positions
        self.cursor_pos  = [0, 32]
        self.img_x       = 0
        self.img_y       = 0

        ## Other
        self.dic_index   = 0
        self.dic_indices = [[0, 0]]
        self.img_names   = ['null', 'null']
        self.locked      = False
        self.detail      = True

        self.category_index = 0 # which category is active
        self.item_index     = 0# which item (in that category) is active

        self.categories = []
        self.items      = []
        self.offset     = 0
        self.choice     = 0

        #########################################################
        # Surface initialization
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

        #########################################################
        # Create cursor
        self.cursor = pygame.Surface((32, 32), pygame.SRCALPHA)
        cursor_data = {
            'size':  31,
            'width': 1,
            'alpha': 128}
        
        self.locked_cursor = pygame.Surface((32, 32), pygame.SRCALPHA)
        locked_cursor_data = {
            'size':  30,
            'width': 2,
            'alpha': 192}
        
        for (cursor, data) in [(self.cursor, cursor_data), (self.locked_cursor, locked_cursor_data)]:

            cursor.fill((255, 255, 255, data['alpha']))
            pygame.draw.polygon(
                self.cursor, 
                pygame.Color('white'), 
                [
                    (0, 0),
                    (data['size'], 0),
                    (data['size'], data['size']),
                    (0, data['size'])
                ],  
                data['width'])

    def run(self):
        
        #########################################################
        # Initialize
        ## Update dictionaries and create cursors
        self.update_data()

        ## Set navigation speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Define shorthand
        pyg = session.pyg

        ## Wait for input
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                #########################################################
                # Move cursor
                if event.key in pyg.key_UP:
                    self.key_UP()
                elif event.key in pyg.key_DOWN:
                    self.key_DOWN()
                
                #########################################################
                # Switch section
                elif event.key in pyg.key_LEFT:
                    self.key_LEFT()
                elif event.key in pyg.key_RIGHT:
                    self.key_RIGHT()
                
                #########################################################
                # Activate or drop item
                elif event.key in pyg.key_ENTER:
                    self.key_ENTER()
                elif event.key in pyg.key_PERIOD:
                    self.key_PERIOD()
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_QUEST:
                    self.key_QUEST()
                
                #########################################################
                # Toggle selection lock
                elif event.key in pyg.key_INV:
                    self.key_INV()
                
                #########################################################
                # Open catalog
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                    return
                
                #########################################################
                # Return to game
                else:
                    self.key_BACK()
                    return

            # Save for later reference
            index = self.dic_index%len(self.dic_indices)
            self.dic_indices[index][0] = self.offset
            self.dic_indices[index][1] = self.choice
        
        pyg.overlay_state = 'inv'
        return

    def render(self):

        #########################################################
        # Adjust GUI
        pyg = session.pyg
        pyg.msg_height = 1
        pyg.update_gui()

        #########################################################
        # Renders
        ## Background
        if not self.locked: pyg.overlay_queue.append([self.background_fade, (0, 0)])
        
        ## Cursor
        #if self.cursor_pos[1] < 32: self.cursor_pos[1] = 32

        ## Color
        session.img.average()
        color = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
        
        ## Items
        for i in range(self.offset, min(len(self.items), self.offset + 12)):
            item = self.items[i]
            Y = 32 + (i - self.offset) * 32
            
            # Render details
            if self.detail:
                Y_detail = int(Y)
                
                if item:
                    if item.equipped: detail = '(equipped)'
                    else:             detail = ''
                else:                 detail = ''
                
                self.menu_choices = [item.name, detail]
                self.menu_choices_surfaces = []
                for i in range(len(self.menu_choices)):
                    self.menu_choices_surfaces.append(
                        pyg.minifont.render(self.menu_choices[i], True, color))
                
                for menu_choice_surface in self.menu_choices_surfaces:
                    pyg.overlay_queue.append([menu_choice_surface, (40, Y_detail)])
                    Y_detail += 12
            
            # Render image
            img = session.img.dict[item.img_names[0]][item.img_names[1]]
            pyg.overlay_queue.append([img, (0, Y)])
        
        if self.locked: pyg.overlay_queue.append([self.locked_cursor, self.cursor_pos])
        else:           pyg.overlay_queue.append([self.cursor,        self.cursor_pos])

    # Keys
    def key_UP(self):

        pyg = session.pyg

        if not self.locked:
            self.item_index = (self.item_index - 1) % len(self.items)
            self.update_cursor()

        else:
            session.player_obj.ent.move(0, -pyg.tile_height)

    def key_DOWN(self):

        pyg = session.pyg

        if not self.locked:
            self.item_index = (self.item_index + 1) % len(self.items)
            self.update_cursor()

        else:
            session.player_obj.ent.move(0, pyg.tile_height)

    def key_LEFT(self):
        if len(self.categories) > 1:
            
            if not self.locked and self.categories:
                self.category_index = (self.category_index - 1) % len(self.categories)
                self.item_index = 0
                self.rebuild_inventory_snapshot()

            else:
                session.player_obj.ent.move(-session.pyg.tile_height, 0)

    def key_RIGHT(self):
        if len(self.categories) > 1:
            
            if not self.locked and self.categories:
                self.category_index = (self.category_index + 1) % len(self.categories)
                self.item_index = 0
                self.rebuild_inventory_snapshot()
            
            else:
                session.player_obj.ent.move(session.pyg.tile_width, 0)

    def key_BACK(self):
        pyg = session.pyg

        pyg.last_press_time = float(time.time())
        pyg.overlay_state   = None

    def key_QUEST(self):
        if not self.detail: self.detail = True
        else:               self.detail = False

    def key_INV(self):
        self.last_press_time = float(time.time())
        self.cursor_border = pygame.Surface((32, 32)).convert()
        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))

        # Thin cursor
        if not self.locked:
            self.locked   = True
            cursor_points = [(0, 0), (30, 0), (30, 30), (0, 30)]
            cursor_width  = 2
        
        # Thick cursor
        else:
            self.locked   = False
            cursor_points = [(0, 0), (31, 0), (31, 31), (0, 31)]
            cursor_width  = 1
        
        pygame.draw.polygon(self.cursor_border, session.pyg.white, cursor_points, cursor_width)

    def key_DEV(self):
        session.pyg.overlay_state = 'dev'
        pygame.event.clear()

    def key_ENTER(self):
        self.find_item().use()
        self.update_data()

    def key_PERIOD(self):
        self.find_item().drop()
        self.update_data()

    # Tools
    def update_data(self):
        self.inventory_dics = self.rebuild_inventory_snapshot()

        self.categories = list(self.inventory_dics.keys())

        if not self.categories:
            session.pyg.overlay_state = None
            return

        self.category_index %= len(self.categories)

        # 4. Update current item list
        self.items = self.inventory_dics[self.categories[self.category_index]]

        if self.items:
            self.item_index %= len(self.items)
        else:
            self.item_index = 0

        # 5. Derive offset/cursor (no manual tweaking here)
        self.update_cursor()

    def rebuild_inventory_snapshot(self):
        """Rebuilds a cleaned dictionary of visible inventory items, grouped by category."""

        inv = session.player_obj.ent.inventory

        inventory_dics = {}

        for category, items in inv.items():
            visible_items = [item for item in items if not item.hidden]
            if visible_items:
                inventory_dics[category] = visible_items

        return inventory_dics

    def update_cursor(self):
        max_visible = 12

        if len(self.items) <= max_visible:
            self.offset = 0
        
        else:
            # Keep the selected item visible
            if self.item_index < self.offset:
                self.offset = self.item_index
            elif self.item_index >= self.offset + max_visible:
                self.offset = self.item_index - max_visible + 1

        # Cursor Y position is derived — not tracked separately
        self.cursor_pos[1] = 32 + (self.item_index - self.offset) * 32
    
    def find_item(self):
        """
        Return the currently selected item in the active category,
        or the item at a relative offset (with cycling wrap-around).
        """
        if not self.categories:
            return None

        # Active category and item list
        category = self.categories[self.category_index]
        items = self.inventory_dics.get(category, [])

        if not items:
            return None

        # Compute wrapped index
        index = (self.item_index + self.item_index - self.offset) % len(items)
        return items[index]

class CatalogMenu:
    
    # Core
    def __init__(self):
        """ Manages catalog menu on the side of the screen. Allows item placemennt. """
        
        pyg = session.pyg

        #########################################################
        # Parameters
        ## Positions
        self.cursor_pos = [pyg.screen_width-pyg.tile_width, 32]
        self.img_x      = 0
        self.img_y      = 0

        ## Other
        self.img_names = ['null', 'null']
        self.locked    = False

        #########################################################
        # Surface initialization
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def run(self):  
        
        #########################################################
        # Initialize
        ## Update dictionaries and create cursors
        self.update_data()
        
        ## Set navigation speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Define shorthand
        pyg = session.pyg

        ## Wait for input
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                #########################################################
                # Move cursor
                if event.key in pyg.key_UP:
                    self.key_UP()
                elif event.key in pyg.key_DOWN:
                    self.key_DOWN()
                
                #########################################################
                # Switch section
                elif event.key in pyg.key_LEFT:
                    self.key_LEFT()
                elif event.key in pyg.key_RIGHT:
                    self.key_RIGHT()
                
                #########################################################
                # Activate item
                elif event.key in pyg.key_ENTER:
                    self.key_ENTER()
                
                #########################################################
                # Toggle selection lock
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                
                #########################################################
                # Open inventory
                elif event.key in pyg.key_INV:
                    self.key_INV()
                    return

                #########################################################
                # Return to game
                else:
                    self.key_BACK()
                    return

            # Save for later reference
            index = self.dic_index%len(self.dic_indices)
            self.dic_indices[index][0] = self.offset
            self.dic_indices[index][1] = self.choice
        
        pyg.overlay_state = 'dev'
        return

    def render(self):
        pyg = session.pyg

        if not self.locked: pyg.overlay_queue.append([self.background_fade, (0, 0)])
        
        pyg.msg_height = 1
        pyg.update_gui()
        
        pyg.overlay_queue.append([self.cursor_fill, self.cursor_pos])
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                img_names = self.dic[list(self.dic.keys())[(i+self.offset)%len(self.dic)]]
                pyg.overlay_queue.append([session.img.dict[img_names[0]][img_names[1]], (pyg.screen_width-pyg.tile_width, Y)])
                Y += pyg.tile_height
                counter += 1
            else: break
        pyg.overlay_queue.append([self.cursor_border, self.cursor_pos])

    # Keys
    def key_UP(self):
        pyg = session.pyg

        if not self.locked:
            self.choice -= 1
            if self.cursor_pos[1] == 32: self.offset -= 1
            else: self.cursor_pos[1] -= pyg.tile_height
        
        else:
            session.player_obj.ent.move(0, -pyg.tile_height)
                
    def key_DOWN(self):
        pyg = session.pyg

        if not self.locked:
            self.choice += 1
            if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
            else: self.cursor_pos[1] += pyg.tile_height
            
        else:
            session.player_obj.ent.move(0, pyg.tile_height)

    def key_LEFT(self):

        if not self.locked:
            self.dic_index -= 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
            while not len(self.dic):
                self.dic_index -= 1
                self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        
        else:
            session.player_obj.ent.move(-session.pyg.tile_height, 0)

        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
        self.choice = self.cursor_pos[1]//32 + self.offset - 1
    
        # Move cursor to the highest spot in the dictionary
        if self.cursor_pos[1] > 32*len(self.dic):
            self.cursor_pos[1] = 32*len(self.dic)
            self.choice = len(self.dic) - self.offset - 1

    def key_RIGHT(self):

        if not self.locked:
            self.dic_index += 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
            while not len(self.dic):
                self.dic_index += 1
                self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        
        else:
            session.player_obj.ent.move(session.pyg.tile_width, 0)
        
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
        self.choice = self.cursor_pos[1]//32 + self.offset - 1
    
        # Move cursor to the highest spot in the dictionary
        if self.cursor_pos[1] > 32*len(self.dic):
            self.cursor_pos[1] = 32*len(self.dic)
            self.choice = len(self.dic) - self.offset - 1

    def key_ENTER(self):
        
        pyg = session.pyg

        from mechanics import place_object
        from items_entities import create_item, create_entity

        # Note location and image names
        self.img_x, self.img_y = int(session.player_obj.ent.X/pyg.tile_width), int(session.player_obj.ent.Y/pyg.tile_height)
        self.img_names[0] = self.dic_categories[self.dic_index%len(self.dic_categories)]
        self.img_names[1] = list(self.dic.keys())[(self.choice)%len(self.dic)]
        
        # Set location for drop
        if session.player_obj.ent.direction == 'front':   self.img_y += 1
        elif session.player_obj.ent.direction == 'back':  self.img_y -= 1
        elif session.player_obj.ent.direction == 'right': self.img_x += 1
        elif session.player_obj.ent.direction == 'left':  self.img_x -= 1
        
        # Place tile
        if self.img_names[0] in ['floors', 'walls', 'roofs']:
            obj = session.player_obj.ent.env.map[self.img_x][self.img_y]
            obj.placed = True
            place_object(
                obj = obj,
                loc = [self.img_x, self.img_y],
                env = session.player_obj.ent.env,
                names = self.img_names.copy())

            # Check if it completes a room
            if self.img_names[0] == 'walls':
                session.player_obj.ent.env.build_room(obj)
        
        # Place entity
        elif self.img_names[0] in session.img.ent_data.keys():
            item = create_entity(
                names = self.img_names.copy())
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_names.copy())
        
        # Place item
        elif self.img_names[1] not in session.img.ent_data.keys():
            item = create_item(
                names = self.img_names)
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_names.copy())
            if item.img_names[0] == 'stairs':
                item.tile.blocked = False
        
        else:
            ent = create_entity(
                names = self.img_names[1])
            place_object(
                obj   = ent,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_names.copy())
        
        self.img_x, self.img_y = None, None
        pyg.overlay_state = None

    def key_DEV(self):
        self.last_press_time = float(time.time())
        self.cursor_border = pygame.Surface((32, 32)).convert()
        self.cursor_border.set_colorkey(self.cursor_border.get_at((0,0)))

        # Thin cursor
        if not self.locked:
            self.locked   = True
            cursor_points = [(0, 0), (30, 0), (30, 30), (0, 30)]
            cursor_width  = 2
        
        # Thick cursor
        else:
            self.locked   = False
            cursor_points = [(0, 0), (31, 0), (31, 31), (0, 31)]
            cursor_width  = 1
        
        pygame.draw.polygon(self.cursor_border, session.pyg.white, cursor_points, cursor_width)

    def key_INV(self):
        session.pyg.overlay_state = 'inv'
        pygame.event.clear()

    def key_BACK(self):
        pyg = session.pyg

        pyg.last_press_time = float(time.time())
        pyg.overlay_state         = None

    # Tools
    def update_data(self):

        # Update cursor
        if bool(self.locked): size, width, alpha = 30, 2, 192
        else:                 size, width, alpha = 31, 1, 128
        self.cursor_border = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)

        # Initialize tile selection
        self.dic    = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]
        
    def update_dict(self):
        
        # Dictionary management
        self.dic_categories = list(session.player_obj.ent.discoveries.keys())
        self.dic_index = 0
        self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]] # {first name: {second name: surface}}
        while not len(self.dic):
            self.dic_index += 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        self.dic_indices = [[0, 0] for _ in self.dic_categories]

class AbilitiesMenu:
    
    def __init__(self):
        """ Shows a sidebar menu when a key is held down, then processes input as a combo.
            Options are based on the player's effects, which are managed in Player. 
            
            Parameters
            ----------
            cursor_pos      : list of two ints; top left corner of the cursor; first value changed by self.run() in multiples of 32
            dic_indices     : list of lists of two ints; offset from wraparound, and choice index from cursor; one for each dictionary
            
            sequence_toggle : bool; True when the botton is held down
            keys            : list of key codes; sets which keys count as a combo
            key_sequence    : three csv strings in [⮜, ⮟, ⮞, ⮝]; combo set in self.run() and cleared after some time
            cooldown_time   : float; the time before the sequence is automatically cleared
            last_press_time : float; the last time the sequence was cleared
            
            detail          : bool; toggles descriptions; altered in self.run() """
        
        pyg = session.pyg

        # Cursor and position saving
        self.dic_indices = [[0, 0]]
        
        # Combo sequences
        self.sequence_toggle = True
        self.keys            = pyg.key_LEFT + pyg.key_DOWN + pyg.key_RIGHT
        self.key_sequence    = []
        self.last_press_time = 0
        self.cooldown_time   = 0.5
        self.last_combo_time = 0
        
        # GUI
        self.detail = True

    def run(self):
        """ Processes input sequences while a key is held down. """
        
        #########################################################
        # Initialize
        ## Update dictionaries and create cursors
        self.update_data()

        ## Set navigation speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Define shorthand
        pyg = session.pyg

        ## Wait for input
        for event in pygame.event.get():
            
            # Clear sequence after some time
            if time.time()-self.last_press_time > self.cooldown_time:
                self.last_press_time = time.time()
                self.key_sequence    = []
            
            if event.type == pygame.KEYDOWN:
                
                #########################################################
                # Listen for sequence
                if event.key in pyg.key_HOLD:
                    self.sequence_toggle = True

                ## Add arrow keys to the current sequence
                if self.sequence_toggle and (event.key in self.keys):
                    self.key_sequence.append(event.key)
                    
                    # Keep three most recent keys
                    if len(self.key_sequence) > 3: self.key_sequence.pop(0)
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_QUEST:
                    if not self.detail: self.detail = True
                    else:               self.detail = False
            
            #########################################################
            # Return to game
            elif event.type == pygame.KEYUP:
                if event.key in pyg.key_HOLD:
                    self.sequence_toggle = False
                    pyg.overlay_state          = None
                    return
            
            #########################################################
            # Trigger an event
            if len(self.key_sequence) == 3:
                sequence_string = ''
                for key in self.key_sequence:
                    if key in pyg.key_LEFT:    sequence_string += '⮜'
                    elif key in pyg.key_DOWN:  sequence_string += '⮟'
                    elif key in pyg.key_RIGHT: sequence_string += '⮞'
                    elif key in pyg.key_UP:    sequence_string += '⮝'
                self.check_sequence(sequence_string)
                self.key_sequence = []
        
        pyg.overlay_state = 'hold'
        return

    def update_data(self):
        """ Sets dictionary for icons and restores location. """
        
        # Finds images and sequences of player effects, then saves them in a dictionary
        inventory_dics      = {'effects': {}}
        self.dic_categories = ['effects']
        self.sequences      = {}
        for effect in session.player_obj.ent.effects:
            if effect.sequence:
                inventory_dics['effects'][effect.name] = session.img.dict[effect.img_names[0]][effect.img_names[1]]
                self.sequences[effect.name] = effect.sequence
        
        # Restore last selection
        if len(self.dic_indices) != len(self.dic_categories):
            self.dic_indices = [[0, 0] for _ in self.dic_categories]
        self.dic = inventory_dics[self.dic_categories[0]]

    def check_sequence(self, sequence_string):
        
        # Look through item effects
        for effect in session.player_obj.ent.effects:
            if effect.sequence == sequence_string:
                if time.time()-effect.last_press_time > effect.cooldown_time:
                    effect.last_press_time = float(time.time())
                    effect.function()
                    return

    def render(self):
        pyg = session.pyg

        pyg.msg_height = 1
        pyg.update_gui()
        
        session.img.average()
        color = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
        
        # Renders menu to update cursor location
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                effects_list = list(self.dic.keys())
                effect_name  = effects_list[i%len(self.dic)]
                
                # Render details
                if self.detail:
                    Y_cache = int(Y)

                    self.menu_choices = [effect_name, self.sequences[effect_name]]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(
                            pyg.minifont.render(self.menu_choices[i], True, color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.overlay_queue.append([menu_choice_surface, (40, Y_cache)])
                        Y_cache += 12
                
                # Render image
                pyg.overlay_queue.append([self.dic[effect_name], (0, Y)])
                Y += pyg.tile_height
                counter += 1
            
            else: break

class ExchangeMenu:

    def __init__(self):
        pyg = session.pyg
        
        # Data for select_item and locked_item
        self.cursor_pos_bnm = [pyg.screen_width-pyg.tile_width, 32]
        self.dic_index_bnm = 0
        self.dic_categories_bnm = session.img.other_names[:-1]
        self.dic_indices_bnm = [[0, 0] for _ in self.dic_categories_bnm] # offset, choice
        self.img_names_bnm = ['null', 'null']
        self.img_x_bnm = 0
        self.img_y_bnm = 0
        
        # Data for select_item and locked_item
        self.cursor_pos = [0, 32]
        self.dic_index = 0
        self.img_names = ['null', 'null']
        self.img_x = 0
        self.img_y = 0
        self.dic_indices = [[0, 0]]
        
        self.detail = True
        self.last_press_time = 0
        self.cooldown_time = 0.1
        
        self.menu_toggle = 'right'
        self.ent         = None

        ## Cursors
        # Left cursor
        size, width, alpha = 30, 2, 192
        self.cursor_border = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)
        
        # Right cursor
        self.cursor_border_bnm = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill_bnm   = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill_bnm.fill((255, 255, 255, alpha))
        pygame.draw.polygon(
            self.cursor_border_bnm, 
            pygame.Color('white'), 
            [(0, 0), (size, 0), (size, size), (0, size)],  width)

        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

    def run(self):
        
        pyg = session.pyg

        # Restrict movement speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        # Update dictionaries and create cursors
        self.update_data()
        
        if self.menu_toggle == 'right':
            self.dic_jkl           = self.dic_bnm
            self.choice_jkl        = self.choice_bnm
            self.cursor_pos_jkl    = self.cursor_pos_bnm
            self.offset_jkl        = self.offset_bnm
            self.dic_index_jkl     = self.dic_index_bnm
            self.dic_indices_jkl   = self.dic_indices_bnm
            self.inv_dics_jkl      = self.inv_dics_bnm
            self.owner             = self.ent
            self.recipient         = session.player_obj.ent
            self.cursor_fill_jkl   = self.cursor_fill_bnm
            self.cursor_border_jkl = self.cursor_border_bnm
        else:
            self.dic_jkl           = self.dic
            self.choice_jkl        = self.choice
            self.cursor_pos_jkl    = self.cursor_pos
            self.offset_jkl        = self.offset
            self.dic_index_jkl     = self.dic_index
            self.dic_indices_jkl   = self.dic_indices
            self.inv_dics_jkl      = self.inv_dics
            self.owner             = self.ent
            self.recipient         = session.player_obj.ent
            self.cursor_fill_jkl   = self.cursor_fill
            self.cursor_border_jkl = self.cursor_border
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
            
                ## >>PLAY GAME<<
                if (event.key in pyg.key_BACK) or (event.key in pyg.key_HOLD):
                    if time.time()-pyg.last_press_time > pyg.cooldown_time:
                        pyg.last_press_time = float(time.time())
                        pyg.overlay_state = None
                        return
                
                ## >>SWITCH<<
                elif event.key in pyg.key_INV: self.menu_toggle = 'left'
                elif event.key in pyg.key_DEV: self.menu_toggle = 'right'    
                
                ## >>NAVIGATE DICTIONARY<<
                elif event.key in pyg.key_UP:
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        self.choice_bnm = (self.choice_bnm - 1)%len(self.dic_bnm)
                        if self.cursor_pos_bnm[1] == 32: self.offset_bnm -= 1
                        else: self.cursor_pos_bnm[1] -= pyg.tile_height
                    
                    # Navigate player's inventory
                    else:
                        self.choice = (self.choice - 1)%len(self.dic)
                        if self.cursor_pos[1] == 32: self.offset -= 1
                        else: self.cursor_pos[1] -= pyg.tile_height
                
                elif event.key in pyg.key_DOWN:
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        self.choice_bnm = (self.choice_bnm + 1)%len(self.dic_bnm)
                        if self.cursor_pos_bnm[1] >= (min(len(self.dic_bnm), 12) * 32): self.offset_bnm += 1
                        else: self.cursor_pos_bnm[1] += pyg.tile_height
                    
                    # Navigate player's inventory
                    else:
                        self.choice = (self.choice + 1)%len(self.dic)
                        if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
                        else: self.cursor_pos[1] += pyg.tile_height
                
                ## >>CHANGE DICTIONARY<<
                elif (event.key in pyg.key_LEFT) or (event.key in pyg.key_RIGHT):
                
                    if event.key in pyg.key_LEFT:
                        if self.menu_toggle == 'right': self.dic_index_bnm = (self.dic_index_bnm - 1)%len(self.dic_indices_bnm)
                        else:                           self.dic_index     = (self.dic_index - 1)%len(self.dic_indices)
                    
                    elif event.key in pyg.key_RIGHT:
                        if self.menu_toggle == 'right': self.dic_index_bnm = (self.dic_index_bnm + 1)%len(self.dic_indices_bnm)
                        else:                           self.dic_index     = (self.dic_index + 1)%len(self.dic_indices)
                    
                    # Navigate trader's inventory
                    if self.menu_toggle == 'right':
                        if self.dic_indices_bnm:
                            self.dic_bnm    = self.inv_dics_bnm[list(self.inv_dics_bnm.keys())[self.dic_index_bnm%len(self.inv_dics_bnm)]]
                            self.offset_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0]
                            self.choice_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1]%len(self.dic_bnm)
                            self.choice_bnm = (self.cursor_pos_bnm[1]//32 + self.offset_bnm - 1)%len(self.dic_bnm)
                            
                            # Move cursor to the highest spot in the dictionary
                            if self.cursor_pos_bnm[1] > 32*len(self.dic_bnm):
                                self.cursor_pos_bnm[1] = 32*len(self.dic_bnm)
                                self.choice_bnm = (len(self.dic_bnm) - self.offset_bnm - 1)%len(self.dic_bnm)
                        else:
                            pyg.overlay_state = None
                            return
                    
                    # Navigate player's inventory
                    else:
                        if self.dic_indices:
                            self.dic    = self.inv_dics[list(self.inv_dics.keys())[self.dic_index%len(self.inv_dics)]]
                            self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
                            self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]%len(self.dic)
                            self.choice = (self.cursor_pos[1]//32 + self.offset - 1)%len(self.dic)
                            
                            # Move cursor to the highest spot in the dictionary
                            if self.cursor_pos[1] > 32*len(self.dic):
                                self.cursor_pos[1] = 32*len(self.dic)
                                self.choice = (len(self.dic) - self.offset - 1)%len(self.dic)
                        else:
                            pyg.overlay_state = None
                            return
                
                ## >>DETAILS<<
                elif event.key in pyg.key_QUEST:
                    if not self.detail: self.detail = True
                    else:               self.detail = False
                
                ## >>SELECT<<
                elif event.key in pyg.key_ENTER:
                    self.select()
            
            # Save for later reference
            if self.menu_toggle == 'right':
                if self.dic_indices_bnm:
                    self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0] = self.offset_bnm
                    self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1] = self.choice_bnm
                else:
                    pyg.overlay_state = None
                    return
            else:
                if self.dic_indices:
                    self.dic_indices[self.dic_index%len(self.dic_indices)][0] = self.offset
                    self.dic_indices[self.dic_index%len(self.dic_indices)][1] = self.choice
                else:
                    pyg.overlay_state = None
                    return
        
        pyg.overlay_state = 'trade'
        return

    def update_data(self):
        
        pyg = session.pyg

        # Restrict movement speed
        session.mech.movement_speed(toggle=False, custom=2)
        
        ## Dictionaries
        # Left dictionary
        self.inventory_dics = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        for key, value in session.player_obj.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics[key][item.name] = [session.img.dict[item.img_names[0]][item.img_names[1]], item]
        self.inv_dics = {}
        for key, value in self.inventory_dics.items():
            if value: self.inv_dics[key] = value
        
        # Right dictionary
        self.inventory_dics_bnm = {'weapons': {}, 'armor': {}, 'potions': {}, 'scrolls': {}, 'drugs': {}, 'other': {}}
        for key, value in self.ent.inventory.items():
            for item in value:
                if not item.hidden:
                    self.inventory_dics_bnm[key][item.name] = [session.img.dict[item.img_names[0]][item.img_names[1]], item]
        self.inv_dics_bnm = {}
        for key, value in self.inventory_dics_bnm.items():
            if value: self.inv_dics_bnm[key] = value
        
        ## Selection
        # Left selection restoration
        if len(self.dic_indices) != len(self.inv_dics):
            self.dic_indices = [[0, 0] for _ in self.inv_dics] # offset, choice
        
        # Quit if the inventory is empty
        if self.dic_indices:
            self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
            self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]%len(self.inv_dics)
            self.dic    = self.inv_dics[list(self.inv_dics.keys())[self.dic_index%len(self.inv_dics)]]
        else:
            pyg.overlay_state = None
            return
        
        # Right selection restoration
        if len(self.dic_indices_bnm) != len(self.inv_dics_bnm):
            self.dic_indices_bnm = [[0, 0] for _ in self.inv_dics_bnm] # offset, choice
        
        # Quit if the inventory is empty
        if self.dic_indices_bnm:
            self.offset_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][0]
            self.choice_bnm = self.dic_indices_bnm[self.dic_index_bnm%len(self.dic_indices_bnm)][1]%len(self.inv_dics_bnm)
            self.dic_bnm    = self.inv_dics_bnm[list(self.inv_dics_bnm.keys())[self.dic_index_bnm%len(self.inv_dics_bnm)]]
        else:
            pyg.overlay_state = None
            return

    def select(self):
        """
        dic         : name, surface, and Item object; ex. {'green clothes': [<Surface>, <Item>]}
        offset      : 
        choice      : 
        dic_indices : list of tuples; one tuple for each nonempty pocket; the first entry is 
        dic index   : int between 0 and the number of pockets; increases when 

        """
        
        # Find owner and item
        if self.menu_toggle == 'right':
            owner     = self.ent
            recipient = session.player_obj.ent
            index     = self.dic_indices_bnm[self.dic_index_bnm%len(self.inv_dics_bnm)][1]
            item      = list(self.dic_bnm.values())[index][1]
        else:
            owner     = session.player_obj.ent
            recipient = self.ent
            index     = self.dic_indices[self.dic_index%len(self.inv_dics)][1]
            item      = list(self.dic.values())[index][1]
        
        # Trade item
        item.trade(owner, recipient)
        
        # Adjust cursor
        if self.menu_toggle == 'right':
            if self.cursor_pos_bnm[1] >= 32*len(self.dic_bnm):
                self.cursor_pos_bnm[1] = 32*(len(self.dic_bnm)-1)
                self.choice_bnm = len(self.dic_bnm) - self.offset_bnm - 2
        else:
            if self.cursor_pos[1] >= 32*len(self.dic):
                self.cursor_pos[1] = 32*(len(self.dic)-1)
                self.choice = len(self.dic) - self.offset - 2
    
    def find_item(self, ent, offset=None):
        
        if self.menu_toggle == 'right':
            dic_index = self.dic_index_bnm
            choice    = self.choice_bnm
            offset    = self.offset_bnm
        
        else:
            dic_index = self.dic_index
            choice    = self.choice
            offset    = self.offset
        
        # Retrieve inventory list
        outer_list   = list(ent.inventory.items())
        length       = len(outer_list)
        filter_empty = []
        
        # Remove names without objects
        for i in range(length):
            if outer_list[i][1]: filter_empty.append(outer_list[i])
        
        # Name and list of objects for the selected category
        outer_key, inner_list = filter_empty[dic_index%len(filter_empty)]
        
        # Remove hidden items
        filtered_list = [item for item in inner_list if not item.hidden]
        
        # Select the item
        if filtered_list:
            
            try:
                if type(offset) == int: item = filtered_list[offset]
                else: item = filtered_list[choice%len(filtered_list)]
                return item
            except:
                pass

    def render(self):
        
        pyg = session.pyg

        # Apply background fade
        pyg.overlay_queue.append([self.background_fade, (0, 0)])
        
        # Basics
        pyg.msg_height = 1
        pyg.update_gui()
        
        # Cursor background and font colors
        session.img.average()
        if self.menu_toggle == 'right':
            left_color  = pygame.Color(session.img.left_correct - 20, session.img.left_correct - 20, session.img.left_correct - 20)
            right_color = pygame.Color(session.img.right_correct, session.img.right_correct, session.img.right_correct)
            pyg.overlay_queue.append([self.cursor_fill_bnm, self.cursor_pos_bnm])
        else:
            left_color  = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
            right_color = pygame.Color(session.img.right_correct - 20, session.img.right_correct - 20, session.img.right_correct - 20)
            pyg.overlay_queue.append([self.cursor_fill, self.cursor_pos])
        
        ## Player's inventory
        Y = 32
        counter = 0
        for i in range(len(list(self.dic))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                items_list = list(self.dic.keys())
                item_name  = items_list[(i+self.offset)%len(self.dic)]
                item       = self.dic[item_name][1]
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    cost = f"⨋ {item.cost}"
                    self.menu_choices = [item_name, cost]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, left_color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        pyg.overlay_queue.append([menu_choice_surface, (40, Y_detail)])
                        Y_detail += 12
                
                # Render image
                pyg.overlay_queue.append([self.dic[item_name][0], (0, Y)])
                Y += pyg.tile_height
                counter += 1                
            else: break
        
        ## Trader's inventory
        Y = 32
        counter = 0
        for i in range(len(list(self.dic_bnm))):
            
            # Stop at the 12th image, starting with respect to the offset 
            if counter <= 12:
                
                # Extract image details
                items_list = list(self.dic_bnm.keys())
                item_name  = items_list[(i+self.offset_bnm)%len(self.dic_bnm)]
                item       = self.dic_bnm[item_name][1]
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    cost = f"⨋ {item.cost}"
                    self.menu_choices = [item_name, cost]
                    self.menu_choices_surfaces = []
                    for i in range(len(self.menu_choices)):
                        self.menu_choices_surfaces.append(pyg.minifont.render(self.menu_choices[i], True, right_color))
                    
                    for menu_choice_surface in self.menu_choices_surfaces:
                        X = pyg.screen_width - pyg.tile_width - menu_choice_surface.get_width() - 8
                        pyg.overlay_queue.append([menu_choice_surface,  (X, Y_detail)])
                        Y_detail += 12
                
                # Render image
                pyg.overlay_queue.append([self.dic_bnm[item_name][0],  (pyg.screen_width-pyg.tile_width, Y)])
                Y += pyg.tile_height
                counter += 1                
            else: break
        
        if self.menu_toggle == 'right': pyg.overlay_queue.append([self.cursor_border_bnm, self.cursor_pos_bnm])
        else:                           pyg.overlay_queue.append([self.cursor_border,     self.cursor_pos])

########################################################################################################################################################