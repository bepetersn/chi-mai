import take
import container

class ContainerItem(take.Takeable, container.Container):
    
    def __init__(self, name, current_room, description, items):
        take.Takeable.__init__(self, name, current_room, description)
        container.Container.__init__(self, items)