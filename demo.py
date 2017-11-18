from server import *

def main():
    while True:
        append_song_to_playlist()
        play_next_track()
        time.sleep(5)


def play_next_track():
    r = requests.post("https://api.spotify.com/v1/me/player/next", headers = get_request_headers())
    if r.status_code == 204:
        s = requests.put("https://api.spotify.com/v1/me/player/seek?position_ms=60000", headers = get_request_headers())
    else:
        logger.critical("Failure to skip to next track")
        logger.critical(r.text)

if __name__ == '__main__':
    main()