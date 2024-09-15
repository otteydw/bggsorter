"""BoardGameGeek API Helper Functions

This module provides helper functions to interact with the BoardGameGeek (BGG) API.
It includes functionality to fetch and parse game data for BGG users.

The module uses requests for HTTP communication and defusedxml for safe XML parsing.
It also implements request caching to improve performance and reduce API load.

Note:
    SSL verification is disabled for the requests session. This is not recommended
    for production use and should be addressed in a secure environment.
"""

import logging

import requests
import requests_cache
from defusedxml.ElementTree import fromstring as defused_fromstring

# Set up logging
logger = logging.getLogger(__name__)

# Create a global session for requests with SSL verification disabled
session = requests_cache.CachedSession("bgg_cache", use_cache_dir=True)
session.verify = False  # Disable SSL verification
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def get_games_played_for_user(username):
    """
    Fetch the list of played games for a given BoardGameGeek user.

    This function sends a request to the BGG XML API2 to retrieve the collection
    of games that the specified user has marked as played.

    Args:
        username (str): The BoardGameGeek username to fetch games for.

    Returns:
        list or None: A list of dictionaries containing game information if successful,
                      or None if an error occurs.

    Raises:
        requests.exceptions.RequestException: If there's an error with the HTTP request.

    Note:
        This function uses a cached session to improve performance and reduce API load.
    """

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
    """
    Parse the XML data returned by the BoardGameGeek API.

    This function takes the raw XML content from a BGG API response and extracts
    relevant game information, returning it as a list of dictionaries.

    Args:
        xml_data (bytes): The raw XML data to parse.

    Returns:
        list: A list of dictionaries, each containing information about a game.
              Each dictionary includes 'id', 'name', and 'image' keys.

    Raises:
        Exception: If there's an error parsing the XML data.

    Note:
        This function uses defusedxml for secure XML parsing to prevent XML vulnerabilities.
    """

    games_dict = {}
    try:
        root = defused_fromstring(xml_data)
        for item in root.findall("item"):
            game_id = int(item.get("objectid"))
            name = item.find("name").text
            image = item.find("image").text if item.find("image") is not None else ""

            # Use the game_id as the key in the dictionary
            games_dict[game_id] = {"id": game_id, "name": name, "image": image}

        logger.debug(f"Successfully parsed {len(games_dict)} unique games from XML")
    except Exception as e:
        logger.error(f"Error parsing XML data: {e}")

    # Convert the dictionary values to a list
    return list(games_dict.values())
