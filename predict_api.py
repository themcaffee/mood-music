import math
from flask import Flask, request, jsonify

# Config
AVERAGE_FILE = "mellow_avg"

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Expected json [{"danceability": 0.0, "energy": 0.0, "id": "songid"}]
    :return: The best song based on the current mood
    """
    json = request.get_json()

    with open(AVERAGE_FILE, 'r') as f:
        read_avg_float = float(f.read())

    # Find the song with the closest energy to the current

    # Calculate the difference between the inverse mellow_avg and the energy
    best_song_id = ""
    smallest_difference = 1
    for i in json:
        energy = i['energy']
        diff = math.fabs(energy-(1-read_avg_float))
        if diff < smallest_difference:
            best_song_id = i["id"]
            smallest_difference = diff

    return jsonify(best_song_id), 200
