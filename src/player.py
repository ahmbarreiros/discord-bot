from search_spotify import *
from auth import get_auth_header, get_token
import spotipy
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

search_token = get_token()
# result = get_search(search_token)
# print(result["name"])
    
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id= client_id,
    client_secret= client_secret,
    redirect_uri= "https://localhost:8080",
    scope="user-read-playback-state, user-modify-playback-state, user-read-currently-playing, streaming"))


file_data = open(".cache")
data = json.load(file_data)
playback_token = data["access_token"]
if data["expires_in"] == 0:
    playback_token = sp.refresh_access_token(data["refresh_token"])
# results = sp.add_to_queue("https://open.spotify.com/track/0hZq8VE52aJJtLUWajO54w?si=1525fb8dcc424ea0")

# device_id = get_available_devices(playback_token)

# start_player(search_token, device_id, result)

# https://open.spotify.com/track/0hZq8VE52aJJtLUWajO54w?si=1525fb8dcc424ea0

