from modules import *
from auth import get_auth_header, get_token
# print(client_id, client_secret)



### SEARCHER PARA BUSCAS EM INPUT

def searcher(token, search):
    """Corpo inicial do algoritmo de busca do Spotify caso a busca seja por escrito, e não um link direto do Spotify

    Args:
        token (String): Token de autenticação da API do Spotify
        search (String): Busca realizada pelo usuário, podendo ser: Músicas, Artistas, Albums, PLaylists.

    Returns:
        object: Resultados da busca
    """
    limit = 1
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={search}&type=artist,track,playlist,album&market=BR&limit={limit}&offset=0&include_external=audio"
    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    if len(json_result) == 0:
        print("no media found...")
        return None
    
    # print(json_result[list(json_result.keys())[0]])
    # print(json_result[list(json_result.keys())[1]])
    # print(json_result[list(json_result.keys())[1]]["items"]) #return
    return check_content(token, search, json_result)

def check_content(token, search, json):
    """Checa se há resultados existentes para a busca feita pelo usuário

    Args:
        search (String): Busca realizada pelo usuário, podendo ser: Músicas, Artistas, Albums, PLaylists.
        json (object): json inicial da busca, podendo conter resultados de: Músicas, Artistas, Albums, PLaylists.
    
    Returns:
        object: json com o resultado correspondente, caso exista
    """
    has_track = False
    has_album = False
    has_artist = False
    has_playlist = False
    
    for object in json:
        json_items = json[object]["items"][0]
        nome = json_items["name"].strip().lower()
        json_type = json_items["type"]
        search_better = search.strip().lower()
        # print("inicio")
        # print("nome: " + nome)
        # print("objeto: " + object)
        # print("tipo dentro do objeto: " + json_items["type"])
        # print("search: " + search)
        # print(json_items)
        equal = search_better == nome
        # print("FIM\n")
        if (equal and json_type == "track"):
            has_track = True
        elif (equal and json_type == "album"):
            has_album = True
        elif (equal and json_type == "artist"):
            has_artist = True
        elif (equal and json_type == "playlist"):
            has_playlist = True
    if (not has_track) and (not has_album) and (not has_artist) and has_playlist:
        return json["playlists"]["items"][0]
    most_popular = compare_popularity(has_track, has_album, has_artist, json, token)
    return most_popular
    
def compare_popularity(track, album, artist, json, token) -> object:
    """Checa se existem tracks, albums, artistas e/ou playlists e comparam a popularidade entre eles

    Args:
        track (boolean): existem tracks que satisfazem a busca? true ou false
        album (boolean): existem albums que satisfazem a busca? true ou false
        artist (boolean): existem artistas que satisfazem a busca? true ou false
        playlist (boolean): existem playlists que satisfazem a busca? true ou false
        json (object): arquivo json que será iterado para descobrir a popularidade dos itens

    Returns:
        object: json que contém o item mais popular entre os existentes
    """
    default_popularity = -1
    track_popularity = default_popularity
    album_popularity = default_popularity
    artist_popularity = default_popularity
    
    print(track)
    print(album)
    print(artist)
    
    if track:
        try:
            track_popularity = json["tracks"]["items"][0]["popularity"]
        except:
            track_popularity = 50
    if album:
        try:
            spotify_url = json["albums"]["items"][0]["external_urls"]["spotify"]
            json_album = check_query(token, spotify_url)
            album_popularity = json_album["popularity"]
        except:
            album_popularity = 50
    if artist:
        try:
            artist_popularity = json["artists"]["items"][0]["popularity"]
        except:
            artist_popularity = 50
        
    print("track: " + str(track_popularity))
    print("album: " + str(album_popularity))
    print("artist: " + str(artist_popularity))
    if(track_popularity > album_popularity and track_popularity > artist_popularity):
        return json["tracks"]["items"][0]
    elif(album_popularity > track_popularity and album_popularity > artist_popularity):
        return json["albums"]["items"][0]
    elif(artist_popularity > album_popularity and artist_popularity > track_popularity):
        return json["artists"]["items"][0]
    elif(artist_popularity > track_popularity and album_popularity > track_popularity):
        if(album_popularity > artist_popularity):
            return json["albums"]["items"][0]
        else:
            return json["artists"]["items"][0]
    else:
        return json["tracks"]["items"][0]
    
    

def check_query(token, query):
    query_str = query.strip()
    result = validators.url(query_str)
    if not result:
        return searcher(token, query)
    else:
        return url_finder(token, query)


### SEARCHER PARA LINKS DO SPOTIFY
def url_finder(token, query_url):
    domain = "open.spotify.com/"
    headers = get_auth_header(token)
    removed_http = query_url.split("//")[-1]
    type_id_list = removed_http.split(domain)[-1].split("/")
    
    type_list = type_id_list[0]
    id_list = type_id_list[1]
    
    endpoint = type_manager(type_list)
    api_url = endpoint + id_list
    result = get(api_url, headers=headers)
    # print(result)
    json_result = json.loads(result.content)
    # json_result[list(json_result.keys())[1]]
    # if json_result["is_playable"] == True:
    return json_result
    


def type_manager(type_list):
    endpoint = ''
    if type_list == "album":
        endpoint = "https://api.spotify.com/v1/albums/"
    elif type_list == "track":
        endpoint = "https://api.spotify.com/v1/tracks/"
    elif type_list == "artist":
        endpoint = "https://api.spotify.com/v1/artists/"
    elif type_list == "playlist":
        endpoint = "https://api.spotify.com/v1/playlists/"
    return endpoint

def get_search(token, search = ""):
    if search:
        query = search
    else: 
        query = input("Faça sua busca: ")
    result = check_query(token, query)
    
    return result

# print(result["artists"][0]["name"])

# result = searcher(token, query)
# result_id = result["id"]
# print(result)
# print(result_id)
# print(result["name"])
# print(result["type"])
# print(result['popularity'])
# print(result["artists"][0]["name"])