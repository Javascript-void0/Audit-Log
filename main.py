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

guild = client.get_guild(802565984602423367)
log_channel = client.get_channel(820699203680468995)

def get_dt():
    t = time.localtime()
    t = time.strftime("%I:%M %p", t)
    d = time.strftime("%m/%d/%Y")
    return d,t
    
def nsfw(n):
    if n == True:
        nsfw = 'Marked'
    else:
        nsfw = 'Unmarked'
    return nsfw

def typeRename(channel):
    if channel == discord.ChannelType.text:
        tp = 'Text Channel'
    elif channel == discord.ChannelType.news:
        tp = 'Announcement Channel'
    elif channel == discord.ChannelType.voice:
        tp = 'Voice Channel'
    return tp

@client.event
async def on_ready():
    print('[+] Started {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Audit Log"))

@client.event
async def on_guild_channel_delete(channel):
    global log_channel
    entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
    d,t = get_dt()
    embed = discord.Embed(title='[-] Channel Deleted', description='{} removed #{}'.format(entry.user.mention, channel.name))
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)

@client.event
async def on_guild_channel_create(channel):
    global log_channel
    entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1).get()

    if channel.type == discord.ChannelType.text:
        tp = 'Text Channel'
        slow = channel.slowmode_delay
        n = nsfw(channel.nsfw)
        if slow == 0:
            slow = 'disabled'

    elif channel.type == discord.ChannelType.news:
        tp = 'Announcement Channel'
        n = nsfw(channel.nsfw)

    elif channel.type == discord.ChannelType.voice:
        tp = 'Voice Channel'

    if tp == 'Voice Channel':
        embed = discord.Embed(title='[+] Channel Created', description='{} created a voice channel **{}**\n`01` - Set the name to **{}**\n`02` - Set the type to **{}**\n`03` - Set the bitrate of **{}**\n`04` - Set the user limit of **{}**'.format(entry.user.mention, channel.name, channel.name, tp, channel.bitrate//1000, channel.user_limit))
    else:
        embed = discord.Embed(title='[+] Channel Created', description='{} created a text channel **#{}**\n`01` - Set the name to **{}**\n`02` - Set the type to **{}**\n`03` - {} the channel as NSFW\n`04` - Set slowmode {}'.format(entry.user.mention, channel.name, channel.name, tp, n, slow))
    
    d,t = get_dt()
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)

@client.event
async def on_guild_channel_update(before, after):

    if before.topic != after.topic:
        x = '`01` - Changed the topic to **{}**'.format(after.topic)
    if before.nsfw != after.nsfw:
        n = nsfw(after.nsfw)
        x = '`01` - {} the channel as NSFW'.format(n)
    if before.slowmode_delay != after.slowmode_delay:
        x = '`01` - Set slowmode to **{}**'.format(after.slowmode_delay//1000)
    if before.type != after.type:
        b = typeRename(before.type)
        a = typeRename(after.type)
        x = '`01` - Changed the type from **{}** to **{}**'.format(b, a)
    if before.name != after.name:
        x = '`01` - Changed the name from **{}** to **{}**'.format(before.name, after.name)
    
    global log_channel, guild
    entry = await guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1).get()
    embed = discord.Embed(title='[+] Channel Updated', description='{} made changes to **#{}**\n{}'.format(entry.user.mention, before, x))
    d,t = get_dt()
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)

@client.event
async def on_member_update(before, after):
    global log_channel, guild
    entry = await guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1).get()
    if len(before.roles) < len(after.roles):
        n = next(role for role in after.roles if role not in before.roles)
        x = '`01` - **Added** a role\n{}'.format(n)
        embed = discord.Embed(title='[+] Member Updated', description='{} updated roles for **{}**\n{}'.format(entry.user.mention, before.mention, x))
    if len(before.roles) > len(after.roles):
        n = next(role for role in before.roles if role not in after.roles)
        x = '`01` - **Removed** a role\n{}'.format(n)
        embed = discord.Embed(title='[-] Member Updated', description='{} updated roles for **{}**\n{}'.format(entry.user.mention, before.mention, x))

    d,t = get_dt()
    embed.set_footer(text=f'{d}, {t}')
    await log_channel.send(embed=embed)
 
if __name__ == '__main__':
    client.run(TOKEN)

'''
    if before.nick != after.nick:
        if after.nick:
            x = '`01` - Set their nickname to **{}**'.format(after.nick)
            embed = discord.Embed(title='[+] Member Updated', description='{} updated **{}**\n{}'.format(entry.user.mention, before.mention, x))
        else:
            x = '`01` - **Removed** their nickname of **{}**'.format(before.nick)
            embed = discord.Embed(title='[-] Member Updated', description='{} updated **{}**\n{}'.format(entry.user.mention, before.mention, x))
'''