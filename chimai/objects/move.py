import game_object

class Moveable(game_object.GameObject):
    
    def __init__(self, name, location, description, aliases):
        game_object.GameObject.__init__(self, name, location, description, aliases)
        self.moveable = True

    
