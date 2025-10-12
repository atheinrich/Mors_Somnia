########################################################################################################################################################
# MORS SOMNIA
#
########################################################################################################################################################

########################################################################################################################################################
# Plot
""" Overview
    --------
    There are many paths, but (almost) all lead to death. (One leads to immortality.)
    In the Overworld, mystery trickles beneath the floorboards.
    There are people to talk to, missions to complete, hidden opportunities, and clues to the endgame.
    Daylight passes quickly. Sleep and drug use lead to roguelike dreams.
    Death is the only way to wake up from a dream or hallucination and return to the Overworld. Death in the Overworld is absolute.
    Only some items and modifications are retained upon death in a dream or hallucination.
    
    Main Quests
    -----------
    Making a Friend     : A tutorial for controls that allows early access to the Sigil.
    Learning a Language : Introduction of the Sigil as a leading artifact in the overarching plot.
    
    Side Quests
    -----------
    Upgrade : A tutorial for trading mechanics that allows early access to a dagger.
    
    The Garden
    ----------
    Let There Be Water : A tutorial for item use and radish interaction in the Garden.
    
    Endgames
    --------
    No Risk, No Reward : The player does nothing substantial and dies in the Overworld. Upon death, the player cannot move (due to death).
    Introspection      : The player escapes the Overworld and returns to Player Creation. Upon death, they arise in the Garden.
    Becoming a God     : The player breaches polynomial depth in dreams and hallucinations. Death results in a stochastic environments forever.
    Resident           : The player mostly survives and helps out around town. One death is prevented; the next results in a funeral.
    Believer           : The player serves the church and saves it from destruction. 
    * additional
    
    Path 1: With the aid of drugs, experience, and the church questline, the player can become effectively immortal through cloning.
    - This is the most difficult path to achieve and leads to the endgame.
    - The church must look favorably on the player, and the player must have sufficient experience and evolutions.
    
    Path 2: With the aid of drugs and experience, the player can defeat the church and live in harmony in the Overworld.
    - The player can still die in the Overworld, in which they do not proceed to the endgame.
    
    Path 3: With the aid of experience and the church questline (but no drugs), the player is doomed to death.
    - The church will eventually reject the player for not following their creed.
    - There is no endgame or bonus content.
    
    Path 4: With the aid of experience alone, the player will perish after the church's revolt.
    - This happens after a fixed number of days.
    - New customization options are available for runs following this path.
    
    Path 5: With the aid of the church questline alone, all life in the overworld will end.
    - This is only achieved if the church questline is completed at Rank 1.
    - Something special happens, but I don't know what yet. """

""" Environments
    ------------
    Through requisite means, the player can access their Home, the Overworld, the Dungeons, the Abyssal Gallery, and the Garden.
    
    Home            : Nothing special happens here; it is a place of refuge.
    Overworld       : The main questline occurs here.
    Dungeons        : This is mostly a placeholder for dream/drug environments that haven't been programmed yet.
    Abyssal Gallery : This is the beginning and the end; strong monsters and powerful items, etc. """

""" NPCs
    ----
    Townsfolk : Average settlers of the Overworld.
    Bloodkin  : Worshipers of the Sigil of Thanato. They rarely leave the church but can be found in dreams.
    Kyrio     : A powerful leader of the Bloodkin. He is a deviant that masquerades as a confused old man.
    Kapno     : The brother of Kyrio and the store manager of the Overworld. He is a pleasant old man that knows nothing of his brother's plot.
    Chameno   : A former leader of the Bloodkin that fled persecution to live in dreams.
    Louloud   : The player's best friend. She lives with her mother and likes to garden.
    Giatro    : The doctor of the Overworld. He is optionally converted to a Bloodkin by the player and attained as a follower.
    Erasti    : An unsuspecting member of the Townsfolk. She may be conscripted as a follower.
    Ypno      : The drug dealer of the Townsfolk. They can be found in the Overworld and in dreams.
    Thanato   : Death itself. They have no physical form but can imbue inanimate objects with deadly prowess.
    Vit       : Life itself. Idk yet. """

########################################################################################################################################################
# Imports
## Specific
import pygame
from pygame.locals import *

## Local
import session
from items_entities import Player
from utilities import Images, Audio, MainMenu, FileMenu, SmallMenu, Info, Pets
from mechanics import Pygame, Mechanics, NewGame, PlayGame, PlayGarden, Inventory, Catalog, Abilities
from mechanics import Exchange
from environments import Environments
from quests import BigMenu
from data_management import API

########################################################################################################################################################
# Global values
super_dig = False
API_toggle = False

########################################################################################################################################################
# Core
def main():
    """ Initializes the essentials and opens the main menu. """

    # API
    if API_toggle: API(state=None, details=None, init=True)
    
    # Pygame
    session.pyg              = Pygame()
    session.pyg.game_state   = 'startup'
    session.pyg.overlay      = None
    
    # Mechanics and audio
    session.mech             = Mechanics()
    session.aud              = Audio()
    
    # Images (sorted dictionary and cache)
    session.img              = Images()
    session.img.flipped      = Images(flipped=True)
    pygame.display.set_icon(session.img.dict['decor']['skeleton'])
    
    # Player data
    session.player_obj       = Player()
    session.player_obj.temp  = True
    session.player_obj.envs  = Environments()
    
    # Gamestates
    session.new_game_obj     = NewGame()
    
    session.play_game_obj    = PlayGame()
    session.garden_obj       = PlayGarden()
    session.pet_obj          = Pets()
    
    # Overlays
    session.main_menu_obj    = MainMenu()
    session.ctrl_menu        = FileMenu(
        name         = 'ctrl_menu',
        header       = "Controls", 
        options = [
            f"Move up:                                {session.pyg.key_UP[0]}                     Exit:                                         {session.pyg.key_BACK[0]}",
            f"Move down:                           {session.pyg.key_DOWN[0]}                     Activate 1:                             {session.pyg.key_ENTER[0]}",
            f"Move left:                               {session.pyg.key_LEFT[0]}                     Activate 2:                               {session.pyg.key_PERIOD[0]}",
            f"Move right:                            {session.pyg.key_RIGHT[0]}",
            "",
            
            f"Toggle inventory:                  {session.pyg.key_INV[0]}                     Enter combo:                         {session.pyg.key_HOLD[0]}",
            f"Toggle Catalog:                   {session.pyg.key_DEV[0]}                     Change speed:                      {session.pyg.key_SPEED[0]}",
            f"Toggle GUI:                            {session.pyg.key_GUI[0]}                     Zoom in:                                {session.pyg.key_PLUS[0]}",
            f"View stats:                             {session.pyg.key_INFO[0]}                     Zoom out:                              {session.pyg.key_MINUS[0]}",
            f"View questlog:                      {session.pyg.key_QUEST[0]}"])
    session.save_account_obj = FileMenu(
        name         = 'save',
        header       = "Save",
        options      = ["File 1",
                        "File 2",
                        "File 3"],
        backgrounds  = ["Data/File_1/screenshot.png",
                        "Data/File_2/screenshot.png",
                        "Data/File_3/screenshot.png"])
    session.load_account_obj = FileMenu(
        name         = 'load',
        header       = "Load",
        options      = ["File 1",
                        "File 2",
                        "File 3"],
        backgrounds  = ["Data/File_1/screenshot.png",
                        "Data/File_2/screenshot.png",
                        "Data/File_3/screenshot.png"])
    
    
    session.questlog_obj = BigMenu(
        name      = 'questlog',
        header    = "                                                        QUESTLOG", 
        options   = ["Test"])
    session.questlog_obj.init_questlog('overworld')
    session.questlog_obj.init_questlog('garden')
    session.inv              = Inventory()
    session.dev              = Catalog()
    session.hold_obj         = Abilities()
    session.trade_obj        = Exchange()
    session.small_menu       = SmallMenu()
    session.info_obj         = Info()
    session.big_menu         = BigMenu(
        name      = 'temp',
        header    = "temp", 
        options   = [""])
    
    game_states()

def game_states():
    
    session.pyg.running    = True
    while session.pyg.running:
        
        # Primary
        if session.pyg.game_state == 'startup':
            session.main_menu_obj.startup()
        
        elif session.pyg.game_state == 'play_game':
            session.play_game_obj.run()
            session.play_game_obj.render()
            
            ## Extra adjustments
            session.player_obj.ent.env.weather.run()
            for image, (X, Y) in session.player_obj.ent.env.weather.render():
                session.pyg.display.blit(image, (X, Y))
            
        elif session.pyg.game_state == 'new_game':
            session.new_game_obj.run()
            session.new_game_obj.render()
        
        elif session.pyg.game_state == 'play_garden':
            session.garden_obj.run()
            session.garden_obj.render()
        
        # Overlays
        if session.pyg.overlay == 'menu':
            game_state = session.main_menu_obj.run()
            session.main_menu_obj.render()
        
        elif session.pyg.overlay == 'ctrl_menu':
            session.ctrl_menu.run()
            session.ctrl_menu.render()
        
        elif session.pyg.overlay == 'load':
            session.load_account_obj.run()
            session.load_account_obj.render()
        
        elif session.pyg.overlay == 'save':
            session.save_account_obj.run()
            session.save_account_obj.render()
        
        elif session.pyg.overlay == 'inv':
            session.inv.run()
            session.inv.render()
        
        elif session.pyg.overlay == 'dev':
            session.dev.run()
            session.dev.render()
        
        elif session.pyg.overlay == 'hold':
            session.hold_obj.run()
            session.hold_obj.render()
        
        elif session.pyg.overlay == 'trade':
            session.trade_obj.run()
            session.trade_obj.render()
        
        elif session.pyg.overlay == 'stats':
            session.small_menu.render()
        
        elif session.pyg.overlay == 'questlog':
            session.questlog_obj.run()
            session.questlog_obj.render()
        
        elif session.pyg.overlay == 'temp':
            session.big_menu.run()
            session.big_menu.render()
        
        # Finish up
        session.img.render()
        pygame.display.flip()
        session.pyg.screen.blit(pygame.transform.scale(session.pyg.display, (session.pyg.screen_width, session.pyg.screen_height)), (0, 0))
        session.pyg.clock.tick(30)
        
        # Update API
        if API_toggle: API(
            details = session.player_obj.ent.env.name.capitalize(),
            state   = ['🌗', '🌘', '🌑', '🌒', '🌓', '🌔', '🌕', '🌖'][session.player_obj.ent.env.env_time-1])

########################################################################################################################################################
# Global scripts
if __name__ == "__main__":
    main()

########################################################################################################################################################