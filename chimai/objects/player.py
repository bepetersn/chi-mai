import actor

class Player(actor.Actor):
    
    def __init__(self,name="",current_room=None,description="",
                inventory=[],conversation=None):
        actor.Actor.__init__(self, name, current_room, description,
            inventory, conversation)

    def add_to_inventory(self, item):
        if item:
            self.items.append(item)
            print "%s added to inventory" % item.name
        else:
            print "take what?"

    def remove_from_inventory(self, item):
        if item:
            self.items.remove(item)
            print "%s removed from inventory" % item.name
        else:
            print "do that to what?"

    def set_current_room(self, room):
        if room:
            self.location = room
            room.describe()
        else:
            print "go where?"

    def converse_with(self, person):
        if type(person) == type(actor.Actor("", "", "", "", "")):
            print person.name, "says hi."
        else:
            print "you can't talk to that." 

    def __repr__(self):
        return "Player: <name: '%s', current_room: '%s'>" % (self.name, self.location)