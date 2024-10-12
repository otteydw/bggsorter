# BGG Sorter

## Overview

**BGG Sorter** is a Flask-based web application that allows users to interactively sort and manage their board game collections using their BoardGameGeek (BGG) profiles. The application fetches the user's played games from the BoardGameGeek API and provides an interface to rank games based on personal preferences using a binary insertion sort algorithm.

### Features

- **Retrieve User Games**: Automatically fetches games played by the user from BoardGameGeek.
- **Interactive Sorting**: Presents users with a comparison between two games to progressively build a ranked list.
- **Skip Functionality**: Users can skip games that they do not want to rank immediately.
- **View Games**: Displays all the games or the top N games for the user.
- **Save and Load Progress**: User data is saved to a JSON file, enabling users to resume sorting at any time.
- **Delete User Data**: Provides the option to delete all saved data for a specific user.

## Requirements

- **Python** (version 3.6 or later)
- **Flask** (version 1.1 or later)
- **BoardGameGeek API account** (for fetching games)

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/otteydw/bggsorter.git
   cd bggsorter
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:

   ```bash
   python app.py
   ```

4. Access the application by opening a web browser and navigating to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage

1. **Enter a Username**: On the main page, enter your BoardGameGeek username to start sorting games. If the username is valid, the app will fetch your played games from BGG.

2. **Sorting Games**: The app will guide you through sorting your games by presenting two games side by side. Click the one you prefer to build a ranked list.

3. **Viewing Sorted and Top Games**: After sorting, you can view a list of all your sorted games or a subset of the top-ranked games by clicking on the relevant links.

4. **Skipping Games**: If you do not want to rank a particular game, you can skip it. Skipped games can be reviewed later in the "Skipped Games" section.

5. **Delete Data**: If you want to clear all your saved data, navigate to the delete page, confirm the action, and the app will remove your data.

## Current Functionality

- **Main Page**: Accepts the username and redirects to sort or load games.
- **Game Sorting**: Utilizes a binary insertion sort to rank games interactively. Users are prompted to compare games in their collection.
- **Game Display**: Displays all the user’s games (sorted and unsorted) or just the top games.
- **Data Persistence**: User progress is saved to JSON files, allowing sorting to resume at any time. Each user has a separate file to store their data.
- **Skip/Unskip Games**: Users can skip games they don’t want to rank and unskip them later to reconsider.
- **Delete Data**: Users can delete their saved game data.

## API Integration

This app uses the **BoardGameGeek API** to fetch played games based on a user’s BGG profile. Ensure that your BGG username is valid to retrieve data successfully.

The app uses the public API and does not alter the data on BGG. Therefore is does not require any authentication.

## Limitations and Future Improvements

- The application is designed primarily for development and testing purposes. For production, consider deploying it using a production-grade WSGI server like **Gunicorn** or **uWSGI**.
- Currently, the app does not support advanced filtering (e.g., excluding expansions automatically) beyond manual user interaction.
- **Planned Enhancements**:
    - A more sophisticated method for excluding expansions automatically.
    - Enhanced sorting algorithms.
    - Improved UI/UX for better interactivity.

## AI Assistance

While developing this app, I used AI as a helpful resource for troubleshooting, generating ideas, and refining code. AI provided suggestions for resolving coding issues and optimizing features, but all final decisions, design choices, and implementations were made by me. This blend of human creativity and AI support allowed me to enhance the app efficiently and effectively.
