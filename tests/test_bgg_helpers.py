"""
Tests for the BoardGameGeek helper functions in bgg_helpers.py.
These tests verify the functionality of fetching and parsing game data from the BGG API.
"""

from unittest.mock import patch

import requests
from bgg_helpers import BGGUserError, boardgame_url, check_bgg_user_exists, get_games_played_for_user, parse_bgg_xml

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
