########################################################################################################################################################
# Quests
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard
import random

## Specific
import pygame
from   pygame.locals import *

## Local
import session
from data_management import load_json

########################################################################################################################################################
# Classes
class QuestMenu:

    # Core
    def __init__(self):
        """ Hosts a menu for the questlog. Toggles between quest names and details.
        
            Parameters
            ----------
            area       : str; name of the current set of environments; toggles the set of quests
            mode       : str in ['log', 'quest']; toggles individual quest view
            choices    : list of str
            categories : list of str
        """
        
        pyg = session.pyg

        #########################################################
        # Parameters        
        ## Basics
        self.area   = None
        self.mode   = 'log'
        self.header = "QUESTLOG"
        
        self.choices    = [] # set later
        self.categories = [] # set later

        ## Positions
        self.spacing      = 24
        self.header_pos   = (0,   32) # set later (centered)
        self.choice_pos   = (136, 67) # top choice
        self.category_pos = (40,  67) # top choice
        self.cursor_pos   = (120, 67) # top choice
        self.backdrop_pos = (32,  32)

        ## Other
        self.choice          = 0
        self.background_size = (pyg.screen_width, pyg.screen_height)
        self.backdrop_size   = (32*18, 32*13)
        self.gui_cache = False
        self.msg_cache = False

        self.cooldown_time   = 1
        
        #########################################################
        # Surface initialization
        ## Background
        self.background_surface = pygame.Surface(self.background_size, pygame.SRCALPHA)
        self.background_surface.fill((0, 0, 0, 50))
        
        ## Backdrop
        self.backdrop_surface = pygame.Surface(self.backdrop_size, pygame.SRCALPHA)
        self.backdrop_surface.fill((0, 0, 0, 128))

        ## Border
        self.border_surface = pygame.Surface(self.backdrop_size, pygame.SRCALPHA)
        pygame.draw.polygon(
            surface = self.border_surface, 
            color   = pyg.gray,
            points  = [
                (0,                       0),
                (self.backdrop_size[0]-1, 0),
                (self.backdrop_size[0]-1, self.backdrop_size[1]-1),
                (0,                       self.backdrop_size[1]-1)],
            width = 1)
        
        ## header
        self.header_surface = pyg.font.render(self.header, True, pyg.white)
        self.header_pos     = (int((pyg.screen_width - self.header_surface.get_width())/2), self.header_pos[1])

        ## Cursor
        self.cursor_surface = pygame.Surface((16, 16)).convert()
        self.cursor_surface.set_colorkey(self.cursor_surface.get_at((0, 0)))
        pygame.draw.polygon(self.cursor_surface, pyg.gray, [(5, 8), (10, 12), (5, 16)], 0)

    def run(self):
        pyg = session.pyg

        #########################################################
        # Initialize
        ## Switch between questlogs for different areas
        if self.area != session.player_obj.ent.env.area.name:
            self.area   = session.player_obj.ent.env.area.name
            self.choice = 0
        self.update_questlog()

        ## Set navigation speed
        session.effects.movement_speed(toggle=False, custom=2)
        
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
                # Switch mode
                ## Switch to quest mode
                elif event.key in pyg.key_RIGHT:
                    self.key_RIGHT()
                
                ## Switch to log mode
                elif event.key in pyg.key_LEFT:
                    self.key_LEFT()
                
                ## Switch mode (either direction)
                elif event.key in pyg.key_ENTER:
                    self.key_ENTER()
                
            elif event.type == pygame.KEYUP:

                #########################################################
                # Return to game
                if event.key in pyg.key_BACK:
                    self.key_BACK()
                    return

        pyg.overlay_state = 'questlog'
        return

    def render(self):
        pyg = session.pyg

        #########################################################
        # Render surfaces
        ## Backdrop
        pyg.overlay_queue.append([self.background_surface, (0, 0)])
        pyg.overlay_queue.append([self.backdrop_surface,   self.backdrop_pos])
        pyg.overlay_queue.append([self.border_surface,     self.backdrop_pos])

        ## Header
        pyg.overlay_queue.append([self.header_surface, self.header_pos])

        ## Choices, categories, and cursor
        categories, category_toggle = [], True
        for i in range(len(self.choices_render)):
            
            #########################################################
            # Check for new category
            ## Show first catgory
            if i == 0: category_toggle = True

            ## Shift positions for consecutive categories
            elif (i >= 1) and (self.categories[i] != self.categories[i-1]):
                categories.append((i, self.categories[i]))
                category_toggle = True

            ## Make sure category is only shown once
            else: category_toggle = False

            #########################################################
            # Set positions and render
            offset       = self.spacing * (i + len(categories))
            choice_pos   = (self.choice_pos[0],   self.choice_pos[1]   + offset)
            category_pos = (self.category_pos[0], self.category_pos[1] + offset)
            cursor_pos   = (self.cursor_pos[0],   self.cursor_pos[1]   + offset)

            pyg.overlay_queue.append([self.choices_render[i], choice_pos])
            if category_toggle:
                pyg.overlay_queue.append([self.categories_render[i], category_pos])
            if (self.choice == i) and (self.mode == 'log'):
                pyg.overlay_queue.append([self.cursor_surface, cursor_pos])

    # Keys
    def key_UP(self):
        if self.mode == 'log':
            self.choice = (self.choice - 1) % len(self.choices)
        
    def key_DOWN(self):
        if self.mode == 'log':
            self.choice = (self.choice + 1) % len(self.choices)

    def key_LEFT(self):
        if self.mode == 'quest':
            self.mode = 'log'
            self.update_questlog()

    def key_RIGHT(self):
        if self.mode == 'log':
            self.mode = 'quest'
            self.update_questlog()

    def key_ENTER(self):
        if self.mode == 'quest': self.mode = 'log'
        elif self.mode == 'log': self.mode = 'quest'
        self.update_questlog()

    def key_BACK(self):
        pyg = session.pyg

        if pyg.game_state != 'play_garden':
            pyg.hud_state = 'on'
        pyg.overlay_state = None

    # Tools
    def update_questlog(self):
        """ Updates and sorts main quests and side quests. """

        log = session.player_obj.ent.env.area.questlog.active_quests

        if self.mode == 'log':            self.update_quest_list(log)
        elif self.mode == 'quest':        self.update_quest_details(log)
        
    def update_quest_list(self, log):
        """ Prepares names and categories of active quests. """

        pyg = session.pyg

        # Extract choices and categories from questlog
        self.choices    = []
        self.categories = []
        for quest in log:
            self.choices.append(quest.name)
            self.categories.append(quest.category)

        # Construct surfaces
        self.header            = "QUESTLOG"
        self.header_surface    = pyg.font.render(self.header, True, pyg.white)
        self.choices_render    = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]
        self.categories_render = [pyg.font.render(f'{category.lower()}', True, pyg.gray) for category in self.categories]

    def update_quest_details(self, log):
        """ Prepares description and objectives for selected quest. """

        pyg   = session.pyg
        quest = log[self.choice]
        
        # Extract categories
        self.categories  = ["notes" for _ in quest.description]
        self.categories += ["tasks" for _ in quest.objectives]

        # Extract objectives
        self.choices = list(quest.description)
        for objective in quest.objectives:
            if objective.complete: checkbox = "☑ "
            else:                  checkbox = "☐ "
            self.choices.append(checkbox + objective.description)

        # Construct surfaces
        self.header            = quest.name.upper()
        self.header_surface    = pyg.font.render(self.header, True, pyg.white)
        self.header_pos        = (int((pyg.screen_width - self.header_surface.get_width())/2), self.header_pos[1])
        self.choices_render    = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]
        self.categories_render = [pyg.font.render(f'{category.lower()}', True, pyg.gray) for category in self.categories]

    # Old
    def default_Quests(self, env_name):
        
        # Stage 0: 
        if env_name == 'garden':
            session.player_obj.gardenlog.add_quest('garden_build_a_shed')
        
            #water = Quest(
            #    name='Lead a root to water',
            #    notes=['These odd beings seem thirsty.',
            #           'I should pour out some water for them.'],
            #    tasks=['☐ Empty your jug of water.',
            #           '☐ Make a radix drink.'],
            #    category='Main')

            #food = Quest(
            #    name='Fruit of the earth',
            #    notes=['Set out some food.'],
            #    tasks=['☐ Get a radix to eat.'],
            #    category='Main')
            
            #building_shelter = Quest(
            #    name='Build a house',
            #    notes=['Shelter would be nice.'],
            #    tasks=['☐ Contruct walls.',
            #           '☐ Set a floor.',
            #           '☐ Decorate.'],
            #    category='Side')
            
            #session.player_obj.ent.gardenlog = {
            #    water.name:             water,
            #    food.name:              food,
            #    building_shelter.name:  building_shelter}
            
            #return water, food, building_shelter
        
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
        
        else: print(env_name)

    def check_tasks(self, name, log):
        pyg = session.pyg

        quest = log[name]

        # Check off task
        if not quest.finished:
            for i in range(len(quest.tasks)):
                task = quest.tasks[i]
                if task[0] == "☐":
                    quest.tasks[i] = task.replace("☐", "☑")
                    pyg.update_gui(quest.tasks[i], pyg.violet)
                    quest.content = quest.notes + quest.tasks
                    break
        
        # Remove finished quests
        else:
            quest.tasks[-1] = quest.tasks[-1].replace("☐", "☑")
            pyg.update_gui(quest.tasks[-1], pyg.violet)
            pyg.update_gui(f"Quest complete: {quest.name}", pyg.violet)
            del log[quest.name]

class Questlog:

    # Initializations
    def __init__(self):
        """ Loads and tracks all active quests and tells them about event information.
            Defines one function for each event that might be needed for a quest, such as dialogue.
        """

        self.active_quests = []
        self._subscribe_events()

    def _subscribe_events(self):
        session.bus.subscribe('entity_interacted', self.on_interact)
        session.bus.subscribe('item_picked_up',    self.on_item_pickup)
        session.bus.subscribe('item_placed',       self.on_item_placed)
        session.bus.subscribe('item_used',         self.on_item_used)

    def load_quest(self, filename):

        # Import file
        data = load_json(f'Data/.Quests/{filename}.json')
        
        # Load objectives as keywords
        objectives = [

            QuestObjective(
                event_id    = obj['event_id'],
                description = obj['description'],
                conditions  = obj['conditions'],
                on_complete = obj.get('on_complete', []))

            for obj in data["objectives"]]
        
        # Load quest as keywords
        quest = Quest(
            quest_id    = data['quest_id'],
            name        = data['name'],
            category    = data['category'],
            description = data['description'],
            objectives  = objectives,
            on_load     = data.get('on_load', []),
            on_complete = data.get('on_complete', []))
        
        self.active_quests.append(quest)

        # Sort alphabetically and by category
        self.sort_quests()
    
    def sort_quests(self):

        def sort_key(quest):
            if quest.category == 'main': category_order = 0
            else:                        category_order = 1
            return (category_order, quest.name.lower())

        return sorted(self.active_quests, key=sort_key)

    # Event functions
    def on_interact(self, ent_id, target_ent_id):
        for quest in self.active_quests:
            quest.notify(
                event_id      = 'entity_interacted',
                ent_id        = ent_id,
                target_ent_id = target_ent_id)

    def on_item_pickup(self, ent_id, item_id):
        for quest in self.active_quests:
            quest.notify(
                event_id = 'item_picked_up',
                ent_id   = ent_id,
                item_id  = item_id)

    def on_item_placed(self, ent_id, item_id):
        for quest in self.active_quests:
            quest.notify(
                event_id = 'item_placed',
                ent_id   = ent_id,
                item_id  = item_id)

    def on_item_used(self, ent_id, item_id):
        for quest in self.active_quests:
            quest.notify(
                event_id = 'item_used',
                ent_id   = ent_id,
                item_id  = item_id)

    def __setstate__(self, state):
        self.__dict__.update(state) 
        self._subscribe_events()

class Quest:

    def __init__(self, quest_id, name, category, description, objectives, on_load=None, on_complete=None):
        """ Represents a single quest. Holds objectives and checks if all are complete.
        
            Parameters
            ----------
            quest_id    : str; unique name for each quest
            name        : str; displayed name for each quest; not necessarily unique
            category    : str in ['main', 'side']; questlog categorization
            description : str; description shown in questlog

            objectives  : list of QuestObjective objects; tasks to be completed
            on_complete : list of dicts; actions associated with completion
        """

        # Identifiers
        self.quest_id    = quest_id
        self.name        = name
        self.category    = category
        self.description = description

        # Actions
        self.objectives  = objectives
        self.on_complete = on_complete

        # Initial action
        if on_load:
            for action in on_load:
                kwargs = {k: v for k, v in action.items() if (k != 'event_id')}
                session.bus.emit(action.get('event_id'), **kwargs)

    def notify(self, event_id, **kwargs):

        # Check if the event satisfies an objective
        for objective in self.objectives:
            satisfied = objective.check_event(event_id, **kwargs)
            if satisfied: break

        # Check if that completes all objectives
        if self.complete():
            if self.on_complete:
                for action in self.on_complete:
                    kwargs = {k: v for k, v in action.items() if (k != 'event_id')}
                    session.bus.emit(action.get('event_id'), **kwargs)

    def complete(self):
        return all(obj.complete for obj in self.objectives)

class QuestObjective:

    def __init__(self, event_id, description, conditions, on_complete=None):
        """ Represents a single objective. Sets which events to listen for.
            Allows a function (on_complete) to run directly and/or emits a completion flag.

            Parameters
            ----------
            event_id    : str; event needed for objective
            target_id   : str; name of an item, object, entity, or location
            description : str; description to be displayed in questlog
            on_complete : function; action to take upon completion of objective

            complete    : bool; toggles task completion
        """

        self.event_id    = event_id
        self.description = description

        self.conditions  = conditions or {}

        self.on_complete = on_complete
        self.complete    = False

    def check_event(self, event_id, **kwargs):
        """ Checks if the event matches the objective. If so, checks if all conditions match. """

        # Ignore events if the objective is complete
        if self.complete:
            return False

        # Ignore events that don't match the objective
        if event_id != self.event_id:
            #print(f'0 \t {event_id} \t {self.event_id} \t {self.description}')
            return False
        
        # Check all conditions
        for key, value in self.conditions.items():
            #print()
            event_val = kwargs.get(key)
            #print(f'{key} \t {value} \t {kwargs} \t {event_val}')

            # Return if none of the possible conditions are satisfied
            if isinstance(value, (list, set, tuple)):
                if event_val not in value:
                    #print(f'1 \t {event_id} \t {self.event_id} \t {event_val} \t {self.description}')
                    return False
            
            # Return if the condition is not satisfied
            else:
                if event_val != value:
                    #print(f'2 \t {event_id} \t {self.event_id} \t {event_val} \t {self.description}')
                    return False

        # All conditions passed
        self.complete = True
        print(f'3 \t {event_id} \t {self.event_id} \t {self.description}')

        # Trigger any objective-level completion actions by emitting them to the bus
        if self.on_complete:
            for action in self.on_complete:
                kwargs = {k: v for k, v in action.items() if (k != 'event_id')}
                session.bus.emit(action.get('event_id'), **kwargs)
        
        return True

########################################################################################################################################################
# Old
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

        pyg = session.pyg

        from entities import Effect
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
            session.questlog_obj.check_tasks("Making a friend", session.player_obj.ent.questlog)
        
        # Complete quest
        if friend_level == 9:
            
            session.player_obj.ent.questlog['Making a friend'].finished = True
            session.questlog_obj.check_tasks("Making a friend", session.player_obj.ent.questlog)
            pyg.update_gui("Woah! What's that?", pyg.violet)
            
            x = lambda dX : int((session.player_obj.ent.X + dX)/pyg.tile_width)
            y = lambda dY : int((session.player_obj.ent.Y + dY)/pyg.tile_height)
            
            # Find a nearby space to place the mysterious note
            found = False
            for i in range(3):
                if found: break
                x_test = x(pyg.tile_width*(i-1))
                for j in range(3):
                    y_test = y(pyg.tile_height*(j-1))
                    if not session.player_obj.ent.env.map[x_test][y_test].entity:
                        session.player_obj.cache = False
                        
                        obj = session.items.create_item('scroll of death')
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
        
        pyg = session.pyg

        from pygame_utilities import Textbox
        
        # Read the note
        if not dialogue:
            note_text = ["ξνμλ λξ ξλι ξγθιβξ ξ θθ.", "Ηκρσ σρσ λβνξθι νθ.", "Ψπθ αβνιθ πθμ."]
            session.textbox = Textbox(
                header = "mysterious note",
                text   = note_text)
            pyg.overlay_state = 'textbox'
            pyg.hud_state     = 'off'
        
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
            pyg.update_gui(f"Quest added: {quest.name}", pyg.violet)
            
            self.names_list, self.dialogue_list, self.progress_list = self.set_entities(quest)

########################################################################################################################################################