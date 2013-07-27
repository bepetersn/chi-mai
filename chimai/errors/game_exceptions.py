from chimai.chimai.components.commands import CommandWords

class GameException(Exception):
	def __init__(self):
		self.message = ""

class FailedParseException(GameException):
    def __init__(self):
    	self.message = "Sorry, I don't understand that sentence. "

class NoCommandException(GameException):
    def __init__(self):
        self.message = "What should we do?"

class UnknownWordException(GameException):
    def __init__(self, word): 
        self.message = "I don't know the word \"%s\"." % word

class InaccessibleDirException(GameException):
    def __init__(self):
    	self.message = "What's that? You can't go that way right now."

class InaccesibleRoomException(GameException):
    def __init__(self):
    	self.message = "You can't get to that room right now. "

class NoSuchObjectException(GameException):
    def __init__(self, object):
        self.message = "You don't see any %s here." % object

class NotInInventoryException(GameException):
    def __init__(self, object):
        self.message = "You're not holding a %s." % object

class UnknownCommandException(GameException):
    def __init__(self, verb):
        self.message = "The verb \"%s\" is not a command." % verb
        if verb == 'quit':
            self.message += (" Unless you were trying to exit the game." 
                " In that case, type 'quit' again, without any trailing words.")
        if verb == 'help':
            self.message += (" Unless you were trying to get help."
                " In that case, type 'help' again, without any trailing words.")

class HelpException(GameException):
    def __init__(self):
        cs = CommandWords()
        self.message = cs.list_commands()

class ItemNotTakeableException(GameException):
    def __init__(self, object_name):
        self.message = "You can't take the %s!" % object_name