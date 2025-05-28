import requests
import json

API_KEY = "ddba85b051b0fadb843f89eeb0721c59"
sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]

for sport in sports:
    response = requests.get(f"https://api.the-odds-api.com/v4/historical/sports/{sport}/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals&oddsFormat=american&date=2025-05-27T12:00:00Z")

    if response.status_code == 200:
        print("Success!")
        print(response.json())  # If the response is JSON
        with open(f"{sport}.json", "w") as f:
            json.dump(response.json(), f, indent=2)
    else:
        print(f"Error: {response.status_code}")

    """response = requests.get(f"https://api.the-odds-api.com/v4/historical/sports/basketball_nba/events/da359da99aa27e97d38f2df709343998/odds?apiKey=YOUR_API_KEY&date=2023-11-29T22:45:00Z&regions=us")

    if response.status_code == 200:
        print("Success!")
        print(response.json())  # If the response is JSON
        with open(f"{sport}-events.json", "w") as f:
            json.dump(response.json(), f, indent=2)
    else:
        print(f"Error: {response.status_code}")"""