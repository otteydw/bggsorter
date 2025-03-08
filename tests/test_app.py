"""
Tests for the Flask application functions in app.py.
These tests verify the functionality of data loading, saving, and other app utilities.
"""

import json
import os
import shutil
import tempfile
from unittest.mock import mock_open, patch

import pytest
from app import delete_data, load_data, max_comparisons, save_data, unskip_selected_games


@pytest.fixture
def temp_data_dir():
    """
    Create a temporary directory for test data files.

    This fixture creates a temporary directory for storing test data files,
    sets the DATA_DIR constant to point to this directory during tests,
    and cleans up the directory after tests are complete.
    """
    original_data_dir = "data"
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch the DATA_DIR constant
        with patch("app.DATA_DIR", temp_dir):
            yield temp_dir


def test_load_data_existing_file(temp_data_dir):
    """
    Test loading data from an existing JSON file.

    This test verifies that:
    1. The function correctly loads data from an existing JSON file
    2. The loaded data matches the expected structure and content
    3. The function handles valid JSON data properly
    """
    # Create a test JSON file
    username = "testuser"
    test_data = {"skipped": [1, 2], "sorted": [3, 4], "unsorted": [5, 6]}
    file_path = os.path.join(temp_data_dir, f"{username}.json")

    with open(file_path, "w") as f:
        json.dump(test_data, f)

    # Load the data
    loaded_data = load_data(username)

    # Verify the loaded data matches the test data
    assert loaded_data == test_data
    assert loaded_data["skipped"] == [1, 2]
    assert loaded_data["sorted"] == [3, 4]
    assert loaded_data["unsorted"] == [5, 6]


def test_load_data_nonexistent_file(temp_data_dir):
    """
    Test loading data when the file doesn't exist.

    This test verifies that:
    1. The function returns a default data structure when the file doesn't exist
    2. The default structure contains the expected keys with empty lists
    3. No error is raised when the file is missing
    """
    # Load data for a username that doesn't have a file
    username = "nonexistentuser"
    loaded_data = load_data(username)

    # Verify the default data structure is returned
    assert loaded_data == {"skipped": [], "sorted": [], "unsorted": []}
    assert isinstance(loaded_data["skipped"], list)
    assert isinstance(loaded_data["sorted"], list)
    assert isinstance(loaded_data["unsorted"], list)


def test_save_data(temp_data_dir):
    """
    Test saving data to a JSON file.

    This test verifies that:
    1. The function correctly saves data to a JSON file
    2. The saved file contains the expected data
    3. The function creates the file if it doesn't exist
    """
    # Data to save
    username = "testuser"
    test_data = {"skipped": [7, 8], "sorted": [9, 10], "unsorted": [11, 12]}

    # Save the data
    save_data(username, test_data)

    # Verify the file was created
    file_path = os.path.join(temp_data_dir, f"{username}.json")
    assert os.path.exists(file_path)

    # Verify the file contains the expected data
    with open(file_path, "r") as f:
        saved_data = json.load(f)

    assert saved_data == test_data
    assert saved_data["skipped"] == [7, 8]
    assert saved_data["sorted"] == [9, 10]
    assert saved_data["unsorted"] == [11, 12]


def test_save_data_overwrites_existing_file(temp_data_dir):
    """
    Test that save_data overwrites an existing file.

    This test verifies that:
    1. The function overwrites an existing file with new data
    2. The old data is completely replaced by the new data
    3. The function handles updating existing files properly
    """
    # Create an initial file
    username = "testuser"
    initial_data = {"skipped": [1], "sorted": [2], "unsorted": [3]}
    file_path = os.path.join(temp_data_dir, f"{username}.json")

    with open(file_path, "w") as f:
        json.dump(initial_data, f)

    # Save new data
    new_data = {"skipped": [4], "sorted": [5], "unsorted": [6]}
    save_data(username, new_data)

    # Verify the file was updated
    with open(file_path, "r") as f:
        saved_data = json.load(f)

    assert saved_data == new_data
    assert saved_data != initial_data


def test_delete_data(temp_data_dir):
    """
    Test deleting user data.

    This test verifies that:
    1. The function correctly deletes a user's data file
    2. The file no longer exists after deletion
    3. No error is raised when deleting a file that exists
    """
    # Create a test file
    username = "testuser"
    test_data = {"skipped": [], "sorted": [], "unsorted": []}
    file_path = os.path.join(temp_data_dir, f"{username}.json")

    with open(file_path, "w") as f:
        json.dump(test_data, f)

    # Verify the file exists
    assert os.path.exists(file_path)

    # Delete the data
    delete_data(username)

    # Verify the file no longer exists
    assert not os.path.exists(file_path)


def test_delete_data_nonexistent_file(temp_data_dir):
    """
    Test deleting data when the file doesn't exist.

    This test verifies that:
    1. The function doesn't raise an error when the file doesn't exist
    2. The function handles the case gracefully
    """
    # Delete data for a username that doesn't have a file
    username = "nonexistentuser"
    file_path = os.path.join(temp_data_dir, f"{username}.json")

    # Verify the file doesn't exist
    assert not os.path.exists(file_path)

    # Delete the data (should not raise an error)
    delete_data(username)

    # Verify the file still doesn't exist
    assert not os.path.exists(file_path)


def test_max_comparisons():
    """
    Test the max_comparisons function.

    This test verifies that:
    1. The function correctly calculates the maximum number of comparisons
    2. The function handles various input values correctly
    3. The function returns the expected values for known inputs
    """
    # Test with various list lengths
    assert max_comparisons(0) == 0  # Empty list
    assert max_comparisons(1) == 1  # One item
    assert max_comparisons(2) == 2  # Two items
    assert max_comparisons(3) == 2  # Three items
    assert max_comparisons(4) == 3  # Four items
    assert max_comparisons(7) == 3  # Seven items
    assert max_comparisons(8) == 4  # Eight items
    assert max_comparisons(15) == 4  # Fifteen items
    assert max_comparisons(16) == 5  # Sixteen items


def test_unskip_selected_games(temp_data_dir):
    """
    Test the unskip_selected_games function.

    This test verifies that:
    1. The function correctly moves games from skipped to unsorted
    2. The function only moves the selected games
    3. The function updates the user data file correctly
    """
    # Create a test file with skipped games
    username = "testuser"
    test_data = {
        "skipped": [{"id": 1, "name": "Game 1"}, {"id": 2, "name": "Game 2"}, {"id": 3, "name": "Game 3"}],
        "sorted": [],
        "unsorted": [{"id": 4, "name": "Game 4"}],
    }
    file_path = os.path.join(temp_data_dir, f"{username}.json")

    with open(file_path, "w") as f:
        json.dump(test_data, f)

    # Unskip selected games
    selected_games = [1, 3]  # Unskip games 1 and 3
    unskip_selected_games(username, selected_games)

    # Verify the data was updated correctly
    with open(file_path, "r") as f:
        updated_data = json.load(f)

    # Check that the skipped list only contains game 2
    assert len(updated_data["skipped"]) == 1
    assert updated_data["skipped"][0]["id"] == 2

    # Check that the unsorted list contains games 1, 3, and 4
    assert len(updated_data["unsorted"]) == 3
    unsorted_ids = [game["id"] for game in updated_data["unsorted"]]
    assert set(unsorted_ids) == {1, 3, 4}
