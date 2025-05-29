from dataclasses import dataclass
from typing import Callable, List

from .backend import Backend, load_backends
from .fixture import Game, Event, Head2Head, Spreads, Totals
from .bet import RawBet
from . import utils

@dataclass
class GameStrategy:
    func: Callable[[Game], List[RawBet]]

    def apply(self, game: Game):
        return self.func(game)
    
class BetOnHome(GameStrategy):
    wager: float
    def __init__(self, wager):
        self.wager = wager
        def func(game: Game):
            a = []
            for f in game.fixtures:
                if not isinstance(f, Event):
                    a.append(f.bet('home', self.wager))
            return a
        super().__init__(func)

class BetOnTeamIfHome(GameStrategy):
    team: str
    wager: float
    def __init__(self, team, wager):
        self.team = team
        self.wager = wager
        def func(game: Game):
            a = []
            for f in game.fixtures:
                if not isinstance(f, Event):
                    if f.home_team_name == self.team:
                        a.append(f.bet('home', self.wager))
            return a
        super().__init__(func)

@dataclass
class BackendStrategy:
    func: Callable[[str, List[Backend]], List[RawBet]]

    def apply(self, backends: List[Backend]=[], bullish: bool=True):
        return self.func(backends, bullish)
    
class BestBets(BackendStrategy):
    game: str
    team: str
    wager: float
    def __init__(self, game, team, wager):
        self.game = game
        self.team = team
        self.wager = wager

        if team == game.home_team_name:
            team = 'home'
        elif team == game.away_team_name:
            team = 'away'
        if not utils.is_subset_of([team], ['home', 'away']):
            raise ValueError(f'Team {team} not valid for game {game}') # gotta split by home and away instead of team name
        other = 'away' if team == 'home' else 'home'
        
        def func(backends: List[Backend]=[], bullish: bool=True):
            if backends == []:
                backends = load_backends()
            best_bets = [None] * 3
            for backend in backends:
                for game in backend.findGames(self.game, num_teams_to_match=2):
                    for fixture in game.fixtures:
                        if isinstance(fixture, Head2Head):
                            if bullish:
                                if best_bets[0] is None:
                                    best_bets[0] = fixture.bet(team, self.wager)
                                    continue
                                odds = fixture.home_team_price if team == 'home' else fixture.away_team_price
                                if odds > best_bets[0].odds:
                                    best_bets[0] = fixture.bet(team, self.wager)
                            else:
                                if best_bets[0] is None:
                                    best_bets[0] = fixture.bet(other, self.wager)
                                    continue
                                odds = fixture.away_team_price if team == 'home' else fixture.home_team_price
                                if odds > best_bets[0].odds:
                                    best_bets[0] = fixture.bet(other, self.wager)
                        elif isinstance(fixture, Spreads):
                            if bullish:
                                if best_bets[1] is None:
                                    best_bets[1] = fixture.bet(team, self.wager)
                                    continue
                                odds = fixture.home_team_point if team == 'home' else fixture.away_team_point
                                if odds > best_bets[1].odds:
                                    best_bets[1] = fixture.bet(team, self.wager)
                            else:
                                if best_bets[1] is None:
                                    best_bets[1] = fixture.bet(other, self.wager)
                                    continue
                                odds = fixture.away_team_point if team == 'home' else fixture.home_team_point
                                if odds > best_bets[1].odds:
                                    best_bets[1] = fixture.bet(other, self.wager)
                        elif isinstance(fixture, Totals):                            
                            if bullish:
                                if best_bets[2] is None:
                                    best_bets[2] = fixture.bet('over', self.wager)
                                odds = fixture.over_price
                                if odds > best_bets[2].odds:
                                    best_bets[2] = fixture.bet('over', self.wager)
                            else:
                                if best_bets[2] is None:
                                    best_bets[2] = fixture.bet('under', self.wager)
                                odds = fixture.under_price
                                if odds > best_bets[2].odds:
                                    best_bets[2] = fixture.bet('under', self.wager)
            return best_bets
        super().__init__(func)