import chimai

class CommandWords:
    
    """ All commands have to be defined in this class, as both a string in 
        the 'instance' variable and a function of the same name. """

    def __init__(self):
        self.instance = ['look', 'go', 'take', 'drop', 'inventory', 'jump', 'talk']

    def list_commands(self):
        output  = "Here is a list of commands you have at your disposal: \n"
        num_commands = len(self.instance)
        for i, command in enumerate(self.instance):
            ouput += command
            if i != num_commands-1:
                output += "\n"
        print output

    def get_command(self, verb):
        print verb
        if verb in self.instance:
        	return eval(verb)
        # ridiculous recursive imports forced me to do this:
        raw_input()
        raise chimai.chimai.errors.game_exceptions.UnknownCommandException(verb)

#########################################################
#########################################################

# Define what each command should do here

def go(player, room):
    player.set_current_room(room)

def look(player, game_object):
    if game_object:
        game_object.describe()
    else:
        player.location.describe()

def take(player, game_object):
    player.location.remove_item(game_object)
    player.add_to_inventory(game_object)
    if game_object.conceal:
        game_object.conceal.concealed = False

def drop(player, game_object):
    player.remove_from_inventory(game_object)
    player.location.add_item(game_object)

def inventory(player, val=None):
    for item in player.get_items():
        print item.name
        if item.container:
            for contained_item in item.items:
                print "the %s contains a %s" % (contained_item, item.name)

def jump(player, val=None):
    print "Are you having fun?"

    def talk(player, person):
        if not person:
        	print "Talk about what? Are you going crazy?"
        else:
        	pass