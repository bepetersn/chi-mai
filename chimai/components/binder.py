from errors import InaccesibleRoomException, InaccessibleDirException, \
        NoSuchObjectException, NotInInventoryException, ItemNotTakeableException

class Binder:

    def __init__(self, player=None, rooms=None):
        self.player = player
        self.rooms = rooms
        self.dirs = ['north', 'south', 'east', 'west', 'up', 'down', \
                        'northwest', 'northeast', 'southwest', 'southeast']
        self.current_room = player.location
        self.current_exits = self.current_room.exits
        self.current_items = self.current_room.items
        self.current_inventory = self.player.items

    def update(self, player, rooms):
        self.player = player
        self.rooms = rooms
        self.current_room = self.player.location
        self.current_exits = self.current_room.exits
        self.current_items = self.current_room.items
        self.current_inventory = self.player.items

    def check_object_name_is_exit(self, object_name, exit):
        if object_name == exit.name:
            return self.rooms[int(exit.end)]
        for alias in exit.aliases:
            if object_name == alias:
                return self.rooms[int(exit.end)]

    def check_object_name_is_dir(self, object_name, exit):
        if object_name == exit.dir:
            return self.rooms[int(exit.end)]

    def check_object_name_is_room(self, object_name, room):
        if object_name == room.name: 
            return room
        if room.aliases:
            for alias in room.aliases:
                if object_name == alias:
                    return room

    def check_object_name_is_item(self, object_name, item):
        if object_name == item.name:
            if not item.concealed:
                return item
        if item.aliases:
            for alias in item.aliases:
                if object_name == alias:
                    return item

    def get_object(self, object_name, action_name):
        object = None

        checks = [self.check_object_name_is_exit, self.check_object_name_is_dir, 
            self.check_object_name_is_room, self.check_object_name_is_item]

        if action_name == 'go':
            
            for exit in self.current_exits:
                for check in checks[:2]:
                    if check(object_name, exit):
                        return check(object_name, exit)
            
            for room in self.rooms.values():
                if checks[2](object_name, room):
                    return checks[2](object_name, room)

            # if no matching exit, dir, or room is found
            raise InaccessibleDirException()

        if action_name == 'take':

            for item in self.current_items:
                if not item.takeable:
                    raise ItemNotTakeableException(item.name)
                else:
                    if checks[3](object_name, item):
                        return checks[3](object_name, item)

            raise NoSuchObjectException(object_name)

        if action_name == 'drop':

            for item in self.current_inventory:
                if checks[3](object_name, item):
                    return checks[3](object_name, item)

            raise NotInInventoryException(object_name)

        if action_name == 'look':

            all_items = self.current_items
            all_items.extend(self.current_inventory)

            for item in all_items:
                if checks[3](object_name, item):
                    return checks[3](object_name, item)

            raise NoSuchObjectException(object_name)
