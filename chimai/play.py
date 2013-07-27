from chimai.chimai.objects import Player
from chimai.chimai.components import Parser, Binder, CommandWords
from chimai.chimai.errors import QuitException, GameException

import logging 
import sys
import pickle
import glob
from os.path import isfile

player = Player()
parser = Parser()
binder = Binder()
commands = CommandWords()
rooms = None

def play():
    init()
    while True:
        sys.stdout.write("\n>")
        try: 
            verb, object_name = parser.get_command()
            game_object = binder.get_object(object_name, verb) if object_name else None
        except QuitException:
            break
        except GameException as err:
            print err.message
            continue
        execute(verb, game_object)
        post_process()

    print "Thanks for playing!"

def init():
    global rooms
    map_name = get_map()
    rooms = create_rooms(map_name)
    sys.stdout.write('\n')
    player.set_current_room(rooms[0])
    binder.update(player, rooms)

def get_map():
    maps = glob.glob('../maps/*.pkl')
    print "What map do you want to use?"
    print "Possibilities: "
    for map in maps:
        print map[8:-4]
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

def execute(verb, game_object):
    action = commands.get_command(verb)
    action(player, game_object)

def post_process():
    binder.update(player, rooms)

if __name__ == '__main__':
    play()
