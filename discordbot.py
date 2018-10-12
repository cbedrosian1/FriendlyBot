import configparser
import random
import asyncio
import aiohttp
import json
import discord
import youtube_dl
from discord.ext.commands import Bot
from discord import Game


config = configparser.ConfigParser()
config.read('tokens.ini')

bot_token = config['Tokens']['BotToken']
TOKEN = bot_token
TRN_KEY = config['Tokens']['trn-api-key']
HEADERS = {'TRN-Api-Key': TRN_KEY}
BOT_PREFIX = ('!')
players = {}
queues = {}
client = Bot(command_prefix=BOT_PREFIX)


async def fortnite_pull_stats(user):
    user = user.title()
    platform = 'pc'
    url = ('https://api.fortnitetracker.com/v1/profile/{}/{}'.format(platform, user))
    async with aiohttp.ClientSession() as session: 
        raw_response = await session.get(url, headers = HEADERS)
        response = await raw_response.text()
        response = json.loads(response)
        return response
   
        
@client.command(name='solo',
                description="Shows solo stats for all games")
async def fortnite_solo_stats(user: str):
    ft_player_data = await fortnite_pull_stats(user)
    try:
        stats = ft_player_data['stats']['p2']
        embed = discord.Embed(title = 'Solo stats for ' + user, color=0x00ff00)
        
        embed.add_field(name='Matches played', value=stats['matches']['value'], inline=True)
        embed.add_field(name='Wins', value=stats['top1']['value'], inline=True)
        embed.add_field(name='Win Percentage', value = '%.2f' % (stats['top1']['valueInt']/stats['matches']['valueInt'] * 100) + '%\n', inline=True)
        embed.add_field(name='Top 10s', value = stats['top10']['value'], inline=True)
        embed.add_field(name='Kills', value = stats['kills']['value'], inline=True)
        embed.add_field(name='K/D', value = stats['kd']['value'], inline=True)
        
        await client.say(embed = embed)  
        
    except KeyError:
        await client.say('Invalid username')

        
@client.command(name='duo',
                description="Shows duo stats for all games")
async def fortnite_duo_stats(user: str):
    ft_player_data = await fortnite_pull_stats(user)
    try:
        stats = ft_player_data['stats']['p10']
        embed = discord.Embed(title = 'Duo stats for ' + user, color=0x00ff00)
        
        embed.add_field(name='Matches played', value=stats['matches']['value'], inline=True)
        embed.add_field(name='Wins', value=stats['top1']['value'], inline=True)
        embed.add_field(name='Win Percentage', value = '%.2f' % (stats['top1']['valueInt']/stats['matches']['valueInt'] * 100) + '%\n', inline=True)
        embed.add_field(name='Top 10s', value = stats['top10']['value'], inline=True)
        embed.add_field(name='Kills', value = stats['kills']['value'], inline=True)
        embed.add_field(name='K/D', value = stats['kd']['value'], inline=True)
        
        await client.say(embed = embed)  
        
    except KeyError:
        await client.say('Invalid username')     

        
@client.command(name='squad',
                description="Shows squad stats for all games")
async def fortnite_squad_stats(user: str):
    ft_player_data = await fortnite_pull_stats(user)
    try:
        stats = ft_player_data['stats']['p9']
        embed = discord.Embed(title = 'Squad stats for ' + user, color=0x00ff00)
        
        embed.add_field(name='Matches played', value=stats['matches']['value'], inline=True)
        embed.add_field(name='Wins', value=stats['top1']['value'], inline=True)
        embed.add_field(name='Win Percentage', value = '%.2f' % (stats['top1']['valueInt']/stats['matches']['valueInt'] * 100) + '%\n', inline=True)
        embed.add_field(name='Top 10s', value = stats['top10']['value'], inline=True)
        embed.add_field(name='Kills', value = stats['kills']['value'], inline=True)
        embed.add_field(name='K/D', value = stats['kd']['value'], inline=True)
        
        await client.say(embed = embed)  
        
    except KeyError:
        await client.say('Invalid username')  


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)              
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no', 
        'It is not looking likely', 
        'Too hard to tell', 
        'It is quite possible', 
        'Definitely'
    ]
    await client.say(random.choice(possible_responses) + ', ' + context.message.author.mention)
    
    
@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)
    
    
@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()
    
    
@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after = lambda: check_queue(server.id))
    players[server.id] = player
    player.start()

    
@client.command(name = 'q',
                pass_context=True)
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after = lambda: check_queue(server.id))
    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
        await client.say('Video queue')
    
    
def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()
        
        
@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()
    
    
@client.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    players[id].stop()
    
    
@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()
    
    
@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)

    
async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current Servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)