import random


class Game(object):
    def __init__(self, channel):
        self.__channel = channel
        self.__players = []
        self.__cpus = 0
        self.__started = False
        self.__games = []
        self.__player_data = []

    def add_players(self, players):
        self.__players += players

    def add_cpus(self, num):
        self.__cpus += num

    def start(self):
        list = self.__players + ["CPU"] * self.__cpus
        random.shuffle(list)
        for i in range(0, len(list), 2):
            self.__games.append(list[i:i + 2])
        print(self.__games)

    def __str__(self):
        return str(self.__players)

g = Game("aldivmsa")
g.add_players(["hi","yes","no"])
g.add_cpus(12)
g.start()