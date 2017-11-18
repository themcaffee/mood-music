import json
import os
from pprint import pprint
from sqlalchemy.exc import IntegrityError

import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    song_id = Column(String(250), nullable=False, unique=True)
    energy = Column(Float, nullable=False)
    danceability = Column(Float, nullable=False)
    key = Column(Integer, nullable=False)
    tempo = Column(Float, nullable=False)


def get_spotify_token():
    # export SPOTIPY_CLIENT_ID={client_id}
    # export SPOTIPY_CLIENT_SECRET={client_secret}
    # export SPOTIPY_REDIRECT_URI={redirect_uri}
    client_credentials_manager = SpotifyClientCredentials()

    scope = "user-read-currently-playing playlist-modify-private"

    # username = "1246334424"
    # run ~$ export SPOTIFY_USERNAME={your spotify username here}
    username = "holyshatots"
    token = util.prompt_for_user_token(username, scope)
    return token


def get_request_headers():
    token = get_spotify_token()
    headers = {"Authorization" : "Bearer %s" % token}
    return headers


def get_recommendations_list(headers, seed_uri):
    payload = {'seed_tracks': seed_uri}
    r = requests.get("https://api.spotify.com/v1/recommendations", headers=get_request_headers(), params=payload)
    tracks = r.json()["tracks"]
    track_ids = []
    for i in tracks:
        track_ids.append(i["id"])
    return track_ids


def get_audio_features(headers, track_uri):
    r = requests.get("https://api.spotify.com/v1/audio-features/{}".format(track_uri), headers=get_request_headers())
    return r.json()


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def get_next(headers, track_list):
    audio_features = {}
    new_track_list = []
    for i in track_list:
        audio_features[i] = get_audio_features(headers, i)
        recommend_list = get_recommendations_list(headers, i)
        for track in recommend_list:
            if track not in new_track_list:
                new_track_list.append(track)
    return audio_features, new_track_list


def create_tables(engine_db):
    Base.metadata.create_all(engine_db)


if __name__ == '__main__':
    engine = create_engine('sqlite:///songs.db')
    create_tables(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    print("Starting to get data from spotify")
    header = get_request_headers()
    track_list = get_recommendations_list(header, "0bRJboc2VNrbM5XAolC5gD")
    audio_features = {}

    for i in range(2):
        new_audio_features, track_list = get_next(header, track_list)
        pprint(track_list)
        audio_features = merge_two_dicts(audio_features, new_audio_features)

    pprint(audio_features)

    # Insert all of the data into db
    print("Inserting into db")
    for song_id, i in audio_features.items():
        try:
            new_song = Song(song_id=song_id,
                            energy=i['energy'],
                            danceability=i['danceability'],
                            key=i['key'],
                            tempo=i['tempo'])
            session.add(new_song)
            session.commit()
        except IntegrityError:
            print("(Dupe)")
            session.rollback()

    # Read records from database
    result = session.query(Song).count()
    print("{} records in database".format(str(result)))
