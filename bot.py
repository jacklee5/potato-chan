import discord
import asyncio
import os
import random
from RPS import *

client = discord.Client()

TYPING_SPEED = 0.25
POSTFIX = "~"
IMAGE_DIRS = ["bts"]

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

# mafia shit
class Player(object):
    def __init__(self, a, b):
        self.author = b.author
        self.name = b.author.name
        self.profession = ""
        self.isdead = False
        self.isheal = False
        self.channel = b.channel
        self.done = False

    def changejob(self, newjob):
        self.profession = newjob
        self.author.sendMessage("You are a " + newjob + "!")

    async def killin(self):
        if self.isheal:
            await sendMessage("The mafia tried to kill " + self.name + ", but they were healed!", self.channel)
            self.isheal = False
        else:
            await sendMessage("The mafia successfully killed " + self.name + "! ", self.channel)
            self.isdead = True

    def healout(self, who):
        global mafiaplayerlist
        if self.isdead:
            self.author.sendMessage("You can't heal someone if you're dead!")
        elif self.profession != "doctor":
            self.author.sendMessage("You don't have the skill to save someone!")
        else:
            for i in range (len(mafiaplayerlist)):
                if mafiaplayerlist[i].isdead:
                    self.author.sendMessage("You can't heal a dead person!")
                elif mafiaplayerlist[i].name == who:
                    mafiaplayerlist[i].healin()
        self.done = True

    def healin(self):
        self.isheal = True

    def killout(self, who):
        global mafiaplayerlist
        if self.isdead:
            self.author.sendMessage("You can't kill someone if you're dead!")
        elif self.profession != "mafia":
            self.author.sendMessage("You probably shouldn't kill someone!")
        else:
            for i in range (len(mafiaplayerlist)):
                if mafiaplayerlist[i].isdead:
                    self.author.sendMessage("You can't kill a dead person!")
                elif mafiaplayerlist[i].name == who:
                    mafiaplayerlist[i].killin()
        self.done = True

    def detect(self, who):
        global mafiaplayerlist
        if self.isdead:
            self.author.sendMessage("You can't detect someone if you're dead!")
        elif self.profession != "detective":
            self.author.sendMessage("You don't have the skill to study this person!")
        else:
            for i in range(len(mafiaplayerlist)):
                if mafiaplayerlist[i].isdead:
                    self.author.sendMessage("This body is far too ruined to detect!")
                elif mafiaplayerlist[i].name == who:

                    self.author.sendMessage("This person is ")
        self.done = True


# end of mafia shit

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