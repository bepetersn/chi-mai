class Command:

    def __init__(self, verb="", action=None, object=[]):
    	self.verb = verb
    	self.action = action
    	self.object = object

    def is_unknown(self):
		return (self.verb == "")
