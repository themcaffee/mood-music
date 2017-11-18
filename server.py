import falcon
import spotipy, json, time, sys, requests, os, re, requests, math
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

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

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class ThingsResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ('\nTwo things awe me most, the starry sky '
                     'above me and the moral law within me.\n'
                     '\n'
                     '    ~ Immanuel Kant\n\n')

class RecommendationsResource(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        current_song_request = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers = get_request_headers())
        current_song_json = json.loads(current_song_request.text)
        current_song_uri = current_song_json["item"]["uri"].split(':')[2]
        print(current_song_json["item"]["uri"].split(':')[2])

        payload = {'seed_tracks': current_song_uri}
        recommendations = requests.get("https://api.spotify.com/v1/recommendations", headers = get_request_headers(), params = payload)
        recommendations_uri_list = recommendation_attributes(recommendations.text)

        #payload = {'ids': recommendations_uri_list.join(",")}
        payload = {'ids': ",".join(recommendations_uri_list)}
        r = requests.get("https://api.spotify.com/v1/audio-features", headers = get_request_headers(), params = payload)
        resp.body = r.text

class CurrentlyPlayingResource(object):
    def on_get(self, req, resp):
        r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers = get_request_headers())
        resp.body = r.text


def recommendation_attributes(recommendations_text):
    uris = re.findall(r'\"(?:spotify:track:)([\S]*)\"', recommendations_text)
    print(uris)
    return uris

def send_uris_to_mitch():
    current_song_request = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers = get_request_headers())
    current_song_json = json.loads(current_song_request.text)
    current_song_uri = current_song_json["item"]["uri"].split(':')[2]
    print(current_song_json["item"]["uri"].split(':')[2])

    mello = requests.get("http://144.39.201.45:8000/mellow")
    keep_it_mello = float(mello.text)
    payload = {'seed_tracks': current_song_uri, 'limit': 10, 'max_energy': keep_it_mello+0.15, 'min_energy': keep_it_mello-0.15}
    recommendations = requests.get("https://api.spotify.com/v1/recommendations", headers = get_request_headers(), params = payload)
    recommendations_uri_list = recommendation_attributes(recommendations.text)

    #payload = {'ids': recommendations_uri_list.join(",")}
    payload = {'ids': ",".join(recommendations_uri_list)}
    r = requests.get("https://api.spotify.com/v1/audio-features", headers = get_request_headers(), params = payload)
    best_song_id = ""
    no_r_json = r.json()['audio_features']
    smallest_difference = 1
    print(r.json())
    for i in no_r_json:
        energy = i['energy']
        diff = math.fabs(energy-(1-keep_it_mello))
        if diff < smallest_difference:
            best_song_id = i["id"]
            smallest_difference = diff
    #mitch = requests.post("http://144.39.201.45:8000/predict", json=json.loads(r.text))
    print(best_song_id)
    track_uri = "spotify:track:%s" % best_song_id.replace("\"", '')
    track_uri = track_uri.replace('\n', '')
    headers = get_request_headers()
    headers['Content-Type'] = 'application/json'
    data_var = "{\"uris\":[\"%s\"]}" % track_uri
    r = requests.post("https://api.spotify.com/v1/users/%s/playlists/%s/tracks" % (get_spotify_user_id(), "5Fbeyv4EISgBQF5P1ol9Tt"), headers = headers, data=data_var)
    print(data_var)
    q = requests.get("https://api.spotify.com/v1/audio-features/?ids=%s" % (",".join([track_uri.split(":")[2], current_song_uri])), headers = get_request_headers())
    print((",".join([track_uri, current_song_uri])))
    print(q.text)


# falcon.API instances are callable WSGI apps
app = falcon.API()

# Resources are represented by long-lived class instances
things = ThingsResource()
recommendations = RecommendationsResource()
currently_playing = CurrentlyPlayingResource()

# things will handle all requests to the '/things' URL path
app.add_route('/things', things)
app.add_route('/recommendations', recommendations)
app.add_route('/currently-playing', currently_playing)

def main():
    send_uris_to_mitch()

if __name__ == '__main__':
    main()