########################################################################################################################################################
# Game states
class Session:

    def __init__(self):

        self.pyg              = None # Pygame
        self.aud              = None # Audio
        self.img              = None # Images

        self.player_obj       = None # PlayerData

        self.play_game_obj    = None # PlayGame
        self.garden_obj       = None # PlayGarden

        self.main_menu_obj    = None # MainMenu
        self.new_game_obj     = None # NewGameMenu
        self.ctrl_menu        = None # CtrlMenu
        self.file_menu        = None # FileMenu

        self.questlog_obj     = None # QuestMenu
        self.textbox          = None # Textbox

        self.inv              = None # InventoryMenu
        self.dev              = None # CatalogMenu
        self.hold_obj         = None # AbilitiesMenu
        self.trade_obj        = None # ExchangeMenu

        self.stats_obj        = None # StatsMenu

        self.bus              = None # EventBus

        self.movement         = None # MovementSystem
        self.interact         = None # InteractionSystem
        self.items            = None # ItemsSystem
        self.effects          = None # EffectsSystem

session = Session()

########################################################################################################################################################