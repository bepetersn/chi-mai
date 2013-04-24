import object
import container

class Actor(object.GameObject, container.Container):
    
    def __init__(self, name, current_room, description, items, conversation):
    	object.GameObject.__init__(self, name, current_room, description)
        container.Container.__init__(self, items)
        self.conversation = conversation
        
