import  discord
from discord.ext import commands
from discord.utils import get

import os
import requests
import time
from collections import deque

token = os.getenv('BOT_TOKEN')
#print(token)

client = commands.Bot(command_prefix=os.getenv('PREFIX'), case_insensitive=True)
voices = {}

@client.event
async def on_ready():
	print('CONNECTED')
	# client.remove_command('help')

@client.command(pass_context = True)
async def join(ctx):
	try:
		channel = ctx.message.author.voice.channel
	except:
		await ctx.send('присоединись к каналу мудак')
		return False

	voice = get(client.voice_clients, guild = ctx.guild)

	if voice and voice.is_connected():
		await voice.move_to(channel)
	else:
		voice = await channel.connect()
	voices[ctx.message.guild.id] = voice
	return True
	# await ctx.send(f'бот присоединился к каналу: {channel}')

@client.command()
async def leave(ctx):
	voice = get(client.voice_clients, guild = ctx.guild)
	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(f'бот отключился')
	else:
		await ctx.send(f'а как какать?')

@client.command()
async def play(ctx, name = ''):
	# global music_q = deque()
	if await join(ctx) == False:
		return
	voice = voices[ctx.message.guild.id]

	if voice.is_paused():
		voice.resume()

	song_path = 'song.mp3'

	if not voice.is_playing():
		voice.play(discord.FFmpegPCMAudio(song_path))

@client.command()
async def pause(ctx):
	voices[ctx.message.guild.id].pause()

client.run(token)
