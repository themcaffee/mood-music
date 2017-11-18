import falcon
import spotipy, json, time, sys, requests, os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

def get_spotify_token():
	client_credentials_manager = SpotifyClientCredentials()

	scope = "user-read-currently-playing playlist-modify-private"

	# username = "1246334424" 
	# run ~$ export SPOTIFY_USERNAME={your spotify username here}
	username = os.environ['SPOTIFY_USERNAME']
	token = util.prompt_for_user_token(username, scope)
	return token

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
		r = requests.get("https://api.spotify.com/v1/recommendations", headers = get_request_headers(), params = payload)
		resp.body = r.text

class CurrentlyPlayingResource(object):
	def on_get(self, req, resp):
		r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers = get_request_headers())
		resp.body = r.text


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