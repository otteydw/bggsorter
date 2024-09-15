import logging

import requests
from defusedxml.ElementTree import fromstring as defused_fromstring

# Set up logging
logger = logging.getLogger(__name__)

# Create a global session for requests with SSL verification disabled
session = requests.Session()
session.verify = False  # Disable SSL verification
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def get_games_played_for_user(username):
    logger.debug(f"Fetching games for user: {username}")
    url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&played=1"

    try:
        response = session.get(url)
        response.raise_for_status()
        logger.info(f"Received response for {username}, status code: {response.status_code}")

        games = parse_bgg_xml(response.content)
        logger.debug(f"Parsed {len(games)} games for user {username}")
        return games

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching games for {username}: {e}")
        return None


def parse_bgg_xml(xml_data):
    games = []
    try:
        root = defused_fromstring(xml_data)
        for item in root.findall("item"):
            game_id = item.get("objectid")
            name = item.find("name").text
            image = item.find("image").text if item.find("image") is not None else ""

            games.append({"id": game_id, "name": name, "image": image})

        logger.debug(f"Successfully parsed {len(games)} games from XML")
    except Exception as e:
        logger.error(f"Error parsing XML data: {e}")

    return games
