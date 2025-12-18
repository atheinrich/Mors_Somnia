import os
import sys
import pathlib
import pygame

# Ensure repository root is on sys.path so local modules import correctly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import session
from pygame_utilities import Pygame, Images, Audio, EventBus
from abilities import _abilities
from effects import _effects
from items import ItemSystem
from mechanics import MovementSystem, InteractionSystem
from entities import PlayerData
from big_menus import FileMenu

# Initialize minimal runtime components (no game loop)
pygame.init()
pygame.display.set_mode((64, 64))

session.bus = EventBus()
session.pyg = Pygame()
session.aud = Audio()
session.img = Images()

# Systems
session.movement = MovementSystem()
session.interact = InteractionSystem()
session.items = ItemSystem()
session.effects = _effects
session.abilities = _abilities

# Stats object if referenced
try:
    from big_menus import StatsMenu
    session.stats_obj = StatsMenu()
except Exception:
    session.stats_obj = None

# Create and finalize a player
session.player_obj = PlayerData()
session.player_obj.init_player()
session.player_obj.finalize_player()

# Save to file 1
fm = FileMenu()
fm.choice = 0
print('Saving...')
fm.save_account()
print('Saved JSON:', os.path.exists('Data/File_1/session.player_obj.json'))
print('Saved PKL:', os.path.exists('Data/File_1/session.player_obj.pkl'))

# Now reset player_obj and load
session.player_obj.__init__()
print('Player reset, ent is', session.player_obj.ent)
fm.choice = 0
print('Loading...')
fm.load_account()
print('Loaded, player ent:', getattr(session.player_obj, 'ent', None))
print('Player file_num:', getattr(session.player_obj, 'file_num', None))

# Quick checks
if session.player_obj and session.player_obj.ent:
    print('Player name:', session.player_obj.ent.name)
    print('Player location env:', getattr(session.player_obj.ent, 'env', None))

print('Integration test complete.')
