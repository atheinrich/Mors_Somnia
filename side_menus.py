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
        ## Item management
        self.categories = []         # cache of category names with visible items
        self.items      = []         # cache of actual item objects in current category

        ## Choice management
        self.category_index = 0      # which category is active
        self.item_index     = 0      # index of highlighted item corresponding to self.items
        self.offset         = 0      # difference of first item in category and first currently shown

        ## Positions
        self.cursor_pos    = [0, 32] # second value is altered
        self.index_history = {}      # position memory; category_name: [item_index, offset]

        ## Other
        self.locked = False          # allows the player to active highlighted item while moving
        self.detail = True           # toggles item names

        #########################################################
        # Surface initialization
        ## Background
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

        ## Cursor
        self.cursor      = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill = pygame.Surface((32, 32), pygame.SRCALPHA)
        cursor_data = {
            'size':  31,
            'width': 1,
            'alpha': 128}
        
        self.locked_cursor      = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.locked_cursor_fill = pygame.Surface((32, 32), pygame.SRCALPHA)
        locked_cursor_data = {
            'size':  30,
            'width': 2,
            'alpha': 192}
        
        cursors = [
            (self.cursor,        self.cursor_fill,        cursor_data),
            (self.locked_cursor, self.locked_cursor_fill, locked_cursor_data)]
        
        for (cursor, fill, data) in cursors:

            fill.fill((255, 255, 255, data['alpha']))

            pygame.draw.polygon(
                cursor, 
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
        session.effects.movement_speed(toggle=False, custom=0)
        
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
                elif event.key in pyg.key_GUI:
                    self.key_GUI()
                
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
            elif event.type == KEYUP:

                if event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
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
        ## Background and cursor fill
        if self.locked:
            pyg.overlay_queue.append([self.locked_cursor_fill, self.cursor_pos])
        else:
            pyg.overlay_queue.append([self.background_fade, (0, 0)])
            pyg.overlay_queue.append([self.cursor_fill, self.cursor_pos])

        ## Color
        session.img.average()
        c     = session.img.left_correct
        color = pygame.Color(c, c, c)
        
        ## Items
        for i in range(self.offset, min(len(self.items), self.offset + 12)):

            # Select next item and position
            item = self.items[i]
            Y    = 32 + (i - self.offset) * 32
            
            # Render details
            if self.detail:
                Y_detail = int(Y)
                
                # Set text
                if item:
                    if item.equipped: detail = '(equipped)'
                    else:             detail = ''
                else:                 detail = ''
                
                # Create text surfaces
                text_lines = [item.name, detail]
                for text in text_lines:
                    surface = pyg.minifont.render(text, True, color)
                    pyg.overlay_queue.append([surface, (40, Y_detail)])
                    Y_detail += 12
            
            # Send to queue
            img = session.img.dict[item.img_IDs[0]][item.img_IDs[1]]
            pyg.overlay_queue.append([img, (0, Y)])
        
        ## Cursor border
        if self.locked: pyg.overlay_queue.append([self.locked_cursor, self.cursor_pos])
        else:           pyg.overlay_queue.append([self.cursor,        self.cursor_pos])

    # Keys
    def key_UP(self):
        if not self.locked:
            self.item_index = (self.item_index - 1) % len(self.items)
            self.update_data()
        else:
            session.movement.move(session.player_obj.ent, 0, -session.pyg.tile_height)

    def key_DOWN(self):
        if not self.locked:
            self.item_index = (self.item_index + 1) % len(self.items)
            self.update_data()
        else:
            session.movement.move(session.player_obj.ent, 0, session.pyg.tile_height)

    def key_LEFT(self):
        if not self.locked:
            self.update_category(-1)
            self.update_data()
        else:
            session.movement.move(session.player_obj.ent, -session.pyg.tile_height, 0)

    def key_RIGHT(self):
        if not self.locked:
            self.update_category(1)
            self.update_data()
        else:
            session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)

    def key_BACK(self):
        self.locked = False
        session.pyg.overlay_state = None

    def key_GUI(self):
        self.detail = not self.detail

    def key_INV(self):
        self.locked = not self.locked

    def key_DEV(self):
        self.locked = False
        session.pyg.overlay_state = 'dev'

    def key_ENTER(self):
        session.items.use(self.items[self.item_index])
        self.update_data()

    def key_PERIOD(self):
        session.items.drop(self.items[self.item_index])
        self.update_data()

    # Tools
    def update_data(self):
        """ Updates current category and its items. """
        
        # Update inventory cache
        inventory_dicts = self._find_visible()
        self.categories = list(inventory_dicts.keys())
        
        # Close the menu if no items are visible
        if not self.categories:
            session.pyg.overlay_state = None
            return

        # Normalize the current category to the number of categories with visible items
        self.category_index %= len(self.categories)

        # Update item cache for selected category
        self.items = inventory_dicts[self.categories[self.category_index]]

        self._update_offset()

    def _find_visible(self):
        """ Rebuilds a dictionary of visible inventory items, grouped by category. """

        inv = session.player_obj.ent.inventory

        inventory_dicts = {}

        for category, items in inv.items():
            visible_items = [item for item in items if not item.hidden]
            if visible_items:
                inventory_dicts[category] = visible_items

        return inventory_dicts

    def _update_offset(self):
        """ Updates which items are currently shown. """

        max_visible = 12

        # Show all visible items
        if len(self.items) <= max_visible:
            self.offset = 0
        
        # Show current 12 items, set by offset
        else:

            # Shift current 12 items up by one; cursor is at the top (not the ultimate top)
            if self.item_index < self.offset:
                self.offset -= 1 #= self.item_index

            # Shift current 12 items down by one; cursor is at the bottom (not the ultimate bottom)
            elif self.item_index >= self.offset + max_visible:
                self.offset += 1 # self.item_index - max_visible + 1

        # Update cursor
        self.cursor_pos[1] = (self.item_index - self.offset + 1) * 32

        # Keep cursor in the desired bounds
        if self.cursor_pos[1] == 0:
            self.cursor_pos[1] = 32
        elif self.cursor_pos[1] == (max_visible + 1) * 32:
            self.cursor_pos[1] += 64
        elif self.cursor_pos[1] == (max_visible + 2) * 32:
            self.cursor_pos[1] += 64

    def update_category(self, direction):
        """ Manages history for cursor position in each category. """
        
        # Check for new categories
        for filled_category in self.categories:
            if filled_category not in self.index_history.keys():
                self.index_history[filled_category] = [0, 0]
    
        # Remove old categories
        for saved_category in list(self.index_history.keys()):
            if saved_category not in self.categories:
                del self.index_history[saved_category]

        # Save last
        last_category = self.categories[self.category_index]
        self.index_history[last_category] = [self.item_index, self.offset]

        # Load new
        self.category_index = (self.category_index + direction) % len(self.categories)
        new_category        = self.categories[self.category_index]
        self.item_index, self.offset = self.index_history[new_category]

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
        self.img_IDs = ['null', 'null']
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
        session.effects.movement_speed(toggle=False, custom=2)
        
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
            elif event.type == KEYUP:
                if event.key in pyg.key_BACK:
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
                img_IDs = self.dic[list(self.dic.keys())[(i+self.offset)%len(self.dic)]]
                pyg.overlay_queue.append([session.img.dict[img_IDs[0]][img_IDs[1]], (pyg.screen_width-pyg.tile_width, Y)])
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
            session.movement.move(session.player_obj.ent, 0, -pyg.tile_height)
                
    def key_DOWN(self):
        pyg = session.pyg

        if not self.locked:
            self.choice += 1
            if self.cursor_pos[1] >= (min(len(self.dic), 12) * 32): self.offset += 1
            else: self.cursor_pos[1] += pyg.tile_height
            
        else:
            session.movement.move(session.player_obj.ent, 0, pyg.tile_height)

    def key_LEFT(self):

        if not self.locked:
            self.dic_index -= 1
            self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
            while not len(self.dic):
                self.dic_index -= 1
                self.dic = session.player_obj.ent.discoveries[self.dic_categories[self.dic_index%len(self.dic_categories)]]
        
        else:
            session.movement.move(session.player_obj.ent, -session.pyg.tile_height, 0)

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
            session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)
        
        self.offset = self.dic_indices[self.dic_index%len(self.dic_indices)][0]
        self.choice = self.dic_indices[self.dic_index%len(self.dic_indices)][1]   
        self.choice = self.cursor_pos[1]//32 + self.offset - 1
    
        # Move cursor to the highest spot in the dictionary
        if self.cursor_pos[1] > 32*len(self.dic):
            self.cursor_pos[1] = 32*len(self.dic)
            self.choice = len(self.dic) - self.offset - 1

    def key_ENTER(self):
        
        pyg = session.pyg

        from environments import place_object
        from entities import create_item, create_entity

        # Note location and image names
        self.img_x, self.img_y = int(session.player_obj.ent.X/pyg.tile_width), int(session.player_obj.ent.Y/pyg.tile_height)
        self.img_IDs[0] = self.dic_categories[self.dic_index%len(self.dic_categories)]
        self.img_IDs[1] = list(self.dic.keys())[(self.choice)%len(self.dic)]
        
        # Set location for drop
        if session.player_obj.ent.direction == 'front':   self.img_y += 1
        elif session.player_obj.ent.direction == 'back':  self.img_y -= 1
        elif session.player_obj.ent.direction == 'right': self.img_x += 1
        elif session.player_obj.ent.direction == 'left':  self.img_x -= 1
        
        # Place tile
        if self.img_IDs[0] in ['floors', 'walls', 'roofs']:
            obj = session.player_obj.ent.env.map[self.img_x][self.img_y]
            obj.placed = True
            place_object(
                obj = obj,
                loc = [self.img_x, self.img_y],
                env = session.player_obj.ent.env,
                names = self.img_IDs.copy())

            # Check if it completes a room
            if self.img_IDs[0] == 'walls':
                session.player_obj.ent.env.build_room(obj)
        
        # Place entity
        elif self.img_IDs[0] in session.img.ent_data.keys():
            item = create_entity(
                names = self.img_IDs.copy())
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_IDs.copy())
        
        # Place item
        elif self.img_IDs[1] not in session.img.ent_data.keys():
            item = create_item(
                names = self.img_IDs)
            place_object(
                obj   = item,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_IDs.copy())
            if item.img_IDs[0] == 'stairs':
                item.tile.blocked = False
        
        else:
            ent = create_entity(
                names = self.img_IDs[1])
            place_object(
                obj   = ent,
                loc   = [self.img_x, self.img_y],
                env   = session.player_obj.ent.env,
                names = self.img_IDs.copy())
        
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
    
    # Core
    def __init__(self):
        """ Shows a sidebar menu when a key is held down, then processes input as a combo.
            Options are based on the player's effects, which are managed in PlayerData. 
            
            Parameters
            ----------            
            keys            : list of key codes; sets which keys count as a combo
            key_sequence    : list; three strings in [⮜, ⮟, ⮞, ⮝]
            cooldown_time   : float; the time before the sequence is automatically cleared
            last_combo_time : float; the last time the sequence was cleared
            
            detail          : bool; toggles descriptions; altered in self.run() """
        
        pyg = session.pyg

        # Combo sequences
        self.keys            = pyg.key_LEFT + pyg.key_DOWN + pyg.key_RIGHT
        self.key_sequence    = []
        self.last_combo_time = 0
        self.cooldown_time   = 0.5
        
        # GUI
        self.detail = True

    def run(self):
        """ Processes input sequences while a key is held down. """
        
        pyg = session.pyg

        ## Wait for input
        for event in pygame.event.get():
            
            # Clear sequence after some time
            if time.time() - self.last_combo_time > self.cooldown_time:
                self.last_combo_time = time.time()
                self.key_sequence    = []
            
            if event.type == pygame.KEYDOWN:
                
                #########################################################
                # Add arrow keys to the current sequence
                if event.key in self.keys:
                    self.add_key(event.key)
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_GUI:
                    self.key_GUI()
            
            #########################################################
            # Return to game
            elif event.type == pygame.KEYUP:
                if event.key in pyg.key_HOLD:
                    pyg.overlay_state = None
                    return
            
            #########################################################
            # Activate ability
            if len(self.key_sequence) == 3:
                self.check_sequence()
        
        pyg.overlay_state = 'hold'
        return

    def render(self):
        pyg = session.pyg

        pyg.msg_height = 1
        pyg.update_gui()
        
        session.img.average()
        color = pygame.Color(session.img.left_correct, session.img.left_correct, session.img.left_correct)
        
        # Renders menu to update cursor location
        Y = 32
        for name, ability in session.player_obj.ent.active_abilities.items():
        
            # Render details
            if self.detail:
                Y_cache = int(Y)

                sequence   = session.player_obj.ent.active_abilities[name].sequence
                text_lines = [name, sequence]
                for text in text_lines:
                    surface = pyg.minifont.render(text, True, color)
                    pyg.overlay_queue.append([surface, (40, Y_cache)])
                    Y_cache += 12
            
            # Render image
            img = session.img.dict[ability.img_IDs[0]][ability.img_IDs[1]]
            pyg.overlay_queue.append([img, (0, Y)])
            Y += pyg.tile_height

    # Keys
    def key_GUI(self):
        if not self.detail: self.detail = True
        else:               self.detail = False

    # Tools
    def add_key(self, key):

        # Add to current sequence
        self.key_sequence.append(key)
        
        # Keep three most recent keys
        if len(self.key_sequence) > 3: self.key_sequence.pop(0)

    def check_sequence(self):
        """ Matches the current sequence to active abilities, then activates the ability if it matches. """

        pyg = session.pyg

        # Convert to arrow notation
        sequence_string = ''
        for key in self.key_sequence:
            if key in pyg.key_LEFT:    sequence_string += '⮜'
            elif key in pyg.key_DOWN:  sequence_string += '⮟'
            elif key in pyg.key_RIGHT: sequence_string += '⮞'
            elif key in pyg.key_UP:    sequence_string += '⮝'
        self.key_sequence = []
    
        # Check for a match
        for ability in session.player_obj.ent.active_abilities.values():
            if ability.sequence == sequence_string:

                # Check for cooldown
                if time.time() - ability.last_press_time > ability.cooldown_time:
                    ability.last_press_time = float(time.time())
                    ability.activate()
                    return

class ExchangeMenu:
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """
        
        pyg = session.pyg

        #########################################################
        # Parameters
        ## Inventory selector
        self.inv_toggle = 0              # toggles player (0) and NPC (1) inventories
        self.trader     = None           # entity to trade with 

        ## Item management
        self.categories = [[], []]       # cache of category names with visible items
        self.items      = [[], []]       # cache of actual item objects in current category

        ## Choice management
        self.category_indices = [0, 0]   # which category is active
        self.item_indices     = [0, 0]   # index of highlighted item corresponding to self.items
        self.offsets          = [0, 0]   # difference of first item in category and first currently shown

        ## Positions
        self.cursor_pos       = [0, 32]  # second value is altered
        self.index_histories  = [{}, {}] # position memory; category_name: [item_index, offset]

        ## Other
        self.detail = True               # toggles item names
        self.X_img = [
            0,
            pyg.screen_width - pyg.tile_width]
        self.X_details = lambda surface: [
            40, 
            self.X_img[1] - surface.get_width() - 8]
        
        #########################################################
        # Surface initialization
        ## Background
        self.background_fade = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))

        ## Cursor
        self.cursor      = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.cursor_fill = pygame.Surface((32, 32), pygame.SRCALPHA)
        cursor_data = {
            'size':  31,
            'width': 1,
            'alpha': 128}
        
        cursors = [(self.cursor, self.cursor_fill, cursor_data)]
        
        for (cursor, fill, data) in cursors:

            fill.fill((255, 255, 255, data['alpha']))

            pygame.draw.polygon(
                cursor, 
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
        session.effects.movement_speed(toggle=False, custom=0)
        
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
                # Switch inventories
                elif event.key in pyg.key_INV:
                    self.key_INV()
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                
                #########################################################
                # Trade an item
                elif event.key in pyg.key_ENTER:
                    self.key_ENTER()
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_GUI:
                    self.key_GUI()
                
            #########################################################
            # Return to game
            elif event.type == KEYUP:

                if event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
        pyg.overlay_state = 'trade'
        return

    def render(self):

        #########################################################
        # Adjust GUI
        pyg = session.pyg
        pyg.msg_height = 1
        pyg.update_gui()

        #########################################################
        # Renders
        ## Background and cursor fill
        pyg.overlay_queue.append([self.background_fade, (0, 0)])
        pyg.overlay_queue.append([self.cursor_fill, self.cursor_pos])

        ## Color
        session.img.average()
        L = session.img.left_correct
        R = session.img.right_correct
        
        if self.inv_toggle: L = L-20
        else:               R = R-20

        colors = [
            pygame.Color(L, L, L),
            pygame.Color(R, R, R)]

        ## Items
        for i in range(len(self.items)):
            for j in range(self.offsets[i], min(len(self.items[i]), self.offsets[i] + 12)):

                # Select next item and position
                item = self.items[i][j]
                Y    = 32 + (j - self.offsets[i]) * 32
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    
                    # Set text
                    if item: detail = f"⨋ {item.cost}"
                    else:    detail = ''
                    
                    # Create text surfaces
                    text_lines = [item.name, detail]
                    for text in text_lines:
                        surface = pyg.minifont.render(text, True, colors[i])
                        pyg.overlay_queue.append([
                            surface,
                            (self.X_details(surface)[i], Y_detail)])
                        Y_detail += 12
                
                # Send to queue
                img = session.img.dict[item.img_IDs[0]][item.img_IDs[1]]
                pyg.overlay_queue.append([img, (self.X_img[i], Y)])
            
        ## Cursor border
        pyg.overlay_queue.append([self.cursor, self.cursor_pos])

    # Keys
    def key_UP(self):
        i = self.inv_toggle
        self.item_indices[i] = (self.item_indices[i] - 1) % len(self.items[i])
        self.update_data()

    def key_DOWN(self):
        i = self.inv_toggle
        self.item_indices[i] = (self.item_indices[i] + 1) % len(self.items[i])
        self.update_data()

    def key_LEFT(self):
        self.update_category(-1)
        self.update_data()

    def key_RIGHT(self):
        self.update_category(1)
        self.update_data()

    def key_BACK(self):
        session.pyg.overlay_state = None

    def key_GUI(self):
        self.detail = not self.detail

    def key_INV(self):
        self.inv_toggle = 0
        self.cursor_pos[0] = self.X_img[self.inv_toggle]

    def key_DEV(self):
        self.inv_toggle = 1
        self.cursor_pos[0] = self.X_img[self.inv_toggle]

    def key_ENTER(self):
        i = self.inv_toggle
        if i:
            owner     = self.trader
            recipient = session.player_obj.ent
        else:
            owner     = session.player_obj.ent
            recipient = self.trader
        
        session.items.trade(self.items[i][self.item_indices[i]], owner, recipient)
        self.update_data()

    # Tools
    def update_data(self):
        """ Updates current category and its items. """

        ents = [
            session.player_obj.ent,
            self.trader]
        
        for i in range(len(ents)):

            # Update inventory cache
            inventory_dicts    = self._find_visible(ents[i])
            self.categories[i] = list(inventory_dicts.keys())
            
            # Close the menu if no items are visible
            if (i == 1) and (not self.categories[i]):
                session.pyg.overlay_state = None
                return

            # Normalize the current category to the number of categories with visible items
            self.category_indices[i] %= len(self.categories[i])

            # Update item cache for selected category
            self.items[i] = inventory_dicts[self.categories[i][self.category_indices[i]]]

            self._update_offset()

    def _find_visible(self, ent):
        """ Rebuilds a dictionary of visible inventory items, grouped by category. """

        inv = ent.inventory

        inventory_dicts = {}

        for category, items in inv.items():
            visible_items = [item for item in items if not item.hidden]
            if visible_items:
                inventory_dicts[category] = visible_items

        return inventory_dicts

    def _update_offset(self):
        """ Updates which items are currently shown. """

        max_visible = 12
        i = self.inv_toggle

        # Show all visible items
        if len(self.items[i]) <= max_visible:
            self.offsets[i] = 0
        
        # Show current 12 items, set by offset
        else:

            # Shift current 12 items up by one; cursor is at the top (not the ultimate top)
            if self.item_indices[i] < self.offsets[i]:
                self.offsets[i] = self.item_indices[i]

            # Shift current 12 items down by one; cursor is at the bottom (not the ultimate bottom)
            elif self.item_indices[i] >= self.offsets[i] + max_visible:
                self.offsets[i] = self.item_indices[i] - max_visible + 1

        # Update cursor
        self.cursor_pos[1] = (self.item_indices[i] - self.offsets[i] + 1) * 32

        # Keep cursor in the desired bounds
        if self.cursor_pos[1] == 0:
            self.cursor_pos[1] = 32
        elif self.cursor_pos[1] == (max_visible + 1) * 32:
            self.cursor_pos[1] += 64
        elif self.cursor_pos[1] == (max_visible + 2) * 32:
            self.cursor_pos[1] += 64

    def update_category(self, direction):
        """ Manages history for cursor position in each category. """
        
        i = self.inv_toggle

        # Check for new categories
        for filled_category in self.categories[i]:
            if filled_category not in self.index_histories[i].keys():
                self.index_histories[i][filled_category] = [0, 0]
    
        # Remove old categories
        for saved_category in list(self.index_histories[i].keys()):
            if saved_category not in self.categories[i]:
                del self.index_histories[i][saved_category]

        # Save last
        last_category = self.categories[i][self.category_indices[i]]
        self.index_histories[i][last_category] = [self.item_indices[i], self.offsets[i]]

        # Load new
        self.category_indices[i] = (self.category_indices[i] + direction) % len(self.categories[i])
        new_category             = self.categories[i][self.category_indices[i]]
        self.item_indices[i], self.offsets[i] = self.index_histories[i][new_category]

########################################################################################################################################################