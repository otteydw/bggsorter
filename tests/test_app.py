from unittest.mock import patch

from app import get_games_played_for_user, parse_bgg_xml
from tests.test_data import MOCK_PLAYED_GAMES_XML


@patch("app.session.get")
def test_get_games_played_for_user(mock_get):
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
    assert games[0]["id"] == "1"
    assert games[1]["name"] == "Game 2"


def test_parse_bgg_xml():
    # Use the shared mock data
    games = parse_bgg_xml(MOCK_PLAYED_GAMES_XML)

    # Assert the results
    assert len(games) == 2
    assert games[0]["id"] == "1"
    assert games[1]["image"] == "http://example.com/image2.jpg"
