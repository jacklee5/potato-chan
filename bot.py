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

rps_games = {}
rps_dms = {}


class RPSPlayer(object):
    def __init__(self, cpu, user=discord.User()):
        self.__points = 0
        self.__user = user
        self.id = user.id
        self.is_CPU = cpu
        self.__play = None
        self.__mention = user.mention

    def win(self):
        self.__points += 1

    async def get_reaction_message(self):
        # TODO: Change input to discord
        if not self.is_CPU:
            message = await client.send_message(self.__user, str(self) + " please react with your choice!")
            await client.add_reaction(message, "💎")
            await client.add_reaction(message, "📜")
            await client.add_reaction(message, "✂")
            return message.id
            # self.__play = input(str(self) + ", please pick r, p, or s.")
        elif self.is_CPU:
            choice = random.choice(["r","p","s"])
            self.__play = choice
            print("A CPU picked " + choice)

    def get_points(self):
        return self.__points

    def __str__(self):
        return ("CPU" if self.is_CPU else ("Player " + self.__mention))


class RPSGame(object):
    def __init__(self, channel, message):
        self.channel = channel
        self.__players = []
        self.users = []
        self.__cpus = 0
        self.started = False
        self.__games = []
        self.__round_count = 0
        self.creator = message.author
        self.reaction_data = {}

    def add_players(self, players):
        for i in players:
            self.__players.append(RPSPlayer(False,i))
            self.users.append(i)

    def add_cpus(self, num):
        for i in range(num):
            self.__players.append(RPSPlayer(True))

    async def start(self):
        self.started = True
        passing = 0
        players = []
        for i in self.__players:
            if i.get_points() == self.__round_count:
                passing += 1
                players.append(i)
        while passing > 1:
            # TODO:discord
            self.generate_games()
            await sendMessage("**Round %d**" % (self.__round_count + 1),self.channel)
            await self.print_games()
            for i in self.__games:
                await self.do_game(i)
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

    async def do_game(self, players):
        if len(players) == 1:
            players[0].win()
        else:
            players[0].get_reaction_message()
            players[1].get_reaction_message()
            if not players[0].is_CPU:
                rps_games[players[0].get_reaction_message()] = {"player":players[0],"game":self}
            else:
                players[0].get_reaction_message()
            if not players[1].is_CPU:
                rps_games[players[1].get_reaction_message()] = {"player":players[1],"game":self}
            else:
                players[1].get_reaction_message()
            # await players[0].get_play()
            # await players[1].get_play()
            # p1 = await players[0].get_play()
            # p2 = await players[1].get_play()
            # while p1 == p2:
            #     # TODO: discord
            #     print("That's a tie! Go again!")
            #     p1 = await players[0].get_play()
            #     p2 = await players[1].get_play()
            # if (p1 == "r" and p2 == "s") or (p1 == "s" and p2 == "p") or (p1 == "p" and p1 == "r"):
            #     print(str(players[0]) + " wins!")
            #     players[0].win()
            #     print(str(players[0]) + " points: " + str(players[0].get_points()))
            # else:
            #     print(str(players[1]) + " wins!")
            #     players[1].win()
            #     print(str(players[1]) + " points: " + str(players[1].get_points()))

    async def print_games(self):
        for i in range(len(self.__games)):
            try:
                p2 = str(self.__games[i][1])
            except:
                p2 = "none"
            await sendMessage("%s vs. %s" % (str(self.__games[i][0]),p2),self.channel)

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
        # beginning_timeout.run_until_complete(self.timeout_start)
        self.leader = b.author
        self.isday = True
        self.time = {
            True: "day",
            False: "night"
        }
        self.force_continue_loop = asyncio.get_event_loop()
        self.mafias = 0
        self.mafia_playerList = []
        self.me = b.server.me

    async def game_start(self):
        if len(self.playerList) < 4:
            await client.send_message(self.leader, "There are not enough players; there are only " + str(len(self.playerList)))
        else:
            self.turn_force = asyncio.get_event_loop()
            self.turn_task = self.turn_force.create_task(self.timeout_restart())
            await sendMessage("Assigning roles!", self.b.channel)
            self.started = True

            random.shuffle(self.playerList)

            for i in range (len(self.playerList)//2 + 1):
                self.playerList[i].player_type = "mafia"

            self.playerList[len(self.playerList)//2 + 2].player_type = "doctor"

            self.playerList[len(self.playerList)//2 + 3].player_type = "detective"

            for i in range (len(self.playerList) - (len(self.playerList)//2 + 3)):
                self.playerList[i + (len(self.playerList)//2 + 4)].player_type = "innocent"

            for i in range (len(self.playerList)):
                print(self.playerList[i].player_type)

            await sendMessage('In the mornings, do "mvote [player]" to vote to lynch someone!', self.b.channel)
            await self.night()

            nonmafia_perms = discord.PermissionOverwrite(read_messages=False)
            mafia_perms = discord.PermissionOverwrite(read_messages=True)
            await client.create_channel(self.b.server, "Mafia", (self.b.server.default_role, nonmafia_perms), self.b.server.me, mafia_perms)

            nondoctor_perms = discord.PermissionOverwrite(read_messages=False)
            doctor_perms = discord.PermissionOverwrite(read_messages=True)
            await client.create_channel(self.b.server, "Doctor", (self.b.server.default_role, nondoctor_perms), self.b.server.me, doctor_perms)

            nondetective_perms = discord.PermissionOverwrite(read_messages=False)
            detective_perms = discord.PermissionOverwrite(read_messages=True)
            await client.create_channel(self.b.server, "Detective", (self.b.server.default_role, nondetective_perms), self.b.server.me, detective_perms)

    async def day(self):
        await sendMessage("Good morning!", self.b.channel)
        await sendMessage("Time to vote for who to lynch.", self.b.channel)
        self.votes = []

    async def night(self):
        await sendMessage("Good night!", self.b.channel)

    async def change_time(self):
        self.isday = not self.isday
        if self.isday:
            self.day()
        if not self.isday:
            self.night()
        self.turn_task.cancel()
        await self.turn_task

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
        await asyncio.sleep(240)
        await sendMessage("60 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        await asyncio.sleep(30)
        await sendMessage("30 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        await asyncio.sleep(15)
        await sendMessage("15 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        await asyncio.sleep(10)
        await sendMessage("5 seconds until the " + self.time[self.isday] + " ends!", self.b.channel)
        self.forced_turns += 1
        if self.forced_turns > 3:
            await sendMessage("The game has ended due to inactivity!", self.b.channel)
        self.change_time()


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
    if b.server.id not in mafiagames.keys():
        mafiagames[b.server.id] = MGameManager(a, b)
        await mafiagames[b.server.id].add_player(b)
        await client.send_message(b.author, "Repeat this command if there are 4 or more players to begin!")
    elif b.author.id == mafiagames[b.server.id].leader.id:
        mafiagames[b.server.id].started = True
        await mafiagames[b.server.id].game_start()
    else:
        await mafiagames[b.server.id].add_player(b)

async def mvote(a, b):
    print(b.mentions)

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
async def rpscreate(a,b):
    if b.channel.id in list(rps_games.keys()):
        await sendMessage("There's already a game in this channel!", b.channel)
    else:
        rps_games[b.channel.id] = RPSGame(b.channel,b)
        await sendMessage("Created a game in channel " + b.channel.name, b.channel)
async def rpsjoin(a,b):
    if b.channel.id in list(rps_games.keys()):
        if not (b.author in rps_games[b.channel.id].users) and not rps_games[b.channel.id].started:
            rps_games[b.channel.id].add_players([b.author])
            await sendMessage(b.author.mention + ", you have been added to the game!",b.channel)
        elif rps_games[b.channel.id].started:
            await sendMessage("Sorry, but the game in this channel has started without you!")
        else:
            await sendMessage(b.author.mention + ", you are already in the game!", b.channel)
    else:
        await sendMessage("There isn't a game in this channel!",b.channel)
async def rpsstart(a,b):
    if b.channel.id in list(rps_games.keys()):
        if len(rps_games[b.channel.id].users) > 1 and rps_games[b.channel.id].creator == b.author:
            await rps_games[b.channel.id].start()
            await sendMessage("Started the game!", b.channel)
        elif rps_games[b.channel.id].creator != b.author:
            await sendMessage("Only the creator of the game can start the game!", b.channel)
        else:
            await sendMessage("Find some friends to play with you! If you don't have any you're out of luck...", b.channel)
    else:
        await sendMessage("There isn't a game in this channel!", b.channel)
async def rpsaddcpus(a,b):
    run = True
    if len(a) == 0:
        num = 1
    else:
        if float(a[0]).is_integer() and float(a[0]) > 0:
            num = int(a[0])
        else:
            await sendMessage("Please enter a POSITIVE number",b.channel)
            run = False

    if run:
        pass

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
    },
    "mvote":{
        "run": mvote,
        "params": "[player]",
        "desc": "Vote to kill someone"
    },
    "rpscreate": {
        "run": rpscreate,
        "desc": "Create a new Rock, Paper, Scissors game in the current channel."
    },
    "rpsjoin": {
        "run": rpsjoin,
        "desc": "Join the current Rock Paper Scissors game."
    },
    "rpsaddcpus": {
        "run": rpsaddcpus,
        "params": "[num]",
        "desc": "Add the specified number of CPU's to the game"
    },
    "rpsstart": {
        "run": rpsstart,
        "desc": "Stop accepting new players and start the Rock Paper Scissors tournament!"
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
                l = list(commands.keys())
                l.sort()
                for i in l:
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

async def on_reaction_add(reaction, user):
    if reaction.message.id in list(rps_dms.keys()):
        sendMessage(reaction.emoji + " by " + rps_dms[reaction.message.id]["player"].name,rps_dms[reaction.message.id]["game"].channel)

client.run('MzkwNTgwOTgxMzE0MDkzMDU2.DRN65Q.-6OaVHeudI3zaPeDAjXWTJMw0Zw')