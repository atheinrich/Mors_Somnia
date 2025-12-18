import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import session
from pygame_utilities import Pygame, Images, Audio, EventBus
from abilities import _abilities
from effects import _effects
from items import ItemSystem
from mechanics import MovementSystem, InteractionSystem
from entities import PlayerData
from environments import EnvironmentSerializer

import pygame
pygame.init()
pygame.display.set_mode((64, 64))

session.bus = EventBus()
session.pyg = Pygame()
session.aud = Audio()
session.img = Images()
session.movement = MovementSystem()
session.interact = InteractionSystem()
session.items = ItemSystem()
session.effects = _effects
session.abilities = _abilities

# Load player json
json_path = 'Data/File_1/session.player_obj.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
print('Top-level ent present in JSON:', 'ent' in data and data['ent'] is not None)
print('Ent keys:', list(data.get('ent', {}).keys()) if data.get('ent') else None)

# Test creating an entity by name
from entities import create_entity
try:
    test_ent = create_entity(data.get('ent', {}).get('name')) if data.get('ent') else None
    print('create_entity by name ->', getattr(test_ent, 'name', None))
except Exception as e:
    print('create_entity failed:', e)

# Try deserializing entity directly
try:
    ent_obj = EnvironmentSerializer.deserialize_entity(data.get('ent'), attach_to=None) if data.get('ent') else None
    print('deserialize_entity returned:', ent_obj)
    if ent_obj:
        print('deserialize_entity name:', ent_obj.name)
except Exception as e:
    print('deserialize_entity raised:', e)

# Load envs metadata if exists
from pathlib import Path
save_base = Path('Data/File_1')
meta_path = save_base / 'envs_metadata.json'
if meta_path.exists():
    with open(meta_path, 'r', encoding='utf-8') as mf:
        envs_meta = json.load(mf)
    print('envs_meta keys:', list(envs_meta.keys()))
    # reconstruct envs dict
    envs_data = {'room_max_size': envs_meta.get('room_max_size'), 'room_min_size': envs_meta.get('room_min_size'), 'max_rooms': envs_meta.get('max_rooms'), 'areas': {}}
    for area_name, area_info in envs_meta.get('areas', {}).items():
        area_dir = save_base / 'envs' / area_name
        try:
            with open(area_dir / 'area.json', 'r', encoding='utf-8') as af:
                area_meta = json.load(af)
        except Exception:
            area_meta = {'name': area_name}
        levels = {}
        for level_name, relpath in area_info.get('levels', {}).items():
            level_path = save_base / relpath
            try:
                with open(level_path, 'r', encoding='utf-8') as lf:
                    level_data = json.load(lf)
                levels[level_name] = level_data
            except Exception as e:
                print('Failed loading level', level_name, 'err', e)
        area_meta['levels'] = levels
        envs_data['areas'][area_name] = area_meta
    data['envs'] = envs_data
else:
    print('No envs metadata found')

# Attempt deserialize
player = EnvironmentSerializer.deserialize_player(data)
print('Deserialized player ent:', getattr(player, 'ent', None))
if getattr(player, 'ent', None):
    print('Ent name:', player.ent.name)
else:
    print('No entity recreated')

print('Done')
