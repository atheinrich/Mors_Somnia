########################################################################################################################################################
# Local mechanics
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import time
import copy

## Specific
import pygame
from   pygame.locals import *

## Local
import session

########################################################################################################################################################
# Standard objects and parameters
def cursor(locked):
    cursor_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    fill_surface   = pygame.Surface((32, 32), pygame.SRCALPHA)

    if locked: data = {'size':  30, 'width': 2, 'alpha': 192}
    else:      data = {'size':  31, 'width': 1, 'alpha': 128}

    pygame.draw.polygon(
        cursor_surface, 
        session.pyg.white, 
        [
            (0,            0),
            (data['size'], 0),
            (data['size'], data['size']),
            (0,            data['size'])
        ],  
        data['width'])

    fill_surface.fill((255, 255, 255, data['alpha']))

    return cursor_surface, fill_surface

def background_fade():
    pyg = session.pyg
    background_surface = pygame.Surface((pyg.screen_width, pyg.screen_height), pygame.SRCALPHA)
    background_surface.fill((0, 0, 0, 50))
    return background_surface

########################################################################################################################################################
# Classes
class InventoryMenu:
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """

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
        self.background_fade = background_fade()

        ## Cursor
        self.cursor,        self.cursor_fill        = cursor(locked=False)
        self.locked_cursor, self.locked_cursor_fill = cursor(locked=True)

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
                # Open catalog
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                    return
            
            elif event.type == KEYUP:

                #########################################################
                # Activate or drop item
                if event.key in pyg.key_ENTER:
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
                # Return to game
                elif event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
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
        """ Manages inventory menu on the side of the screen. Allows item activation. """
        
        pyg   = session.pyg

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
        self.right_pos     = pyg.screen_width - pyg.tile_width
        self.cursor_pos    = [self.right_pos, 32] # second value is altered
        self.index_history = {}      # position memory; category_name: [item_index, offset]

        ## Other
        self.locked = False          # allows the player to active highlighted item while moving
        self.detail = True           # toggles item names

        #########################################################
        # Surface initialization
        ## Background
        self.background_fade = background_fade()

        ## Cursor
        self.cursor,        self.cursor_fill        = cursor(locked=False)
        self.locked_cursor, self.locked_cursor_fill = cursor(locked=True)

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
                # Open inventory
                elif event.key in pyg.key_INV:
                    self.key_INV()
                    return
                
            elif event.type == KEYUP:

                #########################################################
                # Activate or drop item
                if event.key in pyg.key_ENTER:
                    self.key_ENTER()
                elif event.key in pyg.key_PERIOD:
                    self.key_PERIOD()
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_GUI:
                    self.key_GUI()
                
                #########################################################
                # Toggle selection lock
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                
                #########################################################
                # Return to game
                elif event.key in pyg.key_BACK:
                    self.key_BACK()
                    return
        
        pyg.overlay_state = 'dev'
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
                
                # Create text surfaces
                text_lines = [item.name]
                for text in text_lines:
                    surface = pyg.minifont.render(text, True, color)
                    width   = surface.get_width()
                    pyg.overlay_queue.append([surface, (self.right_pos-width-8, Y_detail)])
                    Y_detail += 12
            
            # Send to queue
            img = session.img.dict[item.img_IDs[0]][item.img_IDs[1]]
            pyg.overlay_queue.append([img, (self.right_pos, Y)])
        
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

    def key_DEV(self):
        self.locked = not self.locked

    def key_INV(self):
        self.locked = False
        session.pyg.overlay_state = 'inv'

    def key_ENTER(self):
        from environments import place_object
        pyg = session.pyg

        item = copy.deepcopy(self.items[self.item_index])
        
        # Note location
        x = int(session.player_obj.ent.X / pyg.tile_width)
        y = int(session.player_obj.ent.Y / pyg.tile_height)
        
        direction = session.player_obj.ent.direction
        if direction == 'front':   y += 1
        elif direction == 'back':  y -= 1
        elif direction == 'right': x += 1
        elif direction == 'left':  x -= 1

        place_object(
            obj = item,
            loc = [x, y],
            env = session.player_obj.ent.env)        

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

        inv = session.player_obj.ent.discoveries

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
        for ability in session.player_obj.ent.active_abilities.values():
        
            # Render details
            if self.detail:
                Y_cache = int(Y)

                sequence   = ability.sequence
                text_lines = [ability.name, sequence]
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
        self.background_fade = background_fade()

        ## Cursor
        self.cursor, self.cursor_fill = cursor(locked=False)

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
                
            elif event.type == KEYUP:

                #########################################################
                # Trade an item
                if event.key in pyg.key_ENTER:
                    self.key_ENTER()
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_GUI:
                    self.key_GUI()
                
                #########################################################
                # Return to game
                elif event.key in pyg.key_BACK:
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