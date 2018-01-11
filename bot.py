import discord
import asyncio
import os
import threading
import random
import copy

client = discord.Client()

TYPING_SPEED = 0.25
POSTFIX = "~"
IMAGE_DIRS = ["bts"]
postfixes = {}
COLOR = 0x2956b2


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


mafiagames = {

}

# mafia


class MGameManager(object):
    def __init__(self, a, b):
        self.started = False
        self.playerList = []
        self.forced_turns = 0
        self.a = a
        self.b = b
        beginning_timeout = asyncio.get_event_loop()
        beginning_timeout.run_until_complete(self.timeout_start)
        self.leader = b.author
        self.isday = True
        self.time = {
            True: "day",
            False: "night"
        }
        self.force_continue_loop = asyncio.get_event_loop()
        self.not_assigned = []
        self.mafias = 0

    async def game_start(self):
        if len(self.playerList) < 4:
            await client.send_message(self.leader, "There are not enough players; there are only " + str(len(self.playerList)))
        else:
            self.started = True
            await sendMessage("Assigning roles!")
            for i in range (len(self.playerList)):
                self.not_assigned.append(i)
            self.mafias = len(self.playerList) - (len(self.playerList) // 2)
            for i in range (self.mafias):
                mafia_index = random.choice(self.not_assigned)
                self.playerList[mafia_index].playertype = 'mafia'
                await client.send_message(self.playerList[mafia_index].author, 'You are in the mafia. At night, use "mkill [player]~"')
                self.not_assigned.remove(mafia_index)
            # doctor and detective
            doctor = random.choice(self.not_assigned)
            self.playerList[doctor].player_type = 'doctor'
            await client.send_message(self.playerList[doctor].author, 'You are the doctor. At night, use "mheal [player]~"')
            self.not_assigned.remove(doctor)
            detective = random.choice(self.not_assigned)
            self.playerList[detective].player_type = 'detective'
            await client.send_message(self.playerList[doctor].author, 'You are the detective. At night, use "minspect [player]~"')
            self.not_assigned.remove(detective)
            for i in range (len(self.not_assigned)):
                self.not_assigned[i].playertype = 'innocent'
                await client.send_message(self.playerList[i].author, "You are innocent. Don't die!")
            await sendMessage('In the mornings, do "mvote [player]" to vote to lynch someone!', self.b.channel)
        self.night()

    async def day(self):
        await sendMessage("Good morning!", self.b.channel)

    async def night(self):
        await sendMessage("Good night!", self.b.channel)
        self.turn_force = asyncio.get_event_loop()
        self.turn_force.run_until_complete(self.timeout_start)
        self.isday = False
        self.turn_force.stop()

    async def add_player(self, b):
        new_player = MPlayer(b)
        is_new = True
        for i in range (len(self.playerList)):
            if new_player.id == self.playerList[i].id:
                is_new = False
        if is_new:
            self.playerList.append(copy.copy(new_player))
            await client.send_message(b.author, "You have been added to the game!")
        else:
            await client.send_message(b.author, "You were already in the game!")

    async def timeout_start(self):
        asyncio.sleep(300)
        if not self.started and len(self.playerList) < 4:
            await sendMessage("The game has ended due to inactivity!", self.b.channel)
            del self

    async def timeout_restart(self):
        asyncio.sleep(240)
        await sendMessage("60 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        asyncio.sleep(30)
        await sendMessage("30 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        asyncio.sleep(15)
        await sendMessage("15 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        asyncio.sleep(10)
        await sendMessage("5 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        self.forced_turns += 1

    async def delete(self):
        await sendMessage("The game has ended due to inactivity!", self.b.channel)
        del self


class MPlayer(object):
    def __init__(self, player):
        self.is_dead = False
        self.player_type = ""
        self.will_kill = False
        self.will_heal = False
        self.is_done = False
        self.name = player.author.name
        self.id = player.author.id
        self.author = player.author
        self.channel = player.channel

async def mstart(a, b):
    if b.channel.id not in mafiagames.keys():
        mafiagames[b.channel.id] = MGameManager(a, b)
        await mafiagames[b.channel.id].add_player(b)
        await client.send_message(b.author, "Repeat this command if there are 4 or more players to begin!")
    elif b.author.id == mafiagames[b.channel.id].leader.id:
        mafiagames[b.channel.id].started = True
        mafiagames[b.channel.id].game_start()
    else:
        await mafiagames[b.channel.id].add_player(b)

# end of mafia

def getCommand(message):
    things = message[:-1].lower().split()
    command = {
        "name": things[0],
        "params": things[1:]
    }
    return command

async def send(text, channel):
    await client.send_typing(channel)
    await asyncio.sleep(TYPING_SPEED)
    await client.send_message(channel, text)
async def sendMessage(rslt, channel):
    if len(rslt) <= 2000:
        await send(rslt, channel)
    else:
        while len(rslt) > 2000:
            await send(rslt[:1999], channel)
            rslt = rslt[1999:]
        await send(rslt, channel)

async def test(a, b):
    await sendMessage("tested", b.channel)

async def image(a, b):
    await client.send_file(b.channel, a[0] + "/" + random.choice(os.listdir(a[0])))
async def mhelp(a, b):
    await sendMessage("tested", b.channel)
async def rpshelp(a, b):
    await sendMessage("", b.channel)
    # TODO: write the helpy thingy
async def changepostfix(a,b):
    postfixes[b.server.id] = a[0]
    await sendMessage("Postfix changed to: " + a[0], b.channel)


def listToText(list):
    str = ""
    for i in range(len(list)):
        if i != len(list) - 1:
            str += list[i] + ","
        else:
            str += list[i]
    return list[i]

commands = {
    "test":{
        "run": test,
        "desc": "a test"
    },
    # "image":{
    #     "run": image,
    #     "params": "[category]",
    #     "desc": "displays an image from a category. Current categories are: " + listToText(IMAGE_DIRS)
    # },
    "mhelp":{
        "run": mhelp,
        "desc": "Instructions for mafia."
    },
    "rpshelp":{
        "run": rpshelp,
        "desc": "Instructions for rock-paper-scissors tournament"
    },
    "mstart":{
        "run": mstart,
        "desc": "Creates a mafia game and if there is one, adds you."
    },
    "changepostfix":{
        "run": changepostfix,
        "params": "[newpostfix]",
        "desc": "Change the postfix for this bot"
    }
}

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='help~'))

@client.event
async def on_message(message):
    try:
        print("User " + message.author.name + " on Channel " + message.channel.name + " on " + message.server.name + " says " + message.content)
        is_command = message.content.lower().endswith(postfixes.get(message.server.id, POSTFIX)) and not (
        message.author.id == client.user.id)
    except:
        print("User " + message.author.name + " on a Direct Message says " + message.content)
        is_command = False
    if is_command:
        command = getCommand(message.content)
        print(command)
        if command["name"] in list(commands.keys()):
            print("Command " + command["name"] + POSTFIX + " was used!")
            await commands[command["name"]]["run"](command["params"], message)
        elif command["name"] == "help":
            if len(command["params"]) > 0:
                c = command["params"][0]
                if c in list(commands.keys()):
                    embed = discord.Embed(title="Help for " + c,
                                          color=COLOR)
                    embed.add_field(name="Usage:",value=c + (" " + (commands[c].get("params","")) if "param" in list(commands[c].keys()) else "") + postfixes.get(message.server.id, POSTFIX))
                    embed.add_field(name="Description:",value=commands[c]["desc"])
                    await client.send_message(message.channel, embed=embed)
                else:
                    await sendMessage("That's not a valid command!",message.channel)
            else:
                embed = discord.Embed(title="Help",
                                      description="Use help [command]" + postfixes.get(message.server.id,
                                                                                       POSTFIX) + " to get help for a specfic command",
                                      color=COLOR)
                string = ""
                for i in commands:
                    string += i + ", "
                string = string[:-2]
                embed.add_field(name="Here are my commands: ", value=string)
                await client.send_message(message.channel, embed=embed)


        else:
            embed = discord.Embed(title="Help",
                                  description="Use help [command]" + postfixes.get(message.server.id, POSTFIX) + " to get help for a specfic command",
                                  color=COLOR)
            string = ""
            for i in commands:
                string+=i + ", "
            string = string[:-2]
            embed.add_field(name="Here are my commands: ", value = string)
            await client.send_message(message.channel, embed=embed)

client.run('MzkwNTgwOTgxMzE0MDkzMDU2.DRN65Q.-6OaVHeudI3zaPeDAjXWTJMw0Zw')