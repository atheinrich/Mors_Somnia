########################################################################################################################################################
# Game states
class Session:

    def __init__(self):

        self.pyg              = None # Pygame object

        self.mech             = None # Mechamics object
        self.aud              = None # Audio object
        self.img              = None # Images object

        self.player_obj       = None # Player object

        self.play_game_obj    = None # PlayGame object
        self.new_game_obj     = None # NewGameMenu object
        self.garden_obj       = None # PlayGarden object

        self.main_menu_obj    = None # MainMenu object
        self.ctrl_menu        = None # CtrlMenu object
        self.file_menu        = None # FileMenu object

        self.questlog_obj     = None # QuestMenu object
        self.textbox          = None # Textbox object

        self.inv              = None # InventoryMenu object
        self.dev              = None # CatalogMenu object
        self.hold_obj         = None # AbilitiesMenu object
        self.trade_obj        = None # ExchangeMenu object

        self.stats_obj        = None # StatsMenu object

        self.bus              = EventBus()

class EventBus:

    def __init__(self):
        """ Accepts event information, holds functions tied to events, and calls the functions if events match. """

        self.listeners = {}

    def subscribe(event_type, function):
        """ Adds a new function to be called when the given event type occurs. """

        EventBus.listeners.setdefault(event_type, []).append(function)

    def emit(event_type, **kwargs):
        """ Accepts an event flag and calls any functions with a matching event. """

        for function in EventBus.listeners.get(event_type, []): function(**kwargs)

session = Session()

########################################################################################################################################################