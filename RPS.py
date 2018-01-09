import random


class RPSPlayer(object):
    def __init__(self, cpu, mention=""):
        self.__points = 0
        self.__mention = mention
        self.__is_CPU = cpu
        self.__play = None

    def win(self):
        self.__points += 1

    def get_play(self):
        # TODO: Change input to discord
        if not self.__is_CPU:
            self.__play = input(str(self) + ", please pick r, p, or s.")
        elif self.__is_CPU:
            choice = random.choice(["r","p","s"])
            self.__play = choice
            print("A CPU picked " + choice)
        return self.__play

    def get_points(self):
        return self.__points

    def __str__(self):
        return ("CPU" if self.__is_CPU else ("Player " + self.__mention))

class RPSGame(object):
    def __init__(self, channel):
        self.__channel = channel
        self.__players = []
        self.__cpus = 0
        self.__started = False
        self.__games = []
        self.__round_count = 0

    def add_players(self, players):
        for i in players:
            self.__players.append(RPSPlayer(False,i))

    def add_cpus(self, num):
        for i in range(num):
            self.__players.append(RPSPlayer(True))

    def start(self):
        passing = 0
        players = []
        for i in self.__players:
            if i.get_points() == self.__round_count:
                passing += 1
                players.append(i)
        while passing > 1:
            # TODO:discord
            self.generate_games()
            print("Current round: %d" % (self.__round_count + 1))
            self.print_games()
            for i in self.__games:
                self.do_game(i)
            self.__round_count += 1
            passing = 0
            players = []
            for i in self.__players:
                if i.get_points() == self.__round_count:
                    passing += 1
                    players.append(i)
            self.__players = players
        print("Winners are " + str(players))

    def generate_games(self):
        list = self.__players
        random.shuffle(list)
        self.__games = []
        for i in range(0, len(list), 2):
            self.__games.append(list[i:i + 2])

    def do_game(self, players):
        if len(players) == 1:
            players[0].win()
        else:
            p1 = players[0].get_play()
            p2 = players[1].get_play()
            while p1 == p2:
                # TODO: discord
                print("That's a tie! Go again!")
                p1 = players[0].get_play()
                p2 = players[1].get_play()
            if (p1 == "r" and p2 == "s") or (p1 == "s" and p2 == "p") or (p1 == "p" and p1 == "r"):
                print(str(players[0]) + " wins!")
                players[0].win()
                print(str(players[0]) + " points: " + str(players[0].get_points()))
            else:
                print(str(players[1]) + " wins!")
                players[1].win()
                print(str(players[1]) + " points: " + str(players[1].get_points()))

    def print_games(self):
        print(self.__games)
        for i in range(len(self.__games)):
            print("Game " + str(i + 1))
            try:
                p2 = str(self.__games[i][1])
            except:
                p2 = "none"
            print("%s vs. %s" % (str(self.__games[i][0]),p2))

    def __str__(self):
        return str(self.__players)

g = RPSGame("aldivmsa")
g.add_players(["hi","yes","no"])
g.add_cpus(1)
g.start()