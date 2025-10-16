########################################################################################################################################################
# Quests
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import copy

## Specific
import pygame
from   pygame.locals import *

## Local
import session

########################################################################################################################################################
# Classes
class BigMenu:

    def __init__(self, name, header, options, options_categories=None, position='top left', backgrounds=None):
        """ IMPORTANT. Creates cursor, background, and menu options, then returns index of choice.

            header             : string; top line of text
            options            : list of strings; menu choices
            options_categories : list of strings; categorization; same length as options
            position           : chooses layout preset """
        
        # Basics
        self.name               = name
        self.header             = header
        self.options            = options
        self.options_categories = options_categories
        self.position           = position
        self.backgrounds        = backgrounds
        
        # Initialize temporary data containers
        self.choice                   = 0                   # holds index of option pointed at by cursor
        self.choices_length           = len(self.options)-1 # number of choices
        self.options_categories_cache = ''                  # holds current category
        self.options_render           = self.options.copy()
        
        # Alter layout if categories are present
        if self.options_categories: 
            self.tab_x, self.tab_y = 70, 10
            self.options_categories_cache_2 = self.options_categories[0]
        else:
            self.tab_x, self.tab_y = 0, 0

        # Set initial position of each text type
        self.header_position = {
            'top left':     [5+32, 32],
            'center':       [session.pyg.screen_width//2, 85],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        self.cursor_position = {
            'top left':     [43+self.tab_x, 27+32+self.tab_y],
            'center':       [50, 300],
            'bottom left':  [50+self.tab_x, 65-self.tab_y],
            'bottom right': [60 ,70]}
        self.options_positions = {
            'top left':     [session.pyg.tile_height*3+self.tab_x-34, 22+32],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        self.category_positions = {
            'top left':     [session.pyg.tile_height+session.pyg.tile_height // 4, 22+32],
            'center':       [80, 300],
            'bottom left':  [5, 10],
            'bottom right': [60 ,70]}
        
        # Set mutable copies of text positions
        self.cursor_position_mutable    = copy.deepcopy(self.cursor_position[self.position])
        self.options_positions_mutable  = copy.deepcopy(self.options_positions[self.position])
        self.category_positions_mutable = copy.deepcopy(self.category_positions[self.position])
        
        # Initialize cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, session.pyg.gray, [(5, 3), (10, 7), (5, 11)], 0)
        
        # Initialize menu options
        self.header_render = session.pyg.font.render(self.header, True, session.pyg.white)
        for i in range(len(self.options)):
            color = session.pyg.gray
            self.options_render[i] = session.pyg.font.render(options[i], True, color)
        
        # GUI
        self.msg_toggle = None
        self.gui_toggle = None
        self.background_fade = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))
        
        # Other
        self.questlog_header = "                                                        QUESTLOG"

    def reset(self, name, header, options, options_categories, position):
        choice_cache = self.choice
        
        self.__init__(name, header, options, options_categories, position)
        
        self.choice = choice_cache
        self.cursor_position_mutable = self.cursor_position[self.position].copy()
        
        if self.header == self.questlog_header:
            self.cursor_position_mutable[1] += self.choice * 16
            
            # Handle additional spacing for categories
            if self.options_categories:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                for i in range(self.choice+1):  # Adjust for category shifts
                    if i > 0 and self.options_categories[i] != self.options_categories[i - 1]:
                        self.cursor_position_mutable[1] += self.tab_y

    def run(self):
        session.mech.movement_speed(toggle=False, custom=2)
        
        # Save gui settings before clearing the screen
        if self.msg_toggle is None:
            self.msg_toggle = session.pyg.msg_toggle
            self.gui_toggle = session.pyg.gui_toggle
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                
                # Navigation
                if event.key in session.pyg.key_UP:
                    if self.header == self.questlog_header: self.key_UP()
                elif event.key in session.pyg.key_DOWN:
                    if self.header == self.questlog_header: self.key_DOWN()
                
                # Handle selection
                elif event.key in (session.pyg.key_ENTER + session.pyg.key_LEFT + session.pyg.key_RIGHT):
                    
                    # >>TEXT MENU<<
                    if self.name == 'textbox':
                        session.pyg.overlay = None
                        return
                    
                    # >>QUESTLOG<<
                    elif self.name == 'questlog':
                        
                        # Selected quest
                        if self.header == self.questlog_header:
                            
                            # Select questlog or gardenlog
                            if session.pyg.game_state != 'play_garden':
                                self.selected_quest = session.player_obj.ent.questlog[list(session.player_obj.ent.questlog.keys())[self.choice]]
                            else:
                                self.selected_quest = session.player_obj.ent.gardenlog[list(session.player_obj.ent.gardenlog.keys())[self.choice]]
                            
                            # Set new values to be displayed
                            self.reset(
                                name               = 'questlog',
                                header             = self.selected_quest.name,
                                options            = self.selected_quest.content,
                                options_categories = self.selected_quest.categories,
                                position           = self.position)
                        
                        # Full questlog
                        else:
                            
                            # Select questlog or gardenlog
                            if session.pyg.game_state != 'play_garden': options = list(session.player_obj.ent.questlog.keys())
                            else:                               options = list(session.player_obj.ent.gardenlog.keys())
                            
                            self.reset(
                                name      = 'questlog',
                                header    = self.questlog_header,
                                options   = options,
                                options_categories = self.categories,
                                position = self.position)
                    
                else:
                    session.pyg.overlay     = None
                    session.pyg.msg_toggle  = self.msg_toggle
                    session.pyg.gui_toggle  = self.gui_toggle
                    self.msg_toggle = None
                    self.gui_toggle = None
                    return

        session.pyg.overlay = copy.copy(self.name)
        return

    def key_UP(self):

        # >>SELECT MENU ITEM<<        
        # Move cursor up
        self.cursor_position_mutable[1]     -= 16
        self.choice                         -= 1
        
        # Move to lowest option
        if self.choice < 0:
            self.choice                     = self.choices_length
            self.cursor_position_mutable[1] = self.cursor_position[self.position][1] + (len(self.options)-1) * 16
            if self.options_categories:
                self.cursor_position_mutable[1] += self.tab_y * (len(set(self.options_categories)) - 1)
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] -= self.tab_y

    def key_DOWN(self):

        # >>SELECT MENU ITEM<<        
        # Move cursor down
        self.cursor_position_mutable[1]     += 16
        self.choice                         += 1
        
        # Move to highest option
        if self.choice > self.choices_length:
            self.choice                     = 0
            self.cursor_position_mutable[1] = self.cursor_position[self.position][1]
            if self.options_categories:
                self.options_categories_cache_2 = self.options_categories[self.choice]
        
        # Move cursor again if there are categories
        elif self.options_categories:
            if self.options_categories[self.choice] != self.options_categories_cache_2:
                self.options_categories_cache_2 = self.options_categories[self.choice]
                self.cursor_position_mutable[1] += self.tab_y

    def init_questlog(self, env_name):
        """ Sets intro quests and updates menu. Only runs once when a new game is started.

            quests          : list of Quest objects
            quest_names     : list of strings
            categories      : list of strings; 'main' or 'side'
            main_quests     : list of Quest objects
            side_quests     : list of Quest objects
            selected_quest  : Quest object """
        
        # GUI text and Quest objects for each quest in the current log
        for quest in self.default_Quests(env_name):
            quest.content = quest.notes + quest.tasks
        
        self.update_questlog()

    def default_Quests(self, env_name):
        
        # Stage 0: 
        if env_name == 'garden':
        
            water = Quest(
                name='Leading a radix to water',
                notes=['These odd beings seem thirsty.',
                       'I should pour out some water for them.'],
                tasks=['☐ Empty your jug of water.',
                       '☐ Make a radix drink.'],
                category='Main')

            food = Quest(
                name='Fruit of the earth',
                notes=['Set out some food.'],
                tasks=['☐ Get a radix to eat.'],
                category='Main')
            
            building_shelter = Quest(
                name='Build a house',
                notes=['Shelter would be nice.'],
                tasks=['☐ Contruct walls.',
                       '☐ Set a floor.',
                       '☐ Decorate.'],
                category='Side')
            
            session.player_obj.ent.gardenlog = {
                water.name:             water,
                food.name:              food,
                building_shelter.name:  building_shelter}
            
            return water, food, building_shelter
        
        # Stage one: first dream
        elif env_name in [f'dungeon {n}' for n in range(10)]:
            
            surviving = Quest(
                name='Surviving \'til Dawn',
                notes=['/...huh? Where... am I?/',
                       'You find youself appeared as if an apparition.',
                       'Danger is afoot. How will you survive?'],
                tasks=['☐ Search for aid.',
                       '☐ Dig a tunnel.',
                       '☐ Escape.'],
                category='Main')
            
            session.player_obj.ent.envlog = {
                surviving.name: surviving}
            
            return surviving
        
        # Stage two: meeting the town
        elif env_name == 'overworld':
            
            gathering_supplies = Quest(
                name='Gathering supplies',
                notes=['My bag is nearly empty.',
                       'It would be good to have some items on hand.'],
                tasks=['☐ Collect 3 potions.',
                       '☐ Find a spare shovel.'],
                category='Main')
            
            finding_a_future = Quest(
                name='Finding a future',
                notes=['I should make my way into town.'],
                tasks=['☐ Wander east.'],
                category='Main')
            
            furnishing_a_home = Quest(
                name='Furnishing a home',
                notes=['My house is empty. Maybe I can spruce it up.'],
                tasks=['☐ Use the shovel to build new rooms.',
                       '☐ Drop items to be saved for later use.',
                       '☐ Look for anything interesting.'],
                category='Side')
            
            session.player_obj.ent.questlog = {
                gathering_supplies.name: gathering_supplies,
                finding_a_future.name:   finding_a_future,
                furnishing_a_home.name:  furnishing_a_home}
            
            return gathering_supplies, finding_a_future, furnishing_a_home
        
        else:
            print(env_name)
        
    def update_questlog(self, name=None, questlog=None):
        """ Updates and sorts main quests and side quests. """
        
        if not questlog: questlog = session.player_obj.ent.questlog
        
        ## Look for completed tasks and quests
        if name:
            quest = questlog[name]
            
            # Check off task
            if not quest.finished:
                for i in range(len(quest.tasks)):
                    task = quest.tasks[i]
                    if task[0] == "☐":
                        quest.tasks[i] = task.replace("☐", "☑")
                        session.pyg.update_gui(quest.tasks[i], session.pyg.violet)
                        quest.content = quest.notes + quest.tasks
                        break
            
            # Remove finished quests
            else:
                quest.tasks[-1] = quest.tasks[-1].replace("☐", "☑")
                session.pyg.update_gui(quest.tasks[-1], session.pyg.violet)
                session.pyg.update_gui(f"Quest complete: {quest.name}", session.pyg.violet)
                del questlog[quest.name]
        
        ## Sort quests
        self.main_quests = []
        self.side_quests = []
        self.categories  = []
        quests_cache     = {}
        
        # Find main quests
        for quest in questlog.values():
            if not quest.finished:
                if quest.category == 'Main':
                    quests_cache[quest.name] = quest
                    self.main_quests.append(quest)
                    self.categories.append(quest.category)
        
        # Find side quests
        for quest in questlog.values():
            if not quest.finished:
                if quest.category == 'Side':
                    quests_cache[quest.name] = quest
                    self.side_quests.append(quest)
                    self.categories.append(quest.category)
        questlog = quests_cache
        self.reset(
            name      = 'questlog',
            header    = "                                                        QUESTLOG", 
            options   = list(questlog.keys()),
            options_categories = self.categories,
            position = self.position)

    def render(self):
        
        from utilities import render_all

        # Apply background fade
        session.pyg.screen.blit(self.background_fade, (0, 0))
        
        ## Update tiles
        if self.msg_toggle is not None:
            session.pyg.msg_toggle = False
            session.pyg.gui_toggle = False
        session.pyg.update_gui()
        render_all()
        if session.player_obj.ent.env.name != 'garden':
            for image, (X, Y) in session.player_obj.ent.env.weather.render():
                session.pyg.display.blit(image, (X, Y))
        
        ## Render background
        fill_width  = session.pyg.tile_width  * 18
        fill_height = session.pyg.tile_height * 13
        self.backdrop = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.backdrop.fill((0, 0, 0, 128))
        session.pyg.screen.blit(self.backdrop, (32, 32))
        
        # Render border
        self.cursor_border = pygame.Surface((fill_width, fill_height), pygame.SRCALPHA)
        self.backdrop.fill((0, 0, 0, 128))
        pygame.draw.polygon(
            self.cursor_border, 
            session.pyg.gray,
            [(0, 0),
             (fill_width-1, 0),
             (fill_width-1, fill_height-1),
             (0, fill_height-1)], 1)
        session.pyg.screen.blit(self.cursor_border, (32, 32))
        
        # Render header and cursor
        session.pyg.screen.blit(self.header_render, self.header_position[self.position])
        if self.header == self.questlog_header:
            session.pyg.screen.blit(self.cursor_img, self.cursor_position_mutable)
        
        ## Render categories and options
        for i in range(len(self.options_render)):
            
            # Render category text if it is not present 
            if self.options_categories:
                if self.options_categories[i] != self.options_categories_cache:
                    self.options_categories_cache = self.options_categories[i]
                    text = session.pyg.font.render(f'{self.options_categories_cache.lower()}', True, session.pyg.gray)
                    self.options_positions_mutable[1] += self.tab_y
                    session.pyg.screen.blit(text, (self.category_positions_mutable[0], self.options_positions_mutable[1]))
                
            # Render option text
            session.pyg.screen.blit(self.options_render[i], self.options_positions_mutable)
            self.options_positions_mutable[1] += session.pyg.tile_height//2
        self.options_positions_mutable = self.options_positions[self.position].copy()
        self.category_positions_mutable = self.category_positions[self.position].copy()
        pygame.display.flip()

class QuestMenu:

    def __init__(self):
        """ Hosts a menu for the questlog, but it's also the questlog itself.
            Toggles between quest names and details.
        
            Parameters
            ----------
            overlay    : str in ['questlog', 'gardenlog']; game state; toggles the set of quests
            mode       : str in ['log', 'quest']; toggles individual quest view
            options    : list of str
            categories : list of str
        """
        
        #########################################################
        # Parameters        
        ## Basics
        self.overlay     = 'questlog'
        self.mode        = 'log'
        self.header      = 'questlog'
        self.header_dict = {
            'questlog': "                                                        QUESTLOG",
            'gardenlog': "                                                      GARDENLOG"}

        self.options    = None
        self.categories = None

        ## Positions
        self.choice         = 0
        self.header_pos     = (37, 32)
        self.options_pos    = None
        self.categories_pos = None
        self.backdrop_pos   = (32, 32)
        self.cursor_pos     = (113, 69)

        ## Other
        self.backdrop_size = (32*18, 32*13)
        
        #########################################################
        # Surface initialization
        ## Background
        self.background_fade = pygame.Surface((session.pyg.screen_width, session.pyg.screen_height), pygame.SRCALPHA)
        self.background_fade.fill((0, 0, 0, 50))
        
        ## Backdrop
        self.backdrop = pygame.Surface(self.backdrop_size, pygame.SRCALPHA)
        self.backdrop.fill((0, 0, 0, 128))

        self.border = pygame.Surface(self.backdrop_size, pygame.SRCALPHA)
        pygame.draw.polygon(
            surface = self.border, 
            color   = session.pyg.gray,
            points = [
                (0,                       0),
                (self.backdrop_size[0]-1, 0),
                (self.backdrop_size[0]-1, self.backdrop_size[1]-1),
                (0,                       self.backdrop_size[1]-1)],
            width = 1)
        
        ## Cursor
        self.cursor_img = pygame.Surface((16, 16)).convert()
        self.cursor_img.set_colorkey(self.cursor_img.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_img, session.pyg.gray, [(5, 3), (10, 7), (5, 11)], 0)

    def run(self):
        session.mech.movement_speed(toggle=False, custom=2)
        
        #########################################################
        # Save GUI settings
        self.msg_toggle = session.pyg.msg_toggle
        self.gui_toggle = session.pyg.gui_toggle
        
        if self.overlay != session.pyg.overlay:
            self.overlay = session.pyg.overlay
            self.choice  = 0
            self.update_questlog()
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                
                #########################################################
                # Handle input
                ## Move cursor
                if self.mode == 'log':
                    if event.key in session.pyg.key_UP:     self.key_UP()
                    elif event.key in session.pyg.key_DOWN: self.key_DOWN()
                
                ## Select quest to view
                if event.key in [*session.pyg.key_ENTER, *session.pyg.key_RIGHT]:
                    self.mode = 'quest'
                    self.update_questlog()
                
                ## Select full questlog to view
                elif event.key in [*session.pyg.key_ENTER, *session.pyg.key_LEFT]:
                    self.mode = 'log'
                    self.update_questlog()
                
                ## Return to game
                elif event.key not in session.pyg.key_movement:
                    session.pyg.msg_toggle = self.msg_toggle
                    session.pyg.gui_toggle = self.gui_toggle
                    session.pyg.overlay    = None
                    return

        session.pyg.overlay = self.overlay
        return

    def key_UP(self):
        self.choice = (self.choice - 1) % len(self.options)
        
    def key_DOWN(self):
        self.choice = (self.choice + 1) % len(self.options)

    def init_questlog(self, env_name):
        """ Sets intro quests and updates menu. Only runs once when a new game is started.

            quests          : list of Quest objects
            quest_names     : list of strings
            categories      : list of strings; 'main' or 'side'
            main_quests     : list of Quest objects
            side_quests     : list of Quest objects
            selected_quest  : Quest object """

        # GUI text and Quest objects for each quest in the current log
        for quest in self.default_Quests(env_name):
            quest.content = quest.notes + quest.tasks
        
        self.update_questlog()

    def default_Quests(self, env_name):
        
        # Stage 0: 
        if env_name == 'garden':
        
            water = Quest(
                name='Leading a radix to water',
                notes=['These odd beings seem thirsty.',
                       'I should pour out some water for them.'],
                tasks=['☐ Empty your jug of water.',
                       '☐ Make a radix drink.'],
                category='Main')

            food = Quest(
                name='Fruit of the earth',
                notes=['Set out some food.'],
                tasks=['☐ Get a radix to eat.'],
                category='Main')
            
            building_shelter = Quest(
                name='Build a house',
                notes=['Shelter would be nice.'],
                tasks=['☐ Contruct walls.',
                       '☐ Set a floor.',
                       '☐ Decorate.'],
                category='Side')
            
            session.player_obj.ent.gardenlog = {
                water.name:             water,
                food.name:              food,
                building_shelter.name:  building_shelter}
            
            return water, food, building_shelter
        
        # Stage one: first dream
        elif env_name in [f'dungeon {n}' for n in range(10)]:
            
            surviving = Quest(
                name='Surviving \'til Dawn',
                notes=['/...huh? Where... am I?/',
                       'You find youself appeared as if an apparition.',
                       'Danger is afoot. How will you survive?'],
                tasks=['☐ Search for aid.',
                       '☐ Dig a tunnel.',
                       '☐ Escape.'],
                category='Main')
            
            session.player_obj.ent.envlog = {
                surviving.name: surviving}
            
            return surviving
        
        # Stage two: meeting the town
        elif env_name == 'overworld':
            
            gathering_supplies = Quest(
                name='Gathering supplies',
                notes=['My bag is nearly empty.',
                       'It would be good to have some items on hand.'],
                tasks=['☐ Collect 3 potions.',
                       '☐ Find a spare shovel.'],
                category='Main')
            
            finding_a_future = Quest(
                name='Finding a future',
                notes=['I should make my way into town.'],
                tasks=['☐ Wander east.'],
                category='Main')
            
            furnishing_a_home = Quest(
                name='Furnishing a home',
                notes=['My house is empty. Maybe I can spruce it up.'],
                tasks=['☐ Use the shovel to build new rooms.',
                       '☐ Drop items to be saved for later use.',
                       '☐ Look for anything interesting.'],
                category='Side')
            
            session.player_obj.ent.questlog = {
                gathering_supplies.name: gathering_supplies,
                finding_a_future.name:   finding_a_future,
                furnishing_a_home.name:  furnishing_a_home}
            
            return gathering_supplies, finding_a_future, furnishing_a_home
        
        else:
            print(env_name)

    def check_tasks(self, name, log):
        quest = log[name]

        # Check off task
        if not quest.finished:
            for i in range(len(quest.tasks)):
                task = quest.tasks[i]
                if task[0] == "☐":
                    quest.tasks[i] = task.replace("☐", "☑")
                    session.pyg.update_gui(quest.tasks[i], session.pyg.violet)
                    quest.content = quest.notes + quest.tasks
                    break
        
        # Remove finished quests
        else:
            quest.tasks[-1] = quest.tasks[-1].replace("☐", "☑")
            session.pyg.update_gui(quest.tasks[-1], session.pyg.violet)
            session.pyg.update_gui(f"Quest complete: {quest.name}", session.pyg.violet)
            del log[quest.name]
        
    def update_questlog(self):
        """ Updates and sorts main quests and side quests. """

        if self.overlay == 'questlog':    log = session.player_obj.ent.questlog
        elif self.overlay == 'gardenlog': log = session.player_obj.ent.gardenlog

        ## Look for completed tasks and quests
        if self.mode == 'quest':
            quest = list(log.keys())[self.choice]
            
            self.header = log[list(log.keys())[self.choice]].name
            self.options = log[list(log.keys())[self.choice]].content
            self.categories = log[list(log.keys())[self.choice]].categories

        elif self.mode == 'log':
            self.header = self.header_dict[self.overlay]
            self.options = list(log.keys())
            self.categories = []

            ## Sort quests
            self.main_quests = []
            self.side_quests = []
            
            # Find main quests
            for quest in log.values():
                if not quest.finished:
                    if quest.category == 'Main':
                        self.main_quests.append(quest)
                        self.categories.append(quest.category)
            
            # Find side quests
            for quest in log.values():
                if not quest.finished:
                    if quest.category == 'Side':
                        self.side_quests.append(quest)
                        self.categories.append(quest.category)

        self.options_pos       = [(136, 67+32*i) for i in range(len(self.options))]
        self.categories_pos    = [(40, 67+32*i) for i in range(len(self.categories))]
        self.options_render    = [session.pyg.font.render(option, True, session.pyg.gray) for option in self.options]
        self.header_render     = session.pyg.font.render(self.header, True, session.pyg.white)
        self.categories_render = [session.pyg.font.render(f'{category.lower()}', True, session.pyg.gray) for category in self.categories]
                    
    def render(self):
        
        # Clear GUI
        session.pyg.msg_toggle = False
        session.pyg.gui_toggle = False
        session.pyg.update_gui()
        
        # Backdrop
        session.pyg.screen.blit(self.background_fade, (0, 0))
        session.pyg.screen.blit(self.backdrop,        self.backdrop_pos)
        session.pyg.screen.blit(self.border,          self.backdrop_pos)
        
        # Header
        session.pyg.screen.blit(self.header_render, self.header_pos)

        # Options and categories
        categories = []
        for i in range(len(self.options_render)):

            # Shift position for new category
            options_pos    = [self.options_pos[i][0],    self.options_pos[i][1]    + 32*len(categories)]
            categories_pos = [self.categories_pos[i][0], self.categories_pos[i][1] + 32*len(categories)]
            if i >= 1:
                if self.categories[i] != self.categories[i-1]:
                    options_pos[1]    += 32
                    categories_pos[1] += 32
                    categories.append((i, self.categories[i]))

                    # Only render each category once
                    session.pyg.screen.blit(self.categories_render[i], categories_pos)
            else:   session.pyg.screen.blit(self.categories_render[i], categories_pos)
            
            # Render option
            session.pyg.screen.blit(self.options_render[i],    options_pos)
        
        # Cursor
        if self.mode == 'log':

            # Shift position for current category
            cursor_pos = [self.cursor_pos[0], self.cursor_pos[1] + 32*self.choice]
            for i in range(len(categories)):
                if self.choice >= categories[i][0]:
                    cursor_pos[1] += 32*(i+1)
                    break
            session.pyg.screen.blit(self.cursor_img, cursor_pos)
        
        pygame.display.flip()

class Quest:
    """ Holds quest information. """

    def __init__(self, name, notes, tasks, category, function=None):
        """ name     : string; title of quest
            content  : list of strings; notes and checklists
            category : string in ['main', 'side']; organizes quest priority
            finished : Boolean; notes if the quest has been completed """

        self.name     = name
        self.notes    = notes
        self.tasks    = tasks
        self.category = category
        self.finished = False
        self.ent      = None
        
        self.categories = ['Notes' for i in range(len(notes))]
        self.categories += ['Tasks' for i in range(len(tasks))]
        
        self.function = function

    def dialogue(self, ent):
        """ Sends dialogue from the entity to the quest's function, then updates
            the entity's dialogue if needed. """
        
        message = self.function(ent, ent.dialogue)
        if message:
            return message

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

class QuestTemplate:
    """ Steps
        -----
        1. Write a questline class containing each subquest
        
        2. Initialize the questline class externally.
            session.player_obj.questlines['Bloodkin'] = Bloodkin()

        3. Assign a subquest to an object
            obj        = create_item('scroll of death')
            obj.name   = 'mysterious note'
            obj.effect = self.mysterious_note
            place_object(obj, loc, env)
        
        4. Activate the quest object via Item.use()
        
        5. Complete tasks by sending dialogue and an entity from Entity.move()

        6. Send new dialogue to entity from Quest.dialogue() or complete the quest """

    def __init__(self):
        
        # Optional parameters
        pass
    
    def subquest(self, dialogue=None, ent=None):

        from items_entities import create_NPC

        # Run something upon activating an effect
        if not dialogue and not ent:
            note_text = ["line 1", "line 2", "line 3"]
            #QuestMenu(header="header", options=note_text)
        
        # Generate the Quest object
        if "quest name" not in session.player_obj.ent.questlog.keys():
            quest = Quest(
                name     = 'quest name',
                notes    = ["description", "", "details"],
                tasks    = ["☐ Task."],
                category = 'Main or Side',
                function = self)
            
            # Initialize dialogue
            quest.dialogue_list = ["first message", "second message"]
            quest.content = quest.notes + quest.tasks
            
            # Add quest to questlog
            session.player_obj.ent.questlog[quest.name] = quest
            session.questlog_obj.update_questlog()
            session.pyg.update_gui("Quest added!", session.pyg.violet)
            
            # Generate main characters
            if 'NPC name' not in session.player_obj.ents.keys():
                create_NPC('NPC name')
            session.player_obj.ents['NPC name'].quest = quest
            session.player_obj.ents['NPC name'].dialogue = "NPC name: ..."
        
        else:
            
            # Remove last piece of dialogue and log progression
            ent.quest.dialogue_list.remove(dialogue)
            quest_lvl = 9 - len(ent.quest.dialogue_list)
            
            # Check off a task
            if quest_lvl == 1:
                session.questlog_obj.update_questlog(name='quest name')
            
            # Complete quest
            if quest_lvl == 9:
                session.player_obj.ent.questlog['quest name'].finished = True
                session.questlog_obj.update_questlog(name='quest name')
                
                # Place object to trigger next subquest
                pass
            
            # Return next piece of dialogue if not complete
            if ent.quest.dialogue_list:
                return ent.quest.dialogue_list[0]

class Bloodkin:
    """ Bloodkin quest.
        
        Summary
        -------
        The Bloodkin is a religion that worships the Sigil of Thanato, which is a blood-drawn rune with cryptic and sentient powers.
        They are led by Kyrio, who sentences to death anybody outside of the Bloodkin that know of the Sigil, as well as all kin that speak of it.
        The Sigil can be used for many purposes.
            - A weapon endowed by it will drip with blood; anyone killed in a dream by such a weapon with perish in the Overworld.
            - Any corpse painted with the Sigil will rise and attack anything in sight, stopping only upon second death.
            - When applied to a scroll, it yields the Scroll of Death, which is the only means of accessing the Abyssal Gallery.
        
        Events and triggers
        -------------------
        1.  The quest begins when the player first encounters a Scroll of Death.
            Upon use, the player enters the Abyssal Gallery and swiftly dies from the residing creatures.
        2a. The next possible step is a direct encounter with Kyrio. 
            Disquised as an aging trader, he indirectly leads the player to a path of assured demise. """

    def __init__(self):
        
        # One string for each subquest
        self.path_vals = []

    def making_a_friend(self, ent, dialogue):
        """ Manages friend quest, including initialization and dialogue. """

        from items_entities import create_item, Effect
        from mechanics import place_object

        # Initialization
        if dialogue == "Walk into something to interact with it, or press Enter (↲) if you're above it.":
            ent.quest.dialogue_list = [
                "Walk into something to interact with it, or press Enter (↲) if you're above it.",
                "Press Slash (/) to view the main menu. Try it again to return!",
                "Use Plus (+) to zoom in, or use Minus (-) to zoom out.",
                "Press Four (4) to open your inventory. Period (.) drops, and Enter activates!",
                "Try holding Zero (0) to enter combos. Nine (9) can be used to view details.",
                "Check out Options in the Main Menu!"]
        
        # Increase friendship level
        ent.quest.dialogue_list.remove(dialogue)
        friend_level = 9 - len(ent.quest.dialogue_list)
        
        # First checkpoint
        if friend_level == 1:
            session.questlog_obj.update_questlog(name="Making a friend")
        
        # Complete quest
        if friend_level == 9:
            
            session.player_obj.ent.questlog['Making a friend'].finished = True
            session.questlog_obj.update_questlog(name="Making a friend")
            session.pyg.update_gui("Woah! What's that?", session.pyg.violet)
            
            x = lambda dX : int((session.player_obj.ent.X + dX)/session.pyg.tile_width)
            y = lambda dY : int((session.player_obj.ent.Y + dY)/session.pyg.tile_height)
            
            # Find a nearby space to place the mysterious note
            found = False
            for i in range(3):
                if found: break
                x_test = x(session.pyg.tile_width*(i-1))
                for j in range(3):
                    y_test = y(session.pyg.tile_height*(j-1))
                    if not session.player_obj.ent.env.map[x_test][y_test].entity:
                        session.player_obj.cache = False
                        
                        obj = create_item('scroll of death')
                        obj.name = 'mysterious note'
                        obj.effect = Effect(
                            name          = 'mysterious note',
                            img_names     = ['scrolls', 'open'],
                            function      = self.mysterious_note,
                            trigger       = 'active',
                            sequence      = None,
                            cooldown_time = 0,
                            other         = None)
                        place_object(
                            obj = obj,
                            loc = [x_test, y_test],
                            env = ent.env)
                        
                        found = True
                        break
        
        if ent.quest.dialogue_list:
            return ent.quest.dialogue_list[0]

    def mysterious_note(self, ent=None, dialogue=None):
        """ Manages friend quest, including initialization and dialogue.
            Upon finding a scroll of death, the player must first learn to descipher it.
            People in the town seem to suggest that the church is involved.
            The best lead is Kyrio, who is secretly a leader of the church.
            
            Church: Coax a lizard to the altar (by following). """
        
        from utilities import Textbox
        
        # Read the note
        if not dialogue:
            note_text = ["ξνμλ λξ ξλι ξγθιβξ ξ θθ.", "Ηκρσ σρσ λβνξθι νθ.", "Ψπθ αβνιθ πθμ."]
            session.textbox = Textbox(
                name     = 'textbox',
                header   = "mysterious note",
                options  = note_text,
                position = 'top left')
            session.pyg.overlay = 'textbox'
        
        # Initialize quest and characters
        if 'Learning a language' not in session.player_obj.ent.questlog.keys():
            quest = Quest(
                name = 'Learning a language',
                notes = [
                    "A mysterious note. Someone in town might know what it means.",
                    "",
                    "ξνμλ λξ ξλι ξγθιβξ ξ θθ,", "Ηκρσ σρσ λβνξθι νθ,", "Ψπθ αβνιθ πθμ."],
                tasks = [
                    "☐ See if anyone in town can decipher the note."],
                category = 'Main',
                function = session.player_obj.ent.questlines['Bloodkin'].mysterious_note)

            quest.content = quest.notes + quest.tasks
            session.player_obj.ent.questlog[quest.name] = quest
            session.questlog_obj.update_questlog()
            session.pyg.update_gui(f"Quest added: {quest.name}", session.pyg.violet)
            
            self.names_list, self.dialogue_list, self.progress_list = self.set_entities(quest)
        
        # Update quest
        if dialogue and ent:
            quest = session.player_obj.ents['Kyrio'].quest
            
            # Look for checkpoints
            for i in range(len(self.names_list)):
                if ent.name == self.names_list[i]:
                
                    # Check for task completion
                    if self.progress_list[i] < 3:
                        self.dialogue_list[i].remove(dialogue)
                        self.progress_list[i] = 3 - len(self.dialogue_list[i])
                    
                        # Provide next piece of dialogue
                        if self.dialogue_list[i]:
                            return self.dialogue_list[i][0]
            
            # Complete quest
            if (self.progress_list[0] == 3) and (self.progress_list[1] == 3):
                self.path_vals.append('religion')
                session.player_obj.ent.questlog['Learning a language'].finished = True
                session.questlog_obj.update_questlog(name='Learning a language')
            
            elif self.progress_list[2] == 3:
                self.path_vals.append('drugs')
                session.player_obj.ent.questlog['Learning a language'].finished = True
                session.questlog_obj.update_questlog(name='Learning a language')

    def set_entities(self, quest):

        from items_entities import create_NPC

        names_list, dialogue_list, progress_list = [], [], []
        
        # Generate characters and dialogue
        if 'Kyrio' not in session.player_obj.ents.keys(): session.player_obj.ents['Kyrio'] = create_NPC('Kyrio')
        quest.Kyrio_dialogue = [
            "Kyrio: Huh? A glyph of some sort? I know nothing of such things.",
            "Kyrio: Rather inquisitive, are you? Never turns out well.",
            "Kyrio: Fine, yes, my brother might know. I am busy."]
        quest.Kyrio_progress              = 0
        session.player_obj.ents['Kyrio'].quest    = quest
        session.player_obj.ents['Kyrio'].dialogue = quest.Kyrio_dialogue[0]
        names_list.append('Kyrio')
        dialogue_list.append(quest.Kyrio_dialogue)
        progress_list.append(quest.Kyrio_progress)
        
        if 'Kapno' not in session.player_obj.ents.keys(): session.player_obj.ents['Kapno'] = create_NPC('Kapno')
        quest.Kapno_dialogue = [
            "Kapno: Exquisite! Where was this symbol found?",
            "Kapno: It certainly peaks my interest. Strange occurances are frequent as of late.",
            "Kapno: Let me know if you find anything else, and check out my shop if you need anything."]
        quest.Kapno_progress              = 0
        session.player_obj.ents['Kapno'].quest    = quest
        session.player_obj.ents['Kapno'].dialogue = quest.Kapno_dialogue[0]
        names_list.append('Kapno')
        dialogue_list.append(quest.Kapno_dialogue)
        progress_list.append(quest.Kapno_progress)
        
        if 'Oxi' not in session.player_obj.ents.keys(): session.player_obj.ents['Oxi'] = create_NPC('Oxi')
        quest.Oxi_dialogue = [
            "Oxi: What do you want? You selling something?",
            "Oxi: Hey! Don't just wave the arcane around like that.",
            "Oxi: Yeah, I've seen it before. Come find me later tonight... we can talk then."]
        quest.Oxi_progress              = 0
        session.player_obj.ents['Oxi'].quest    = quest
        session.player_obj.ents['Oxi'].dialogue = quest.Oxi_dialogue[0]
        names_list.append('Oxi')
        dialogue_list.append(quest.Oxi_dialogue)
        progress_list.append(quest.Oxi_progress)
        
        if 'Erasti' not in session.player_obj.ents.keys(): session.player_obj.ents['Erasti'] = create_NPC('Erasti')
        quest.Erasti_dialogue = [
            "Erasti: Oh...! Hi!",
            "Erasti: That symbol... have you seen it before? It gives me an eerie sense of déjà vu.",
            "Erasti: I saw Kyrio with something like that once. Or maybe it was a dream..."]
        quest.Erasti_progress              = 0
        session.player_obj.ents['Erasti'].quest    = quest
        session.player_obj.ents['Erasti'].dialogue = quest.Erasti_dialogue[0]
        names_list.append('Erasti')
        dialogue_list.append(quest.Erasti_dialogue)
        progress_list.append(quest.Erasti_progress)
    
        if 'Merci' not in session.player_obj.ents.keys(): session.player_obj.ents['Merci'] = create_NPC('Merci')
        quest.Merci_dialogue = [
            "Merci: Welcome! ...are you not here for my merchandise?",
            "Merci: I do not deal in the occult, so I will be of no help to you. Sorry.",
            "Merci: Oxi is shady enough... he seems like the type to ask."]
        quest.Merci_progress              = 0
        session.player_obj.ents['Merci'].quest    = quest
        session.player_obj.ents['Merci'].dialogue = quest.Merci_dialogue[0]
        names_list.append('Merci')
        dialogue_list.append(quest.Merci_dialogue)
        progress_list.append(quest.Merci_progress)
    
        return names_list, dialogue_list, progress_list

class FriendlyFaces:
    """ FriendlyFaces quest.
        
        Summary
        -------
        Meet the town. """

    def making_an_introduction(self, ent=None, dialogue=None):
        
        # Initialize quest and characters
        if 'Making an introduction' not in session.player_obj.ent.questlog.keys():
            quest = Quest(
                name = 'Making an introduction',
                notes = ["I should get to know my neighbors."],
                tasks = ["☐ Talk to people."],
                category = 'Main',
                function = session.player_obj.ent.questlines['Friendly Faces'].making_an_introduction)

            quest.content = quest.notes + quest.tasks
            session.player_obj.ent.questlog[quest.name] = quest
            session.questlog_obj.update_questlog()
            
            self.names_list, self.dialogue_list, self.progress_list = self.set_entities(quest)
        
        # Update quest
        if dialogue and ent:
            quest = session.player_obj.ents[ent.name].quest
            
            # Look for checkpoints
            for i in range(len(self.names_list)):
                if ent.name == self.names_list[i]:
                
                    # Check for task completion
                    if self.progress_list[i] < 1:
                        self.dialogue_list[i].remove(dialogue)
                        self.progress_list[i] = 1
            
            # Complete quest
            if 0 not in self.progress_list:
                session.player_obj.ent.questlog['Making an introduction'].finished = True
                session.questlog_obj.update_questlog(name='Making an introduction')

    def set_entities(self, quest):

        from items_entities import create_NPC

        names_list, dialogue_list, progress_list = [], [], []
        
        # Generate characters and dialogue
        if 'Kyrio' not in session.player_obj.ents.keys(): session.player_obj.ents['Kyrio'] = create_NPC('Kyrio')
        quest.Kyrio_dialogue = ["Kyrio: ... Yes, hello. Do you need something?"]
        quest.Kyrio_progress              = 0
        session.player_obj.ents['Kyrio'].quest    = quest
        session.player_obj.ents['Kyrio'].dialogue = quest.Kyrio_dialogue[0]
        names_list.append('Kyrio')
        dialogue_list.append(quest.Kyrio_dialogue)
        progress_list.append(quest.Kyrio_progress)
        
        if 'Kapno' not in session.player_obj.ents.keys(): session.player_obj.ents['Kapno'] = create_NPC('Kapno')
        quest.Kapno_dialogue = ["Kapno: Hello! I run a general store. Looking for anything specific?"]
        quest.Kapno_progress              = 0
        session.player_obj.ents['Kapno'].quest    = quest
        session.player_obj.ents['Kapno'].dialogue = quest.Kapno_dialogue[0]
        names_list.append('Kapno')
        dialogue_list.append(quest.Kapno_dialogue)
        progress_list.append(quest.Kapno_progress)
        
        if 'Oxi' not in session.player_obj.ents.keys(): session.player_obj.ents['Oxi'] = create_NPC('Oxi')
        quest.Oxi_dialogue = ["Oxi: Can't sleep? I might have something for that. Come find me at night."]
        quest.Oxi_progress              = 0
        session.player_obj.ents['Oxi'].quest    = quest
        session.player_obj.ents['Oxi'].dialogue = quest.Oxi_dialogue[0]
        names_list.append('Oxi')
        dialogue_list.append(quest.Oxi_dialogue)
        progress_list.append(quest.Oxi_progress)
        
        if 'Erasti' not in session.player_obj.ents.keys(): session.player_obj.ents['Erasti'] = create_NPC('Erasti')
        quest.Erasti_dialogue = ["Erasti: Oh! My name is Erasi. Have we met?"]
        quest.Erasti_progress              = 0
        session.player_obj.ents['Erasti'].quest    = quest
        session.player_obj.ents['Erasti'].dialogue = quest.Erasti_dialogue[0]
        names_list.append('Erasti')
        dialogue_list.append(quest.Erasti_dialogue)
        progress_list.append(quest.Erasti_progress)
    
        if 'Merci' not in session.player_obj.ents.keys(): session.player_obj.ents['Merci'] = create_NPC('Merci')
        quest.Merci_dialogue = ["Merci: Welcome! ...are you not here for my merchandise?"]
        quest.Merci_progress              = 0
        session.player_obj.ents['Merci'].quest    = quest
        session.player_obj.ents['Merci'].dialogue = quest.Merci_dialogue[0]
        names_list.append('Merci')
        dialogue_list.append(quest.Merci_dialogue)
        progress_list.append(quest.Merci_progress)
    
        if 'Aya' not in session.player_obj.ents.keys(): session.player_obj.ents['Aya'] = create_NPC('Aya')
        quest.Aya_dialogue = ["Aya: You look like you can handle a blade... Oh! Did I say that out loud?"]
        quest.Aya_progress              = 0
        session.player_obj.ents['Aya'].quest    = quest
        session.player_obj.ents['Aya'].dialogue = quest.Aya_dialogue[0]
        names_list.append('Aya')
        dialogue_list.append(quest.Aya_dialogue)
        progress_list.append(quest.Aya_progress)
    
        if 'Zung' not in session.player_obj.ents.keys(): session.player_obj.ents['Zung'] = create_NPC('Zung')
        quest.Zung_dialogue = ["Zung: Hey, good to meet you. See you around."]
        quest.Zung_progress              = 0
        session.player_obj.ents['Zung'].quest    = quest
        session.player_obj.ents['Zung'].dialogue = quest.Zung_dialogue[0]
        names_list.append('Zung')
        dialogue_list.append(quest.Zung_dialogue)
        progress_list.append(quest.Zung_progress)
    
        if 'Lilao' not in session.player_obj.ents.keys(): session.player_obj.ents['Lilao'] = create_NPC('Lilao')
        quest.Lilao_dialogue = ["Lilao: Huh?"]
        quest.Lilao_progress              = 0
        session.player_obj.ents['Lilao'].quest    = quest
        session.player_obj.ents['Lilao'].dialogue = quest.Lilao_dialogue[0]
        names_list.append('Lilao')
        dialogue_list.append(quest.Lilao_dialogue)
        progress_list.append(quest.Lilao_progress)
    
        return names_list, dialogue_list, progress_list

########################################################################################################################################################
# Tools

########################################################################################################################################################