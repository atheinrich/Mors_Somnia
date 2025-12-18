import json
from pathlib import Path

class EnvironmentSerializer:
    """Handles serialization and deserialization of Environments to/from JSON."""
    
    @staticmethod
    def save_environments(envs, filepath):
        """Save all environments to a JSON file."""
        data = {
            'room_max_size': envs.room_max_size,
            'room_min_size': envs.room_min_size,
            'max_rooms': envs.max_rooms,
            'areas': {}
        }
        
        for area_name, area in envs.areas.items():
            data['areas'][area_name] = EnvironmentSerializer.serialize_area(area)
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_environments(envs, filepath):
        """Load environments from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        envs.room_max_size = data['room_max_size']
        envs.room_min_size = data['room_min_size']
        envs.max_rooms = data['max_rooms']
        
        for area_name, area_data in data['areas'].items():
            area = EnvironmentSerializer.deserialize_area(area_data, envs)
            envs.areas[area_name] = area
    
    @staticmethod
    def serialize_area(area):
        """Serialize an Area object."""
        return {
            'name': area.name,
            'permadeath': area.permadeath,
            'levels': {
                name: EnvironmentSerializer.serialize_environment(env)
                for name, env in area.levels.items()
            },
            'last_env': area.last_env.name if area.last_env else None,
            'display_fx': None,
            'questlog': [EnvironmentSerializer.serialize_quest(q) for q in (getattr(area, 'questlog').active_quests if getattr(area, 'questlog', None) else [])]
        }
    
    @staticmethod
    def deserialize_area(data, envs):
        """Deserialize an Area object."""
        area = Area(data['name'], envs, data['permadeath'])
        area.levels = {
            name: EnvironmentSerializer.deserialize_environment(env_data, area)
            for name, env_data in data['levels'].items()
        }
        # Restore questlog for area if provided
        if 'questlog' in data and data['questlog']:
            try:
                area.questlog = Questlog()
                for qdata in data['questlog']:
                    try:
                        quest = EnvironmentSerializer.deserialize_quest(qdata)
                        area.questlog.active_quests.append(quest)
                    except Exception:
                        continue
            except Exception:
                pass
        return area

    @staticmethod
    def serialize_quest(quest):
        """Serialize a Quest object into a dict."""
        return {
            'quest_id': getattr(quest, 'quest_id', None),
            'name': getattr(quest, 'name', None),
            'category': getattr(quest, 'category', None),
            'description': getattr(quest, 'description', []),
            'objectives': [EnvironmentSerializer.serialize_objective(obj) for obj in getattr(quest, 'objectives', [])],
            'on_load': getattr(quest, 'on_load', None),
            'on_complete': getattr(quest, 'on_complete', None)
        }

    @staticmethod
    def serialize_objective(obj):
        return {
            'event_id': getattr(obj, 'event_id', None),
            'description': getattr(obj, 'description', None),
            'conditions': getattr(obj, 'conditions', None),
            'on_complete': getattr(obj, 'on_complete', None),
            'complete': getattr(obj, 'complete', False)
        }

    @staticmethod
    def deserialize_quest(data):
        """Deserialize a quest dict into a Quest object without triggering on_load actions."""
        objectives = [EnvironmentSerializer.deserialize_objective(o) for o in data.get('objectives', [])]
        quest = Quest(
            data.get('quest_id'),
            data.get('name'),
            data.get('category'),
            data.get('description', []),
            objectives,
            on_load=None,
            on_complete=data.get('on_complete', None)
        )
        return quest

    @staticmethod
    def deserialize_objective(data):
        obj = QuestObjective(
            event_id=data.get('event_id'),
            description=data.get('description'),
            conditions=data.get('conditions', {}),
            on_complete=data.get('on_complete', None)
        )
        obj.complete = data.get('complete', False)
        return obj
    
    @staticmethod
    def serialize_environment(env):
        """Serialize an Environment object."""
        data = {
            'name': env.name,
            'lvl_num': env.lvl_num,
            'size': env.size,
            'soundtrack': env.soundtrack,
            'wall_img_IDs': env.wall_img_IDs,
            'floor_img_IDs': env.floor_img_IDs,
            'roof_img_IDs': env.roof_img_IDs,
            'env_date': env.env_date,
            'env_time': env.env_time,
            'player_coordinates': env.player_coordinates,
            'center': env.center,
            'rooms': [EnvironmentSerializer.serialize_room(room) for room in env.rooms],
            'weather': EnvironmentSerializer.serialize_weather(env.weather)
        }

        # Serialize map tiles (store minimal per-tile state plus references to items/entities)
        data['map'] = []
        for x in range(len(env.map)):
            col = []
            for y in range(len(env.map[0])):
                col.append(EnvironmentSerializer.serialize_tile(env.map[x][y]))
            data['map'].append(col)

        return data
    
    @staticmethod
    def deserialize_environment(data, area):
        """Deserialize an Environment object."""
        env = Environment(
            envs=area.envs,
            name=data['name'],
            size=data['size'],
            soundtrack=data['soundtrack'],
            lvl_num=data['lvl_num'],
            wall_img_IDs=data['wall_img_IDs'],
            floor_img_IDs=data['floor_img_IDs'],
            roof_img_IDs=data['roof_img_IDs'],
            img_IDs=data.get('floor_img_IDs', ['','']),
            area=area
        )
        env.env_date = data['env_date']
        env.env_time = data['env_time']
        env.player_coordinates = data['player_coordinates']
        env.center = data['center']
        env.weather = EnvironmentSerializer.deserialize_weather(data['weather'], env)
        env.rooms = [EnvironmentSerializer.deserialize_room(room_data, env) for room_data in data['rooms']]
        # Restore map tiles, items, and entities
        if 'map' in data:
            for x in range(len(data['map'])):
                for y in range(len(data['map'][0])):
                    tile_data = data['map'][x][y]
                    EnvironmentSerializer.deserialize_tile(tile_data, x, y, env)

        return env

    @staticmethod
    def serialize_tile(tile):
        """Serialize a Tile object to a compact dict."""
        tile_data = {
            'img_IDs': tile.img_IDs,
            'biome': tile.biome,
            'blocked': tile.blocked,
            'hidden': tile.hidden,
            'unbreakable': tile.unbreakable,
            'placed': getattr(tile, 'placed', False)
        }

        # Item reference
        if getattr(tile, 'item', None):
            item = tile.item
            tile_data['item'] = getattr(item, 'id', None) or getattr(item, 'name', None)
        else:
            tile_data['item'] = None

        # Entity reference (store enough to reconstruct)
        if getattr(tile, 'ent', None):
            ent = tile.ent
            ent_data = {
                'img_IDs': getattr(ent, 'img_IDs', None),
                'name': getattr(ent, 'name', None),
                'role': getattr(ent, 'role', None),
                'hp': getattr(ent, 'hp', None),
                'max_hp': getattr(ent, 'max_hp', None),
                'inventory': []
            }

            # Serialize lightweight inventory (item ids)
            try:
                for lst in ent.inventory.values():
                    for it in lst:
                        ent_data['inventory'].append(getattr(it, 'id', None) or getattr(it, 'name', None))
            except Exception:
                ent_data['inventory'] = []

            # Equipment
            try:
                ent_data['equipment'] = {slot: (getattr(it, 'id', None) or getattr(it, 'name', None)) if it else None for slot, it in ent.equipment.items()}
            except Exception:
                ent_data['equipment'] = {}

            # Active effects: try to find effect_id from session.effects._data
            try:
                active_effect_ids = []
                for eff in getattr(ent, 'active_effects', {}).values():
                    fid = getattr(eff, 'function_id', None)
                    found_id = None
                    if fid and hasattr(session, 'effects') and hasattr(session.effects, '_data'):
                        for k, v in session.effects._data.items():
                            if v.get('function_id') == fid or v.get('name') == getattr(eff, 'name', None):
                                found_id = k
                                break
                    # fallback to effect name
                    if not found_id:
                        found_id = getattr(eff, 'name', None)
                    if found_id:
                        active_effect_ids.append(found_id)
                ent_data['active_effects'] = active_effect_ids
            except Exception:
                ent_data['active_effects'] = []

            # Active abilities: map ability objects to ability ids via session.abilities._data
            try:
                active_ability_ids = []
                for ab in getattr(ent, 'game_abilities', {}).values():
                    fid = getattr(ab, 'function_id', None)
                    found_id = None
                    if fid and hasattr(session, 'abilities') and hasattr(session.abilities, '_data'):
                        for k, v in session.abilities._data.items():
                            if v.get('function_id') == fid or v.get('name') == getattr(ab, 'name', None):
                                found_id = k
                                break
                    if not found_id:
                        found_id = getattr(ab, 'name', None)
                    if found_id:
                        active_ability_ids.append(found_id)
                ent_data['active_abilities'] = active_ability_ids
            except Exception:
                ent_data['active_abilities'] = []

            tile_data['ent'] = ent_data
        else:
            tile_data['ent'] = None

        return tile_data

    @staticmethod
    def deserialize_tile(data, x, y, env):
        """Restore a tile's state at map coordinate (x,y) in env."""
        tile = env.map[x][y]
        # Basic attributes
        tile.img_IDs = data.get('img_IDs', tile.img_IDs)
        tile.biome = data.get('biome', tile.biome)
        tile.blocked = data.get('blocked', tile.blocked)
        tile.hidden = data.get('hidden', tile.hidden)
        tile.unbreakable = data.get('unbreakable', tile.unbreakable)
        tile.placed = data.get('placed', getattr(tile, 'placed', False))

        # Restore item if present
        item_id = data.get('item')
        if item_id:
            try:
                item = create_item(item_id)
                place_object(item, [x, y], env)
            except Exception:
                # ignore missing item definitions
                pass

        # Restore entity if present
        ent_data = data.get('ent')
        if ent_data:
            try:
                # Prefer creating by name when available, otherwise try img_IDs
                if ent_data.get('name'):
                    ent = create_entity(ent_data.get('name'))
                elif ent_data.get('img_IDs'):
                    ent = create_entity(ent_data.get('img_IDs'))
                else:
                    ent = None

                # Restore basic properties
                ent.name = ent_data.get('name', getattr(ent, 'name', None))
                ent.role = ent_data.get('role', getattr(ent, 'role', None))
                ent.hp = ent_data.get('hp', getattr(ent, 'hp', None))
                ent.max_hp = ent_data.get('max_hp', getattr(ent, 'max_hp', None))

                # Restore inventory (lightweight)
                for iid in ent_data.get('inventory', []):
                    try:
                        it = create_item(iid)
                        session.items.pick_up(ent, it, silent=True)
                    except Exception:
                        continue

                # Restore equipment
                for slot, iid in ent_data.get('equipment', {}).items():
                    if iid:
                        try:
                            it = create_item(iid)
                            session.items.pick_up(ent, it, silent=True)
                            session.items.toggle_equip(it, silent=True)
                        except Exception:
                            continue

                place_object(ent, [x, y], env)

                # Restore active effects (by id or name)
                try:
                    for eff_key in ent_data.get('active_effects', []):
                        try:
                            eff_id = None
                            if hasattr(session, 'effects') and hasattr(session.effects, '_data'):
                                if eff_key in session.effects._data:
                                    eff_id = eff_key
                                else:
                                    for k, v in session.effects._data.items():
                                        if v.get('name') == eff_key:
                                            eff_id = k
                                            break

                            if eff_id:
                                eff_obj = session.effects.create_effect(ent, eff_id)
                                try:
                                    session.effects.toggle_effect(ent, eff_obj)
                                except Exception:
                                    ent.active_effects[eff_obj.name] = eff_obj
                        except Exception:
                            continue
                except Exception:
                    pass

                # Restore active abilities (by id or name)
                try:
                    for ab_key in ent_data.get('active_abilities', []):
                        try:
                            ab_id = None
                            if hasattr(session, 'abilities') and hasattr(session.abilities, '_data'):
                                if ab_key in session.abilities._data:
                                    ab_id = ab_key
                                else:
                                    for k, v in session.abilities._data.items():
                                        if v.get('name') == ab_key:
                                            ab_id = k
                                            break

                            if ab_id:
                                ab_obj = session.abilities.create_ability(ent, ab_id)
                                try:
                                    session.abilities.toggle_ability(ent, ab_obj)
                                except Exception:
                                    ent.game_abilities[ab_obj.name] = ab_obj
                        except Exception:
                            continue
                except Exception:
                    pass
            except Exception:
                # ignore if entity creation fails
                pass
    
    @staticmethod
    def serialize_room(room):
        """Serialize a Room object."""
        return {
            'name': room.name,
            'biome': room.biome,
            'x1': room.x1,
            'y1': room.y1,
            'x2': room.x2,
            'y2': room.y2,
            'floor_img_IDs': room.floor_img_IDs,
            'wall_img_IDs': room.wall_img_IDs,
            'roof_img_IDs': room.roof_img_IDs,
            'hidden': room.hidden,
            'objects': room.objects,
            'unbreakable': room.unbreakable
        }
    
    @staticmethod
    def deserialize_room(data, env):
        """Deserialize a Room object."""
        room = Room(
            name=data['name'],
            env=env,
            x1=data['x1'],
            y1=data['y1'],
            width=data['x2'] - data['x1'],
            height=data['y2'] - data['y1'],
            biome=data['biome'],
            hidden=data['hidden'],
            objects=data['objects'],
            floor_img_IDs=data['floor_img_IDs'],
            wall_img_IDs=data['wall_img_IDs'],
            roof_img_IDs=data['roof_img_IDs'],
            unbreakable=data['unbreakable']
        )
        return room
    
    @staticmethod
    def serialize_weather(weather):
        """Serialize a Weather object."""
        return {
            'light_set': weather.light_set,
            'cloudy': weather.cloudy,
            'env_date': weather.env.env_date,
            'env_time': weather.env.env_time
        }
    
    @staticmethod
    def deserialize_weather(data, env):
        """Deserialize a Weather object."""
        weather = Weather(env, light_set=data['light_set'], clouds=data['cloudy'])
        env.env_date = data['env_date']
        env.env_time = data['env_time']
        return weather

    @staticmethod
    def serialize_entity(ent):
        """Serialize an Entity into a JSON-friendly dict."""
        data = {
            'name': getattr(ent, 'name', None),
            'role': getattr(ent, 'role', None),
            'hp': getattr(ent, 'hp', None),
            'max_hp': getattr(ent, 'max_hp', None),
            'attack': getattr(ent, 'attack', None),
            'defense': getattr(ent, 'defense', None),
            'player_id': getattr(ent, 'player_id', None),
            'ability_ids': getattr(ent, 'ability_ids', []),
            'inventory': {},
            'equipment': {},
        }

        # Inventory: list of item ids per role
        try:
            for role, lst in getattr(ent, 'inventory', {}).items():
                data['inventory'][role] = [getattr(it, 'id', None) or getattr(it, 'name', None) for it in lst]
        except Exception:
            data['inventory'] = {}

        # Equipment: map slot -> item id
        try:
            for slot, it in getattr(ent, 'equipment', {}).items():
                data['equipment'][slot] = (getattr(it, 'id', None) or getattr(it, 'name', None)) if it else None
        except Exception:
            data['equipment'] = {}

        # Active effects and abilities saved as ids or names
        try:
            data['active_effects'] = [k for k in getattr(ent, 'active_effects', {}).keys()]
        except Exception:
            data['active_effects'] = []

        try:
            data['active_abilities'] = [k for k in getattr(ent, 'game_abilities', {}).keys()]
        except Exception:
            data['active_abilities'] = []

        # Discoveries
        try:
            disc = getattr(ent, 'discoveries', None)
            if disc:
                # Convert Discoveries object to serializable dict of id/name lists
                d_out = {}
                for key, lst in disc.discoveries.items():
                    ids = []
                    for obj in (lst or []):
                        try:
                            ids.append(getattr(obj, 'id', None) or getattr(obj, 'name', None) or str(obj))
                        except Exception:
                            try:
                                ids.append(str(obj))
                            except Exception:
                                continue
                    d_out[key] = ids
                data['discoveries'] = d_out
            else:
                data['discoveries'] = {}
        except Exception:
            data['discoveries'] = {}

        # Location (area name, env name, tile coords)
        try:
            if getattr(ent, 'env', None):
                env = ent.env
                area_name = env.area.name if getattr(env, 'area', None) else None
                env_name = env.name
                if getattr(ent, 'tile', None):
                    tx = int(ent.tile.X // session.pyg.tile_width)
                    ty = int(ent.tile.Y // session.pyg.tile_height)
                    data['location'] = {'area': area_name, 'env': env_name, 'pos': [tx, ty]}
                else:
                    data['location'] = {'area': area_name, 'env': env_name, 'pos': None}
            else:
                data['location'] = None
        except Exception:
            data['location'] = None

        # Per-entity quest logs (optional)
        try:
            data['questlog'] = [EnvironmentSerializer.serialize_quest(q) for q in (getattr(ent, 'questlog').values() if getattr(ent, 'questlog', None) else [])]
        except Exception:
            data['questlog'] = []

        try:
            data['envlog'] = [EnvironmentSerializer.serialize_quest(q) for q in (getattr(ent, 'envlog').values() if getattr(ent, 'envlog', None) else [])]
        except Exception:
            data['envlog'] = []

        try:
            data['gardenlog'] = [EnvironmentSerializer.serialize_quest(q) for q in (getattr(ent, 'gardenlog').values() if getattr(ent, 'gardenlog', None) else [])]
        except Exception:
            data['gardenlog'] = []

        return data

    @staticmethod
    def deserialize_entity(data, attach_to=None):
        """Recreate an Entity from serialized dict. If `attach_to` (Environment) is provided, place entity in that env."""
        from entities import create_entity, create_NPC

        ent = None
        try:
            name = data.get('name') if data else None
            img_IDs = data.get('img_IDs') if data else None

            # Prefer creating by image ID tuple/list if available
            if img_IDs:
                try:
                    ent = create_entity(img_IDs)
                except Exception:
                    ent = None

            # If not created by img, try name-based creation
            if not ent and name:
                try:
                    # NPCs may be created via create_NPC; try that first
                    ent = create_NPC(name)
                except Exception:
                    ent = None

                if not ent:
                    try:
                        ent = create_entity(name)
                    except Exception:
                        ent = None

            # Special-case player fallback: create a default skin and set name
            if not ent and name == 'player':
                try:
                    ent = create_entity('white')
                    ent.name = 'player'
                except Exception:
                    ent = None

        except Exception:
            ent = None

        if not ent:
            return None

        # Basic stats
        ent.hp = data.get('hp', getattr(ent, 'hp', None))
        ent.max_hp = data.get('max_hp', getattr(ent, 'max_hp', None))
        ent.attack = data.get('attack', getattr(ent, 'attack', None))
        ent.defense = data.get('defense', getattr(ent, 'defense', None))
        if data.get('player_id'):
            ent.player_id = data.get('player_id')

        # Restore inventory
        try:
            for role, ids in data.get('inventory', {}).items():
                for iid in ids:
                    try:
                        it = create_item(iid)
                        session.items.pick_up(ent, it, silent=True)
                    except Exception:
                        continue
        except Exception:
            pass

        # Restore equipment
        try:
            for slot, iid in data.get('equipment', {}).items():
                if iid:
                    try:
                        it = create_item(iid)
                        session.items.pick_up(ent, it, silent=True)
                        session.items.toggle_equip(it, silent=True)
                    except Exception:
                        continue
        except Exception:
            pass

        # Attach active effects/abilities by name or id
        try:
            for eff_key in data.get('active_effects', []):
                try:
                    if hasattr(session, 'effects') and hasattr(session.effects, '_data'):
                        if eff_key in session.effects._data:
                            eff_obj = session.effects.create_effect(ent, eff_key)
                        else:
                            # try find by name
                            found = None
                            for k, v in session.effects._data.items():
                                if v.get('name') == eff_key:
                                    found = k
                                    break
                            if found:
                                eff_obj = session.effects.create_effect(ent, found)
                            else:
                                continue
                        try:
                            session.effects.toggle_effect(ent, eff_obj)
                        except Exception:
                            ent.active_effects[eff_obj.name] = eff_obj
                except Exception:
                    continue
        except Exception:
            pass

        try:
            for ab_key in data.get('active_abilities', []):
                try:
                    if hasattr(session, 'abilities') and hasattr(session.abilities, '_data'):
                        if ab_key in session.abilities._data:
                            ab_obj = session.abilities.create_ability(ent, ab_key)
                        else:
                            found = None
                            for k, v in session.abilities._data.items():
                                if v.get('name') == ab_key:
                                    found = k
                                    break
                            if found:
                                ab_obj = session.abilities.create_ability(ent, found)
                            else:
                                continue
                        try:
                            session.abilities.toggle_ability(ent, ab_obj)
                        except Exception:
                            ent.game_abilities[ab_obj.name] = ab_obj
                except Exception:
                    continue
        except Exception:
            pass

        # Restore discoveries
        try:
            if data.get('discoveries'):
                from entities import Discoveries
                d = Discoveries()
                d.discoveries = data.get('discoveries')
                ent.discoveries = d
        except Exception:
            pass

        # Restore per-entity quest logs (questlog/envlog/gardenlog)
        try:
            if data.get('questlog'):
                ent.questlog = {}
                for qdata in data.get('questlog'):
                    try:
                        q = EnvironmentSerializer.deserialize_quest(qdata)
                        ent.questlog[q.name] = q
                    except Exception:
                        continue
        except Exception:
            pass

        try:
            if data.get('envlog'):
                ent.envlog = {}
                for qdata in data.get('envlog'):
                    try:
                        q = EnvironmentSerializer.deserialize_quest(qdata)
                        ent.envlog[q.name] = q
                    except Exception:
                        continue
        except Exception:
            pass

        try:
            if data.get('gardenlog'):
                ent.gardenlog = {}
                for qdata in data.get('gardenlog'):
                    try:
                        q = EnvironmentSerializer.deserialize_quest(qdata)
                        ent.gardenlog[q.name] = q
                    except Exception:
                        continue
        except Exception:
            pass

        # If an environment is provided, place entity in it at its last known tile (if present)
        # If attach_to provided externally, place there; otherwise place according to serialized location
        placed = False
        if attach_to:
            try:
                cx, cy = attach_to.center
                place_object(ent, [int(cx), int(cy)], attach_to)
                placed = True
            except Exception:
                placed = False

        if (not placed) and data.get('location'):
            try:
                loc = data.get('location')
                if loc and loc.get('area') and loc.get('env') and loc.get('pos'):
                    area_name = loc.get('area')
                    env_name = loc.get('env')
                    pos = loc.get('pos')
                    env_obj = None
                    # Find env object in current session or provided attach_to's envs
                    if hasattr(session, 'player_obj') and getattr(session.player_obj, 'envs', None):
                        try:
                            area_obj = session.player_obj.envs.areas.get(area_name)
                            if area_obj:
                                env_obj = area_obj.levels.get(env_name)
                        except Exception:
                            env_obj = None

                    # Fallback: if attach_to is an Environment, use it
                    if not env_obj and isinstance(attach_to, Environment):
                        env_obj = attach_to

                    if env_obj and pos:
                        place_object(ent, [int(pos[0]), int(pos[1])], env_obj)
            except Exception:
                pass

        return ent

    @staticmethod
    def serialize_player(player_obj):
        """Serialize PlayerData (session.player_obj) into a dict for JSON saving."""
        data = {
            'file_num': getattr(player_obj, 'file_num', None),
            'ent': EnvironmentSerializer.serialize_entity(getattr(player_obj, 'ent', None)) if getattr(player_obj, 'ent', None) else None,
            'envs': None,
        }

        try:
            envs = player_obj.envs
            envs_data = {
                'room_max_size': envs.room_max_size,
                'room_min_size': envs.room_min_size,
                'max_rooms': envs.max_rooms,
                'areas': {name: EnvironmentSerializer.serialize_area(area) for name, area in envs.areas.items()}
            }
            data['envs'] = envs_data
        except Exception:
            data['envs'] = None

        # Dialogue state
        try:
            if getattr(player_obj, 'dialogue', None):
                data['dialogue'] = getattr(player_obj.dialogue, 'npc_states', {})
            else:
                data['dialogue'] = {}
        except Exception:
            data['dialogue'] = {}

        # Garden log (player-level questlog)
        try:
            data['gardenlog'] = [EnvironmentSerializer.serialize_quest(q) for q in (getattr(player_obj, 'gardenlog').active_quests if getattr(player_obj, 'gardenlog', None) else [])]
        except Exception:
            data['gardenlog'] = []

        # Cache flag (used by various systems)
        try:
            data['cache'] = getattr(player_obj, 'cache', False)
        except Exception:
            data['cache'] = False

        # Stats (pet levels/moods)
        try:
            if hasattr(session, 'stats_obj') and session.stats_obj:
                data['stats'] = {
                    'pet_levels': getattr(session.stats_obj, 'pet_levels', {}),
                    'pet_moods': getattr(session.stats_obj, 'pet_moods', {})
                }
            else:
                data['stats'] = {}
        except Exception:
            data['stats'] = {}

        return data

    @staticmethod
    def deserialize_player(data):
        """Recreate PlayerData from serialized dict. Returns a PlayerData instance."""
        from entities import PlayerData

        player = PlayerData()
        player.file_num = data.get('file_num')

        # Recreate envs first so entities can be placed into them
        try:
            if data.get('envs'):
                envs_data = data.get('envs')
                envs = Environments(player)
                envs.room_max_size = envs_data.get('room_max_size', envs.room_max_size)
                envs.room_min_size = envs_data.get('room_min_size', envs.room_min_size)
                envs.max_rooms = envs_data.get('max_rooms', envs.max_rooms)
                for name, area_data in envs_data.get('areas', {}).items():
                    try:
                        area = EnvironmentSerializer.deserialize_area(area_data, envs)
                        envs.areas[name] = area
                    except Exception:
                        continue
                player.envs = envs
        except Exception:
            player.envs = None

        # Recreate entity (place into env if location provided)
        if data.get('ent'):
            ent_data = data.get('ent')
            ent = None
            try:
                # If location references exist, find env to attach_to
                loc = ent_data.get('location') if ent_data else None
                attach_env = None
                if loc and loc.get('area') and loc.get('env') and player.envs:
                    try:
                        area_obj = player.envs.areas.get(loc.get('area'))
                        if area_obj:
                            attach_env = area_obj.levels.get(loc.get('env'))
                    except Exception:
                        attach_env = None

                ent = EnvironmentSerializer.deserialize_entity(ent_data, attach_to=attach_env)
                player.ent = ent
            except Exception:
                player.ent = ent

        # Re-subscribe runtime hooks and rebuild runtime-only state
        try:
            # Dialogue subscriptions
            if getattr(player, 'dialogue', None) and hasattr(player.dialogue, '_subscribe_events'):
                try:
                    player.dialogue._subscribe_events()
                except Exception:
                    pass

            # Gardenlog / questlogs
            if getattr(player, 'gardenlog', None) and hasattr(player.gardenlog, '_subscribe_events'):
                try:
                    player.gardenlog._subscribe_events()
                except Exception:
                    pass

            # Area questlogs
            if getattr(player, 'envs', None):
                for area in player.envs.areas.values():
                    try:
                        if getattr(area, 'questlog', None) and hasattr(area.questlog, '_subscribe_events'):
                            area.questlog._subscribe_events()
                    except Exception:
                        pass

                    # Rebuild weather surfaces if needed
                    try:
                        for env in area.levels.values():
                            if getattr(env, 'weather', None) and hasattr(env.weather, '__getstate__') and hasattr(env.weather, '__setstate__'):
                                try:
                                    state = env.weather.__getstate__()
                                    env.weather.__setstate__(state)
                                except Exception:
                                    pass

                            # Ensure camera references the player entity
                            try:
                                if getattr(player, 'ent', None):
                                    env.camera = Camera(player.ent)
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pass

        # Restore dialogue state
        try:
            if data.get('dialogue'):
                from entities import Dialogue
                player.dialogue = Dialogue()
                player.dialogue.npc_states = data.get('dialogue')
            else:
                player.dialogue = None
        except Exception:
            player.dialogue = None

        # Restore gardenlog
        try:
            if data.get('gardenlog'):
                player.gardenlog = Questlog()
                for qdata in data.get('gardenlog'):
                    try:
                        q = EnvironmentSerializer.deserialize_quest(qdata)
                        player.gardenlog.active_quests.append(q)
                    except Exception:
                        continue
        except Exception:
            player.gardenlog = None

        # Restore cache flag
        try:
            player.cache = data.get('cache', False)
        except Exception:
            player.cache = False

        # Restore stats
        try:
            stats = data.get('stats')
            if stats and hasattr(session, 'stats_obj') and session.stats_obj:
                session.stats_obj.pet_levels = stats.get('pet_levels', session.stats_obj.pet_levels)
                session.stats_obj.pet_moods = stats.get('pet_moods', session.stats_obj.pet_moods)
        except Exception:
            pass

        return player

class FileMenu:
    
    def save_account(self):
        """ Pickles a Player object and takes a screenshot. """

        from pygame_utilities import screenshot
        pyg = session.pyg

        #########################################################
        # Add asterisk to active option
        for i in range(len(self.choices)):
            if self.choices[i][-1] == '*': self.choices[i] = self.choices[i][:-2]
        self.choices[self.choice] += ' *'
        self.choice_surfaces = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]
        
        #########################################################
        # Save data from current player
        file_num = self.choice + 1
        session.player_obj.file_num = file_num

        # JSON save (new) - partition envs into separate files
        try:
            save_base = Path(f"Data/File_{file_num}")
            save_base.mkdir(parents=True, exist_ok=True)
            data = EnvironmentSerializer.serialize_player(session.player_obj)

            # If envs present, write each area and environment into separate files
            envs = data.pop('envs', None)
            if envs:
                envs_meta = {
                    'room_max_size': envs.get('room_max_size'),
                    'room_min_size': envs.get('room_min_size'),
                    'max_rooms': envs.get('max_rooms'),
                    'areas': {}
                }

                envs_dir = save_base / 'envs'
                for area_name, area_data in envs.get('areas', {}).items():
                    area_dir = envs_dir / area_name
                    area_dir.mkdir(parents=True, exist_ok=True)

                    # Save each level as its own file
                    levels = {}
                    for level_name, level_data in area_data.get('levels', {}).items():
                        level_path = area_dir / f"{level_name}.json"
                        try:
                            with open(level_path, 'w', encoding='utf-8') as lf:
                                json.dump(level_data, lf, indent=2)
                            levels[level_name] = str(level_path.relative_to(save_base).as_posix())
                        except Exception:
                            continue

                    # Save minimal area metadata (permadeath, questlog summary, levels list)
                    area_meta = {k: v for k, v in area_data.items() if k != 'levels'}
                    area_meta['levels'] = list(levels.keys())
                    try:
                        with open(area_dir / 'area.json', 'w', encoding='utf-8') as af:
                            json.dump(area_meta, af, indent=2)
                    except Exception:
                        pass

                    envs_meta['areas'][area_name] = {'levels': levels, 'meta_file': str((area_dir / 'area.json').relative_to(save_base).as_posix())}

                # Write envs metadata to main save dir
                try:
                    with open(save_base / 'envs_metadata.json', 'w', encoding='utf-8') as em:
                        json.dump(envs_meta, em, indent=2)
                except Exception:
                    pass

            # Write lightweight player file (without embedded full envs)
            save_path = save_base / 'session.player_obj.json'
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

        # Also keep legacy pickle for compatibility
        try:
            with open(f"Data/File_{file_num}/session.player_obj.pkl", 'wb') as file:
                pickle.dump(session.player_obj, file)
        except Exception:
            pass
        
        #########################################################
        # Take a screenshot
        screenshot(
            folder   = f"Data/File_{file_num}",
            filename = "screenshot.png",
            blur     = True)
        self.backgrounds_render = [pygame.image.load(path).convert() for path in self.backgrounds]

    def load_account(self):
        """ Loads a pickled Player object. """
        
        pyg = session.pyg
        
        ## Update event bus
        session.bus.clear()

        #########################################################
        # Add asterisk to active option
        for i in range(len(self.choices)):
            if self.choices[i][-1] == '*':
                self.choices[i] = self.choices[i][:-2]
        self.choices[self.choice] += ' *'
        self.choice_surfaces = [pyg.font.render(choice, True, pyg.gray) for choice in self.choices]

        #########################################################
        # Load data onto fresh player
        session.player_obj.__init__()

        file_num = self.choice + 1
        json_path = f"Data/File_{file_num}/session.player_obj.json"
        pkl_path  = f"Data/File_{file_num}/session.player_obj.pkl"

        loaded = False
        # Try JSON first (supports partitioned envs)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reconstruct envs from partitioned files if present
            save_base = Path(f"Data/File_{file_num}")
            meta_path = save_base / 'envs_metadata.json'
            if meta_path.exists():
                try:
                    with open(meta_path, 'r', encoding='utf-8') as mf:
                        envs_meta = json.load(mf)
                    envs_data = {
                        'room_max_size': envs_meta.get('room_max_size'),
                        'room_min_size': envs_meta.get('room_min_size'),
                        'max_rooms': envs_meta.get('max_rooms'),
                        'areas': {}
                    }
                    for area_name, area_info in envs_meta.get('areas', {}).items():
                        area_dir = save_base / 'envs' / area_name
                        # load area metadata if exists
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
                            except Exception:
                                continue

                        area_meta['levels'] = levels
                        envs_data['areas'][area_name] = area_meta

                    data['envs'] = envs_data
                except Exception:
                    pass

            session.player_obj = EnvironmentSerializer.deserialize_player(data)
            loaded = True
        except Exception:
            loaded = False

        # Fallback to pickle for older saves
        if not loaded:
            try:
                with open(pkl_path, 'rb') as file:
                    session.player_obj = pickle.load(file)
                    loaded = True
            except Exception:
                loaded = False

        if not loaded:
            # If neither worked, leave a fresh player_obj initialized earlier
            pass
        
        #########################################################
        # Clean up and return
        ## Check if dead
        if getattr(session.player_obj, 'ent', None) and getattr(session.player_obj.ent, 'dead', False):
            try:
                session.play_game_obj.death_checked = True
            except Exception:
                pass

        ## Update zoom (if player present)
        try:
            if getattr(session.player_obj, 'ent', None) and getattr(session.player_obj.ent, 'env', None) and getattr(session.player_obj.ent.env, 'camera', None):
                session.player_obj.ent.env.camera.zoom_in(factor=0)
        except Exception:
            pass

        ## Update gamestate
        pyg.msg_history    = {}
        pyg.gui_toggle     = True
        pyg.msg_toggle     = True
        pyg.startup_toggle = False
        pyg.game_state     = 'play_game'

def test_serialization_roundtrip():
    """Build a minimal Environment, serialize and deserialize it, and print comparison."""
    import session
    import pygame

    # Minimal pyg mock
    class PygMock:
        pass
    pyg = PygMock()
    pyg.tile_width = 32
    pyg.tile_height = 32
    pyg.screen_width = 64
    pyg.screen_height = 64
    session.pyg = pyg

    # Provide minimal session bus to satisfy Questlog subscriptions
    class BusMock:
        def subscribe(self, *a, **k): pass
        def emit(self, *a, **k): pass
    session.bus = BusMock()

    # Create envs and area
    envs = Environments(player_obj=None)
    area = Area('test_area', envs, permadeath=False)

    # Build a simple environment (provide valid img_IDs)
    env = Environment(
        envs=envs,
        name='test_env',
        size=1,
        soundtrack=[],
        lvl_num=0,
        wall_img_IDs=['walls', 'gray'],
        floor_img_IDs=['floors', 'grass4'],
        roof_img_IDs=None,
        blocked=False,
        hidden=False,
        img_IDs=['floors', 'grass4'],
        area=area)

    env.weather = Weather(env, light_set=0, clouds=False)

    # Provide minimal items/effects systems used when placing objects
    from items import ItemSystem
    session.items = ItemSystem()
    class EffectsMock:
        def toggle_effect(self, *a, **k): pass
    session.effects = EffectsMock()

    # Place an item and an entity onto the map
    try:
        item = create_item('shovel')
        place_object(item, [1, 1], env)
    except Exception:
        # fallback to any created item
        try:
            item = create_item('bald')
            place_object(item, [1, 1], env)
        except Exception:
            item = None

    try:
        ent = create_entity('white')
        place_object(ent, [2, 1], env)
    except Exception:
        ent = None

    data = EnvironmentSerializer.serialize_environment(env)
    env2 = EnvironmentSerializer.deserialize_environment(data, area)

    checks = [
        ('name', env.name, env2.name),
        ('lvl_num', env.lvl_num, env2.lvl_num),
        ('size', env.size, env2.size),
        ('map_dims', (len(env.map), len(env.map[0])), (len(env2.map), len(env2.map[0]))),
        ('tile_sample', env.map[1][1].img_IDs, env2.map[1][1].img_IDs)
    ]

    # Check item and entity preservation
    if item:
        try:
            id_a = getattr(env.map[1][1].item, 'id', getattr(env.map[1][1].item, 'name', None))
            id_b = getattr(env2.map[1][1].item, 'id', getattr(env2.map[1][1].item, 'name', None))
            checks.append(('item_at_1_1', id_a, id_b))
        except Exception:
            checks.append(('item_at_1_1', None, None))

    if ent:
        try:
            ent_a = getattr(env.map[2][1].ent, 'name', None)
            ent_b = getattr(env2.map[2][1].ent, 'name', None)
            checks.append(('ent_at_2_1', ent_a, ent_b))
        except Exception:
            checks.append(('ent_at_2_1', None, None))

    ok = True
    for key, a, b in checks:
        print(f"{key}: {a == b} | {a} -> {b}")
        if a != b:
            ok = False

    print('Roundtrip OK' if ok else 'Roundtrip FAILED')
