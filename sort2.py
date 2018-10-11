#!/usr/bin/python
import json

class Game:
    id = None
    name = None
    plays = None

    def __init__(self, id, name, plays):
        self.id = id
        self.name = name
        self.plays = plays

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def get_name(self):
        # print 'Game name is %s' % self.name
        return self.name

    def get_plays(self):
        # print 'Play count is %d' % self.plays
        return self.plays

    def add_play(self):
        self.plays += 1

# g = Game(0, 'Catan', 1)

# g.get_plays()
# g.add_play()
# g.get_plays()

my_list = []
my_list.append(Game(0, 'Catan', 1))
my_list.append(Game(1, 'Dominion', 1))

my_list[0].add_play()

# for item in my_list:
#     print "You have played %s %d times." % (item.get_name(), item.get_plays())

with open('your_file.csv', 'w') as f:
    for item in my_list:
        print "You have played %s %d times." % (item.get_name(), item.get_plays())
        f.write("%s,%d\n" % (item.get_name(), item.get_plays()))

# print(my_list[0].toJSON())

print json.dumps(my_list)