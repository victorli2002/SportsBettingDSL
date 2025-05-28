from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import random

from .bet import RawBet, H2hBet, SpreadsBet, TotalsBet, OutrightsBet, EventsBet
from . import utils

@dataclass(kw_only=True, frozen=True)
class Fixture:
    timestamp: datetime | str = field(default_factory=datetime.now)
    commence_time: datetime | str = field(default_factory=datetime.now)
    backend_name: str = ""

    def formatted_timestamp(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M')

    def formatted_commence_time(self):
        return self.commence_time.strftime('%Y-%m-%d %H:%M')
    
    def __str__(self):
        return f"timestamp: {self.formatted_timestamp()}\ncommence_time: {self.formatted_commence_time()}\nbackend: {self.backend_name}"

@dataclass(frozen=True)
class Head2Head(Fixture):
    home_team_name: str #note that in theodds api the away team is actual first i think
    away_team_name: str
    home_team_price: int
    away_team_price: int

    def bet(self, team, wager):
        if utils.team_picker(team, self.home_team_name, self.away_team_name) == 0:
            return H2hBet(self.backend_name, self.home_team_price, wager, self.home_team_name)
        return H2hBet(self.backend_name, self.away_team_price, wager, self.away_team_name)
    
    def __str__(self):
        s = "Head 2 Head:\n"
        s += super().__str__()
        s += f"\n{self.home_team_name} ({utils.print_odds(self.home_team_price)}) vs {self.away_team_name} ({utils.print_odds(self.away_team_price)})"
        s += '\n'
        return s

@dataclass(frozen=True)
class Spreads(Fixture):
    home_team_name: str
    away_team_name: str
    home_team_price: int
    away_team_price: int
    home_team_point: float
    away_team_point: float

    def bet(self, team, wager):
        if utils.team_picker(team, self.home_team_name, self.away_team_name) == 0:
            return SpreadsBet(self.backend_name, self.home_team_price, wager, self.home_team_name, self.home_team_point)
        return SpreadsBet(self.backend_name, self.away_team_price, wager, self.away_team_name, self.away_team_point)
    
    def __str__(self):
        s = "Spreads:\n"
        s += super().__str__()
        s += f"\n{self.home_team_name} {utils.print_odds(self.home_team_point)} ({utils.print_odds(self.home_team_price)})"
        s += f"\nvs"
        s += f"\n{self.away_team_name} {utils.print_odds(self.away_team_point)} ({utils.print_odds(self.away_team_price)})"
        s += '\n'
        return s

@dataclass(frozen=True)
class Totals(Fixture):
    home_team_name: str
    away_team_name: str
    home_team_price: int
    away_team_price: int
    home_team_point: float
    away_team_point: float
    #should be home_team_name, away_team_name, over_price, under_price, over_point, under_point

    def bet(self, team, wager):
        if utils.team_picker(team, self.home_team_name, self.away_team_name) == 0:
            return TotalsBet(self.backend_name, self.home_team_price, wager, self.home_team_name, self.home_team_point)
        return TotalsBet(self.backend_name, self.away_team_price, wager, self.away_team_name, self.away_team_point)
    
    def __str__(self):
        s = "Totals:\n"
        s += super().__str__()
        s += f"\n{self.home_team_name} {self.home_team_point} ({utils.print_odds(self.home_team_price)})"
        s += f"\nvs"
        s += f"\n{self.away_team_name} {self.away_team_point} ({utils.print_odds(self.away_team_price)})"
        s += '\n'
        return s

@dataclass(frozen=True)
class Game:
    home_team_name: str
    away_team_name: str
    fixtures: List[Fixture]
    commence_time: datetime | str = field(default_factory=datetime.now)

    def __str__(self):
        s = "*"*80
        s += f"\nGame: {self.home_team_name} vs {self.away_team_name}\n\n"
        for f in self.fixtures:
            s += f"{str(f)}\n"
        return s
    
    def __eq__(self, other):
        return self.home_team_name == other.home_team_name and self.away_team_name == other.away_team_name and self.fixtures == other.fixtures
    
    def __getitem__(self, index):
        return self.fixtures[index]

@dataclass(frozen=True)
class Outrights(Fixture):
    pass

@dataclass(frozen=True)
class Event(Fixture):
    name: str
    point: float
    description: str

@dataclass(frozen=True)
class OtherEvent(Event):
    price: int

    def bet(self, wager):
        return EventsBet(self.backend_name, self.price, wager, self.name, self.point, self.description)
    
    def __str__(self):
        s = f"{self.name}:\n"
        s += super().__str__()
        s += f"\n{self.description}, {self.point} ({utils.print_odds(self.price)})"
        s += '\n'
        return s
    
@dataclass(frozen=True)
class OverUnderEvent(Event):
    over_price: int
    under_price: int

    def bet(self, wager, over_under):
        match over_under:
            case 'over':
                return EventsBet(self.backend_name, self.over_price, wager, self.name, self.point, self.description, 'over')
            case 'under':
                return EventsBet(self.backend_name, self.under_price, wager, self.name, self.point, self.description, 'under')
            case _:
                raise ValueError(f"Must specify over or under, instead of {over_under}")
    
    def __str__(self):
        s = f"{self.name}:\n"
        s += super().__str__()
        s += f"\n{self.description}, {self.point} (over: {utils.print_odds(self.over_price)}, under: {utils.print_odds(self.under_price)})"
        s += '\n'
        return s
    
class PlannedBet:
    options: List[Fixture]

    def __init__(self, backend, league, type, entities, match_criteria='all'):
        match type:
            case "h2h":
                fixtures = backend.findFixtures(league, entities, Head2Head, match_criteria)
            case "spreads":
                fixtures = backend.findFixtures(league, entities, Spreads, match_criteria)
            case "totals":
                fixtures = backend.findFixtures(league, entities, Totals, match_criteria)
            case "outrights":
                raise NotImplementedError
            case "any":
                fixtures = backend.findFixtures(league, entities, None, match_criteria)
            case _: # for events
                # figure out keyword for name, description
                fixtures = backend.findFixtures(league, entities, Event, match_criteria, type)
        

        self.options = sorted(fixtures, key=lambda x: x.timestamp)
    
    @classmethod
    def empty(cls):
        obj = cls.__new__(cls) 
        obj.options = []
        return obj

    def select(self, method:str, idx:Optional[int] = -1) -> Fixture:
        match method:
            case "random":
                f = random.choice(self.options)
            case "last_updated":
                f = max(self.options, key=lambda x: x.timestamp)
            case "soonest":
                f = max(self.options, key=lambda x: x.commence_time)
            case "index":
                f = self.options[idx]
            case _:
                raise ValueError(f"Error: invalid method {method}")
        return f
    
    def __add__(self, other):
        if isinstance(other, PlannedBet):
            merged = utils.merge_ordered_sets(self.options, other.options)
        elif isinstance(other, Fixture):
            merged = utils.merge_ordered_sets(self.options, [other])
        else:
            raise TypeError(f"Error: invalid type {type(other)}")
        p = PlannedBet.empty()
        p.options = merged
        return p

    def __str__(self):
        s = "Options:\n\n"
        for f in self.options:
            s += f"{f}\n"
        return s
