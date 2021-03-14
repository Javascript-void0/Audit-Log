import discord
import os
import time
from datetime import datetime
from discord.ext import commands
from discord.utils import get

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='.', intents=intents)
client.remove_command('help')
TOKEN = os.getenv("AUDIT_TOKEN")

def get_dt():
    t = time.localtime()
    t = time.strftime("%I:%M %p", t)
    d = time.strftime("%m/%d/%Y")
    return d,t
    
@client.event
async def on_ready():
    print('[+] Started {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Audit Log"))

@client.event
async def on_guild_channel_delete(channel):
    log_channel = client.get_channel(820718179918676018)
    entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
    d,t = get_dt()
    embed = discord.Embed(title='[-] Channel Deleted', description='{} removed #{}'.format(entry.user.mention, channel.name))
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)

@client.event
async def on_guild_channel_create(channel):
    log_channel = client.get_channel(820718179918676018)
    entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1).get()

    if channel.type == discord.ChannelType.text:
        tp = 'Text Channel'
        slow = channel.slowmode_delay
        if channel.nsfw == True:
            nsfw = 'Marked'
        else:
            nsfw = 'Unmarked'
        if slow == 0:
            slow = 'disabled'

    elif channel.type == discord.ChannelType.news:
        tp = 'Announcement Channel'
        if channel.nsfw == True:
            nsfw = 'Marked'
        else:
            nsfw = 'Unmarked'

    elif channel.type == discord.ChannelType.voice:
        tp = 'Voice Channel'

    if tp == 'Voice Channel':
        embed = discord.Embed(title='[+] Channel Created', description='{} created a voice channel **{}**\n`01` - Set the name to **{}**\n`02` - Set the type to **{}**\n`03` - Set the bitrate of **{}**\n`04` - Set the user limit of **{}**'.format(entry.user.mention, channel.name, channel.name, tp, channel.bitrate//1000, channel.user_limit))
    else:
        embed = discord.Embed(title='[+] Channel Created', description='{} created a text channel **#{}**\n`01` - Set the name to **{}**\n`02` - Set the type to **{}**\n`03` - {} the channel as NSFW\n`04` - Set slowmode {}'.format(entry.user.mention, channel.name, channel.name, tp, nsfw, slow))

    d,t = get_dt()
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)

@client.event
async def on_guild_channel_update(before, topic):
    log_channel = client.get_channel(820718179918676018)
    entry = await log_channel.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1).get()
    changes = 0
    if entry.channel.topic:
        changes += 1
        x = '`0{}` - {}'.format(changes, entry.topic)
    embed = discord.Embed(title='[+] Channel Updated', description='{} made changes to **#{}**\n{}'.format(entry.user.mention, channel.name, x))
    d,t = get_dt()
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)

if __name__ == '__main__':
    client.run(TOKEN)