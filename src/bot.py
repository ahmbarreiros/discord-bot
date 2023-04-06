import discord
from discord.ext import commands
from modules import *
from auth import get_auth_header, get_token
from search_spotify import *
import asyncio


load_dotenv()
token = os.getenv("DISC_TOKEN")



intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix = "$", intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return

    if message.content.startswith('$play'):
        channel = message.author.voice.channel
        voice_connect = await channel.connect()
        search = message.content.split("$play ", 1)[1]
        json_result = send_search(search)
        # print(json_result)
        url = json_result["external_urls"]["spotify"]
        arg = os.system(f"spotdl download {url}")
        source = discord.FFmpegPCMAudio(arg)
        player = voice_connect.play(source)
        
        # source = discord.FFmpegPCMAudio("sexta dos cria.mp4")
        # voice_connect.play(source)


def send_search(search):
    token = get_token()
    return get_search(token, search)

@client.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        # source = discord.FFmpegPCMAudio("sexta dos cria.mp4")
        # player = voice.play(source)
    else:
        await ctx.send("nao esta em um canal")

@client.command(pass_context = True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("sai")
    else:
        await ctx.send("nao to no canal")
        
@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("audio pausado")
    else:
        await ctx.send("nao tem audio")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send("audio tocando novamente")
    else:
        await ctx.send("nao tem audio pausado")

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send("audio parado")
    else:
        await ctx.send("nao tem audio tocando")
        
@client.command(pass_context = True)
async def tocar(ctx, arg):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        voice.heartbeat_timeout = 300
        # source = discord.FFmpegPCMAudio("sexta dos cria.mp4")
        # player = voice.play(source)
    else:
        await ctx.send("nao esta em um canal")
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        await ctx.send("audio ja está tocando")
    else:
        vc = ctx.guild.voice_client
        json_result = send_search(arg)
        search_name = json_result["name"]
        url = json_result["external_urls"]["spotify"]
        os.system(f"spotdl download {url}")
        files = os.listdir(os.getcwd())
        for file in files:
            if search_name in file:
                name = file
        print(name)
        source = discord.FFmpegPCMAudio(name)
        player = voice.play(source)
        await ctx.send("audio tocando agora")
        if voice.is_playing() == False:
            voice.cleanup()

client.run(token)

def iterate_files(search_name, files):
    for file in files:
            print(file)
            print(search_name)
            if file == search_name:
                return file