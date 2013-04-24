import game_object
import container

""" Room class """

class Room(game_object.GameObject, container.Container):

    def __init__(self, id, name="name", description="desc", items=[], exits=[]):
        game_object.GameObject.__init__(self, name, self, description)
        container.Container.__init__(self, items)
        self.id = id
        self.exits = exits

    def add_exit(self, exit):
	    self.exits.append(exit)

    def is_accessible_from(self, other_room):
        return other_room.id in [exit.end for exit in self.exits]

    def __repr__(self):
        return ("Room: \nname: '%s', \ndescription: '%s', \nid: '%s'>"
            "\nitems: {%s}, \nexits: {%s}" % (self.name, self.description[:50],
            str(self.id), self.items, self.exits))