from modules import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    """Gera o token para a API do Spotify, necessário para autenticação

    Returns:
        String: retorna o Token; se adquirido com sucesso.
    """
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    result = post(url, headers=headers, params= data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token



def get_auth_header(token):
    """Pega o header do GET request necessário para as buscas pela API

    Args:
        token (String): Token de autenticação da API do Spotify

    Returns:
        String: Contém a header do GET request
    """
    return {"Authorization": "Bearer " + token}