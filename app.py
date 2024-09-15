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


# Load existing data from file for a specific user
def load_data(username):
    file_path = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {"unsorted": [], "sorted": []}


# Save data to file for a specific user
def save_data(username, data):
    file_path = os.path.join(DATA_DIR, f"{username}.json")
    with open(file_path, "w") as file:
        json.dump(data, file)


@app.route("/", methods=["GET", "POST"])
def index():
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
    username = request.args.get("username")
    if not username:
        return "Username required", 400

    user_data = load_data(username)
    all_games = user_data["unsorted"] + user_data["sorted"]
    return render_template("games.html", games=all_games)


@app.route("/top_games")
def top_games():
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
