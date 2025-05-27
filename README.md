# sportsbetpy

## Overview

**sportsbetpy** is an internal Domain-Specific Language (DSL) built in Python to simplify and streamline creation, searching, and comparison of sports bets. 

---

## Features

- Obtain fake sports bets from your favorite NBA, NFL, MLB, or NHL teams
- Search for bets that match your desired criteria
- Create hypothetical parlays and analyze them
- Apply strategies to 
- Look at odds, implied probability, payout

## Soon-to-be Implemented

- More prebuilt strategies
- Real-time/historical sports betting data so you can move to the realm of reality

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

### Bets

Before you bet on something, its a planned bet.
Since it's just a plan, PlannedBet is a list of fixtures that you can select.

You supply a backend, a league, the type of bet  ("any" if any type is fine"), the entities you're looking for, and whether to find bets with *any* or *all* of the entities included.
```python
california_basketball_fan = PlannedBet(fake_backend, "NBA", "any", 
    ["Golden State Warriors", "Los Angeles Lakers", "Los Angeles Clippers", "Sacramento Kings"], "any")
california_football_fan = PlannedBet(fake_backend, "NFL", "any", 
    ["San Francisco 49ers", "Los Angeles Chargers", "Los Angeles Rams"], "any")
california_sports_fan = california_basketball_fan + california_football_fan
some_h2h_bet = PlannedBet(fake_backend, "nba", "h2h", []).select("random")
```

To bet on one of these, specify the team and the wager amount.
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
