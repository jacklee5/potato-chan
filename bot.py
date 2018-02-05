import discord
import asyncio
import os
import random
import copy
import time

client = discord.Client()

TYPING_SPEED = 0.25
POSTFIX = "~"
IMAGE_DIRS = ["bts", "anime"]
postfixes = {}
COLOR = 0x2956b2

user_data = {}

rps_games = {}
rps_dms = {}


class RPSPlayer(object):
    def __init__(self, cpu, user=discord.User()):
        self.__points = 0
        self.__user = user
        self.user = user
        self.id = user.id
        self.is_CPU = cpu
        self.play = None
        self.__mention = user.mention
        self.private_channel = None

    def win(self):
        self.__points += 1

    async def get_reaction_message(self):
        # TODO: Change input to discord
        if not self.is_CPU:
            message = await client.send_message(self.__user, ("Player " + self.__mention) + " please react with your choice!")
            await client.add_reaction(message, "💎")
            await client.add_reaction(message, "📜")
            await client.add_reaction(message, "✂")
            return message
            # self.play = input(str(self) + ", please pick r, p, or s.")
        elif self.is_CPU:
            choice = random.choice(["r","p","s"])
            self.play = choice
            print("A CPU picked " + choice)

    def get_points(self):
        return self.__points

    def __str__(self):
        return ("CPU" if self.is_CPU else ("Player " + self.__mention))


class RPSGame(object):
    def __init__(self, channel, message):
        self.channel = channel
        self.players = []
        self.users = []
        self.cpus = 0
        self.started = False
        self.games = []
        self.round_count = 0
        self.creator = message.author
        self.reaction_data = {}

    def add_players(self, players):
        for i in players:
            self.players.append(RPSPlayer(False,i))
            self.users.append(i)

    def add_cpus(self, num):
        for i in range(num):
            self.players.append(RPSPlayer(True))

    async def start(self):
        self.started = True
        passing = 0
        players = []
        for i in self.players:
            if i.get_points() == self.round_count:
                passing += 1
                players.append(i)
        self.generate_games()
        await sendMessage("**Round %d**" % (self.round_count + 1),self.channel)
        await self.print_games()
        for i in self.games:
            await self.do_game(i)

    def generate_games(self):
        list = self.players
        random.shuffle(list)
        self.games = []
        for i in range(0, len(list), 2):
            self.games.append(list[i:i + 2])

    async def do_game(self, players):
        if len(players) == 1:
            players[0].win()
        else:
            if not players[0].is_CPU:
                msg = await players[0].get_reaction_message()
                rps_dms[msg.id] = {"player":players[0],"channel":self.channel,"message":msg}
            else:
                await players[0].get_reaction_message()
            if not players[1].is_CPU:
                msg = await players[1].get_reaction_message()
                rps_dms[msg.id] = {"player":players[1],"channel":self.channel,"message":msg}
            else:
                await players[1].get_reaction_message()

    async def print_games(self):
        for i in range(len(self.games)):
            try:
                p2 = str(self.games[i][1])
            except:
                p2 = "none"
            await sendMessage("%s vs. %s" % (str(self.games[i][0]),p2),self.channel)

    def __str__(self):
        return str(self.players)


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
        self.dones = 0
        beginning_timeout = asyncio.get_event_loop()
        # beginning_timeout.run_until_complete(self.timeout_start)
        self.leader = b.author
        self.isday = False
        self.time = {
            True: "day",
            False: "night"
        }
        self.force_continue_loop = asyncio.get_event_loop()
        self.mafias = 0
        self.mafia_playerList = []
        self.me = b.server.me
        self.healdone = False
        self.killdone = False
        self.votedone = False
        self.detectdone = False
        self.votes = 0
        self.mafiateam = []
        self.innocentteam = []
        for i in range (len(self.mafia_playerList)):
            self.mafiateam.append(self.mafia_playerList[i].author)
        for i in range (len(self.playerList)):
            self.innocentteam.append(self.playerList[i].author)
        for i in range (len(self.mafiateam)):
            if self.mafiateam[i] in self.innocentteam:
                self.innocentteam.remove(self.mafiateam[i])

    async def game_start(self):
        if len(self.playerList) < 4:
            await client.send_message(self.leader, "There are not enough players; there are only " + str(len(self.playerList)))
        else:
            self.turn_force = asyncio.get_event_loop()
            self.turn_task = self.turn_force.create_task(self.timeout_restart())
            await sendMessage("Assigning roles!", self.b.channel)
            self.started = True

            random.shuffle(self.playerList)
            mafiafirst = True

            for i in range (len(self.playerList)//2):
                self.playerList[i].player_type = "mafia"
                # print(self.playerList[i].player_type)
                self.mafia_playerList.append(self.playerList[i])
                if mafiafirst:
                    nonmafia_perms = discord.PermissionOverwrite(read_messages=False)
                    mafia_perms = discord.PermissionOverwrite(read_messages=True)
                    self.mafiachannel = await client.create_channel(self.b.server, "mafia", (self.b.server.default_role, nonmafia_perms), (self.mafia_playerList[0].author, mafia_perms))
                    # self.mafiachannel = discord.utils.find(lambda c: c.name == 'mafia', self.b.server.channels)
                    mafiafirst = False

                else:
                    overwrite = discord.PermissionOverwrite()
                    overwrite.read_messages = True
                    await client.edit_channel_permissions(self.mafiachannel, self.playerList[i].author, overwrite)

            await sendMessage('You are mafia!\nUse "mvote [player]~" to vote and kill someone.', self.mafiachannel)
            for i in range(len(self.mafia_playerList)):
                await sendMessage(self.mafia_playerList[i].author.mention, self.mafiachannel)

            self.playerList[len(self.playerList)//2].player_type = "doctor"
            # print(self.playerList[len(self.playerList)//2].player_type)
            self.doctor = self.playerList[len(self.playerList)//2].author

            self.playerList[len(self.playerList)//2 + 1].player_type = "detective"
            # print(self.playerList[len(self.playerList)//2 + 1].player_type)
            self.detective = self.playerList[len(self.playerList)//2 + 1].author

            for i in range (len(self.playerList)):
                if self.playerList[i].player_type not in ["mafia", "doctor", "detective"]:
                    self.playerList[i].player_type = "innocent"

            await sendMessage('Whoever was not added to a channel is innocent.', self.b.channel)
            await sendMessage('In the mornings, do "mvote [player]" to vote to lynch someone!', self.b.channel)

            nondoctor_perms = discord.PermissionOverwrite(read_messages=False)
            doctor_perms = discord.PermissionOverwrite(read_messages=True)
            self.doctorchannel = await client.create_channel(self.b.server, "doctor", (self.b.server.default_role, nondoctor_perms), (self.doctor, doctor_perms))
            await sendMessage("You are the doctor, " + self.doctor.mention + '!\nUse "mheal [player]~" to heal someone!', self.doctorchannel)

            nondetective_perms = discord.PermissionOverwrite(read_messages=False)
            detective_perms = discord.PermissionOverwrite(read_messages=True)
            self.detectivechannel = await client.create_channel(self.b.server, "detective", (self.b.server.default_role, nondetective_perms), (self.detective, detective_perms))
            await sendMessage("You are the detective, " + self.detective.mention + '!\n Use "mdetect [player]~" to check if someone is in the mafia.', self.detectivechannel)

            self.playerids = []
            for i in range (len(self.playerList)):
                self.playerids.append(self.playerList[i].author.id)
            await self.night()


    async def day(self):
        await sendMessage("Good morning!", self.b.channel)
        await sendMessage("Time to vote for who to lynch.", self.b.channel)

    async def night(self):
        await sendMessage("Good night!", self.b.channel)

    async def change_time(self):
        self.votedone = False
        if not self.isday:
            # print("doing mafia kill")
            for i in range(len(self.playerList)):
                if self.playerList[i].will_kill == True and self.playerList[i].will_heal == True:
                    await sendMessage(self.playerList[i].author.mention + " was killed, but healed!", self.b.channel)
                    # print('await sendMessage(self.playerList[i].author.mention + " was killed, but healed!", self.b.channel)')
                elif self.playerList[i].will_kill:
                    await sendMessage(self.playerList[i].author.mention + " was killed!", self.b.channel)
                    self.playerList[i].isdead = True
                    self.playerids.remove(self.playerList[i].id)
                    if self.playerList[i] in self.mafia_playerList:
                        self.mafia_playerList.remove(self.playerList[i])
                    self.playerList.remove(self.playerList[i])
                    # print('await sendMessage(self.playerList[i].author.mention + " was killed!", self.b.channel)')
                    break
        mafias = 0
        innocents = 0
        win = False
        for i in range(len(self.playerList)):
            if self.playerList[i].player_type == "mafia":
                mafias += 1
            else:
                innocents += 1
        if mafias == 0:
            await sendMessage("The innocents win! You get 20 PotatoPounds.", self.b.channel)
            for i in range (len(self.innocentteam)):
                getAccount(self.innocentteam[i]).pounds += 20
            await client.delete_channel(self.mafiachannel)
            await client.delete_channel(self.detectivechannel)
            await client.delete_channel(self.doctorchannel)
            win = True
        elif innocents == 1:
            await sendMessage("The mafia wins! You get 20 PotatoPounds.", self.b.channel)
            for i in range (len(self.mafiateam)):
                getAccount(self.mafiateam[i]).pounds += 20
            await client.delete_channel(self.mafiachannel)
            await client.delete_channel(self.detectivechannel)
            await client.delete_channel(self.doctorchannel)
            win = True
        if not win:
            self.isday = not self.isday
            for i in range(len(self.playerList)):
                self.playerList[i].reset()
            self.healdone = False
            self.killdone = False
            self.votedone = False
            self.detectdone = False
            self.votes = 0
            if self.isday:
                await self.day()
            if not self.isday:
                await self.night()
            self.turn_task.cancel()
            await self.turn_task
        else:
            del mafiagames[self.b.server.id]

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
            await self.change_time()


    async def delete(self):
        await sendMessage("The game has ended due to inactivity!", self.b.channel)
        del self

    async def vote(self, b):
        if b.author.id not in self.playerids:
            await sendMessage("You are not in a game!", b.channel)
        elif self.isday:
            for i in range (len(self.playerids)):
                if b.author.id == self.playerList[i].author.id:
                    voter = self.playerList[i]
            if voter.hasvoted:
                await sendMessage("You have voted already!", b.channel)
            else:
                for i in range(len(self.playerList)):
                    if b.mentions[0].id == self.playerList[i].author.id:
                        self.playerList[i].votes += 1
                        self.votes += 1
                        if self.votes == len(self.playerList):
                            self.votes = 0
                            await self.lynch()
                            break
        elif not self.isday:
            for i in range (len(self.mafia_playerList)):
                if b.author.id == self.mafia_playerList[i].author.id:
                    voter = self.mafia_playerList[i]
            if voter.player_type != "mafia":
                await sendMessage("You are not the mafia!", b.channel)
            elif voter.hasvoted:
                await sendMessage("You have voted already!", b.channel)
            else:
                for i in range (len(self.playerList)):
                    if b.mentions[0].id == self.playerList[i].author.id:
                        self.playerList[i].votes += 1
                        self.votes += 1
                        if self.votes == len(self.playerList) - len(self.mafia_playerList):
                            self.votes = 0
                            await self.mafiakill()

    async def lynch(self):
        votelist = []
        # print("got to lynch")
        for i in range(len(self.playerList)):
            votelist.append(0)
        for i in range(len(self.playerList)):
            votelist[i] += self.playerList[i].votes
        # print(votelist)
        for i in range(len(self.playerList)):
            if votelist[i] == max(votelist) and not self.votedone:
                self.votedone = True
                self.playerList[i].isdead = True
                await sendMessage(self.playerList[i].author.mention + " was killed!", self.b.channel)
                self.playerids.remove(self.playerList[i].id)
                if self.playerList[i] in self.mafia_playerList:
                    self.mafia_playerList.remove(self.playerList[i])
                self.playerList.remove(self.playerList[i])
                await self.change_time()

    async def mafiakill(self):
        votelist = []
        for i in range(len(self.playerList)):
            votelist.append(0)
        for i in range(len(self.playerList)):
                votelist[i] += self.playerList[i].votes
        for i in range(len(self.playerList)):
            if votelist[i] == max(votelist) and not self.votedone:
                self.votedone = True
                self.playerList[i].will_kill = True
                # print(str(self.playerList[votelist[i]].will_kill) + str(self.playerList[votelist[i]].name))
                await self.endnight()

    async def endnight(self):
        self.dones += 1
        # print(self.dones)
        if self.dones == 3:
            self.dones = 0
            await self.change_time()

    async def heal(self, b):
        isdoctor = False
        toheal = None
        for i in range (len(self.playerids)):
            if self.playerids[i] == b.author.id:
                if self.playerList[i].player_type == "doctor":
                    isdoctor = True
        for i in range (len(self.playerids)):
            if self.playerids[i] == b.mentions[0].id:
                toheal = self.playerList[i]

        if b.author.id not in self.playerids:
            await sendMessage("You are not in a game!", b.channel)
        elif self.isday:
            await sendMessage("It is not the time to heal.", b.channel)
        elif not isdoctor:
            await sendMessage("You are not the doctor!", b.channel)
        elif self.healdone:
            await sendMessage("You already healed someone tonight!", b.channel)
        elif toheal.is_dead:
            await sendMessage("This person is dead...", b.channel)
        else:
            toheal.will_heal = True
            await sendMessage("You healed " + toheal.author.display_name + ".", b.channel)
            self.healdone = True
            await self.endnight()

    async def detect(self, b):
        isdetective = False
        todetect = None
        for i in range (len(self.playerids)):
            if self.playerids[i] == b.author.id:
                if self.playerList[i].player_type == "detective":
                    isdetective = True
        for i in range (len(self.playerids)):
            if self.playerids[i] == b.mentions[0].id:
                todetect = self.playerList[i]
        if b.author.id not in self.playerids:
            await sendMessage("You are not in a game!", b.channel)
        elif self.isday:
            await sendMessage("It is not the time to detect.", b.channel)
        elif not isdetective:
            await sendMessage("You are not the detective!", b.channel)
        elif self.detectdone:
            await sendMessage("You already detected someone tonight!", b.channel)
        elif todetect.is_dead:
            await sendMessage("This person is dead...", b.channel)
        else:
            if todetect.player_type == "mafia":
                what = "in the mafia."
            else:
                what = "is not in the mafia."
            await sendMessage(todetect.author.display_name + " is " + what, b.channel)
            self.detectdone = True
            await self.endnight()

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
        self.hasvoted = False
        self.votes = 0

    def reset(self):
        self.will_kill = False
        self.will_heal = False
        self.is_done = False
        self.hasvoted = False
        self.votes = 0


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

async def mvote (a, b):
    if b.server.id not in mafiagames.keys():
        await sendMessage('There are no mafia games in this server. Type "mstart~" to start one.', b.channel)
    else:
        await mafiagames[b.server.id].vote(b)

async def mdetect (a, b):
    if b.server.id not in mafiagames.keys():
        await sendMessage('There are no mafia games in this server. Type "mstart~" to start one.', b.channel)
    else:
        await mafiagames[b.server.id].detect(b)

async def mheal (a, b):
    if b.server.id not in mafiagames.keys():
        await sendMessage('There are no mafia games in this server. Type "mstart~" to start one.', b.channel)
    else:
        await mafiagames[b.server.id].heal(b)

# end of mafia


class Player(object):
    def __init__(self, user):
        self.user = user
        self.pounds = 0
        self.lastDaily = None
        self.name = user.name


def getCommand(message):
    things = message[:-1].lower().split()
    command = {
        "name": things[0],
        "params": things[1:]
    }
    return command
def getAccount(user):
    if user.id in list(user_data.keys()):
        return user_data[user.id]
    else:
        user_data[user.id] = Player(user)
        return user_data[user.id]
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
    testa = a
    testb = b
    print(str(a) + str(b))

async def image(a, b):
    await client.send_file(b.channel, a[0] + "/" + random.choice(os.listdir(a[0])))
async def mhelp(a, b):
    await sendMessage("tested", b.channel)
async def rpshelp(a, b):
    await sendMessage("To start a new Rock Paper Scissors Game, make use the rpscreate command to create a new game, rpsjoin to join an existing game, and rpsstart to start the game!", b.channel)
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
            await sendMessage("Sorry, but the game in this channel has started without you!", b.channel)
        else:
            await sendMessage(b.author.mention + ", you are already in the game!", b.channel)
    else:
        await sendMessage("There isn't a game in this channel!",b.channel)
async def rpsstart(a,b):
    if b.channel.id in list(rps_games.keys()):
        if len(rps_games[b.channel.id].players) > 1 and rps_games[b.channel.id].creator == b.author:
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
        if b.channel.id in rps_games:
            rps_games[b.channel.id].add_cpus(num)
            await sendMessage("Added %d CPU's to this game!" % (num), b.channel)
        else:
            await sendMessage("There isn't a game in this channel!", b.channel)
async def daily(a,b):
    account = getAccount(b.author)
    if account.lastDaily == None or time.time() - account.lastDaily > 86400:
        await sendMessage("Collected daily!", b.channel)
        account.pounds += 10
        account.lastDaily = time.time()
    else:
        secondsSince = time.time() - account.lastDaily
        await sendMessage("Already collected today! You can collect again in %d hours and %d minutes" % (24 - secondsSince/3600, (60 - (secondsSince % 3600)/60)), b.channel)
async def profile(a,b):
    if len(a) == 0:
        account = getAccount(b.author)
    else:
        account = getAccount(b.mentions[0])
    pounds = account.pounds
    await sendMessage("**Profile for %s**\n**Potato Pounds: ** %d\n**Level: **: %d" % (account.name, pounds, pounds ** .5), b.channel)


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
    "mvote":{
        "run": mvote,
        "params": "[player]",
        "desc": "If it is the day, you vote for who to lynch. If it's the night and you are in the mafia, you can vote for who to kill!"
    },
    "mheal":{
        "run": mheal,
        "desc": "If it is the night, a doctor can choose to save someone from being killed from the mafia!",
        "params": "[player]",
    },
    "mdetect":{
        "run": mdetect,
        "desc": "If it is the night, a detective can check if an alive person is a part of the mafia or innocent!",
        "params": "[player]",
    },
    # "changepostfix":{
    #     "run": changepostfix,
    #     "params": "[newpostfix]",
    #     "desc": "Change the postfix for this bot"
    # },
    "rpscreate": {
        "run": rpscreate,
        "desc": "Create a new Rock, Paper, Scissors game in the current channel."
    },
    "rpsjoin": {
        "run": rpsjoin,
        "desc": "Join the current Rock Paper Scissors game."
    },
    # "rpsaddcpus": {
    #     "run": rpsaddcpus,
    #     "params": "[num]",
    #     "desc": "Add the specified number of CPU's to the game"
    # },
    "rpsstart": {
        "run": rpsstart,
        "desc": "Stop accepting new players and start the Rock Paper Scissors tournament!"
    },
    "daily": {
        "run": daily,
        "desc":"Get your daily sum of PotatoPounds"
    },
    "profile": {
        "run": profile,
        "params": "(user)",
        "desc": "Get profile information about yourself, or a specified user."
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

@client.event
async def on_reaction_add(reaction, user):
    # RPS stuff
    print("reaction added")
    if reaction.message.id in list(rps_dms.keys()) and user != client.user:
        #💎📜✂
        player = rps_dms[reaction.message.id]["player"]
        channel = reaction.message.channel
        player.private_channel = channel
        game = rps_games[rps_dms[reaction.message.id]["channel"].id]
        async def tieHandler(player, other):
            print(player.play + " " + other.play)
            await sendMessage("That's a tie! Go again!", channel)
            await sendMessage("That's a tie! Go again!", other.private_channel)
            player.play = None
            other.play = None
            if not player.is_CPU:
                msg = await player.get_reaction_message()
                rps_dms[msg.id] = {"player": player, "channel": game.channel,
                                   "message": msg}
            else:
                await player.get_reaction_message()
            if not other.is_CPU:
                msg = await other.get_reaction_message()
                rps_dms[msg.id] = {"player": other, "channel": game.channel,
                                   "message": msg}
            else:
                await other.get_reaction_message()
        async def winHandler(player, other):
            player.win()
            if not player.is_CPU:
                await sendMessage("Good job! You won against %s" % (str(other)), channel)
            if not other.is_CPU:
                await sendMessage("Better luck next time... You lost against %s" % (str(player)),
                              other.private_channel)
        async def loseHandler(player, other):
            other.win()
            if not player.is_CPU:
                await sendMessage("Better luck next time... You lost against %s" % (str(other)), channel)
            if not player.is_CPU:
                await sendMessage("Good job! You won against %s" % (str(other)), other.private_channel)
        async def handleChoice():
            del rps_dms[reaction.message.id]
            await client.delete_message(reaction.message)
            for i in game.games:
                finished = True
                if player in i:
                    if len(i) == 1:
                        if not player.is_CPU:
                            await sendMessage("Surprise! You were the only one in your branch. Free points!", channel)
                    else:
                        if player == i[0]:
                            if i[1].play != None:
                                other = i[1]
                                if (other.play == "r" and player.play == "p") or (other.play == "p" and player.play == "s") or (other.play == "s" and player.play == "r"):
                                    await winHandler(player, other)
                                elif other.play == player.play:
                                    await tieHandler(player, other)
                                    finished = False
                                else:
                                    await loseHandler(player, other)
                            else:
                                if not player.is_CPU:
                                    await sendMessage("Waiting for the other player...", channel)
                        elif player == i[1]:
                            if i[0].play != None:
                                other = i[0]
                                if (other.play == "r" and player.play == "p") or (
                                        other.play == "p" and player.play == "s") or (
                                        other.play == "s" and player.play == "r"):
                                    await winHandler(player, other)
                                elif other.play == player.play:
                                    await tieHandler(player, other)
                                    finished = False
                                else:
                                    await loseHandler(player, other)
                            else:
                                if not player.is_CPU:
                                    await sendMessage("Waiting for other player...", channel)
                for j in i:
                    if j.play == None:
                        finished = False
                if finished:
                    game.round_count += 1
                    passing = 0
                    players = []
                    for i in game.players:
                        if i.get_points() == game.round_count:
                            passing += 1
                            players.append(i)
                    game.players = players
                    if len(game.players) > 1:
                        game.generate_games()
                        await sendMessage("**Round %d**" % (game.round_count + 1), game.channel)
                        await game.print_games()
                        for i in game.games:
                            await game.do_game(i)
                    else:
                        await sendMessage("The game has ended! The winner is %s. Have 10 PotatoPounds as a reward!" % (str(game.players[0])), game.channel)
                        getAccount(game.players[0].user).pounds += 10
                        for i in game.players:
                            print("Points for %s is %d" % (str(i),i.get_points()))
                        del rps_games[game.channel.id]
        if reaction.emoji == "💎":
            player.play = "r"
            await handleChoice()
        elif reaction.emoji == "📜":
            player.play = "p"
            await handleChoice()
        elif reaction.emoji == "✂":
            player.play = "s"
            await handleChoice()

client.run('MzkwNTgwOTgxMzE0MDkzMDU2.DRN65Q.-6OaVHeudI3zaPeDAjXWTJMw0Zw')