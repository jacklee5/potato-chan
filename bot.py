import discord
import asyncio

client = discord.Client()

TYPING_SPEED = 0.25
POSTFIX = "~"

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

main_module = {
    "test":{
        "run": test,
        "desc": "a test"
    }
}

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    is_command = message.content.lower().endswith(POSTFIX) and not (message.author.id == client.user.id)
    print("User " + message.author.name + " on Channel " + message.channel.name + " on " + message.server.name + " says " + message.content)
    if is_command:
        command = getCommand(message.content)
        print(command)
        if command["name"] in list(main_module.keys()):
            print("Command " + command["name"] + POSTFIX + " was used!")
            await main_module[command["name"]]["run"](command["params"], message)
        else:
            embed = discord.Embed(title="Help",
                                  description="Some message",
                                  color=0x7289da)
            for i in list(main_module.keys()):
                embed.add_field(name="!o" + i + " " + main_module[i].get("params", ""), value=main_module[i]["desc"],
                                inline=False)
            await client.send_message(message.channel, embed=embed)

client.run('MzkwNTgwOTgxMzE0MDkzMDU2.DRN65Q.-6OaVHeudI3zaPeDAjXWTJMw0Zw')