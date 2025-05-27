from datetime import datetime
import random
import math
from typing import List
from collections import Counter

from .leagues import LEAGUE_TEAMS

def is_subset_of(a: List, b: List) -> bool:
    return set(a).issubset(set(b))

def nonempty_intersection(a: List, b: List) -> bool:
    return bool(set(a) & set(b)) 

def merge_ordered_sets(a: List, b: List) -> List:
    combined = a + b
    counts = Counter(combined)
    unique_elements = [x for x in combined if counts[x] == 1]
    return sorted(unique_elements,key=lambda x: x.commence_time)

def get_teams_from_league(league: str) -> List[str]:
    if league == "nba" or league == "NBA":
        league = "basketball_nba"
    elif league == "nfl" or league == "NFL":
        league = "americanfootball_nfl"
    elif league == "mlb" or league == "MLB":
        league = "baseball_mlb"
    elif league == "nhl" or league == "NHL":
        league = "hockey_nhl"

    if league not in LEAGUE_TEAMS.keys():
        raise ValueError(f"Error: {league} is not a supported league name")
    return LEAGUE_TEAMS[league]

def team_in_league(team: str, league: str) -> bool:
    teams = get_teams_from_league(league)
    return team in teams

def parse_timestamp(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def random_nba_score() -> tuple[int, int]:
    AVERAGE_HOME = 117
    AVERAGE_AWAY = 114
    STDEV = 10
    home_score = max(0, round(random.gauss(AVERAGE_HOME, STDEV)))
    away_score = max(0, round(random.gauss(AVERAGE_AWAY, 10)))
    if home_score == away_score:
        tiebreak = random.randint(0, 1)
        if tiebreak == 0:
            home_score += 1
        else:
            away_score += 1
    return (home_score, away_score)

def random_house_odds() -> int:
    x= min(-100, int(random.gauss(mu=-110, sigma=3)))
    return x

def prob_to_moneyline(prob: float) -> int:
    if prob == 0:
        return 10000
    elif prob == 1:
        return -10000
    elif prob >= 0.5:
        return round(-100 * prob / (1 - prob))
    else:
        return round(100 * (1 - prob) / prob)

def score_to_h2h_odds(score_a: int, score_b: int) -> tuple[int, int]:
    score_diff = max(min(score_a - score_b, 20), -20)

    # Logistic probability for team A win
    prob_a = 1 / (1 + math.exp(-score_diff / 5))
    prob_b = 1 - prob_a

    odds_a = prob_to_moneyline(prob_a)
    odds_b = prob_to_moneyline(prob_b)
    return odds_a, odds_b


def team_picker(team, home, away):
    match team:
        case "home":
            return 0
        case "away":
            return 1
        case "Trail Blazers":
            t = "Portland Trail Blazers"
        case "Sox":
            raise ValueError("Choose a Sox team")
        case "White Sox":
            t = "Chicago White Sox"
        case "Red Sox":
            t = "Boston Red Sox"
        case "Blue Jays":
            t = "Toronto Blue Jays"
        case "Red Wings":
            t = "Detroit Red Wings"
        case "Blue Jackets":
            t = "Columbus Blue Jackets"
        case "Golden Knights":
            t = "Portland Trail Blazers"
        case _:
            if " " in team:
                t = team
            else:
                if home.endswith(team):
                    return 0
                elif away.endswith(team):
                    return 1
                else:
                    raise ValueError(f"Error: {team} is not a valid team")
    if home == t:
        return 0
    elif away == t:
        return 1
    raise ValueError(f"Error: {team} is not a valid team")

def print_odds(odds):
    if isinstance(odds, str):
        odds = int(odds)
    if odds > 0:
        return f"+{odds}"
    return str(odds)

    
    