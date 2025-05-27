from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import random
from . import utils

@dataclass
class RawBet:
    backend_name: str
    odds: int
    wager: float

    def __post_init__(self):
        if not isinstance(self.backend_name, str):
            raise TypeError("Error: backend names must be a string")
        if isinstance(self.odds, str):
            self.odds = int(self.odds)
        if isinstance(self.wager, str) | isinstance(self.wager, int):
            self.wager = float(self.wager)
        if not isinstance(self.odds, int):
            raise TypeError("Error: odds must be an integer")
        if self.odds == 0:
            raise ValueError("Error: invalid odds")
        if not isinstance(self.wager, float):
            raise TypeError("Error: wager must be a float")
        if self.wager < 0:
            raise ValueError("Error: wager cannot be negative")
        
        self.payout_on_win = self.payout_on_win()
        self.profit_on_win = self.profit_on_win()
        self.implied_probability = self.implied_probability()
        
    def payout_on_win(self):
        if self.odds < 0:
            return self.wager * 100 / (-self.odds) + self.wager 
        else:
            return self.wager * (1 + self.odds / 100)
    
    def profit_on_win(self):
        return self.payout_on_win - self.wager

    def implied_probability(self):
        if self.odds < 0:
            return -self.odds / (-self.odds + 100)
        elif self.odds > 0:
            return 100 / (self.odds + 100)
        else:
            raise ValueError("Error: Invalid odds")
        
    def set_wager(self, wager):
        self.wager = wager
    
    def __add__(self, other):
        if isinstance(other, RawBet):
            from parlay import Parlay
            p = Parlay([])
            p.legs = [self, other]
            return p
        
    def __str__(self):
        s = f"payout on hit: {self.payout_on_win}\n"
        s += f"profit on hit: {self.profit_on_win}\n"
        s += f"implied probability of hit: {self.implied_probability}\n"
        return s

@dataclass
class H2hBet(RawBet):
    team: str

    def __str__(self):
        s = ""
        s += f"{self.wager} on {self.team} to win at {utils.print_odds(self.odds)} odds\n"
        s += super().__str__()
        return s
    
    def __add__(self, other):
        if isinstance(other, float) | isinstance(other, int):
            return H2hBet(self.backend_name, self.odds, self.wager + other, self.team)
        return super().__add__(other)

@dataclass
class SpreadsBet(RawBet):
    team: str
    point: float

    def __str__(self):
        s = ""
        if self.point >= 0:
            s += f"{self.wager} on {self.team} to win by more than {self.point} points at {utils.print_odds(self.odds)} odds\n"
        else:
            s += f"{self.wager} on {self.team} to win or lose by at most {-self.point} points at {utils.print_odds(self.odds)} odds\n"
        s += super().__str__()
        return s
    
    def __add__(self, other):
        if isinstance(other, float) | isinstance(other, int):
            return SpreadsBet(self.backend_name, self.odds, self.wager + other, self.team, self.point)
        return super().__add__(other)

@dataclass
class TotalsBet(RawBet):
    team: str
    point: float

    def __str__(self):
        s = ""
        s += f"{self.wager} on {self.team} to score over {self.point} points at {utils.print_odds(self.odds)} odds\n"
        s += super().__str__()
        return s
    
    def __add__(self, other):
        if isinstance(other, float) | isinstance(other, int):
            return TotalsBet(self.backend_name, self.odds, self.wager + other, self.team, self.point)
        return super().__add__(other)

class OutrightsBet(RawBet):
    pass

@dataclass
class EventsBet(RawBet):
    name: str
    point: float
    description: str
    over_under: str = ""

    def __str__(self):
        s = ""
        s += f"{self.wager} on {self.description} to get {self.over_under} {self.point} {self.name} at {utils.print_odds(self.odds)} odds\n"
        s += super().__str__()
        return s
    
    def __add__(self, other):
        if isinstance(other, float) | isinstance(other, int):
            return EventsBet(self.backend_name, self.odds, self.wager + other, self.name, self.point, self.description, self.over_under)
        return super().__add__(other)

    

