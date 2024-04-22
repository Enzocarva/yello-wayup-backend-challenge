from flask import Flask, request, jsonify, g, render_template
import string
import random
import mysql.connector

app = Flask(__name__)


# Create the application and return the entire app inside of the scope of app_context in order to close it properly later
def create_app():
    with app.app_context():
        return app


# Establish a connection to MySQL create the table if necessary, and return the cursor
def get_db_cursor():
    if "db_cursor" not in g:
        g.db_connection = mysql.connector.connect(
            host="localhost", user="ecarvalho", password="mypassword123", database="URL_shortener"
        )
        g.db_cursor = g.db_connection.cursor()

        g.db_cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS url_mappings (
        id INT PRIMARY KEY AUTO_INCREMENT,
        short_url VARCHAR(255) NOT NULL,
        long_url VARCHAR(511) NOT NULL
        );
                    """
        )
        g.db_connection.commit()

    return g.db_cursor


def generate_short_url():
    """
    Generate a random 6-character string for the short URL (from upper, lower case and digits)
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(6))


@app.route("/encode", methods=["POST"])
def encode():
    """
    Encode a long URL to a short URL
    """
    # Retrieve the JSON data and get the long_url value
    data = request.get_json()
    long_url = data.get("long_url")

    # Return an error if there is no long_url in JSON received
    if not long_url:
        return jsonify({"error": "Missing long_url parameter"}), 400

    # Get the database cursor (and create it if not already created)
    cursor = get_db_cursor()

    # Check if long_url is already in the database, if yes return it, else generate a new short_url
    query = "SELECT short_url FROM url_mappings WHERE long_url = %s"
    cursor.execute(query, (long_url,))
    row = cursor.fetchone()
    if row:
        short_url = row[0]
    else:
        # Generate a short_url and map it to the long_url in the database
        short_url = generate_short_url()
        query = "INSERT INTO url_mappings (short_url, long_url) VALUES (%s, %s)"
        cursor.execute(query, (short_url, long_url))
        g.db_connection.commit()

    return jsonify({"short_url": f"https://short.est/{short_url}"}), 200


@app.route("/decode", methods=["POST"])
def decode():
    """
    Decode a short URL to its original URL
    """
    # Retrieve the JSON data received and get the short_url value
    data = request.get_json()
    short_url = data.get("short_url")

    # Return an error if there is no short_url in JSON received
    if not short_url:
        return jsonify({"error": "Missing short_url parameter"}), 400

    # Get the short_url "key" (the random 6 character string at the end of the short_url)
    short_url_key = short_url.split("/")[-1]

    # Attempt to retrieve the short_url that was encoded in the database
    cursor = get_db_cursor()
    query = "SELECT long_url FROM url_mappings WHERE short_url = %s"
    cursor.execute(query, (short_url_key,))
    row = cursor.fetchone()
    if not row:
        # return an error if ther is not short URL associated with qued long_url
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({"long_url": row[0]}), 200


@app.route("/")
def index():
    return render_template("index.html")


@app.teardown_appcontext
def close_database(exception):
    if hasattr(g, "db_cursor"):
        g.db_cursor.close()
    if hasattr(g, "db_connection"):
        g.db_connection.close()


if __name__ == "__main__":
    create_app()  # Call this method before app.run to get the whole app in app.context's scope.
    app.run(debug=True)
