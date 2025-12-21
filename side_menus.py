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
# General tools
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

def find_visible(inv):
    """ Rebuilds a dictionary of visible inventory items, grouped by category. """

    inventory_dicts = {}

    for category, items in inv.items():
        visible_items = [item for item in items if not item.hidden]
        if visible_items:
            inventory_dicts[category] = visible_items

    return inventory_dicts

########################################################################################################################################################
# Classes
class ColumnData:

    def __init__(self, col_id):

        # Identifier
        self.col_id         = col_id
        self.active         = False

        # Item management
        self.ent            = None    # owner
        self.inv            = None    # set of objects to display
        self.categories     = []      # cache of category names with visible items
        self.items          = []      # cache of actual item objects in current category

        # Choice management
        self.category_index = 0       # which category is active
        self.item_index     = 0       # index of highlighted item corresponding to self.items
        self.offset         = 0       # difference of first item in category and first currently shown

        # Positions
        self.cursor_pos     = [0, 0]  # second value is altered
        self.detail_pos     = [0, 0]  # second value is altered
        self.index_history  = {}      # position memory; category_name: [item_index, offset]

class ColumnMenu:

    # Core
    def __init__(self):
        
        # Parameters
        self.locked  = False # allows the player to active highlighted item while moving
        self.detail  = True  # toggles item names

        # Background
        self.background_fade = background_fade()

        # Cursor
        self.cursor,        self.cursor_fill        = cursor(locked=False)
        self.locked_cursor, self.locked_cursor_fill = cursor(locked=True)

    def run(self):
        pyg = session.pyg
        
        #########################################################
        # Initialize
        ## Update dictionaries and create cursors
        for data in self.columns:
            self.update_data(data)

        ## Set navigation speed
        session.effects.movement_speed(toggle=False, custom=0)
        
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
                # Switch category
                elif event.key in pyg.key_LEFT:
                    self.key_LEFT()
                elif event.key in pyg.key_RIGHT:
                    self.key_RIGHT()
                
            elif event.type == KEYUP:

                #########################################################
                # Select an item
                if event.key in pyg.key_ENTER:
                    self.key_ENTER()
                elif event.key in pyg.key_PERIOD:
                    self.key_PERIOD()
                
                #########################################################
                # Toggle details
                elif event.key in pyg.key_GUI:
                    self.key_GUI()
                
                #########################################################
                # Switch columns
                elif event.key in pyg.key_INV:
                    self.key_INV()
                elif event.key in pyg.key_DEV:
                    self.key_DEV()
                
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
        ## Background fade
        if not self.locked:
            pyg.overlay_queue.append([self.background_fade, (0, 0)])
        
        ## Color
        session.img.average()
        L = session.img.left_correct
        R = session.img.right_correct
        
        if self.active != self.columns[0]: L = L-20
        else:                              R = R-20

        for data in self.columns:
            if data.cursor_pos[0] == 0: color = pygame.Color(L, L, L)
            else:                       color = pygame.Color(R, R, R)
            
            ## Cursor fill
            if self.active == data:
                if self.locked: pyg.overlay_queue.append([self.locked_cursor_fill, data.cursor_pos])
                else:           pyg.overlay_queue.append([self.cursor_fill, data.cursor_pos])

            ## Items
            for i in range(data.offset, min(len(data.items), data.offset + 12)):

                # Select next item and position
                item = data.items[i]
                Y    = pyg.tile_height + (i - data.offset) * pyg.tile_height
                
                # Render details
                if self.detail:
                    Y_detail = int(Y)
                    
                    # Create text surfaces
                    for text in self.details(item):
                        surface = pyg.minifont.render(text, True, color)
                        pyg.overlay_queue.append([
                            surface,
                            (data.detail_pos(surface)[0], Y_detail)])
                        Y_detail += 12
                
                # Send to queue
                img = session.img.dict[item.img_IDs[0]][item.img_IDs[1]]
                pyg.overlay_queue.append([img, (data.cursor_pos[0], Y)])
                
            ## Cursor border
            if self.active == data:
                if self.locked: pyg.overlay_queue.append([self.locked_cursor, data.cursor_pos])
                else:           pyg.overlay_queue.append([self.cursor,        data.cursor_pos])

    # Keys
    def key_UP(self):
        if not self.locked:
            self.active.item_index = (self.active.item_index - 1) % len(self.active.items)
            self.update_data(self.active)
        else:
            session.movement.move(session.player_obj.ent, 0, -session.pyg.tile_height)

    def key_DOWN(self):
        if not self.locked:
            self.active.item_index = (self.active.item_index + 1) % len(self.active.items)
            self.update_data(self.active)
        else:
            session.movement.move(session.player_obj.ent, 0, session.pyg.tile_height)

    def key_LEFT(self):
        if not self.locked:
            self.update_category(self.active, -1)
            self.update_data(self.active)
        else:
            session.movement.move(session.player_obj.ent, -session.pyg.tile_height, 0)

    def key_RIGHT(self):
        if not self.locked:
            self.update_category(self.active, 1)
            self.update_data(self.active)
        else:
            session.movement.move(session.player_obj.ent, session.pyg.tile_width, 0)

    def key_BACK(self):
        session.pyg.overlay_state = None

    def key_GUI(self):
        self.detail = not self.detail

    # Tools
    def update_data(self, data):
        """ Updates current category and its items. """

        # Update entity and select inventory
        if data.col_id in ['inv', 'dev']:
            data.ent = session.player_obj.ent
            if data.col_id == 'inv':
                data.inv = session.player_obj.ent.inventory
            else:
                data.inv = session.player_obj.ent.discoveries
        else:
            data.inv = data.ent.inventory
        
        # Update inventory cache
        inventory_dicts = find_visible(data.inv)
        data.categories = list(inventory_dicts.keys())

        # Normalize the current category to the number of categories with visible items
        data.category_index %= len(data.categories)

        # Update item cache for selected category
        data.items = inventory_dicts[data.categories[data.category_index]]

        self._update_offset(data)

    def _update_offset(self, data):
        """ Updates which items are currently shown. """

        pyg = session.pyg

        max_visible = 12

        # Show all visible items
        if len(data.items) <= max_visible:
            data.offset = 0
        
        # Show current 12 items, set by offset
        else:

            # Shift current 12 items up by one; cursor is at the top (not the ultimate top)
            if data.item_index < data.offset:
                data.offset -= 1

            # Shift current 12 items down by one; cursor is at the bottom (not the ultimate bottom)
            elif data.item_index >= data.offset + max_visible:
                data.offset += 1

        # Update cursor
        data.cursor_pos[1] = (data.item_index - data.offset + 1) * pyg.tile_height

        # Keep cursor in the desired bounds
        if data.cursor_pos[1] == 0:
            data.cursor_pos[1] = pyg.tile_height
        elif data.cursor_pos[1] == (max_visible + 1) * pyg.tile_height:
            data.cursor_pos[1] += pyg.tile_height * 2
        elif data.cursor_pos[1] == (max_visible + 2) * pyg.tile_height:
            data.cursor_pos[1] += pyg.tile_height * 2

    def update_category(self, data, direction):
        """ Manages history for cursor position in each category. """
        
        # Check for new categories
        for filled_category in data.categories:
            if filled_category not in data.index_history.keys():
                data.index_history[filled_category] = [0, 0]
    
        # Remove old categories
        for saved_category in list(data.index_history.keys()):
            if saved_category not in data.categories:
                del data.index_history[saved_category]

        # Save last
        last_category                     = data.categories[data.category_index]
        data.index_history[last_category] = [data.item_index, data.offset]

        # Load new
        data.category_index = (data.category_index + direction) % len(data.categories)
        new_category        = data.categories[data.category_index]
        data.item_index, data.offset = data.index_history[new_category]

class InventoryMenu(ColumnMenu):
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """

        super().__init__()

        self.columns = [ColumnData('inv')]
        self.columns[0].cursor_pos = [0, 32]
        self.columns[0].detail_pos = lambda surface: [40, 32]
        self.active  = self.columns[0]

        self.details = lambda item: [item.name] + ["(equipped)" if item.equipped else ""]

    # Keys
    def key_INV(self):
        self.locked = not self.locked

    def key_DEV(self):
        self.locked = False
        session.pyg.overlay_state = 'dev'

    def key_ENTER(self):
        session.items.use(self.active.items[self.active.item_index])
        self.update_data(self.active)

    def key_PERIOD(self):
        session.items.drop(self.active.items[self.active.item_index])
        self.update_data(self.active)

class CatalogMenu(ColumnMenu):
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """

        pyg = session.pyg
        super().__init__()

        right_side = pyg.screen_width - pyg.tile_width
        self.columns = [ColumnData('dev')]
        self.columns[0].cursor_pos = [right_side, 32]
        self.columns[0].detail_pos = lambda surface: [right_side-surface.get_width()-8, 0]
        self.active  = self.columns[0]

        self.details = lambda item: [item.name]

    # Keys
    def key_DEV(self):
        self.locked = not self.locked

    def key_INV(self):
        self.locked = False
        session.pyg.overlay_state = 'inv'

    def key_ENTER(self):
        from environments import place_object
        pyg = session.pyg

        item = copy.deepcopy(self.active.items[self.active.item_index])
        
        # Note location
        x = int(session.player_obj.ent.X / pyg.tile_width)
        y = int(session.player_obj.ent.Y / pyg.tile_height)
        
        direction = self.active.ent.direction
        if direction == 'front':   y += 1
        elif direction == 'back':  y -= 1
        elif direction == 'right': x += 1
        elif direction == 'left':  x -= 1

        place_object(
            obj = item,
            loc = [x, y],
            env = self.active.ent.env)        

    def key_PERIOD(self):
        session.items.drop(self.active.items[self.active.item_index])
        self.update_data(self.active)

class ExchangeMenu(ColumnMenu):
    
    # Core
    def __init__(self):
        """ Manages inventory menu on the side of the screen. Allows item activation. """
        
        pyg = session.pyg
        super().__init__()

        right_side = pyg.screen_width - pyg.tile_width
        self.columns = [ColumnData('inv'), ColumnData('trade')]
        self.columns[0].cursor_pos = [0, 32]
        self.columns[0].detail_pos = lambda surface: [40, 0]
        self.columns[1].cursor_pos = [right_side, 32]
        self.columns[1].detail_pos = lambda surface: [right_side-surface.get_width()-8, 0]
        self.active = self.columns[0]
    
        self.details = lambda item: [item.name, f"⨋ {item.cost}"]

    # Keys
    def key_INV(self):
        if self.active == self.columns[1]:
            self.active = self.columns[0]

    def key_DEV(self):
        if self.active == self.columns[0]:
            self.active = self.columns[1]

    def key_ENTER(self):
        for data in self.columns:
            if self.active == data: owner = data.ent
            else:                   recipient = data.ent
        
        session.items.trade(self.active.items[self.active.item_index], owner, recipient)
        self.update_data(self.active)

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
        c = session.img.left_correct
        color = pygame.Color(c, c, c)
        
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

########################################################################################################################################################