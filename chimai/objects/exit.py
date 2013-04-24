import game_object

class Exit(game_object.GameObject):
	def __init__(self, location, name="exit", description="", dir="inward", end="where you began"):
		game_object.GameObject.__init__(self, name, location, description)
		self.dir = dir
		self.end = end

	def __repr__(self):
		return ("Exit: <name: '%s', direction: '%s', room you end in: '%s'>" % 
				(self.name, self.dir, str(self.end)))
