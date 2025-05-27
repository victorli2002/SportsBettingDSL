from dataclasses import dataclass
from typing import Callable, List

from backend import Backend
from fixture import Game, Event
from bet import RawBet
import utils

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

