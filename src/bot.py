import discord
from discord.ext import commands
from modules import *
import random
import wavelink
from wavelink.ext import spotify
from datetime import datetime, timedelta


load_dotenv()
token = os.getenv("DISC_TOKEN")
wavelink_uri = os.getenv("WAVELINK_URI")
wavelink_password = os.getenv("WAVELINK_PASSWORD")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix = "$", intents=intents)

class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
    previous_tracks = []
    thumb = ""
    on_rewind = False
    first_ctx = ""
    playlist_ctx = None
    last_playlist_track = None
    
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

    if message.author.id == 416282849768112128:
        xingamentos = ["vai tomar no cu weld", "vai se fude weld", "chupa meu pau de robo welde"]
        vaiXingar = [True, False, False, False, False, False, False, False, False]
        if random.choice(vaiXingar):
            await message.channel.send(random.choice(xingamentos))
        
    # if message.author.id == 426863952949936130:
    #     gols = ["gooool do navarro", "goooool do vitor guimaraes"]
    #     vaiGol = [True, False]
    #     if random.choice(vaiGol):
    #         await message.channel.send(random.choice(gols))


@client.command()
async def entrar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
            await ctx.send("voce precisa estar em um canal de voz burro")
    elif ctx.me.voice:
        await ctx.send(f"eu ja estou nesse canal de voz 👉 {ctx.me.voice.channel.name}")
    elif not vc:
        try:
            await ctx.author.voice.channel.connect(cls=CustomPlayer())
            await ctx.send("🐊")
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
                await ctx.send(f"🐊")
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
            CustomPlayer.thumb = search.thumbnail
            search_thumb = CustomPlayer.thumb
            em = discord.Embed(
                title=search.title,
                colour=discord.Colour.random().value,
                description="adicionada na fila, use $fila para ver a posição 💿💃"
            )
            em.set_author(name=search.author)
            em.set_thumbnail(url=search_thumb)
            em.add_field(name="Duração:", value=f"{str(timedelta(milliseconds=search.length))}")
            em.add_field(name="Video URL:", value=f"{str(search.uri)}")
            return await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("erro ao botar musica na fila. adm cheque o sistema!!!")
            print(f"erro musica fila: {type(e).__name__}")
    else:
        try:
            await vc.play(search)
            CustomPlayer.thumb = search.thumbnail
            search_thumb = CustomPlayer.thumb
            em = discord.Embed(
            title=search.title,
            colour=discord.Colour.random().value,
            description="💿💃tocando agora..."
            )
            em.set_author(name=search.author)
            em.set_thumbnail(url=search_thumb)
            em.add_field(name="Duração:", value=f"{str(timedelta(milliseconds=search.length))}")
            em.add_field(name="Video URL:", value=f"{str(search.uri)}")
            await ctx.send(embed=em)
            
        except Exception as e:
            await ctx.send("erro ao tocar a musica. adm cheque o sistema!!!")
            print(f"erro musica: {type(e).__name__}")
        
    vc.ctx = ctx
    setattr(vc, "loop", False)
    
@client.command()
async def playlist(ctx, search: str):
    vc = ctx.voice_client
    CustomPlayer.playlist_ctx = ctx
    node = wavelink.NodePool.get_connected_node()
    if not vc:
        try:
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=CustomPlayer())
            await ctx.send(f"🐊")
        except Exception as e:
            await ctx.send("erro ao me conectar. adm cheque o sistema!!!")
            print(f"erro musica conectar: {type(e).__name__}")
    elif not ctx.author.voice.channel.name:
        return await ctx.send("voce precisa estar em um canal de voz. burro.")
    elif ctx.author.voice.channel.name != ctx.me.voice.channel.name:
        return await ctx.send("a gente precisa estar no mesmo canal bobo. eu sou só 1")
    playlist = await wavelink.YouTubePlaylist.search(search)
    tracks: list[wavelink.YouTubeTrack] = playlist.tracks
    last_track = tracks[-1]
    CustomPlayer.last_playlist_track = last_track
    if not vc.is_playing():
        for track in tracks:
            vc.queue.put(track)
        first = vc.queue.get()
        await vc.play(first)
        CustomPlayer.thumb = first.thumbnail
        first_thumb = CustomPlayer.thumb
        em = discord.Embed(
        title=first.title,
        colour=discord.Colour.random().value,
        description="💿💃tocando agora... (proximas musicas na fila)"
        )
        em.set_author(name=first.author)
        em.set_thumbnail(url=first_thumb)
        em.add_field(name="Duração:", value=f"{str(timedelta(milliseconds=first.length))}")
        em.add_field(name="Video URL:", value=f"{str(first.uri)}")
        await ctx.send(embed=em)
        vc.ctx = ctx
    else:
        for track in tracks:
            vc.queue.put(track)
        await ctx.send(f"{search} adicionada na fila!")
        vc.ctx = ctx
    

@client.command()
async def pular(ctx, position: int = None):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra pular burro")
    elif not vc:
        return await ctx.send("preciso estar em um canal")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, so vai pular se entrar aqui")
    if position is None:
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
                await ctx.send("musica pulada, tocando a proxima...")
            else:
                await ctx.send("tente de novo em alguns segundos")
        except Exception as e:
            await ctx.send("erro ao tocar a musica. adm cheque o sistema!!!")
            print(f"erro pular: {type(e).__name__}")
    elif type(position) is int:
        if not vc.is_playing():
            return await ctx.send("nao está tocando nada")
        if vc.queue.is_empty:
            return await ctx.send("impossivel pular para a posição, a fila está vazia")
        if vc.is_paused():
            await vc.resume()
        
        if len(vc.queue) < position or position > 5:
            return await ctx.send("posição inválida, use $fila para achar a posição da música")
        
        if position == 1 and vc.is_playing():
            await vc.seek(player.position * 1000)
            return await ctx.send("musica pulada, tocando a proxima...")
        
        if vc.is_playing():
            await vc.seek(player.position * 1000)
            queue_len = len(vc.queue)
            for i in range(queue_len - 1):
                skipped_track = vc.queue.get()
                print(f"pulada {skipped_track}")
                await vc.play(skipped_track)
                print(f"apos {vc.queue}")
                await vc.seek(player.position * 1000)
            await ctx.send(f"musica pulada para a posição {position}")
        

@client.event
async def on_wavelink_track_start(payload: wavelink.TrackEventPayload):
    player = payload.player
    track = player.current
    try:
        ctx = player.ctx.channel
        CustomPlayer.thumb = track.thumbnail
        track_thumb = CustomPlayer.thumb
    except AttributeError:
        pass
    if track == CustomPlayer.last_playlist_track:
        CustomPlayer.last_playlist_track = None
        CustomPlayer.playlist_ctx = None
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
            try:
                print(f"custom 2: {CustomPlayer.previous_tracks}")
                em = discord.Embed(
                title=track.title,
                colour=discord.Colour.random().value
                )
                em.set_author(name=track.author)
                em.set_thumbnail(url=track_thumb)
                em.add_field(name="Duração:", value=f"{str(timedelta(milliseconds=track.length))}")
                em.add_field(name="Video URL:", value=f"{str(track.uri)}")
                return await ctx.send(embed=em)
            except AttributeError:
                pass
    except Exception as e:
        print(f"erro on start: {type(e).__name__}")


@client.event
async def on_wavelink_track_end(payload: wavelink.TrackEventPayload):
    if CustomPlayer.playlist_ctx is not None:
        ctx = CustomPlayer.playlist_ctx
        vc = ctx.voice_client
        print("dentro")
    else:
        vc = payload.player
        ltrack = payload.track
        ctx = vc.ctx
        channel = ctx.channel
    try:
        if vc.loop and CustomPlayer.playlist_ctx is None:
            await vc.play(ltrack)
    except Exception as e:
        print(f"erro wavelink_track_end loop: {type(e).__name__}")
        pass
    if not vc.is_playing() and not vc.queue.is_empty:
        try:
            track = vc.queue.get()
            await vc.play(track)
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
async def fila(ctx, dont_send = False):
    vc = ctx.voice_client
    em = discord.Embed(title="Posição na fila:", colour=discord.Colour.orange().value)
    if not vc.queue.is_empty:
        queue = vc.queue.copy()
        songs = 0
        for song in queue:
            songs += 1
            em.add_field(name=f"{songs}.", value=f"{song.title}", inline= True)
    else:
        em.add_field(name="Erro lista:", value="Nenhuma música na fila.")
    
    if not dont_send:
        return await ctx.send(embed=em)
    
@client.command()
async def reiniciar(ctx):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    track = player.current
    CustomPlayer.thumb = track.thumbnail
    track_thumb = CustomPlayer.thumb
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
                em = discord.Embed(
                title=track.title,
                colour=discord.Colour.random().value,
                description="💿💃tocando novamente..."
                )
                em.set_author(name=track.author)
                try:
                    em.set_thumbnail(url=track_thumb)
                except:
                    pass
                em.add_field(name="Duration:", value=f"{str(timedelta(milliseconds=track.length))}")
                em.add_field(name="Video URL:", value=f"{str(track.uri)}")
                return await ctx.send(embed=em)
                
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
        atual = history.pop()
        vc.queue.put_at_front(item=atual)
        last_track = history.pop()
        CustomPlayer.previous_tracks = history
        await vc.play(last_track)
        await ctx.send("retrocedido... tocando de novo a última música")
    elif vc.is_playing() and type(index_pos) is int:
        try:
            if index_pos < 0 or index_pos > len(history):
                raise Exception
            last_tracks = history.copy()
            for song in range(index_pos):
                actual_song = last_tracks.pop()
                vc.queue.put_at_front(item=actual_song)
            song = last_tracks.pop()
            CustomPlayer.previous_tracks = last_tracks
            await vc.play(song)
            await ctx.send("retrocedido... tocando a musica especificada")
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
    CustomPlayer.thumb = track.thumbnail
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
    em.add_field(name="Duração:", value=f"{str(timedelta(milliseconds=track.length))}")
    em.add_field(name="Video URL:", value=f"{str(track.uri)}")
    return await ctx.send(embed=em)

@client.command()
async def wesley(ctx):
    return await ctx.send("CARA 😤😤..........................EU VOU MATAR ESSE FILHA DA PUTA 🚫😡😡🤬......EU VOU MATAR ESSE FILHA DA PUTA NA HORA QUE ELE SAIR 🤬👊 🏃(do estadio 🥰)........ CARALHO CARA 😡😡😠....... PORRA FOI FALTA CLARA ALI CARA.......(ei juiz, vai tomar no cu)...... EI JUIZ VAI TOMAR NO CU 🤬🤬🥵 EI JUIZ VAI TOMAR NO CU 🤬🤬🥵........... SEU FILHO DA PUTA 😮‍💨😮‍💨🤱............ caralho rapaziada 😓😓..... ta foda......😔😔😞")

@client.command()
async def boost(ctx):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra pular burro")
    elif not vc:
        return await ctx.send("preciso estar em um canal")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}, so vai pular se entrar aqui")
    if vc._filter is None:
        await vc.set_filter(wavelink.Filter())
    if vc:
        t = {
            "boost": await vc.set_filter(wavelink.Filter(vc._filter, equalizer=wavelink.Equalizer.boost()))
        }
        await vc.set_filter(wavelink.Filter(t["boost"]))
        await ctx.send("boost ativado")
        
@client.command()
async def ajuda(ctx):
    em = discord.Embed(title="Lista de comandos :D", colour=discord.Colour.random().value, description="Para usar os comandos, é necessário estar em um canal de voz")
    em.add_field(name="$entrar", value=" - entra em um canal de voz", inline=False)
    em.add_field(name="$sair", value=" - sai do canal de voz", inline=False)
    em.add_field(name="$musica [busca]", value=" - começa a tocar a musica da busca ou adiciona ela na fila. Pode ser uma URL.", inline=False)
    em.add_field(name="$playlist [URL]", value=" - adiciona URL de uma playlist a fila do bot. Loop é desativado quando playlist é ativada", inline=False)
    em.add_field(name="$pular [posição]", value=" - pula a música para a posição da fila especificada. Pula para a próxima música por padrão.", inline=False)
    em.add_field(name="$pausar", value=" - pausa a música", inline=False)
    em.add_field(name="$voltar", value=" - volta a tocar a música", inline=False)
    em.add_field(name="$parar", value=" - interrompe a música", inline=False)
    em.add_field(name="$loop", value=" - ativa/desativa o loop na música atual", inline=False)
    em.add_field(name="$fila", value=" - mostra todas as músicas que estão na fila.", inline=False)
    em.add_field(name="$reiniciar", value=" - reinicia a música", inline=False)
    em.add_field(name="$retroceder [posição]", value=" - Volta para uma das últimas 5 músicas tocadas, sendo especificada pela posição. Toca a última música por padrão.", inline=False)
    em.add_field(name="$ir [hh:mm:ss]", value=" - pula para um tempo do vídeo, respeitando o formato em horas:minutos:segundos.", inline=False)
    em.add_field(name="$volume [valor]", value=" - configura o volume do bot, podendo aceitar um valor entre [0-200]", inline=False)
    em.add_field(name="$tocando", value=" - mostra a música atual que está tocando", inline=False)
    return await ctx.send(embed=em)
        
@musica.error
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("musica invalida (nao esta no youtube)")
    else:
        print(error)
        await ctx.send("tem que entrar em um canal de voz burro")
  
client.run(token)