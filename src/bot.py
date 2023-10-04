import discord
from discord.ext import commands
from modules import *
import random
import wavelink
from wavelink.ext import spotify
from datetime import datetime, timedelta
import asyncio


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
    loop = False
    jacare = False
    
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


@client.command()
async def entrar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
            await ctx.send("voce precisa estar em um canal de voz")
    elif ctx.me.voice:
        await ctx.send(f"eu ja estou nesse canal de voz 👉 {ctx.me.voice.channel.name}")
    elif not vc:
        try:
            await ctx.author.voice.channel.connect(cls=CustomPlayer())
            await ctx.send("🐊")
        except Exception as e:
            await ctx.send("Erro 0x4A4C")
            #print(f"{type(e).__name__}\n{repr(e)}") 

@client.command(pass_context = True)
async def sair(ctx):
    if not ctx.author.voice or not ctx.me.voice.channel or ctx.author.voice.channel.id != ctx.me.voice.channel.id:
        return await ctx.send("você precisa estar no mesmo canal que eu 👉 {ctx.me.voice.channel.name}")  
    elif ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("sai")
        

@client.command(pass_context = True)
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
            await ctx.send("Erro 0x4A4D")
            print(f"{type(e).__name__}\n{repr(e)}") 
    elif not ctx.author.voice.channel.name and channel == None:
        return await ctx.send("voce precisa estar em um canal de voz. .")
    elif ctx.author.voice.channel.name != ctx.me.voice.channel.name:
        return await ctx.send("a gente precisa estar no mesmo canal")
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
            await ctx.send("Erro 0x4A4E")
            #print(f"{type(e).__name__}\n{repr(e)}") 
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
            await ctx.send("Erro 0x4A4F")
            #print(f"{type(e).__name__}\n{repr(e)}") 
        
    #vc.ctx = ctx
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
            await ctx.send("Erro 0x4A5A")
            #print(f"{type(e).__name__}\n{repr(e)}") 
    elif not ctx.author.voice.channel.name:
        return await ctx.send("voce precisa estar em um canal de voz. .")
    elif ctx.author.voice.channel.name != ctx.me.voice.channel.name:
        return await ctx.send("a gente precisa estar no mesmo canal")
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
        CustomPlayer.playlist_ctx = ctx
    

@client.command()
async def pular(ctx, position: int = None):
    vc = ctx.voice_client
    node = wavelink.NodePool.get_connected_node()
    player = node.get_player(ctx.guild.id)
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz")
    elif not vc:
        return await ctx.send("preciso estar em um canal")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
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
            await ctx.send("Erro 0x4A5B")
            print(f"{type(e).__name__}\n{repr(e)}") 
    elif type(position) is int:
        if vc.queue.is_empty:
            return await ctx.send("impossivel pular para a posição, a fila está vazia")
        if vc.is_paused():
            await vc.resume()
        if not vc.is_playing():
            return await ctx.send("nao está tocando nada")
        
        if len(vc.queue) < position or position > len(vc.queue):
            return await ctx.send("posição inválida, use $fila para achar a posição da música")
        
        if position == 1 and vc.is_playing():
            await vc.seek(player.position * 1000)
            return await ctx.send("musica pulada, tocando a proxima...")
        
        if vc.is_playing():
            await vc.seek(player.position * 1000)
            cont = 1
            async for track in vc.queue:
                if cont > position - 1:
                    await vc.play(track)
                    break
                cont = cont + 1
                await asyncio.sleep((10/1000))
            await ctx.send(f"musica pulada para a posição {position}")
            
@client.command()
async def historico(ctx):
    vc = ctx.voice_client
    print(vc.queue.history)
    em = discord.Embed(title="Últimas 10 músicas tocadas: ", colour=discord.Colour.orange().value)
    if not vc.queue.is_empty:
        queue = vc.queue.history.copy()
        print(queue)
        songs = 0
        for song in queue:
            songs += 1
            if songs <= 10:
                em.add_field(name=f"{songs}.", value=f"{song.title}", inline= True)
    else:
        em.add_field(name="Erro no histórico:", value="Nenhuma música no histórico.")
    
    return await ctx.send(embed=em)

@client.event
async def on_wavelink_track_end(payload: wavelink.TrackEventPayload):
    vc = payload.player
    ltrack = payload.track
    if not vc.is_playing() and not vc.queue.is_empty:
        print("aqui")
        track = vc.queue.get()
        del vc.queue[0]
        await vc.play(track)

@client.command(pass_context = True)
async def pausar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("Você precisa estar em um canal de voz pra me pausar.")
    elif not vc:
        return await ctx.send("eu não estou em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
    
    if vc.is_playing():
        await vc.pause()
        return await ctx.send("audio pausado")
    else:
        return await ctx.send("nao tem audio tocando")

@client.command(pass_context = True)
async def voltar(ctx):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("Você precisa estar em um canal de voz pra eu voltar a tocar.")
    elif not vc:
        return await ctx.send("eu não to em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to nesse canal ó 👉 {ctx.me.voice.channel.name}")
    
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
        return await ctx.send("eu não estou em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"EU SOU O DONO DO CANAL {ctx.me.voice.channel.name} MUA HA HA ")
    
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
        return await ctx.send("eu não to em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
    
    try:
        vc.loop ^= True
        if vc.loop:
            CustomPlayer.on_rewind = True
        else:
            CustomPlayer.on_rewind = False
    except Exception as e:
        setattr(vc, "loop", False)
        await ctx.send("Erro 0x4A6A")
        #print(f"{type(e).__name__}\n{repr(e)}") 
    if vc.loop:
        await ctx.send("loop ativado")
    else:
        await ctx.send("loop desativado")

@client.command()
async def fila(ctx, dont_send = False):
    vc = ctx.voice_client
    em = discord.Embed(title=f"Próximas 10 músicas da lista (Total de {vc.queue.count})", colour=discord.Colour.orange().value)
    if not vc.queue.is_empty:
        queue = vc.queue.copy()
        songs = 0
        for song in queue:
            songs += 1
            if songs <= 10:
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
        return await ctx.send("eu não to em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
    
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
            await ctx.send("Erro 0x4A6B")
            #print(f"{type(e).__name__}\n{repr(e)}") 
    else:
        await ctx.send("bot nao está em um canal de musica")

@client.command()
async def retroceder(ctx, position = None):
    vc = ctx.voice_client
    index_pos = 0
    try:
        index_pos = int(position)
    except Exception as e:
        await ctx.send("Erro 0x4A6C-1")
        #print(f"{type(e).__name__}\n{repr(e)}") 
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra retroceder")
    elif not vc:
        return await ctx.send("eu não to em um canal de voz")
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
            await ctx.send("Erro 0x4A6C-2")
            #print(f"{type(e).__name__}\n{repr(e)}") 
            return await ctx.send("index inválido, não foi possível retroceder a música desejada. Tente de novo com um index válido ou com o nome da música")
        
@client.command()
async def ir(ctx, tempo):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz pra ir para um tempo especifico na musica")
    elif not vc:
        return await ctx.send("eu não to em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
    try:
        if tempo == None:
            print(f"tempo: {tempo}")
            raise AttributeError
        formato = time_to_ms(tempo)
        #print(f"formato: {formato}")
    except Exception as e:
            await ctx.send("Erro 0x4A6D")
            print(f"{type(e).__name__}\n{repr(e)}") 
            return await ctx.send("você precisa determinar um tempo para eu pular para. O formato é hh:mm:ss")
    try:
        if vc.is_paused():
            await vc.resume()
        if vc.is_playing():
            await vc.seek(formato)
    except Exception as e:
            await ctx.send("Erro 0x4A6E")
            #print(f"{type(e).__name__}\n{repr(e)}") 
            return await ctx.send("erro ao ir para o tempo especificado. O formato é hh:mm:ss")


@client.command()
async def volume(ctx, volume: int = 0):
    vc = ctx.voice_client
    if not ctx.author.voice:
        return await ctx.send("voce precisa estar em um canal de voz para mudar meu volume")
    elif not vc:
        return await ctx.send("eu não to em um canal de voz")
    elif ctx.me.voice.channel.name != ctx.author.voice.channel.name:
        return await ctx.send(f"eu to tocando musica nesse canal ó 👉 {ctx.me.voice.channel.name}")
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
    if not vc:
        return await ctx.send("eu não to em um canal de voz")
    
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
async def jacare(ctx):
    vc = ctx.voice_client
    CustomPlayer.playlist_ctx = ctx
    node = wavelink.NodePool.get_connected_node()
    if not vc:
        try:
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=CustomPlayer())
            await ctx.send(f"🐊 $jacare")
        except Exception as e:
            await ctx.send("Erro 0x4A6F")
            print(f"{type(e).__name__}\n{repr(e)}") 
    elif not ctx.author.voice.channel.name:
        return await ctx.send("voce precisa estar em um canal de voz. burro.")
    elif ctx.author.voice.channel.name != ctx.me.voice.channel.name:
        return await ctx.send("a gente precisa estar no mesmo canal bobo. eu sou só 1")
    if vc.jacare:
            return await ctx.send("Playlist tocando, espere acabar ou digite $parar para adicionar outras músicas.")
    playlist = await wavelink.YouTubePlaylist.search("https://www.youtube.com/playlist?list=PLlj4onbCBVbJXICgBqXbaifw23Xs5nGSk")
    playlist2 = await wavelink.YouTubePlaylist.search("https://www.youtube.com/playlist?list=PLlj4onbCBVbJpkaL9ms0-mUV1dSTD7D05")
    tracks: list[wavelink.YouTubeTrack] = playlist.tracks
    tracks2: list[wavelink.YoutubeTrack] = playlist2.tracks
    print(len(tracks))
    last_track = tracks[-1]
    print(tracks[0])
    print(last_track)
    print("###")
    last_track2 = tracks2[-1]
    print(len(tracks2))
    print(tracks2[0])
    print(last_track2)
    CustomPlayer.last_playlist_track = last_track2
    vc.queue.clear()
    cont = 0
    for track in tracks:
        vc.queue.put(track)
    for track in tracks2:
        vc.queue.put(track)
        vc.queue.shuffle()
    if not vc.is_playing():
        first = vc.queue.get()
        await vc.play(first)
        await asyncio.sleep(1)
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
    await ctx.send("Jacaré musicas tocando agora")
    vc.jacare = True 
    
        
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
    em.add_field(name="$jacare", value=" - se quiser, ouça a nossa playlist! :D")
    return await ctx.send(embed=em)
        
@musica.error
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Erro 0x4A6F-1")
        #print(f"{type(error).__name__}\n{repr(error)}") 
        await ctx.send("É possível que a música não esteja no Youtube.")
    else:
        await ctx.send("Erro 0x4A6F-2")
        #print(f"{type(error).__name__}\n{repr(error)}") 
  
client.run(token)
