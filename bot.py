import discord
import asyncio
import os
import threading
import random
from RPS import *

client = discord.Client()

TYPING_SPEED = 0.25
POSTFIX = "~"
IMAGE_DIRS = ["bts", "anime"]
mafiagames = {

}

# mafia


class MGameManager(object):
    def __init__(self, a, b):
        self.started = False
        self.playerList = []
        threading.Timer(300, self.timeout_start()).start()
        self.forced_turns = 0
        self.a = a
        self.b = b

    def add_player(self, player):
        not_added = True
        for i in range (len(self.playerList)):
            if self.playerList[i].id == player:
                not_added = False
                player.sendMessage("You are already in the game!")
        if not_added:
            self.playerList.append(MPlayer(player))
            player.sendMessage("You have been added to the game!")

    def timeout_start(self):
        if not self.started and len(self.playerList) < 4:
            del self

    def timeout_restart(self):
        self.timer.cancel()
        self.timer = threading.Timer(300, self.delete()).start()
        self.forced_turns += 1
        self.delete()

    async def delete(self):
        if self.forced_turns > 3:
            await sendMessage("The game has ended due to inactivity!", self.b.channel)
            del self


class MPlayer(object):
    def __init__(self, player):
        self.is_dead = False
        self.player_type = ""
        self.will_kill = False
        self.will_heal = False
        self.is_done = False
        self.id = player

def mstart(a, b):
    if not (mafiagames.get(bool(b.channel.id), False)):
        mafiagames[b.channel.id] = MGameManager(a, b)
        mafiagames[b.channel.id].addplayer(b.author)
    else:
        mafiagames[b.channel.id].addplayer(b.author)

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
    "image":{
        "run": image,
        "params": "[category]",
        "desc": "displays an image from a category. Current categories are: " + listToText(IMAGE_DIRS)
    },
    "mhelp":{
        "run": mhelp,
        "desc": "Instructions for mafia."
    },
    "rpshelp":{
        "run": rpshelp,
        "desc": "Instructions for rock-paper-scissors tournament"
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
    is_command = message.content.lower().endswith(POSTFIX) and not (message.author.id == client.user.id)
    print("User " + message.author.name + " on Channel " + message.channel.name + " on " + message.server.name + " says " + message.content)
    if is_command:
        command = getCommand(message.content)
        print(command)
        if command["name"] in list(commands.keys()):
            print("Command " + command["name"] + POSTFIX + " was used!")
            await commands[command["name"]]["run"](command["params"], message)
        else:
            embed = discord.Embed(title="Help",
                                  description="Some message",
                                  color=0x7289da)
            for i in list(commands.keys()):
                embed.add_field(name=i + commands[i].get("params", "") + "~", value=commands[i]["desc"],
                                inline=False)
            await client.send_message(message.channel, embed=embed)

client.run('MzkwNTgwOTgxMzE0MDkzMDU2.DRN65Q.-6OaVHeudI3zaPeDAjXWTJMw0Zw')