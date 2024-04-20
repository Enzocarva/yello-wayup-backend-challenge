from flask import Flask, request, jsonify
import string
import random

app = Flask(__name__)

# Dictionary to store short URLs and their corresponding original URLs
url_mapping = {}


def generate_short_url():
    """
    Generate a random 6-character string for the short URL
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(6))


@app.route("/encode", methods=["POST"])
def encode():
    """
    Encode a long URL to a short URL
    """
    data = request.get_json()
    long_url = data.get("long_url")

    if not long_url:
        return jsonify({"error": "Missing long_url parameter"}), 400

    short_url = generate_short_url()
    url_mapping[short_url] = long_url

    return jsonify({"short_url": f"https://short.est/{short_url}"}), 200


@app.route("/decode", methods=["POST"])
def decode():
    """
    Decode a short URL to its original URL
    """
    data = request.get_json()
    short_url = data.get("short_url")

    if not short_url:
        return jsonify({"error": "Missing short_url parameter"}), 400

    short_url_key = short_url.split("/")[-1]
    long_url = url_mapping.get(short_url_key)

    if not long_url:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({"long_url": long_url}), 200


if __name__ == "__main__":
    app.run(debug=True)
