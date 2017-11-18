# Muse Music

Play music based on your current mood.
Using a Muse EEG headband we are able to scan a current level of mellowness from the wearer and use that to queue up songs on Spotify that keep up with the mood of the wearer in realtime.

![Muse Music in Action.gif](https://github.com/themcaffee/muse-music/blob/master/output.gif)
## Getting Started


### Prerequisites
You will need:
* Muse EEG-reading headband
* Device with python3 to process the headband data and interface with Spotify
* Spotify account with premium subscription
* Spotify developer account (free - https://developer.spotify.com)


### Usage

```
./muse-io --device 00:06:66:65:92:94 --osc osc.udp://127.0.0.1:5000
```

```
python muse_tool.py
```

```
export FLASK_RUN=predict_api.py
flask run --port 8000
```

To run the demo application also run this:
```
python demo.py
```

## Built With
* [Muse](http://www.choosemuse.com/) - EEG Headband
* [Spotipy](https://github.com/plamere/spotipy/) - Used for Spotify API Authentication
* [Spotify Web API](https://developer.spotify.com/web-api/) - Spotify API

## Authors
This project was created by Mitch McAffee and Rahul Ramkumar for hackusu 2017
