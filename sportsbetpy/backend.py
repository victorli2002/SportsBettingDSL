from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .leagues import LEAGUE_TEAMS
from .fixture import Head2Head, Totals, Spreads, Event, OverUnderEvent, Game,  Fixture
from .utils import *
import random

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
            
if __name__ == "__main__":
    print("HELLO")
    x = FakeBackend()
    print(x.fixtures)
        

