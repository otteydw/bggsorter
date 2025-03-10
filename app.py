"""BGG Sorter

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
import math
import os

from bgg_helpers import BGGUserError, check_bgg_user_exists, get_games_played_for_user
from flask import Flask, redirect, render_template, request, url_for

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
        {"skipped": [], "sorted": [], "unsorted": []}
    """
    file_path = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    user_data = {"skipped": [], "sorted": [], "unsorted": []}
    return user_data


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


def delete_data(username):
    """Delete user data from a JSON file.

    This function takes a username and deletes the corresponding JSON file from
    the directory specified by DATA_DIR.

    Args:
        username (str): The username of the user whose data is being deleted.

    Returns:
        None

    Raises:
        IOError: If there's an issue deleting the file.
    """
    file_path = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(file_path):
        os.remove(file_path)


def max_comparisons(n):
    """
    Calculate the maximum number of comparisons needed to insert a game into a sorted list.

    This function computes the maximum number of binary comparisons required to insert a new
    game into a sorted list of length `n`, following a binary insertion sort algorithm.

    Args:
        n (int): The length of the sorted list into which the game is being inserted.

    Returns:
        int: The maximum number of comparisons needed for the insertion.

    Raises:
        ValueError: If `n` is negative, as a list cannot have a negative length.
    """
    return math.ceil(math.log2(n + 1))


def total_remaining_comparisons(sorted_length, unsorted_length):
    """
    Calculate the maximum number of remaining comparisons to sort all unsorted games.

    This function computes the worst-case total number of comparisons needed to
    insert all remaining unsorted games into the sorted list using binary insertion sort.

    Args:
        sorted_length (int): The current length of the sorted list.
        unsorted_length (int): The number of unsorted games remaining.

    Returns:
        int: The maximum number of comparisons needed to sort all remaining games.
    """
    total = 0
    for i in range(unsorted_length):
        # For each unsorted game, we need at most ceil(log2(n+1)) comparisons
        # where n is the current length of the sorted list
        current_sorted_length = sorted_length + i
        total += math.ceil(math.log2(current_sorted_length + 1))
    return total


@app.route("/", methods=["GET", "POST"])
def index():
    """Display the index page of the application or redirect based on user data.

    This route function handles GET and POST requests. On a GET request, it
    displays the index page. On a POST request (or if a `username` query
    parameter is provided), it checks for user data and redirects the user
    to the appropriate page based on whether unsorted data exists.

    Args:
        None

    Returns:
        str: A rendered 'index.html' template if no username is provided.
        werkzeug.wrappers.Response: A redirect to the 'load' or 'games' route based on user data.

    Raises:
        None

    Route: /
    Methods: GET, POST
    Query Parameters:
        username (str, optional): The username used to load user-specific data.
    """
    username = request.args.get("username") or request.form.get("username")
    if not username:
        return render_template("index.html")

    try:
        if not check_bgg_user_exists(username):
            return render_template("index.html", error=f"Username {username} not found on BoardGameGeek")
        user_data = load_data(username)
        if not user_data["unsorted"]:
            return redirect(url_for("load", username=username))

        return redirect(url_for("games", username=username))
    except BGGUserError as e:
        return render_template("index.html", error=str(e))


@app.route("/delete", methods=["GET", "POST"])
def delete():
    """Handle user data deletion confirmation or completion.

    This route function handles both GET and POST requests to manage user data deletion.
    On a GET request or if no confirmation is provided in a POST request, it displays
    a confirmation page asking the user to confirm whether they want to delete the data.
    On receiving a POST request with a confirmation, it deletes the user's data.

    Args:
        None

    Returns:
        str: A "Username required" message with a 400 status if no username is provided.
        str: A rendered 'delete_confirm.html' template if no confirmation is provided.
        str: A rendered 'delete_complete.html' template after successfully deleting data.

    Raises:
        None

    Route: /delete
    Methods: GET, POST
    Query Parameters:
        username (str, optional): The username of the user whose data is to be deleted.
    Form Data:
        confirm (str, optional): A confirmation from the user ('yes' indicates data deletion).
    """
    username = request.args.get("username") or request.form.get("username")

    if not username:
        return "Username required", 400

    confirm = request.form.get("confirm")
    if not confirm == "yes":
        return render_template("delete_confirm.html", username=username)

    delete_data(username)
    return render_template("delete_complete.html", username=username)


@app.route("/load", methods=["GET", "POST"])
def load():
    """Load user data and fetch games played by the user.

    This route function handles both GET and POST requests to load user data and
    fetch games played by the user. It requires a 'username' parameter, either as
    a query parameter or form data.

    Args:
        None

    Returns:
        Union[str, werkzeug.wrappers.Response]:
            - For GET requests: Returns a rendered 'load.html' template with the username.
            - For POST requests: Redirects to the games page after loading and saving user data.

    Raises:
        None

    Route: /load
    Methods: GET, POST
    Query/Form Parameters:
        username (str): The username of the user whose data is to be loaded.
        order (str, optional): The order in which to fetch games (POST only, default is "default").
    """

    username = request.args.get("username") or request.form.get("username")

    if request.method == "POST":
        order = request.form.get("order", "default")
        user_data = load_data(username)

        # Fetch and store data if not already stored
        games = get_games_played_for_user(username, order=order)

        if games:
            user_data["unsorted"] = [
                {"id": game["id"], "name": game["name"], "image": game["image"], "url": game["url"]} for game in games
            ]
            save_data(username, user_data)

        return redirect(url_for("games", username=username))

    return render_template("load.html", username=username)


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
    all_games.sort(key=lambda game: game["name"])  # Assuming games have a "name" key
    return render_template("games.html", stylesheet="gamelist.css", username=username, games=all_games)


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

    max = request.args.get("max", None)
    if max is None:
        title = f"Top Games for {username}"
    else:
        max = int(max)
        title = f"Top {max} Games for {username}"
    return render_template(
        "top_games.html",
        stylesheet="gamelist.css",
        username=username,
        title=title,
        max=max,
        games=user_data["sorted"][:max],
    )


@app.route("/sort", methods=["GET", "POST"])
def sort_games():
    """Sort games for a given user.

    This route function handles both GET and POST requests to sort games for a
    specified user. It requires a 'username' parameter, either as a query parameter
    or form data.

    Args:
        None

    Returns:
        Union[str, Tuple[str, int], werkzeug.wrappers.Response]:
            - If a valid username is provided:
                - If all games are sorted: Returns a success message.
                - If sorting the first game: Returns a rendered 'sort_first_game.html' template.
                - During sorting: Returns a rendered 'sort_games.html' template.
                - After inserting a game: Returns a redirect to the sort_games route.
            - If no username is provided: Returns an error message with a 400 status code.

    Raises:
        None

    Route: /sort
    Methods: GET, POST
    Query/Form Parameters:
        username (str): The username of the user whose games are being sorted.
        add_first (str, optional): Flag to add the first game to the sorted list.
        skip (str, optional): Flag to skip the current game.
        low (int, optional): Lower bound for binary search.
        high (int, optional): Upper bound for binary search.
        current_comparison_count (int, optional): Number of comparisons made so far.
    """

    username = request.args.get("username") or request.form.get("username")
    if not username:
        return "Username is required", 400

    user_data = load_data(username)
    unsorted_games = user_data["unsorted"]
    sorted_games = user_data["sorted"]
    skipped_games = user_data.get("skipped")

    if not unsorted_games:
        return "All games have been sorted!"

    # Check if we're adding the first game
    if not sorted_games and "add_first" in request.args:
        sorted_games.append(unsorted_games.pop(0))
        save_data(username, user_data)
        return redirect(url_for("sort_games", username=username))

    # Check if we're skipping a game
    if "skip" in request.args:
        skipped_game = unsorted_games.pop(0)
        skipped_games.append(skipped_game)
        user_data["skipped"] = skipped_games
        save_data(username, user_data)
        return redirect(url_for("sort_games", username=username))

    # If sorted_games is empty, prompt to add or skip the first game
    if not sorted_games:
        return render_template("sort_first_game.html", username=username, first_game=unsorted_games[0])

    game = unsorted_games[0]
    low = int(request.form.get("low", 0))
    high = int(request.form.get("high", len(sorted_games) - 1))
    current_comparison_count = int(request.form.get("current_comparison_count", 0)) + 1

    if low <= high:
        mid = (low + high) // 2
        return render_template(
            "sort_games.html",
            username=username,
            current_game=game,
            comparison_game=sorted_games[mid],
            low=low,
            mid=mid,
            high=high,
            current_comparison_count=current_comparison_count,
            max_comparisons=max_comparisons(len(sorted_games)),
            sorted_games=sorted_games,
            unsorted_games_count=len(unsorted_games),
            total_remaining_comparisons=total_remaining_comparisons(len(sorted_games), len(unsorted_games)),
        )
    else:
        sorted_games.insert(low, game)
        unsorted_games.pop(0)
        save_data(username, user_data)
        return redirect(url_for("sort_games", username=username))


def unskip_selected_games(username, selected_games):
    """Unskip the selected games for a given user and moved them back to unsorted.

    Args:
        username (str): The username of the user whose games are to be unskipped.
        selected_games (list): A list of game IDs to be unskipped.

    Returns:
        None
    """
    user_data = load_data(username)
    skipped_games = user_data["skipped"]
    unsorted_games = user_data["unsorted"]

    for game_id in selected_games:
        # print(f"Unskipping game with ID: {game_id}")
        for game in skipped_games:
            if game["id"] == game_id:
                # print(f"Unskipping game: {game['name']}")
                unsorted_games.append(game)
                skipped_games.remove(game)
                break

    save_data(username, user_data)


@app.route("/unskip", methods=["GET", "POST"])
def unskip():
    username = request.args.get("username") or request.form.get("username")
    if not username:
        return "Username required", 400

    selected_games = [int(game_id) for game_id in request.form.getlist("selected_games")]

    if not selected_games:
        user_data = load_data(username)
        skipped_games = user_data["skipped"]
        skipped_games.sort(key=lambda game: game["name"])
        return render_template("unskip.html", stylesheet="gamelist.css", username=username, games=skipped_games)

    # print(f"Going to unskip these game ids: {selected_games}")
    unskip_selected_games(username, selected_games)

    return redirect(url_for("unskip", username=username))


@app.route("/game_plays/<username>/<int:game_id>")
def game_plays(username, game_id):
    """Display play history for a specific game.

    This route function handles GET requests to display all logged plays for a
    specific game from a user's BGG account.

    Args:
        username (str): The BGG username whose play history to display.
        game_id (int): The BGG ID of the game to show play history for.

    Returns:
        str: A rendered 'game_plays.html' template with the play history.

    Raises:
        None

    Route: /game_plays/<username>/<int:game_id>
    Methods: GET
    """
    from bgg_helpers import get_plays_for_game

    try:
        plays = get_plays_for_game(username, game_id)
        game_name = plays[0]["name"] if plays else "Unknown Game"
        return render_template("game_plays.html", username=username, game_id=game_id, game_name=game_name, plays=plays)
    except Exception as e:
        return f"Error retrieving play history: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)
