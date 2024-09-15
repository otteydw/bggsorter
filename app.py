import json
import os

from flask import Flask, redirect, render_template, request, url_for

from bgg_helpers import get_games_played_for_user

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
    return {}


# Save data to file for a specific user
def save_data(username, data):
    file_path = os.path.join(DATA_DIR, f"{username}.json")
    with open(file_path, "w") as file:
        json.dump(data, file)


# Main page route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            user_games = load_data(username)
            if not user_games:
                # Fetch and store data if not already stored
                games = get_games_played_for_user(username)
                if games:
                    user_games = [game["id"] for game in games]
                    save_data(username, user_games)
            return redirect(url_for("show_games", username=username))
    return render_template("index.html")


# Page to show games for the user
@app.route("/games/<username>")
def show_games(username):
    user_games = load_data(username)
    return render_template("games.html", username=username, games=user_games)


if __name__ == "__main__":
    app.run(debug=True)
