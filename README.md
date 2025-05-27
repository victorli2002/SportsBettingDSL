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
