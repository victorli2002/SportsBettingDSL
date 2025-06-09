# sportsbetpy

## Overview

**sportsbetpy** is an internal Domain-Specific Language (DSL) built in Python to simplify and streamline creation, searching, and comparison of sports bets. 

---

## Features

- Obtain real (or mock) betting lines for your favorite NBA, NFL, MLB, or NHL teams
- Search for bets that match your desired criteria
- Create hypothetical parlays and analyze them
- Apply strategies to different games/backends in order to find the best bets for you
- Look at odds, implied probability, payout

## Not-yet Implemented

- More prebuilt strategies
- Easier accessing of historical odds

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/victorli2002/SportsBettingDSL
   cd yourrepo

2. Navigate to the folder with the clone repo.
3. Install the package in editable mode:
   ```bash
   pip install -e .
4. Import sportsbetpy and have fun fake gambling.
   ```python
   from sportsbetpy import *

---

## Examples

### Loading Backends

The first step is to load a backend that contains information on available bets. 
Currently, we only support a fakebackend, which is created randomly. You can specify the league(s) to include.
```python
fake_backend = FakeBackend(["basketball_nba", "americanfootball_nfl"], seed=57)
```

### Fixtures

A Fixture is a scheduled event / scenario / game to bet on. 

You can load fixtures from a backend (through PlannedBet in the next section), or you can also manually construct them.
Currently supported types are 
- Head2Head (who wins), 
- Spreads (cover by winning by more than X (negative) or by not losing by more than X(positive)), 
- Totals (get at leeast that many points)
- OverUnderEvent (XXX gets at least XXX)

```
fake_h2h = Head2Head("49ers", "Warriors", +170, -220)
fake_spreads = Spreads("49ers", "Warriors", -112, +120, 4.5, -4.5)
fake_totals = Totals("49ers", "Warriors", -130, -150, 24, 105)
fake_event = OverUnderEvent("player_assists", 6, "Stephen Curry", -115, -120)
fake_event.bet(200, "under")
```

You can also make a fake Game (which is just a list of fixtures that take place during that game).
```python
niners_vs_warriors_fake_game = Game("San Francisco 49ers", "Golden State Warriors", [fake_h2h, fake_spreads, fake_totals, fake_event])
```

To find bets that are close to this game, you can use the findGames function of some backend.
```python
fake_backend.findGames(niners_vs_warriors_fake_game, num_teams_to_match = 1)
```

### Bets

Before you bet on something, its a planned bet
Since it's just a plan, PlannedBet is a list of fixtures that you can select.

arguments:
- a backend
- a league
- the type of bet  ("any" if any type is fine")
- the entities you're looking for
- whether to find bets with "any" or "all" of the entities included
```python
california_basketball_fan = PlannedBet(fake_backend, "NBA", "any", 
    ["Golden State Warriors", "Los Angeles Lakers", "Los Angeles Clippers", "Sacramento Kings"], "any")
california_football_fan = PlannedBet(fake_backend, "NFL", "any", 
    ["San Francisco 49ers", "Los Angeles Chargers", "Los Angeles Rams"], "any")
california_sports_fan = california_basketball_fan + california_football_fan
```

To select a fixture, use `.select` and the selection method, either
- "random"
- "last_updated"
- "soonest"
- "index" (also takes in an index of the list of fixtures)
```python
some_h2h_bet = PlannedBet(fake_backend, "nba", "h2h", []).select("random")
another_h2h_bet = PlannedBet(fake_backend, "nba", "h2h", []).select("index", -1)
lebron_james_event = PlannedBet(another_fake_backend, "NBA", "player_assists", ["Lebron James"], "all")
```

To bet on one of these, specify 
- the team
- the wager amount
```python
home_team_probably_wins = some_h2h_bet.bet("home", 500)
bigBet = california_sports_fan.select('random').bet("home", 1000)
print(bigBet)
smallBet = california_sports_fan.select('soonest').bet("away", 50)
```

You can get data from the bets.
```python
print(bigBet)
>>>
1000.0 on San Francisco 49ers to win or lose by at most 5.5 points at -112 odds
payout on hit: 1892.857142857143
profit on hit: 892.8571428571429
implied probability of hit: 0.5283018867924528
```

### Parlays

A parlay is a bet that's composed of other smaller bets (legs). All of the bets must hit, and the odds are combined.
Note that actual betting sites typically offer very different odds than you might expect for these (often worse).
To create one, specify a list of bets.
```python
myParlay = Parlay([bigBet, smallBet, lebron_bet])
```

### Strategies

Strategies are basically just lambdas. Currently, there are two supported predefined strategies:
- BetOnHome
- BetOnTeamIfHome
```python
bet = BetOnHome(60).apply(game) # the wager is 60
chase_center_bet = BetOnTeamIfHome("Golden State Warriors", 60).apply(game): # the wager is 60
```

