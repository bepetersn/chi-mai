import os.isfile
import pickle

## INCOMPLETE

def get_filename():
	maps = glob.glob('../maps/*.pkl')
	print "Which map do want to edit?"
	print "Possibilities: "
    for map in maps:
        print map[8:]
    while True:
        map = '../maps/' + raw_input()
        if not isfile(map):
            print "that's not a map!"
        else:
            return filename

def get_map():
    with open(map_name) as f:
    	return pickle.load(f)
		
def prompt(a_str):
	return raw_input(a_str + '\n')

def yes_no(a_str):
	"Type 'yes' or just 'y' to say so."
	return prompt(a_str).lower()

#####################

def get_property(property, object):

	return properties[property](object)

def get_name(object):

	return prompt("What would you like to name the %s?" % object)

def get_desc(object):

	return prompt("Enter a description for the %s:" % object)

def get_aliases(object):
	answer = prompt("Any aliases? If so, say yes.")
	aliases = []
	while answer in affirm:
		aliases.append(prompt("What is the %s's alias?" % object))
		answer = prompt("Does it have another? If so, say yes.")
	return aliases

def get_item_type(object):
	return prompt(("What kind of %s is it?" 
	"\nPossibilities: fix, move, take, equip, consume") % object)

def get_exit_dir(object):
	return prompt(
		"Direction, from %s to %s:\n example: 'north'," 
		"'east', 'southwest'" % object)

######################

properties = {
	'name': get_name,
	'description': get_desc,
	'aliases': get_aliases,
	'item_type': get_item_type,
	'dir': get_exit_dir
	}

item_types = {
	'fix': fix.Fixture,
	'move': move.Moveable,
	'take': take.Takeable,
	'consume': consume.Consumable,
	'equip': equip.Equippable
	}

#######################

def prompt_until(map, object, func=lambda x: x, possibilities=None):
	while True:
		name = prompt("Which %s do you want to edit?")
		if possibilities:
			print "Possibilities: %s" % possibilities
		try:
			return func(name, map)
		except:
			print "That's not a room."

def find_room_by_name(name, map):
	for i, room in map.iteritems():
		print "name: '%s', room.name: '%s'" % (name, room.name)
		if room.name == name:
			return i

def create_exits(map, object='exit'):

	print "OK! All rooms entered. Now, which rooms do you want to be connected?"
	print "Add one room per line, in pairs, by their NAMES."

	exit_response = 'y'
	#exit_stack = []

	while exit_response in affirm:

		room1 = prompt('Room 1: ')
		room2 = prompt('Room 2: ')
		
		for i in range(2):

			room1id = find_room_by_name(map, room1)
			room2id = find_room_by_name(map, room2)

			exit = ex.Exit(room1id)
			exit.end = room2id
			exit.name = get_property('name', object)
			exit.dir = get_property('dir', (room1, room2))
			exit.aliases = get_property('aliases', object)
			map[room1id].exits.append(exit)

			room1, room2 = room2, room1

		print "added exits in each room!"
		raw_input()

		exit_response = yes_no("got another pair of rooms to connect? If so, say yes.")
		if exit_response not in affirm:
			exit_response = yes_no("Are you sure you don't want any more exits? If you do, say yes.")

def specialize(item):
	try:
		item_type = get_property('item_type', 'item')
	except KeyError:
		item_type = prompt("Sorry, that's not a type of item. Try again.")
	return item_types[item_type].from_super(item)

def create_items(room, object='item'):
	
	items = []
	#item_stack = []
	item_response = 'y'
	print "Now we'll get some items."
	raw_input()

	while item_response in affirm:
	 
		print "Creating a new item"
		item = o.GameObject("", room.id, "")

		item.name = get_property('name', object)
		item.description = get_property('description', object)
		item.aliases = get_property('aliases', object)
		item = specialize(item)

		#yes_no(("Are you sure this %s is exactly how you want it?"
			#" You will not be able to change it after this point.") % object)

		items.append(item)
		item_response = yes_no("Is there another %s in the room? If so, say yes" % object)
		if item_response not in affirm:
			item_response = yes_no("Are you sure you don't want any more items? If you do, say yes.")

	return items

def edit_rooms(map, object='room'):

	room_response = 'y'
	room_num = 0

	room_response = yes_no("do you want to add a %s? [y/n]" % object)

	while room_response in affirm:

		prompt_until(map, object, find_room_by_name, [room.name for room in map.values()])
		room.name = get_property('name', object)
		room.description = get_property('description', object)
		room.items = create_items(room)
		rooms[room_num] = room
		room_num += 1

		room_response = yes_no("do you want to add another %s? If so, say yes." % object)
		if room_response not in affirm:
			room_response = yes_no("Are you sure you don't want any more rooms? If you do, say yes.")

def edit_map():
	
	print ("We're gonna edit an existing map. It is recommended"
	" that you have a list visible of all the rooms you want"
	" to create, their descriptions, as well as, hopefully," 
	" a picture you can reference. This will make it easier"
	" to create the spatial environment of your map.")

	map = get_map()
	edit_rooms(map)
	edit_exits(map)

	print "All done! Now we just have to save this map to a file."
	raw_input()

	with open(get_filename(), 'w') as f:
		pickle.dump(map, f)

	print "Sucessful map-making!"
	raw_input()

if __name__ == '__main__':
	edit_map()
