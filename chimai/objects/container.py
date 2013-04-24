class Container(object):
    
    def __init__(self, items):
        self.items = items
        self.container = True
        self.locked = False

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)
