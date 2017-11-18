import spotipy, json, time, sys, requests, os, re, requests, math, logging
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

MAX_MELLOW_DIFFERENCE = 0.15
NUMBER_OF_RECOMMENDATIONS = 10
SPOTIFY_PLAYLIST_ID="5Fbeyv4EISgBQF5P1ol9Tt"
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-16s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_spotify_token():
    client_credentials_manager = SpotifyClientCredentials()

    scope = "user-read-currently-playing playlist-modify-private playlist-modify-public user-modify-playback-state"

    # username = "1246334424" 
    # run ~$ export SPOTIFY_USERNAME={your spotify username here}
    username = os.environ['SPOTIFY_USERNAME']
    token = util.prompt_for_user_token(username, scope)
    return token

def get_spotify_user_id():
    return os.environ['SPOTIFY_USERNAME']

def get_request_headers():
    token = get_spotify_token()
    headers = {"Authorization" : "Bearer %s" % token}
    return headers

def recommendation_attributes(recommendations_text):
    uris = re.findall(r'\"(?:spotify:track:)([\S]*)\"', recommendations_text)
    print(uris)
    return uris

def get_current_song_uri():
    current_song_request = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers = get_request_headers())
    current_song_json = json.loads(current_song_request.text)
    current_song_uri = current_song_json["item"]["uri"].split(':')[2]
    logger.info("Current Playing Song URI: %s" % current_song_uri)
    return current_song_uri

def get_mitches_mellow():
    mello = requests.get("http://144.39.201.45:8000/mellow")
    logger.info("Mitch's mellow is at %s" % mello.text.replace('\n', ''))
    return float(mello.text)

def generate_recommendation():
    mitches_mellow = get_mitches_mellow()
    payload = {'seed_tracks': get_current_song_uri(), 
    'limit': NUMBER_OF_RECOMMENDATIONS, 'max_energy': mitches_mellow+MAX_MELLOW_DIFFERENCE, 
    'min_energy': mitches_mellow-MAX_MELLOW_DIFFERENCE}
    r = requests.get("https://api.spotify.com/v1/audio-features", 
        headers = get_request_headers(), params = payload)
    json_data = r.json()['audio_features']
    smallest_diff = 1
    best_song_id = ''
    for i in json_data:
        energy = i['energy']
        diff = math.fabs(energy-(1-mitches_mellow))
        if diff < smallest_diff:
            best_song_id = i["id"]
            smallest_diff = diff
    logger.info("Closest Song URI: %s" % best_song_id)
    return best_song_id

def append_song_to_playlist():
    track_uri = "spotify:track:%s" % generate_recommendation().replace("\"", '')
    track_uri = track_uri.replace('\n', '')
    headers = get_request_headers()
    headers['Content-Type'] = 'application/json'
    data_var = "{\"uris\":[\"%s\"]}" % track_uri
    r = requests.post("https://api.spotify.com/v1/users/%s/playlists/%s/tracks" % (get_spotify_user_id(), SPOTIFY_PLAYLIST_ID), headers = headers, data=data_var)
    logger.info("Added track to playlist: %s" % track_uri)
    q = requests.get("https://api.spotify.com/v1/audio-features/?ids=%s" % (",".join([track_uri.split(":")[2], get_current_song_uri()])), headers = get_request_headers())
    print(q.text)

def main():
    append_song_to_playlist()
    

if __name__ == '__main__':
    main()