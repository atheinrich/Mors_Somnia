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
## Standard
import time

## Specific
import pygame
from pygame.locals import *
from pypresence import Presence

## Local
import session
from pygame_utilities import Pygame, Images, Audio, EventBus
from entities import PlayerData
from abilities import _abilities
from effects import _effects
from items import ItemSystem
from mechanics import MovementSystem, InteractionSystem
from mechanics import PlayGame, PlayGarden
from big_menus import MainMenu, NewGameMenu, FileMenu, StatsMenu, CtrlMenu, Textbox
from side_menus import InventoryMenu, CatalogMenu, AbilitiesMenu, ExchangeMenu
from quests import QuestMenu
from pygame_utilities import render_display, render_hud

## Debugging
import cProfile

########################################################################################################################################################
# Global values
API_toggle = False

########################################################################################################################################################
# Core
def init():
    """ Initializes the essentials and opens the main menu. """
    
    #########################################################
    # Core
    ## Pygame
    session.bus              = EventBus()
    session.pyg              = Pygame()
    session.aud              = Audio()
    
    ## Images (sorted dictionary and cache)
    session.img              = Images()
    session.img.flipped      = Images(flipped=True)
    pygame.display.set_icon(session.img.dict['decor']['skeleton'])
    
    ## Save data
    session.player_obj       = PlayerData()
    
    #########################################################
    # Gamestates
    ## Mechanics
    session.movement         = MovementSystem()
    session.interact         = InteractionSystem()
    session.items            = ItemSystem()
    session.effects          = _effects
    session.abilities        = _abilities

    ## Primary
    session.play_game_obj    = PlayGame()
    session.garden_obj       = PlayGarden()

    ## Big overlays
    session.main_menu_obj    = MainMenu()
    session.new_game_obj     = NewGameMenu()
    session.file_menu        = FileMenu()
    session.ctrl_menu        = CtrlMenu()
    session.questlog_obj     = QuestMenu()
    session.textbox          = Textbox()

    ## Side overlays
    session.inv              = InventoryMenu()
    session.dev              = CatalogMenu()
    session.hold_obj         = AbilitiesMenu()
    session.trade_obj        = ExchangeMenu()
    session.stats_obj        = StatsMenu()
    
    #########################################################
    # Run game
    if API_toggle: API(state=None, details=None, init=True)
    game_states()

def game_states():
    pyg = session.pyg

    pyg.running = True
    while pyg.running:

        #########################################################
        # Play game
        if pyg.game_state == 'startup':
            session.new_game_obj.run()
        
        elif pyg.game_state == 'play_garden':
            session.garden_obj.run()
            session.garden_obj.render()
        
        elif pyg.game_state == 'play_game':
            session.play_game_obj.run()
            session.play_game_obj.render()
            session.player_obj.ent.env.weather.run()
        
        #########################################################
        # Add big overlay
        if pyg.overlay_state == 'menu':
            session.main_menu_obj.run()
            session.main_menu_obj.render()
        
        elif pyg.overlay_state == 'new_game':
            session.new_game_obj.run()
            session.new_game_obj.render()
        
        elif pyg.overlay_state in ['save', 'load']:
            session.file_menu.run()
            session.file_menu.render()
        
        elif pyg.overlay_state == 'ctrl_menu':
            session.ctrl_menu.run()
            session.ctrl_menu.render()
        
        elif pyg.overlay_state == 'questlog':
            session.questlog_obj.run()
            session.questlog_obj.render()
        
        elif pyg.overlay_state == 'textbox':
            session.textbox.run()
            session.textbox.render()
        
        #########################################################
        # Add side overlay
        elif pyg.overlay_state == 'inv':
            session.inv.run()
            session.inv.render()
        
        elif pyg.overlay_state == 'dev':
            session.dev.run()
            session.dev.render()
        
        elif pyg.overlay_state == 'hold':
            session.hold_obj.run()
            session.hold_obj.render()
        
        elif pyg.overlay_state == 'trade':
            session.trade_obj.run()
            session.trade_obj.render()
        
        elif pyg.overlay_state in ['ent_stats', 'pet_stats']:
            session.stats_obj.run()
            session.stats_obj.render()
        
        #########################################################
        # Add fade
        if pyg.fade_state != 'off':
            pyg.update_fade()
        
        #########################################################
        # Rendering
        rendering()
        API_updating()

def rendering():
    pyg = session.pyg

    #########################################################
    # Render display (tiles, items, entities, weather)
    render_display()
    session.img.render()
    for (surface, pos) in pyg.display_queue:
        pyg.display.blit(surface, pos)
    display = pygame.transform.scale(
        pyg.display, (pyg.screen_width, pyg.screen_height))
    
    ## Apply effects
    if session.img.render_fx == 'bw_binary':
        from pygame_utilities import bw_binary
        display = bw_binary(display)

    pyg.screen.blit(display, (0, 0))

    #########################################################
    # Render HUD (messages, time, health, stamina)
    render_hud()
    for (surface, pos) in pyg.hud_queue:
        pyg.overlays.blit(surface, pos)
    hud = pygame.transform.scale(
        pyg.hud, (pyg.screen_width, pyg.screen_height))
    pyg.screen.blit(hud, (0, 0))

    #########################################################
    # Render overlays (menus)
    for (surface, pos) in pyg.overlay_queue:
        pyg.overlays.blit(surface, pos)
    overlays = pygame.transform.scale(
        pyg.overlays, (pyg.screen_width, pyg.screen_height))
    pyg.screen.blit(overlays, (0, 0))

    #########################################################
    # Render fade (intertitles)
    for (surface, pos) in pyg.fade_queue:
        pyg.fade.blit(surface, pos)
    fade = pygame.transform.scale(
        pyg.fade, (pyg.screen_width, pyg.screen_height))
    pyg.screen.blit(fade, (0, 0))

    #########################################################
    # Prepare for next frame
    pygame.display.flip()
    pyg.clock.tick(30)
    
    pyg.display.fill(pyg.black)
    pyg.hud.fill((0, 0, 0, 0))
    pyg.overlays.fill((0, 0, 0, 0))
    pyg.fade.fill((0, 0, 0, 0))

    pyg.display_queue = []
    pyg.hud_queue     = []
    pyg.overlay_queue = []
    pyg.fade_queue    = []

########################################################################################################################################################
# Other
def API_updating():
    env = session.player_obj.ent.env
    if API_toggle: API(
        state   = env.weather.symbols[env.env_time-1],
        details = env.name.capitalize())

def API(state, details, init=False):
    global RPC
    
    if init:
        RPC = Presence(1384311591662780586)
        RPC.connect()
    
    else:
        RPC.update(
            state       = state,
            details     = details,
            large_image = "logo",
            start       = time.time())

########################################################################################################################################################
# Global scripts
if __name__ == "__main__":
    init() #cProfile.run('init()', sort='cumtime')

########################################################################################################################################################