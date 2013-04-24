import take

class Equippable(take.Takeable):
    
    def __init__(self, name, current_room, description):
        take.Takeable.__init__(self, name, current_room, description, aliases)
        self.equippable = True