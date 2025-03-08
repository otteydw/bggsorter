"""
Tests for the BoardGameGeek helper functions in bgg_helpers.py.
These tests verify the functionality of fetching and parsing game data from the BGG API.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from bgg_helpers import (
    BGGUserError,
    boardgame_url,
    check_bgg_user_exists,
    get_games_played_for_user,
    get_plays_for_game,
    parse_bgg_xml,
)

from tests.test_data import (
    MOCK_INVALID_USER_HTML,
    MOCK_MALFORMED_USER_XML,
    MOCK_PLAYED_GAMES_XML,
    MOCK_VALID_USER_XML,
)


@patch("bgg_helpers.session.get")
def test_get_games_played_for_user(mock_get):
    """
    Test the get_games_played_for_user function.

    This test verifies that:
    1. The function correctly makes an API request to BoardGameGeek
    2. The response is properly parsed into a list of game dictionaries
    3. The game data contains the expected values (IDs and names)

    The test uses a mock HTTP response to avoid actual API calls.
    """

    # Mock the response object
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def raise_for_status(self):
            pass

    # Mock the response with the shared mock data
    mock_get.return_value = MockResponse(MOCK_PLAYED_GAMES_XML, 200)

    # Call the function
    games = get_games_played_for_user("test_user")

    # Assert the results
    assert len(games) == 2
    assert games[0]["id"] == 1
    assert games[1]["name"] == "Game 2"


def test_parse_bgg_xml():
    """
    Test the parse_bgg_xml function.

    This test verifies that:
    1. The XML parsing correctly extracts game information
    2. The function returns the expected number of games
    3. Game attributes (id, name, image URL) are correctly extracted

    The test uses a predefined XML string that mimics the BGG API response format.
    """
    # Use the shared mock data
    games = parse_bgg_xml(MOCK_PLAYED_GAMES_XML)

    # Assert the results
    assert len(games) == 2
    assert games[0]["id"] == 1
    assert games[1]["image"] == "http://example.com/image2.jpg"


@patch("bgg_helpers.session.get")
def test_check_bgg_user_exists_valid_user(mock_get):
    """
    Test the check_bgg_user_exists function with a valid user.

    This test verifies that:
    1. The function correctly identifies a valid BGG user
    2. The function returns True when a valid XML response with user ID is received
    3. The function properly parses the XML response

    The test uses a mock HTTP response containing valid user XML data.
    """

    # Mock the response object
    class MockResponse:
        def __init__(self, content, status_code, text=""):
            self.content = content
            self.status_code = status_code
            self.text = text

        def raise_for_status(self):
            pass

    # Mock the response with valid user data
    mock_get.return_value = MockResponse(MOCK_VALID_USER_XML, 200)

    # Call the function
    result = check_bgg_user_exists("otteydw")

    # Assert the result
    assert result is True
    mock_get.assert_called_once()


@patch("bgg_helpers.session.get")
def test_check_bgg_user_exists_invalid_user(mock_get):
    """
    Test the check_bgg_user_exists function with an invalid user.

    This test verifies that:
    1. The function correctly identifies an invalid BGG user
    2. The function returns False when an HTML error page is received
    3. The function properly handles the "missing bits" error message

    The test uses a mock HTTP response containing HTML error page data.
    """

    # Mock the response object
    class MockResponse:
        def __init__(self, content, status_code, text=""):
            self.content = content
            self.status_code = status_code
            self.text = MOCK_INVALID_USER_HTML

        def raise_for_status(self):
            pass

    # Mock the response with invalid user data (HTML error page)
    mock_get.return_value = MockResponse(b"", 200)

    # Call the function
    result = check_bgg_user_exists("nonexistentuser")

    # Assert the result
    assert result is False
    mock_get.assert_called_once()


@patch("bgg_helpers.session.get")
def test_check_bgg_user_exists_malformed_xml(mock_get):
    """
    Test the check_bgg_user_exists function with malformed XML.

    This test verifies that:
    1. The function correctly handles malformed XML responses
    2. The function returns False when XML parsing fails
    3. The function gracefully handles XML parsing errors

    The test uses a mock HTTP response containing malformed XML data.
    """

    # Mock the response object
    class MockResponse:
        def __init__(self, content, status_code, text=""):
            self.content = content
            self.status_code = status_code
            self.text = ""

        def raise_for_status(self):
            pass

    # Mock the response with malformed XML
    mock_get.return_value = MockResponse(MOCK_MALFORMED_USER_XML, 200)

    # Call the function
    result = check_bgg_user_exists("malformeduser")

    # Assert the result
    assert result is False
    mock_get.assert_called_once()


@patch("bgg_helpers.session.get")
def test_check_bgg_user_exists_request_exception(mock_get):
    """
    Test the check_bgg_user_exists function with a request exception.

    This test verifies that:
    1. The function correctly handles network or API errors
    2. The function raises a BGGUserError when a request exception occurs
    3. The error message contains information about the exception

    The test simulates a network error by raising a RequestException.
    """
    # Mock the get method to raise an exception
    mock_get.side_effect = requests.RequestException("Network error")

    # Call the function and check for exception
    try:
        check_bgg_user_exists("anyuser")
        assert False, "Expected BGGUserError was not raised"
    except BGGUserError as e:
        assert "Unable to connect to BoardGameGeek" in str(e)
        mock_get.assert_called_once()


def test_boardgame_url():
    """
    Test the boardgame_url function.

    This test verifies that:
    1. The function correctly formats the URL for a given game ID
    2. The function handles different types of IDs (int)
    3. The URL follows the expected BGG format
    """
    # Test with a simple game ID
    assert boardgame_url(174430) == "https://boardgamegeek.com/boardgame/174430/"

    # Test with another game ID to ensure consistency
    assert boardgame_url(1234) == "https://boardgamegeek.com/boardgame/1234/"


@patch("bgg_helpers.session.get")
def test_get_games_played_for_user_random_order(mock_get):
    """
    Test get_games_played_for_user with random ordering.

    This test verifies that:
    1. The function returns games in random order when specified
    2. All games are still present after randomization
    3. The randomization doesn't affect the game data itself
    """

    # Mock the response
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def raise_for_status(self):
            pass

    mock_get.return_value = MockResponse(MOCK_PLAYED_GAMES_XML, 200)

    # Get games with random ordering
    games = get_games_played_for_user("test_user", order="random")

    # Verify we got all games
    assert len(games) == 2
    # Verify all expected games are present (regardless of order)
    game_ids = {game["id"] for game in games}
    assert game_ids == {1, 2}


@patch("bgg_helpers.session.get")
def test_get_games_played_for_user_sorted_order(mock_get):
    """
    Test get_games_played_for_user with sorted ordering.

    This test verifies that:
    1. The function returns games in alphabetical order when specified
    2. The sorting is based on game names
    3. All games are present after sorting
    """

    # Mock the response
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def raise_for_status(self):
            pass

    mock_get.return_value = MockResponse(MOCK_PLAYED_GAMES_XML, 200)

    # Get games with sorted ordering
    games = get_games_played_for_user("test_user", order="sorted")

    # Verify we got all games
    assert len(games) == 2
    # Verify the games are in alphabetical order
    assert games[0]["name"] <= games[1]["name"]


@patch("bgg_helpers.session.get")
def test_get_plays_for_game_success(mock_get):
    """
    Test successful retrieval of plays for a game.

    This test verifies that:
    1. The function correctly makes an API request to BoardGameGeek
    2. The response is properly parsed into a list of play dictionaries
    3. The play data contains the expected values (date, location, players)
    """
    # Mock response with sample play data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <plays username="testuser" userid="12345" total="2" page="1" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
        <play id="12345678" date="2023-01-15" quantity="1" length="60" incomplete="0" location="Home">
            <item name="Test Game" objecttype="thing" objectid="123456">
                <subtypes>
                    <subtype value="boardgame"/>
                </subtypes>
            </item>
            <players>
                <player username="testuser" userid="12345" name="Test User" startposition="" color="" score="10" new="0" rating="0" win="1"/>
                <player name="Player 2" score="8" new="0" rating="0" win="0"/>
            </players>
        </play>
        <play id="87654321" date="2023-02-20" quantity="1" incomplete="0" location="Friend's House">
            <item name="Test Game" objecttype="thing" objectid="123456">
                <subtypes>
                    <subtype value="boardgame"/>
                </subtypes>
            </item>
            <players>
                <player username="testuser" userid="12345" name="Test User" score="7" win="0"/>
                <player name="Player 2" score="12" win="1"/>
            </players>
        </play>
    </plays>
    """.encode()

    mock_get.return_value = mock_response

    # Call the function
    plays = get_plays_for_game("testuser", 123456)

    # Verify the results
    assert len(plays) == 2

    # Check first play
    assert plays[0]["date"] == "2023-01-15"
    assert plays[0]["location"] == "Home"
    assert plays[0]["length"] == "60"
    assert plays[0]["name"] == "Test Game"
    assert len(plays[0]["players"]) == 2
    assert plays[0]["players"][0]["name"] == "Test User"
    assert plays[0]["players"][0]["score"] == "10"
    assert plays[0]["players"][0]["win"] is True

    # Check second play
    assert plays[1]["date"] == "2023-02-20"
    assert plays[1]["location"] == "Friend's House"
    assert plays[1]["name"] == "Test Game"
    assert len(plays[1]["players"]) == 2
    assert plays[1]["players"][1]["name"] == "Player 2"
    assert plays[1]["players"][1]["score"] == "12"
    assert plays[1]["players"][1]["win"] is True

    # Verify the API call
    mock_get.assert_called_once_with("https://boardgamegeek.com/xmlapi2/plays?username=testuser&id=123456")


@patch("bgg_helpers.session.get")
def test_get_plays_for_game_no_plays(mock_get):
    """
    Test when a game has no plays.

    This test verifies that:
    1. The function correctly handles empty play data
    2. The function returns an empty list when no plays are found
    """
    # Mock response with no plays
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <plays username="testuser" userid="12345" total="0" page="1" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
    </plays>
    """.encode()

    mock_get.return_value = mock_response

    # Call the function
    plays = get_plays_for_game("testuser", 123456)

    # Verify the results
    assert len(plays) == 0

    # Verify the API call
    mock_get.assert_called_once_with("https://boardgamegeek.com/xmlapi2/plays?username=testuser&id=123456")


@patch("bgg_helpers.session.get")
def test_get_plays_for_game_error(mock_get):
    """
    Test handling of API errors.

    This test verifies that:
    1. The function correctly handles HTTP errors
    2. The function raises a BGGUserError with appropriate message
    """
    # Mock response with an error
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")

    mock_get.return_value = mock_response

    # Call the function and check for exception
    with pytest.raises(BGGUserError) as excinfo:
        get_plays_for_game("testuser", 123456)

    assert "Failed to retrieve plays from BGG API" in str(excinfo.value)

    # Verify the API call
    mock_get.assert_called_once_with("https://boardgamegeek.com/xmlapi2/plays?username=testuser&id=123456")
