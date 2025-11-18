########################################################################################################################################################
# Item creation and management
# There are no effects here -- only generic tools.
#
########################################################################################################################################################

########################################################################################################################################################
# Imports
## Standard

## Local
import session
from environments import place_object, create_tile
from entities import create_entity
from items import create_item

########################################################################################################################################################

########################################################################################################################################################
# Classes
def Discoveries():
    
    def __init__(self):
        self.walls     = {}
        self.floors    = {}
        self.stairs    = {}
        self.decor     = {}
        self.furniture = {}
        self.paths     = {}
        self.entities  = {}

def DiscoverySystem():

    def add_discovery(self, object_ID, ent=False, item=False, tile=False):
        if ent:    self._add_entity(object_ID)
        elif item: self._add_item(object_ID)
        elif tile: self._add_tile(object_ID)
        
    def _add_entity(self, object_ID):

        ent = create_entity(
            names = self.img_IDs.copy())

        place_object(
            obj   = ent,
            loc   = [self.img_x, self.img_y],
            env   = session.player_obj.ent.env,
            names = self.img_IDs.copy())
        
    def _add_item(self, object_ID):

        item = create_item(
            names = self.img_IDs)
        
        place_object(
            obj   = item,
            loc   = [self.img_x, self.img_y],
            env   = session.player_obj.ent.env,
            names = self.img_IDs.copy())
        
        if item.img_IDs[0] == 'stairs':
            item.tile.blocked = False

    def _add_tile(self, object_ID):

        obj = session.player_obj.ent.env.map[self.img_x][self.img_y]
        obj.placed = True

        place_object(
            obj = obj,
            loc = [self.img_x, self.img_y],
            env = session.player_obj.ent.env,
            names = self.img_IDs.copy())

        # Check if it completes a room
        if self.img_IDs[0] == 'walls':
            session.player_obj.ent.env.build_room(obj)
        
########################################################################################################################################################