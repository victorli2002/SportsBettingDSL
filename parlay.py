from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import random
import utils

from bet import RawBet
@dataclass
class Parlay:
    legs: List[RawBet]

    def __post_init__(self):
        self.wager = self.wager()
        self.payout_on_win = self.payout_on_win()
        self.profit_on_win = self.profit_on_win()
        self.implied_probability = self.implied_probability()
        self.odds = self.odds()

    def __str__(self):
        s = f'{len(self.legs)}-leg parlay\n'
        s += f'total wager: {self.wager}\n'
        s += f'total odds: {self.odds}\n'
        s += f"payout on hit: {self.payout_on_win}\n"
        s += f"profit on hit: {self.profit_on_win}\n"
        s += f"implied probability of hit: {self.implied_probability}\n\n"
        for i, bet in enumerate(self.legs):
            s += f'Leg {i+1}\n{bet}\n'
        return s
    
    def add_leg(self, leg):
        self.legs.append(leg)

    def __add__(self, other):
        if isinstance(other, RawBet):
            p = Parlay([])
            p.legs = self.legs + [other]
            return p
        if isinstance(other, Parlay):
            p = Parlay([])
            p.legs = self.legs + other.legs
            return p
    
    def __radd__(self, other):
        return self + other
        
    def odds(self):
        p = self.implied_probability
        if not (0 <= p <= 1):
            raise ValueError("Probability must be between 0 and 1.")
        if p == 0.5:
            return 100  # even odds
        elif p < 0.5:
            return int((100 * (1 - p)) / p)
        else:
            return int((-100 * p) / (1 - p))
        
    def wager(self):
        return sum([leg.wager for leg in self.legs])
        
    def payout_on_win(self):
        return sum([leg.payout_on_win for leg in self.legs])
    
    def profit_on_win(self):
        return self.payout_on_win - self.wager

    def implied_probability(self):
        m = 1
        for leg in self.legs:
            m *= leg.implied_probability
        return m