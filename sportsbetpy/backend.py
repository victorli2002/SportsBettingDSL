from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .leagues import LEAGUE_TEAMS
from .fixture import Head2Head, Totals, Spreads, Event, OverUnderEvent, Game,  Fixture
from .utils import *
import random
import json
import os
from copy import deepcopy

@dataclass
class Backend:
    name: str
    fixtures: List[Game] = field(default_factory=list) 

    def findFixtures(self, league: str, entities: List[str], type=None, criteria='all', event_type=None):
        fixtures = []
        if type == Event:
            for game in self.fixtures:
                for f in game.fixtures:
                    if not isinstance(f, Event):
                        continue
                    if event_type is not None and f.name != event_type:
                        continue
                    if criteria == 'all':
                        match = is_subset_of(entities, [f.description])
                    elif criteria == 'any':
                        match = nonempty_intersection(entities, [f.description])
                    else:
                        match = False
                    if match:
                        fixtures.append(f)
            return fixtures
        
        league_teams = get_teams_from_league(league)
        if is_subset_of(entities, league_teams) == False:
            raise ValueError(f"Error: invalid teams {entities}")
        for team in entities:
            if team not in league_teams:
                raise ValueError(f"Error: {team} is not a valid team in {league}")
                
        for game in self.fixtures:
            home_team = game.home_team_name
            if not team_in_league(home_team, league):
                continue
            away_team = game.away_team_name
            if criteria == 'all':
                match = is_subset_of(entities, [home_team, away_team])
            elif criteria == 'any':
                match = nonempty_intersection(entities, [home_team, away_team])
            else:
                match = False
            if match:
                for f in game.fixtures:
                    if type == None or isinstance(f, type):
                        fixtures.append(f)

        return fixtures

    def findGames(self, other, num_teams_to_match = 2):
        games = []
        teams = [other.away_team_name, other.home_team_name]
        if isinstance(other, Game):
            if num_teams_to_match == 2:
                for game in self.fixtures:
                    if game.home_team_name in teams and game.away_team_name in teams:
                        games.append(game)
                return games
            elif num_teams_to_match == 1:
                for game in self.fixtures:
                    if game.home_team_name in teams or game.away_team_name in teams:
                        games.append(game)
                return games
            return games
        raise TypeError(f"Error: invalid type {type(other)}")
    
    def __add__(self, other):
        assert isinstance(other, Backend)
        assert self.name == other.name

        combined_games = []
        for game in self.fixtures:
            fixtures = game.fixtures
            new_fixtures = deepcopy(fixtures)
            for other_game in other.fixtures:
                if game.commence_time == other_game.commence_time and game.home_team_name == other_game.home_team_name and game.away_team_name == other_game.away_team_name:
                    new_fixtures = union_lists(new_fixtures, other_game.fixtures)
            combined_games.append(Game(game.home_team_name, game.away_team_name, new_fixtures, game.commence_time))
        for other_game in other.fixtures:
            if not (game.commence_time == other_game.commence_time and game.home_team_name == other_game.home_team_name and game.away_team_name == other_game.away_team_name):
                combined_games.append(deepcopy(other_game))
        
        return Backend(self.name, combined_games)

    
class FakeBackend(Backend):
    def __init__(self, leagues=["basketball_nba"], seed:int=42):
        random.seed(seed)
        self.name = f"fake_seed{seed}"
        self.fixtures = []
        for league in leagues:
            teams = get_teams_from_league(league)
            self.fake_week(teams)


    def fake_week(self, teams: List[str]):
        teams = teams.copy()  # Avoid modifying the original list
        random.shuffle(teams)
        pairs = [teams[i:i+2] for i in range(0, len(teams), 2)]
        for pair in pairs:
            home_team, away_team = pair
            home_score, away_score = random_nba_score()

            h2h_odds = score_to_h2h_odds(home_score, away_score)
            h2h = Head2Head(home_team, away_team, h2h_odds[0], h2h_odds[1], backend_name=self.name)
            rand = random.randint(0, 1)
            diff = away_score - home_score + 0.5
            if rand == 0:
                diff - 1
            spreads = Spreads(home_team, away_team, 
                              random_house_odds(), random_house_odds(), diff, -diff, backend_name=self.name)
            totals = Totals(home_team, away_team, 
                            random_house_odds(), random_house_odds(), home_score, away_score, backend_name=self.name)
            if home_team == "Los Angeles Lakers" or away_team == "Los Angeles Lakers":
                event = OverUnderEvent("player_assists", 6.5, "Lebron James", -140, +190, backend_name=self.name)
                self.fixtures.append(Game(home_team, away_team, [h2h, spreads, totals, event]))
            else:
                self.fixtures.append(Game(home_team, away_team, [h2h, spreads, totals]))

SPORTSBOOKS = {
    'DraftKings' : 'draftkings',
    'LowVig.ag': 'lowvig',
    'BetOnline.ag': 'betonlineag',
    'BetMGM': 'betmgm',
    'FanDuel': 'fanduel',
    'BetRivers': 'betrivers',
    'Fanatics': 'fanatics',
    'BetUS': 'betus',
    'Caesars': 'williamhill_us',
    'MyBookie.ag': 'mybookieag',
    'Bovada': 'bovada'
}

def SportsBook(name):
    if name not in SPORTSBOOKS.keys():
        if name not in SPORTSBOOKS.values():
            raise ValueError(f"{name} is not a valid sportsbook.")
        backend_key = name
    else:
        backend_key = SPORTSBOOKS[name]

    backends = load_backends()
    backend = backends[backend_key]
    return backend


def load_backends(paths=None):
    if paths is None:
        folder_path = os.path.join(os.path.dirname(__file__), "backend1")
        paths = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, filename)) and not filename.endswith("events.json")
        ]

    backend_jsons = []
    for path in paths:
        try:
            with open(path, "r") as f:
                backend_jsons.append(json.load(f))
        except FileNotFoundError:
            print(f"File not found: {path}")
            raise FileNotFoundError
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {path}")
            raise json.JSONDecodeError
    
    backends = {}
    for backend_json in backend_jsons:
        backends = from_theodds_json(backend_json, backends)
    return backends

def from_theodds_json(json, backends={}):
    ts = parse_timestamp(json['timestamp'])
    for game in json['data']:
        sport = game['sport_key']
        commence_time = parse_timestamp(game['commence_time'])
        home = game['home_team']
        away = game['away_team']
        for bookmaker in game['bookmakers']:
            backend_key = bookmaker['key']
            backend_name = bookmaker['title']
            fixtures = []
            for market in bookmaker['markets']:
                type = market['key']
                if type == 'totals': # temporary
                    continue
                for outcome in market['outcomes']:
                    team = outcome['name']
                    if not team in [home, away]:
                        raise ValueError(f"Couldn't find team {team} in {[home, away]}")
                    assert team in LEAGUE_TEAMS[sport]
                    if team == home:
                        home_price = outcome['price']
                        if 'point' in outcome:
                            home_point = outcome['point']
                    else:
                        away_price = outcome['price']
                        if 'point' in outcome:
                            away_point = outcome['point']
                    
                match type:
                    case 'h2h':
                        fixture = Head2Head(
                            home, away, 
                            home_price, away_price, 
                            timestamp=ts, commence_time=commence_time, backend_name=backend_name
                            )
                    case 'spreads':
                        fixture = Spreads(
                            home, away, 
                            home_price, away_price, 
                            home_point, away_point,
                            timestamp=ts, commence_time=commence_time, backend_name=backend_name
                            )
                    case 'totals':
                        raise NotImplementedError
                    case _:
                        fixture = None
                if not fixture is None:
                    fixtures.append(fixture)
            backend = backends.get(backend_key, Backend(backend_name, []))
            backend.fixtures.append(Game(home, away, fixtures, commence_time=commence_time))
            backends[backend_key] = backend
    return backends

