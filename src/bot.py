import discord
from discord.ext import commands, Interactions
from modules import *
from auth import get_auth_header, get_token
from search_spotify import *
# import yt_dlp
import random
import wavelink
from datetime import datetime, timedelta
from typing import Union


load_dotenv()
token = os.getenv("DISC_TOKEN")
wavelink_uri = os.getenv("WAVELINK_URI")
wavelink_password = os.getenv("WAVELINK_PASSWORD")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix = "$", intents=intents)
last_channel = ""

class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
    previous_tracks = []
    thumb = ""
    on_rewind = False
    
def checkChannels(channel_name):
    for guild in client.guilds:
        for channel in guild.channels:
            if  str(channel.id) == channel_name:
                return channel


def time_to_ms(time_stamp):
    times = time_stamp.split(":")
    time_str = ""
    for time in times:
        if len(time) == 1:
            times[times.index(time)] = "0" + time
    if len(times) == 1:
        time_str = "00:00:" + times[0]
    elif len(times) == 2:
        time_str = "00:" + times[0] + ":" + times[1]
    elif len(times) == 3:
        time_str = times[0] + ":" + times[1] + ":" + times[2]
    dt_obj = datetime.strptime(time_str, "%H:%M:%S")
    dt_obj_ms = int((dt_obj - datetime(1900, 1, 1)).total_seconds() * 1000)
    return dt_obj_ms


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    client.loop.create_task(connect_nodes())
    
async def connect_nodes():
    await client.wait_until_ready()
    node =  wavelink.Node(uri=wavelink_uri, password=wavelink_password)
    await wavelink.NodePool.connect(client=client, nodes=[node])

@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'Node: <{node.status}> is ready')

@client.event
async def on_message(message):
    
    await client.process_commands(message)
    if message.author == client.user:
        return

    # print(type(message.author.id))
    # if message.author.id == 416282849768112128:
    #     xingamentos = ["vai tomar no cu weld", "vai se fude weld", "chupa meu pau de robo welde"]
    #     vaiXingar = [True, False]
    #     if random.choice(vaiXingar):
    #         await message.channel.send(random.choice(xingamentos))
        
    # if message.author.id == 426863952949936130:
    #     gols = ["gooool do navarro", "goooool do vitor guimaraes"]
    #     vaiGol = [True, False]
    #     if random.choice(vaiGol):
    #         await message.channel.send(random.choice(gols))


@client.command()
async def entrar(ctx):
    vc = ctx.voice_client
    # try:
    #     channel = ctx.author.voice.channel
    #     voice = await channel.connect()
    #     # source = discord.FFmpegPCMAudio("sexta dos cria.mp4")
    #     # player = voice.play(source)
    # except AttributeError:
    #     return await ctx.send("nao esta em um canal"
    if not ctx.author.voice:
            await ctx.send("voce precisa estar em um canal de voz burro")
    elif ctx.me.voice:
        await ctx.send(f"eu ja estou nesse canal de voz 👉 {ctx.me.voice.channel.name}")
    elif not vc:
        try:
            await ctx.author.voice.channel.connect(cls=CustomPlayer())
            await ctx.send("entrei")
        except Exception as e:
            await ctx.send("erro ao entrar")
            print(f"erro entrar: {type(e).__name__}") 

@client.command(pass_context = True)
async def sair(ctx):
    if not ctx.author.voice or not ctx.me.voice.channel or ctx.author.voice.channel.id != ctx.me.voice.channel.id:
        return await ctx.send("você precisa estar no mesmo canal que eu pra me tirar daqui duvido 👉 {ctx.me.voice.channel.name}")  
    elif ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("sai")
        

@client.command(pass_context = True)
#search: Union[wavelink.YoutubeTrack, etcetc...]
async def musica(ctx, *, search: wavelink.YouTubeTrack, channel = None):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    if not vc:
        try:
            if not channel == None:
                print(channel)
                channel_ctx = checkChannels(channel)
                print(channel_ctx)
                vc: CustomPlayer = await channel_ctx.connect(cls=CustomPlayer())
                await ctx.send(f"conectado no canal desejado")
            else:
                vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=CustomPlayer())
                await ctx.send(f"conectado")
        except Exception as e:
            await ctx.send("erro ao me conectar. adm cheque o sistema!!!")
            print(f"erro musica conectar: {type(e).__name__}")
    elif not ctx.author.voice.channel.name and channel == None:
        return await ctx.send("voce precisa estar em um canal de voz. burro.")
    elif ctx.author.voice.channel.name != ctx.me.voice.channel.name:
        return await ctx.send("a gente precisa estar no mesmo canal bobo. eu sou só 1")
            
    if vc.is_playing():
        try:
            print(search.length)
            vc.queue.put(item=search)
            await ctx.send(embed=discord.Embed(
                title=search.title,
                description=f"botei {search.title} na fila...(no canal {vc.channel.name})"
            ))
        except Exception as e:
            await ctx.send("erro ao botar musica na fila. adm cheque o sistema!!!")
            print(f"erro musica fila: {type(e).__name__}")
    else:
        try:
            await vc.play(search)
            await ctx.send(f"{search.title} tocando")
            player = node.get_player(ctx.guild.id)
            duracao = search.duration * 1000
            duracao = datetime.fromtimestamp(duracao / 1000)
            await ctx.send(
                embed=discord.Embed(
                    color=discord.Colour.red().value,
                title=search.title,
                url=search.uri,
                description= f"tocando agora. duração: {duracao}"
            )
            )
            CustomPlayer.thumb = search.thumbnail
        except Exception as e:
            await ctx.send("erro ao tocar a musica. adm cheque o sistema!!!")
            print(f"erro musica: {type(e).__name__}")
            
    vc.ctx = ctx
    setattr(vc, "loop", False)

@client.command()
async def pular(ctx):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra pular burro")
    elif not vc:
        return await ctx.send("preciso estar em um canal")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, so vai pular se entrar aqui")
    try:
        if not vc.is_playing():
            return await ctx.send("nao está tocando nada")
        if vc.queue.is_empty:
            if not vc.loop:
                await ctx.send("musica pulada, adicione mais musicas com $musica")
            else:
                await ctx.send("musica reiniciada pois $loop está ligado")
            return await vc.stop()
        
        if vc.is_paused():
            await vc.resume()
            
        if vc.is_playing():
            await vc.seek(player.position * 1000)
            # track = player.queue.get()
            # print(f"queue get method: {track}")
            await ctx.send("musica pulada, tocando a proxima...")
            # await vc.play(track)
        else:
            await ctx.send("tente de novo em alguns segundos")
    except Exception as e:
        await ctx.send("erro ao tocar a musica. adm cheque o sistema!!!")
        print(f"erro pular: {type(e).__name__}")

@client.event
async def on_wavelink_track_start(payload: wavelink.TrackEventPayload):
    if not CustomPlayer.on_rewind:
        tracks_history_copy = CustomPlayer.previous_tracks.copy()
        CustomPlayer.rewind_history = tracks_history_copy
    track = payload.track
    try:
            track_history = CustomPlayer.previous_tracks
            if len(track_history) >= 5:
                track_history.pop(0)
            track_history.append(track)
            CustomPlayer.previous_tracks = track_history
            print(f"custom 2: {CustomPlayer.previous_tracks}")
    except Exception as e:
        print(f"erro on start: {type(e).__name__}")


@client.event
async def on_wavelink_track_end(payload: wavelink.TrackEventPayload):
    vc = payload.player
    ltrack = payload.track
    ctx = vc.ctx
    channel = ctx.channel
    if vc.loop:
        try:
            await vc.play(ltrack)
        except Exception as e:
            await ctx.send("erro ao repetir a musica. adm cheque o sistema!!!")
            print(f"erro: {type(e).__name__}")
    if not vc.is_playing() and not vc.queue.is_empty:
        try:
            track = vc.queue.get()
            await vc.play(track)
            await channel.send(
                embed=discord.Embed(
                color=discord.Colour.red().value,
                title=track.title,
                url=track.uri,
                description= f"tocando agora. duração: {track.duration}"
            )
            )
        except Exception as e:
            await ctx.send("Erro ao tocar a próxima musica da fila. adm cheque o sistema!!!")
            print(f"erro on end: {type(e).__name__}")

@client.command(pass_context = True)
async def pausar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra me pausar cara")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, so vai pausar se entrar aqui")
    
    if vc.is_playing():
        await vc.pause()
        return await ctx.send("audio pausado")
    else:
        return await ctx.send("nao tem audio tocando")

@client.command(pass_context = True)
async def voltar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra eu voltar a tocar lá")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to nesse canal ó 👉 {ctx.me.voice.channel.name}, usa o comando quando vc estiver aqui também")
    
    if vc.is_paused():
        await vc.resume()
        await ctx.send("audio tocando novamente")
    else:
        await ctx.send("nao tem audio pausado")

@client.command(pass_context = True)
async def parar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("VOCE NAO VAI ME PARAR")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"EU SOU O DONO DO CANAL {ctx.me.voice.channel.name}. NINGUEM ME PARARARA ")
    
    if vc.is_playing():
        vc.queue.clear()
        await vc.stop()
        await ctx.send("audio parado")
    else:
        await ctx.send("nao tem audio tocando")
        
@client.command(pass_context = True)
async def loop(ctx):
    vc = ctx.voice_client
    
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra me loooooooooopar")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, loooooooopa eu aqui")
    
    try:
        vc.loop ^= True
        if vc.loop:
            CustomPlayer.on_rewind = True
        else:
            CustomPlayer.on_rewind = False
    except:
        setattr(vc, "loop", False)
        await ctx.send("erro ao mudar loop")
    if vc.loop:
        await ctx.send("loop ativado")
    else:
        await ctx.send("loop desativado")

@client.command()
async def lista(ctx):
    vc = ctx.voice_client
    em = discord.Embed()
    if not vc.queue.is_empty:
        queue = vc.queue.copy()
        songs = 0
        for song in queue:
            songs += 1
            em.add_field(name=f"{songs}.", value=f"{song.title}")
        return await ctx.send(embed=em)
    else:
        em.add_field(name="Erro lista:", value="Nenhuma música na fila.")
        return await ctx.send(embed=em)
    
@client.command()
async def reiniciar(ctx):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra reiniciar a musica")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, só vou reiniciar aqui")
    
    if vc:
        try:
            if not vc.is_playing():
                return await ctx.send("nao está tocando nada")
            if vc.is_paused():
                await vc.resume()
            if vc.is_playing():
                await vc.seek(player.position * 0)
                return await ctx.send("musica reinicada eba")
                
        except Exception as e:
            await ctx.send("erro ao tocar a musica. adm cheque o sistema!!!")
            print(f"erro reiniciar: {type(e).__name__}")
    else:
        await ctx.send("bot nao está em um canal de musica")

@client.command()
async def retroceder(ctx, position = None):
    vc = ctx.voice_client
    index_pos = 0
    try:
        index_pos = int(position)
    except:
        print("erro 1")
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra retroceder")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
    history = CustomPlayer.previous_tracks
    if len(history) <= 1:
        return await ctx.send("não existem registros do histórico. Adicione musicas com $musica para registrá-las")
    
    if vc.is_paused():
        await vc.resume()
        
    if vc.is_playing() and position == None:
        print('-'*10)
        print(f"histo: {history}")
        print('-'*10)
        atual = history.pop()
        vc.queue.put_at_front(item=atual)
        print(f"atual: {atual}")
        print('-'*10)
        last_track = history.pop()
        print(f"lt: {last_track}")
        print('-'*10)
        CustomPlayer.previous_tracks = history
        await vc.play(last_track)
        # CustomPlayer.on_rewind = True
        await ctx.send("retrocedido... tocando de novo a última música")
        print(f"custom: {CustomPlayer.previous_tracks}")
        print('-'*10)
    elif vc.is_playing() and type(index_pos) is int:
        try:
            if index_pos < 0 or index_pos > len(history):
                raise Exception
            print('-'*10)
            print(f"histo: {history}")
            print('-'*10)
            last_tracks = history.copy()
            for song in range(index_pos):
                actual_song = last_tracks.pop()
                vc.queue.put_at_front(item=actual_song)
            print(f"last: {last_tracks}")
            print('-'*10)
            song = last_tracks.pop()
            CustomPlayer.previous_tracks = last_tracks
            print(song)
            print('-'*10)
            await vc.play(song)
            # CustomPlayer.on_rewind = True
            await ctx.send("retrocedido... tocando a musica especificada")
            print(f"custom: {CustomPlayer.previous_tracks}")
            print('-'*10)
        except:
            return await ctx.send("index inválido, não foi possível retroceder a música desejada. Tente de novo com um index válido ou com o nome da música")
        
@client.command()
async def ir(ctx, tempo):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra ir para um tempo especifico na musica")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, usa o comando aqui")
    try:
        if tempo == None:
            print(f"tempo: {tempo}")
            raise AttributeError
        formato = time_to_ms(tempo)
        print(f"formato: {formato}")
    except Exception as e:
            print(f"erro: {type(e).__name__}")
            return await ctx.send("você precisa determinar um tempo para eu pular para. O formato é hh:mm:ss")
    print("-" * 8)
    print(tempo)
    print(formato)
    print("-" * 8)
    try:
        if vc.is_paused():
            await vc.resume()
        if vc.is_playing():
            await vc.seek(formato)
    except Exception as e:
            print(f"erro: {type(e).__name__}")
            return await ctx.send("erro ao ir para o tempo especificado. O formato é hh:mm:ss")


@client.command()
async def volume(ctx, volume: int = 0):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz para mudar meu volume")
    elif not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, usa o comando aqui")
    if volume == 0:
        return await ctx.send(f"o volume atual é {vc.volume}")
    
    if volume > 200:
        return await ctx.send("passou do limite (0-200)")
    elif volume < 0:
        return await ctx.send("muito baixo (0-200)")
    
    if volume > 100:
        await ctx.send("aviso: acima de 100 o audio pode não funcionar da maneira correta")
    await ctx.send(f"mudando o volume para {volume}")
    return await vc.set_volume(volume)

@client.command()
async def tocando(ctx):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    track = player.current
    track_thumb = CustomPlayer.thumb
    print("-"*10)
    print(track_thumb)
    if not vc:
        return await ctx.send("eu nem to em um canal de voz esquizofrenico")
    
    if not vc.is_playing():
        return await ctx.send("nao esta tocando nada")

    em = discord.Embed(
        title=track.title,
        colour=discord.Colour.dark_purple().value
        )
    em.set_author(name=track.author)
    em.set_thumbnail(url=track_thumb)
    em.add_field(name="Duration:", value=f"{str(timedelta(milliseconds=track.length))}")
    em.add_field(name="Video URL:", value=f"{str(track.uri)}")
    return await ctx.send(embed=em)
    
        
@musica.error
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("musica invalida (nao esta no youtube)")
    else:
        print(error)
        await ctx.send("tem que entrar em um canal de voz burro")
        
# @client.command(pass_context = True)
# async def tocar(ctx, arg):
#     if ctx.author.voice:
#         channel = ctx.message.author.voice.channel
#         voice = await channel.connect()
#         voice.heartbeat_timeout = 300
#     else:
#         await ctx.send("nao esta em um canal")
#     voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#     if voice.is_playing():
#         await ctx.send("audio ja está tocando")
#     else:
#         #YDL_OPTIONS = {'format': 'bestaudio'} #, 'postprocessors': 'extract-audio'}
#         YDL_OPTIONS = {
#             'format': 'bestaudio',
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }],
#             'outtmpl': 'song.%(ext)s',
#         }
#         #FFMPEG_OPTIONS = {'options': '-vn'}
#         FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
#         vc = ctx.guild.voice_client
#         # json_result = send_search(arg)
#         # search_name = json_result["name"]
#         # url = json_result["external_urls"]["spotify"]
#         # os.system(f"spotdl download {url}")
#         # os.system(f"spotdl save {url} --save-file {search_name}.spotdl --preload")
#         # file = open(f"{search_name}.spotdl", "r")
#         # json_results = json.load(file)[0]
#         # music_url = json_results["download_url"]
#         music_url = arg
#         # with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
#         #     info = ydl.extract_info(music_url, download=False)
#         #     str = f"""
#         #         \n\n\n
#         #         --------------------------------------
#         #         {info}
#         #         --------------------------------------
#         #         \n\n\n
#         #     """
#             # print(str)
#             arr = [i for i in info['formats'] if i.get('format_note') != 'storyboard']
#             # print(f"array: {arr}")
#         new_url = info["url"]
#         print(f"new url: {new_url}")
#         # play = await voice.
        
#         # os.system(f"spotdl url 'Frank Ocean - Provider'")
#         # print(os.system(f"spotdl url 'Frank Ocean - Provider'"))
#         # files = os.listdir(os.getcwd())
#         # for file in files:
#         #     if search_name in file:
#         #         name = file
#         # print(name)
#         # source = discord.FFmpegPCMAudio(music_url, **FFMPEG_OPTIONS)
#         # player = voice.play(source)
#         ctx.voice_client.play(discord.FFmpegPCMAudio(music_url, **FFMPEG_OPTIONS))
#         await ctx.send("audio tocando agora")
#     if not voice.is_playing():
#         await ctx.send("nao esta tocando mais nada")

def iterate_files(search_name, files):
    for file in files:
            print(file)
            print(search_name)
            if file == search_name:
                return file
  
client.run(token)