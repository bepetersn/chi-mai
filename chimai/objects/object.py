
class GameObject(object):
    
    def __init__(self, name="", location=None, description="", aliases=[]):
        self.name = name
        self.location = location
        self.description = description
        self.aliases = aliases

        self.concealed = False
        self.conceal = False

        self.container = False
        self.moveable = False
        self.takeable = False
        self.equippable = False
        self.consumable = False

    @classmethod
    def from_values(cls, name, location, description, aliases=[]):
        return cls(name, location, description, aliases)

    @classmethod
    def from_super(cls, object):
        return cls(object.name, object.location, \
            object.description, object.aliases)

    def describe(self):
        if not self.description:
            print "There is nothing special about the ", self.name
        else:
            print self.description

    def __repr__(self):
        return (type(self).__name__ + " { name: '%s', location: '%s', desc: '%s' }" 
                % (self.name, self.location, 
                   self.description[:35] + '...') )
        
