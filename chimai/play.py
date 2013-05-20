import objects.player as l
import objects.room as r
import objects.exit as e
import objects.game_object as o
import objects.fix as fix

import components.parser as p
import components.binder as b
import components.commands as cs

from errors import QuitException, GameException

import logging 
import sys
import pickle
import glob

from os.path import isfile

player = l.Player()
rooms = None
commands = cs.CommandWords()
parser = p.Parser()

def play():
    init()
    while True:
        sys.stdout.write("\n>")
        try:
            command = parser.get_command()
        except QuitException:
            break
        except GameException as err:
            print err.message
            continue
        execute(command)
        post_process()

    print "Thanks for playing!"

def init():
    global rooms
    map_name = get_map()
    rooms = create_rooms(map_name)
    sys.stdout.write('\n')

    print rooms

    player.set_current_room(rooms[0])
    parser.actions = create_actions()
    parser.binder = b.Binder(player, rooms)

def get_map():
    maps = glob.glob('../maps/*.pkl')
    print "What map do you want to use?"
    print "Possibilities: "
    for map in maps:
        print map[8:-4] + "    "
    while True:
        map = '../maps/' + raw_input() + '.pkl'
        if not isfile(map):
            print "that's not a map!"
        else:
            return map

def create_rooms(map):
    map_filename = str(map)
    with open(map_filename) as f:
        rooms = pickle.load(f)
    return rooms

def create_actions():
    the_actions = []
    for command in commands.instance:
        the_actions.append((command, actions[command]))
    return the_actions

def execute(command):
    command.action(command.object)

def post_process():
    parser.binder.update(player, rooms)

###########################################
###########################################

def go(room):
    player.set_current_room(room)

def look(object):
    if object:
        object.describe()
    else:
        player.location.describe()

def take(object):
    player.location.remove_item(object)
    player.add_to_inventory(object)
    if object.conceal:
        conceal.concealed = False

def drop(object):
    player.remove_from_inventory(object)
    player.location.add_item(object)

def inventory(val=None):
    for item in player.get_items():
        print item.name
        if item.container:
            for contained_item in item.items:
                print "the %s contains a %s" % (contained_item, item.name)

def jump(val=None):
    print "Are you having fun?"

def talk(person):
    pass

def climb():
    pass

def read():
    pass

def say():
    pass

def attack():
    pass

actions = {
    'go': go,
    'look': look,
    'take': take,
    'drop': drop,
    'inventory': inventory,
    'jump': jump,
    'talk': talk,
    'climb': climb,
    'read': read,
    'say': say,
    'attack': attack,
}

###############################################
###############################################


if __name__ == '__main__':
    play()
