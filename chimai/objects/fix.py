import game_object

class Fixture(game_object.GameObject):
    
    def __init__(self, name, current_room, description, aliases):
        game_object.GameObject.__init__(self, name, current_room, description, aliases)