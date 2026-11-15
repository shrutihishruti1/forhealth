"""
simulate.py - creates a SIMULATED mission log for one astronaut.

No real astronaut data is used anywhere in this project. This script invents
60 days of daily readings and plants a slow drift in two of them, so the demo
can show the app catching a change that a simple range check would miss.

Run it once from the project folder:
    python simulate.py
It writes the file data/mission_log.csv.

AI-use note: this file was written with assistance from an AI tool (Claude).
"""

import numpy as np      # numpy: fast maths on lists of numbers
import pandas as pd     # pandas: tables (rows and columns), like a spreadsheet

DAYS = 60               # how many mission days to invent
DRIFT_START = 25        # the day the slow drift begins
SEED = 42               # fixing the seed makes the "random" numbers repeatable


def steady(rng, centre, spread):
    """Readings that wobble around one value with no trend."""
    # rng.normal draws DAYS random numbers from a bell curve
    return rng.normal(loc=centre, scale=spread, size=DAYS)


def drifting(rng, start, end, spread):
    """Readings that stay near `start`, then slide slowly to `end`."""
    centre = np.full(DAYS, float(start))            # begin with a flat line
    steps = DAYS - DRIFT_START                      # number of drifting days
    # np.linspace makes evenly spaced values from start to end
    centre[DRIFT_START:] = np.linspace(start, end, steps)
    # add day-to-day wobble on top of the sliding centre
    return centre + rng.normal(loc=0.0, scale=spread, size=DAYS)


def build_log():
    """Return the whole simulated mission log as a pandas table."""
    rng = np.random.default_rng(SEED)               # the random-number generator

    log = pd.DataFrame({
        "day": np.arange(1, DAYS + 1),              # 1, 2, 3 ... 60
        # --- steady indicators: nothing wrong planted in these ---
        "systolic":    steady(rng, 108, 3.5).round(0),
        "diastolic":   steady(rng, 70, 3.0).round(0),
        "glucose":     steady(rng, 86, 3.5).round(0),
        "temperature": steady(rng, 36.7, 0.12).round(1),
        "mood":        steady(rng, 8, 0.7).round(0).clip(1, 10),
        # --- planted drift: both stay INSIDE the healthy range all mission ---
        "heart_rate":  drifting(rng, 66, 78, 2.0).round(0),     # creeps up
        "sleep_hours": drifting(rng, 7.9, 7.4, 0.2).round(2),   # shortens
    })
    return log


# This block only runs when you type "python simulate.py".
# It does not run when another file imports build_log.
if __name__ == "__main__":
    mission_log = build_log()
    mission_log.to_csv("data/mission_log.csv", index=False)   # save as CSV
    print(mission_log.tail())                                 # show last 5 days
    print("Saved data/mission_log.csv with", len(mission_log), "days")
