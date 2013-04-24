
class CommandWords:
    
    def __init__(self):
        self.instance = ['look', 'go', 'take', 'drop', 'inventory', 'jump', 'talk']
    def is_command(self, command):
        return command in self.instance
