import os
import keep_alive
import re

import json

import discord
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions

from dotenv import load_dotenv

import requests

channels = {}
width = 30


def readJSON():
    global channels
    with open('channels.json', 'r') as infile:
        channels = json.load(infile)


def writeJSON():
    with open('channels.json', 'w') as outfile:
        json.dump(channels, outfile)


def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None


def getLeaderboard(ctx):
    code = channels[str(ctx.guild.id)][0]['code']
    year = channels[str(ctx.guild.id)][0]['year']
    session = channels[str(ctx.guild.id)][0]['session']
    try:
        link = 'https://adventofcode.com/' + str(
            year) + '/leaderboard/private/view/' + str(code) + '.json'
        x = requests.get(
            link,
            cookies={
                "_ga": "GA1.2.1941296263.1606786137",
                "_gid": "GA1.2.641639940.1606786137",
                "session": session,
                "_gat": "1"
            })
        data = x.json()

        members = data['members']
        mydata = sorted(
            members,
            key=lambda x: ( members[x]['stars'],members[x]['local_score']),
            reverse=True)

        names = []
        for i in mydata:
            if not str(data['members'][i]['name']) == "None":
                name = str(data['members'][i]['name']).replace("_", "˾")
                stars = str(data['members'][i]['stars'])
                score = str(data['members'][i]['local_score'])

                dots1 = " " * (channels[str(ctx.guild.id)][0]['width'] - len(
                    str(data['members'][i]['name']))-5)

            else:
                name = str("Anonymous(#" +
                           str(data['members'][i]['id'] + ")")).replace(
                               "_", "˾")
                stars = str(data['members'][i]['stars'])
                score = str(data['members'][i]['local_score'])

                dots1 = " " * (channels[str(ctx.guild.id)][0]['width'] - len(
                    str("Anonymous(#" + str(data['members'][i]['id'] + ")")))-5)
                

            names.append(score+". "+(" "*(4-len(score)))+name + "  " + dots1 + " | " + stars)

        return "\n".join(names[:20])
    except:
        return 'Leaderboard unavailable'


load_dotenv()
TOKEN = os.getenv('TOKEN')

readJSON()

default_prefix = "="

def getPrefix(bot,message):
    readJSON()
    return channels[str(message.guild.id)][0]['prefix']

client = commands.Bot(command_prefix=getPrefix)

client.remove_command("help")


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    game = discord.Game("with the API")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_guild_join(guild):
    channels[guild.id] = []
    channels[guild.id].append({
        'prefix': default_prefix,
        'channel': '',
        'code': '',
        'year': 2020,
        'width': width
    })
    writeJSON()


@client.command()
async def ping(ctx):
    channel = client.get_channel(
        int(channels[str(ctx.guild.id)][0]['channel']))
    if ctx.message.channel == channel:
        await ctx.channel.send("Pong")


@client.command()
@has_permissions(manage_roles=True, ban_members=True)
async def prefix(ctx, message):
    global client
    channels[str(ctx.guild.id)][0]['prefix'] = message
    writeJSON()
    client.command_prefix=getPrefix
    await ctx.channel.send('Prefix changed to: ``' + message + "``")


@client.command()
@has_permissions(manage_roles=True, ban_members=True)
async def setChannel(ctx, message):
    channels[str(ctx.guild.id)][0]['channel'] = message
    writeJSON()
    await ctx.channel.send('Channel set to: ``' + message + "``")


@client.command()
@has_permissions(manage_roles=True, ban_members=True)
async def setCode(ctx, message):
    channels[str(ctx.guild.id)][0]['code'] = message
    writeJSON()
    await ctx.channel.send('Code set to: ``' + message + "``")


@client.command()
@has_permissions(manage_roles=True, ban_members=True)
async def setWidth(ctx, message):
    channels[str(ctx.guild.id)][0]['width'] = int(message)
    writeJSON()
    await ctx.channel.send('Width set to: ``' + str(message) + "``")


@client.command()
async def setYear(ctx, message):
    channels[str(ctx.guild.id)][0]['year'] = int(message)
    writeJSON()
    await ctx.channel.send('Year set to: ``' + str(message) + "``")


@client.command()
@has_permissions(manage_roles=True, ban_members=True)
async def setSession(ctx, message):
    channels[str(ctx.guild.id)][0]['session'] = str(message)
    writeJSON()
    await ctx.channel.send('Session set to: ``' + str(message) + "``")

@client.command()
async def showSettings(ctx):
  name = "Advent of Code"
  description = "Settings"
  embed = discord.Embed(
      title=name, description=description, color=discord.Color.blue())
  message = '   Setting'+(" "*(10-len('Setting')))+'|  Value\n===================\n'
  for i in channels[str(ctx.message.guild.id)]:
    count=0
    for x in i:
      message+=str(count)+". "+str(x)+(" "*(10-len(str(x))))+"|  "+str(i[x])+"\n"
      count+=1
  embed.add_field(name='Settings', value="```md\n"+message+"```")
  await ctx.send(embed=embed)

helpWidth = 12
com = [
    'help', 'prefix {prefix}', 'setChannel {id}', 'setCode {code}',
    'setWidth {width}', 'setYear {year}', 'setSession {id}', 'ldr'
]
desc = [
    'Generates this help box', 'Changes the prefix of the bot',
    'Sets the channel to display the board', 'Sets the code of the board (before -)',
    'Sets the width of the board', 'Sets the year of the leaderboard',
    'Sets the session id', 'Displays the leaderboard'
]

commandsList = []
for i in range(len(com)):
    commandsList.append(com[i] + (
        ' ' * (len('Command' + (" " * helpWidth)) - len(com[i]))) + desc[i])


@client.command()
async def help(ctx):
  name = "Advent of Code"
  description = "List of commands"
  embed = discord.Embed(
      title=name, description=description, color=discord.Color.blue())
  helpTitle = 'Command' + (" " * helpWidth) + "| Description" + (
      " " * (helpWidth * 2))
  dots = "=" * len(helpTitle)
  commandsHeader = helpTitle + "\n" + dots + "\n"
  commandList = "\n".join(commandsList)
  embed.add_field(
      name="Help",
      value='```md\n' + str(commandsHeader) + str(commandList) + '```',
      inline=True)
  await ctx.send(embed=embed)


@client.command()
async def ldr(ctx):
    channel = client.get_channel(
        int(channels[str(ctx.guild.id)][0]['channel']))
    if ctx.message.channel == channel:
        leaderboard = getLeaderboard(ctx)
        if leaderboard == "Leaderboard unavailable":
            leaderboard = ""
        name = "Advent of Code"
        code = channels[str(ctx.guild.id)][0]['code']
        year = channels[str(ctx.guild.id)][0]['year']
        description = "Year: " + str(year) + " | Table: " + str(code)
        dots = " " * (
            channels[str(ctx.guild.id)][0]['width'] - len(str("Scr.  Name")))
        ldTitle = "Scr.  Name " + dots + "  |Stars"
        link = 'https://adventofcode.com/' + str(
            year) + '/leaderboard/private/view/' + str(code)
        embed = discord.Embed(
            title=name,
            description=description,
            color=discord.Color.blue(),
            url=link)
        embed.add_field(
            name="Leaderboard Top 20",
            value='```md\n' + ldTitle + '\n' + ('=' * len(ldTitle)) + '\n' +
            leaderboard + '```',
            inline=True)
        embed.set_author(name="Visit the bot website",url="https://AdventDiscordbot.mchrisgm.repl.co")
        await channel.send(embed=embed)

keep_alive.keep_alive()

client.run(TOKEN)
