from boardgamegeek import BGGClient

username = 'otteydw'

# class Game:
#     id = None
#     name = None
#     plays = None

#     def __init__(self, id, name, plays):
#         self.id = id
#         self.name = name
#         self.plays = plays

#     def get_name(self):
#         print 'Game name is %s' % self.name

#     def get_plays(self):
#         print 'Play count is %d' % self.plays

#     def add_play(self):
#         self.plays += 1


# g = Game(0, 'Catan', 1)

# g.get_plays()
# g.add_play()
# g.get_plays()

# my_list = [g]

# print my_list
# for item in my_list:
#     item.get_name()


bgg = BGGClient()

# mygame = bgg.game('Catan')
# print mygame.name
# print mygame.id

myplays = bgg.plays(username)

for item in myplays:
    print '%d %s' % (item.game_id, item.game_name)