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
        self.new_game_obj     = None # NewGame object
        self.garden_obj       = None # PlayGarden object
        self.pets_obj         = None # Pets object

        self.main_menu_obj    = None # MainMenu object
        self.ctrl_menu        = None # CtrlMenu object
        self.file_menu        = None # FileMenu object

        self.questlog_obj     = None # BigMenu object
        self.inv              = None # Inventory object
        self.dev              = None # Catalog object
        self.hold_obj         = None # Abilities object
        self.trade_obj        = None # Exchange object
        self.small_menu       = None # SmallMenu object
        self.info_obj         = None # Info object
        self.big_menu         = None # BigMenu object

session = Session()

########################################################################################################################################################