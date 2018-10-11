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

gameplaycount_d = {}

myplays = bgg.plays(username)

for item in myplays:
    # print '%d %s' % (item.game_id, item.game_name)
    if not item.game_id in gameplaycount_d:
        gameplaycount_d[item.game_id] = 1
    else:
        gameplaycount_d[item.game_id] += 1

# print gameplaycount_d

# for game in gameplaycount_d:
#     print game

for game in sorted(gameplaycount_d.items(), key=lambda x: x[1]):
    # print(game)
    print(bgg.game(game_id=game.key).name)

# print(bgg.game(game_id=36218).name)