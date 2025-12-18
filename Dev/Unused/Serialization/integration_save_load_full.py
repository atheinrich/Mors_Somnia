import os, sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import session
from pygame_utilities import Pygame, Images, Audio, EventBus
from abilities import _abilities
from effects import _effects
from items import ItemSystem
from mechanics import MovementSystem, InteractionSystem
from entities import PlayerData
from big_menus import FileMenu
from environments import EnvironmentSerializer

import pygame
pygame.init()
pygame.display.set_mode((64, 64))

# Minimal runtime
session.bus = EventBus()
session.pyg = Pygame()
session.aud = Audio()
session.img = Images()
session.movement = MovementSystem()
session.interact = InteractionSystem()
session.items = ItemSystem()
session.effects = _effects
session.abilities = _abilities

try:
    from big_menus import StatsMenu
    session.stats_obj = StatsMenu()
except Exception:
    session.stats_obj = None

# Create and finalize a player
session.player_obj = PlayerData()
session.player_obj.init_player()
session.player_obj.finalize_player()

# Make some deterministic checks by recording baseline
baseline = {}
baseline['file_num'] = 1
baseline['ent_name'] = session.player_obj.ent.name
baseline['inventory_counts'] = {k: len(v) for k, v in session.player_obj.ent.inventory.items()}
baseline['equipment_slots'] = {k: (v.name if v else None) for k, v in session.player_obj.ent.equipment.items()}
baseline['discoveries'] = {k: len(v) for k, v in session.player_obj.ent.discoveries.discoveries.items()}
baseline['env_areas'] = list(session.player_obj.envs.areas.keys())
baseline['gardenlog_qs'] = len(getattr(session.player_obj, 'gardenlog').active_quests) if getattr(session.player_obj, 'gardenlog', None) else 0
baseline['dialogue_states'] = len(getattr(session.player_obj, 'dialogue').npc_states) if getattr(session.player_obj, 'dialogue', None) else 0
baseline['stats'] = {'pet_levels': getattr(session.stats_obj, 'pet_levels', None) if session.stats_obj else None}

# Save to file 1
fm = FileMenu()
fm.choice = 0
print('Saving...')
fm.save_account()
print('Saved JSON exists:', os.path.exists('Data/File_1/session.player_obj.json'))
print('Saved envs metadata exists:', os.path.exists('Data/File_1/envs_metadata.json'))

# Reset player_obj and reload
session.player_obj.__init__()
print('After reset, ent is', session.player_obj.ent)
fm.choice = 0
print('Loading...')
fm.load_account()
loaded = session.player_obj is not None
print('Loaded:', loaded)

# Run checks
results = {}
results['ent_present'] = getattr(session.player_obj, 'ent', None) is not None
if results['ent_present']:
    ent = session.player_obj.ent
    results['ent_name'] = ent.name
    results['inventory_counts'] = {k: len(v) for k, v in ent.inventory.items()}
    results['equipment_slots'] = {k: (v.name if v else None) for k, v in ent.equipment.items()}
    try:
        results['discoveries'] = {k: len(v) for k, v in ent.discoveries.discoveries.items()}
    except Exception:
        results['discoveries'] = None
else:
    results['ent_name'] = None

results['envs_areas'] = list(session.player_obj.envs.areas.keys()) if getattr(session.player_obj, 'envs', None) else None
results['gardenlog_qs'] = len(getattr(session.player_obj, 'gardenlog').active_quests) if getattr(session.player_obj, 'gardenlog', None) else None
results['dialogue_states'] = len(getattr(session.player_obj, 'dialogue').npc_states) if getattr(session.player_obj, 'dialogue', None) else None
results['stats_pet_levels'] = getattr(session.stats_obj, 'pet_levels', None) if session.stats_obj else None

# Print baseline and results for comparison
print('\nBASELINE:')
for k, v in baseline.items():
    print(k, ':', v)
print('\nRESULTS:')
for k, v in results.items():
    print(k, ':', v)

# Quick pass/fail summary
ok = True
if not results['ent_present']:
    ok = False
if baseline['ent_name'] != results.get('ent_name'):
    ok = False
if baseline['env_areas'] != results.get('envs_areas'):
    ok = False

print('\nOverall pass:', ok)

# Exit with non-zero on failure to aid CI
if not ok:
    sys.exit(2)
else:
    sys.exit(0)
