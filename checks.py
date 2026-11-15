"""
checks.py - the decision logic of the Forhealth app.

Two checks are run on every reading:
  1. RANGE CHECK     - is the reading inside the accepted healthy range?
  2. BASELINE CHECK  - is the reading unusual for THIS astronaut?
They are combined into one status: "green", "amber" or "red".

There is no screen code in this file, so the logic can be tested on its own.

AI-use note: this file was written with assistance from an AI tool (Claude).
"""

BASELINE_DAYS = 14   # the first 14 mission days define "normal for you"
RECENT_DAYS = 5      # how many latest days make up "your recent average"
Z_LIMIT = 2.0        # limit for the 5-day average (see z_score below)
Z_LIMIT_SINGLE = 3.0 # stricter limit for one single day
# Why two limits? One odd day happens often by chance, and with seven
# indicators checked daily a loose limit would raise false alarms most weeks.
# So a single day must be very unusual (3), while a 5-day average only needs
# to be clearly unusual (2), because five days moving together is rarely chance.
# These are common statistical conventions ("two / three standard deviations").
# They are design choices for this prototype, not medical standards.


def range_check(value, indicator):
    """Compare one reading with the healthy range. Returns a colour or None."""
    # If the indicator has no range at all (mood), there is nothing to check.
    limits = [indicator["green_min"], indicator["green_max"],
              indicator["red_below"], indicator["red_above"]]
    if all(limit is None for limit in limits):
        return None

    # Red first: is the reading beyond an "act now" limit?
    if indicator["red_below"] is not None and value < indicator["red_below"]:
        return "red"
    if indicator["red_above"] is not None and value >= indicator["red_above"]:
        return "red"

    # Then amber: outside the green band but not red.
    if indicator["green_min"] is not None and value < indicator["green_min"]:
        return "amber"
    if indicator["green_max"] is not None and value > indicator["green_max"]:
        return "amber"

    return "green"


def z_score(value, mean, std):
    """
    How unusual is `value`, measured in units of normal day-to-day variation?
      0   = exactly your average
      +2  = two "typical wobbles" above your average
      -2  = two "typical wobbles" below it
    """
    if std == 0:                 # no variation at all: avoid dividing by zero
        return 0.0
    return (value - mean) / std


def is_unusual(z, direction, limit):
    """Decide whether a z-score is worth flagging, given which way matters."""
    if direction == "low":                # only a drop matters (sleep, mood)
        return z <= -limit
    return abs(z) >= limit                # "both": a rise or a drop matters


def assess(log, indicator):
    """
    Assess one indicator using the mission log up to and including "today"
    (the last row of `log`). Returns a dictionary describing the result.
    """
    key = indicator["key"]
    series = log[key]                     # the column of readings for this indicator
    today = float(series.iloc[-1])        # iloc[-1] means "the last row"

    result = {
        "today": today,
        "range_status": range_check(today, indicator),
        "baseline_ready": False,          # becomes True once we have enough days
        "baseline_flag": False,           # becomes True if check 2 finds a change
        "mean": None, "std": None,
        "z_today": None, "z_recent": None,
        "reasons": [],                    # plain-language explanations for the card
    }

    # ---------- check 1: healthy range ----------
    if result["range_status"] == "red":
        result["reasons"].append("Outside the healthy range by a wide margin.")
    elif result["range_status"] == "amber":
        result["reasons"].append("Outside the healthy range.")

    # ---------- check 2: personal baseline ----------
    # We need the full baseline window PLUS at least one later day to compare.
    if len(series) > BASELINE_DAYS:
        baseline = series.iloc[:BASELINE_DAYS]        # the first 14 readings
        mean = float(baseline.mean())                 # your average
        std = float(baseline.std())                   # your typical wobble
        recent = float(series.iloc[-RECENT_DAYS:].mean())   # average of last 5 days

        result["baseline_ready"] = True
        result["mean"], result["std"] = mean, std
        result["z_today"] = z_score(today, mean, std)
        result["z_recent"] = z_score(recent, mean, std)

        direction = indicator["watch_direction"]
        shifted = is_unusual(result["z_recent"], direction, Z_LIMIT)
        odd_day = is_unusual(result["z_today"], direction, Z_LIMIT_SINGLE)
        result["baseline_flag"] = shifted or odd_day
        if shifted:
            # the 5-day average has moved: this is a sustained shift, not a blip
            way = "higher" if result["z_recent"] > 0 else "lower"
            result["reasons"].append(
                f"Your last {RECENT_DAYS} days average {recent:.1f}, clearly {way} "
                f"than your usual {mean:.1f}. This is a sustained change.")
        elif odd_day:
            way = "higher" if result["z_today"] > 0 else "lower"
            result["reasons"].append(
                f"Today is much {way} than your usual {mean:.1f}. One unusual day; "
                f"see whether it repeats.")

    # ---------- combine the two checks into one colour ----------
    if result["range_status"] == "red":
        result["status"] = "red"
    elif result["range_status"] == "amber" or result["baseline_flag"]:
        result["status"] = "amber"
    else:
        result["status"] = "green"

    if not result["reasons"]:
        if result["range_status"] is None:        # no healthy range exists (mood)
            result["reasons"].append("In line with your usual readings.")
        elif not result["baseline_ready"]:        # still inside the first 14 days
            result["reasons"].append("In range.")
        else:
            result["reasons"].append("In range and in line with your usual readings.")
    return result


def overall_status(results):
    """The overall status is the worst colour found among all indicators."""
    colours = [r["status"] for r in results]
    if "red" in colours:
        return "red"
    if "amber" in colours:
        return "amber"
    return "green"
