import logging
import xml.etree.ElementTree as ET

import requests
from flask import Flask, render_template
from urllib3.exceptions import InsecureRequestWarning

app = Flask(__name__)

# Configure the logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG

# Create a global session for requests with SSL verification disabled
session = requests.Session()
session.verify = False  # Disable SSL verification

# Suppress InsecureRequestWarning (optional but recommended in this case)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Function to get games played by a BGG user
def get_games_played_for_user(username):
    app.logger.debug(f"Fetching games for user: {username}")
    url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&played=1"

    try:
        response = session.get(url)  # Use the session to make the request
        response.raise_for_status()  # Raise an error for bad responses
        app.logger.info(f"Received response for {username}, status code: {response.status_code}")

        games = parse_bgg_xml(response.content)
        app.logger.debug(f"Parsed {len(games)} games for user {username}")
        return games

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching games for {username}: {e}")
        return None


# Helper function to parse the XML data returned by the BGG API
def parse_bgg_xml(xml_data):
    games = []
    root = ET.fromstring(xml_data)

    for item in root.findall("item"):
        game_id = item.get("objectid")
        name = item.find("name").text
        image = item.find("image").text if item.find("image") is not None else ""

        games.append({"id": game_id, "name": name, "image": image})

    app.logger.debug(f"Successfully parsed {len(games)} games from XML")
    return games


# Sample route to test API call
@app.route("/")
def index():
    username = "otteydw"
    games = get_games_played_for_user(username)

    if games:
        return render_template("index.html", games=games[:5])
    else:
        return "No games found or error in fetching data."


if __name__ == "__main__":
    app.run(debug=True)
