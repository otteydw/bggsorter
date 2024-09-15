"""BGG Sorter 2

This Flask application provides functionality to sort and manage board game collections
for users based on their BoardGameGeek (BGG) profiles. It allows users to interactively
rank their games and view their sorted game collections.

Main features:
- Fetch and store user's played games from BoardGameGeek
- Interactive game sorting using a binary insertion sort algorithm
- Display all games and top games for a user
- Save and load user data from JSON files

The application uses Flask for web routing and rendering templates, and interacts
with the BoardGameGeek API to retrieve user game data.

Usage:
    Run this script to start the Flask development server.
    Access the application through a web browser at the provided local URL.

Note:
    This application is intended for development and testing purposes.
    For production deployment, consider using a production-grade WSGI server.
"""

import json
import logging
import os

from flask import Flask, redirect, render_template, request, url_for

from bgg_helpers import get_games_played_for_user

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DATA_DIR = "data"

# Create the data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)


def load_data(username):
    """
    Load user data from a JSON file.

    This function attempts to load user data from a JSON file named after the
    provided username. If the file exists, it reads and returns the data.
    If the file doesn't exist, it returns a default data structure.

    Args:
        username (str): The username of the user whose data should be loaded.

    Returns:
        dict: A dictionary containing the user's data with two keys:
            - 'unsorted': A list of unsorted items (default: empty list)
            - 'sorted': A list of sorted items (default: empty list)

    Notes:
        - The function expects JSON files to be stored in the directory specified
          by the DATA_DIR constant.
        - If the file doesn't exist, no error is raised. Instead, a default
          structure is returned.

    Example:
        >>> user_data = load_data('johndoe')
        >>> print(user_data)
        {'unsorted': [], 'sorted': []}
    """
    file_path = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {"unsorted": [], "sorted": []}


def save_data(username, data):
    """Save user data to a JSON file.

    This function takes a username and corresponding data, then saves it to a JSON
    file in the directory specified by DATA_DIR. The filename is created by
    appending '.json' to the username.

    Args:
        username (str): The username of the user whose data is being saved.
        data (dict): The data to be saved, typically containing 'unsorted' and
            'sorted' lists.

    Returns:
        None

    Raises:
        IOError: If there's an issue writing to the file.
        TypeError: If the data is not JSON serializable.
    """

    file_path = os.path.join(DATA_DIR, f"{username}.json")
    with open(file_path, "w") as file:
        json.dump(data, file)


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle the index page for both GET and POST requests.

    This route function serves as the entry point for the application. It handles
    both GET and POST requests. For GET requests, it displays the index page. For
    POST requests, it processes the submitted username, loads or fetches user data,
    and redirects to the game sorting page.

    Args:
        None

    Returns:
        Union[str, werkzeug.wrappers.Response]: For GET requests or POST requests
        without a username, returns the rendered index.html template. For POST
        requests with a valid username, returns a redirect to the sort_games route.

    Raises:
        None

    Route: /
    Methods: GET, POST
    """

    if request.method == "POST":
        username = request.form.get("username")
        if username:
            user_data = load_data(username)
            if not user_data["unsorted"]:
                # Fetch and store data if not already stored
                games = get_games_played_for_user(username)
                if games:
                    user_data["unsorted"] = [
                        {"id": game["id"], "name": game["name"], "image": game["image"]} for game in games
                    ]
                    save_data(username, user_data)
            return redirect(url_for("sort_games", username=username))
    return render_template("index.html")


@app.route("/games")
def games():
    """Retrieve and display all games for a given user.

    This route function handles GET requests to display all games (both sorted and
    unsorted) for a specified user. It requires a 'username' query parameter.

    Args:
        None

    Returns:
        Union[str, Tuple[str, int]]: If a valid username is provided, returns a
        rendered 'games.html' template with all games. If no username is provided,
        returns an error message with a 400 status code.

    Raises:
        None

    Route: /games
    Methods: GET
    Query Parameters:
        username (str): The username of the user whose games are to be displayed.
    """

    username = request.args.get("username")
    if not username:
        return "Username required", 400

    user_data = load_data(username)
    all_games = user_data["unsorted"] + user_data["sorted"]
    return render_template("games.html", games=all_games)


@app.route("/top_games")
def top_games():
    """Retrieve and display top games for a given user.

    This route function handles GET requests to display the top games for a
    specified user. It requires a 'username' query parameter and optionally
    accepts a 'max' parameter to limit the number of games displayed.

    Args:
        None

    Returns:
        Union[str, Tuple[str, int]]: If a valid username is provided, returns a
        rendered 'top_games.html' template with the top games. If no username is
        provided, returns an error message with a 400 status code.

    Raises:
        None

    Route: /top_games
    Methods: GET
    Query Parameters:
        username (str): The username of the user whose top games are to be displayed.
        max (int, optional): The maximum number of games to display. If not provided,
                             all sorted games will be displayed.
    """

    username = request.args.get("username")
    if not username:
        return "Username required", 400

    user_data = load_data(username)

    max = int(request.args.get("max", None))
    if max is None:
        title = f"Top Games for {username}ß"
    else:
        title = f"Top {max} Games for {username}"
    return render_template("top_games.html", title=title, max=max, games=user_data["sorted"][:max])


@app.route("/sort", methods=["GET", "POST"])
def sort_games():
    """Handle the game sorting process for a user.

    This route function manages the interactive sorting of games for a given user.
    It handles both GET and POST requests, implementing a binary insertion sort
    algorithm to organize games based on user preferences.

    Args:
        None

    Returns:
        Union[str, werkzeug.wrappers.Response]:
            - If all games are sorted: A success message.
            - If username is missing: An error message with 400 status code.
            - During sorting process: Rendered 'sort_games.html' template for user input.
            - After inserting a game: Redirect to this route for the next comparison.

    Raises:
        None

    Route: /sort
    Methods: GET, POST
    Query Parameters:
        username (str): The username of the user whose games are being sorted.
    Form Data (POST only):
        username (str): The username (redundant with query parameter).
        low (int): The lower bound of the current sorting range.
        high (int): The upper bound of the current sorting range.

    Notes:
        - This function implements a binary insertion sort algorithm.
        - It saves the updated sorting progress after each insertion.
        - If the sorted list is empty, it initializes it with the first unsorted game.
    """

    username = request.args.get("username") or request.form.get("username")
    if not username:
        return "Username is required", 400

    user_data = load_data(username)
    unsorted_games = user_data["unsorted"]
    sorted_games = user_data["sorted"]

    if not unsorted_games:
        return "All games have been sorted!"

    # Ensure the sorted list will contain at least one game to start.
    if not sorted_games:
        sorted_games.append(unsorted_games.pop())

    game = unsorted_games[-1]

    low = int(request.form.get("low", 0))
    high = int(request.form.get("high", len(sorted_games) - 1))

    if low <= high:
        mid = (low + high) // 2

        # This is where we ask the user to compare game with sorted_games[mid]
        return render_template(
            "sort_games.html",
            username=username,
            current_game=game,
            comparison_game=sorted_games[mid],
            low=low,
            mid=mid,
            high=high,
            sorted_games=sorted_games,
        )
    else:
        sorted_games.insert(low, game)
        unsorted_games.pop()
        save_data(username, user_data)
        return redirect(url_for("sort_games", username=username))


if __name__ == "__main__":
    app.run(debug=True)
