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
import random
from xml.etree import ElementTree

import requests
import requests_cache
from defusedxml.ElementTree import fromstring as defused_fromstring


class BGGUserError(Exception):
    pass


# Set up logging
logger = logging.getLogger(__name__)

# Create a global session for requests with SSL verification disabled
session = requests_cache.CachedSession("bgg_cache", use_cache_dir=True)
session.verify = False  # Disable SSL verification
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def get_games_played_for_user(username, order="default"):
    """
    Fetch the list of played games for a given BoardGameGeek user.

    This function sends a request to the BGG XML API2 to retrieve the collection
    of games that the specified user has marked as played. The order of games can
    be default (as fetched), random, or sorted by game name.

    Args:
        username (str): The BoardGameGeek username to fetch games for.
        order (str): The order in which to return the games. Options are:
                     'default' (as fetched), 'random' (random order),
                     or 'sorted' (sorted alphabetically by game name).

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

        # Parse the XML response
        root = ElementTree.fromstring(response.content)

        # Check if the response contains an error
        error_elem = root.find(".//error")
        if error_elem is not None:
            error_message = error_elem.find("message").text
            logger.error(f"BGG API error for {username}: {error_message}")
            raise BGGUserError(error_message)

        games = parse_bgg_xml(response.content)
        logger.debug(f"Parsed {len(games)} games for user {username}")

        # Process the ordering
        if order == "random":
            random.shuffle(games)
            logger.debug(f"Games shuffled randomly for user {username}")
        elif order == "sorted":
            games.sort(key=lambda game: game["name"])  # Assuming games have a "name" key
            logger.debug(f"Games sorted alphabetically for user {username}")

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
            url = boardgame_url(game_id)

            # Use the game_id as the key in the dictionary
            games_dict[game_id] = {"id": game_id, "name": name, "image": image, "url": url}

        logger.debug(f"Successfully parsed {len(games_dict)} unique games from XML")
    except Exception as e:
        logger.error(f"Error parsing XML data: {e}")

    # Convert the dictionary values to a list
    return list(games_dict.values())


def boardgame_url(id):
    """
    Generates a BoardGameGeek URL for a given board game ID.

    This function constructs the URL to the BoardGameGeek webpage for a specific
    board game using its unique identifier.

    Args:
        id (int): The unique identifier of the board game.

    Returns:
        str: The URL of the board game on BoardGameGeek.

    Raises:
        None
    """
    return f"https://boardgamegeek.com/boardgame/{id}/"


def check_bgg_user_exists(username):
    """
    Check if a BGG username exists using the lightweight user endpoint.

    Args:
        username (str): The BGG username to check

    Returns:
        bool: True if user exists, False if not

    Raises:
        BGGUserError: If there's a network or API issue
    """
    url = f"https://boardgamegeek.com/xmlapi2/user?name={username}"

    try:
        response = session.get(url)
        response.raise_for_status()
        # Check if response is HTML (indicating user doesn't exist)
        if "<h1>It appears we're missing some bits" in response.text:
            return False

        # If we got XML, try to parse it
        try:
            user = defused_fromstring(response.content)
            logger.debug(f"{user=}")
            return user is not None and "id" in user.attrib
        except ElementTree.ParseError:
            # If we can't parse as XML, user probably doesn't exist
            return False

    except requests.RequestException as e:
        raise BGGUserError(f"Unable to connect to BoardGameGeek: {str(e)}")
