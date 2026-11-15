# Forhealth: astronaut daily self-check

A NASA Space Apps Challenge 2026 project (Hamilton, New Zealand) for the challenge
**Create Health Monitoring Software for Astronauts on Space Missions**.

On a long mission an astronaut cannot see a doctor, and help from Earth gets
slower the farther they travel. Forhealth is a two-minute daily check-in that
answers three questions: *Am I okay today? Is anything changing? What should I do?*

## What it does

Every reading gets two checks:

1. **Healthy range** - is the reading inside the accepted adult range?
2. **Personal baseline** - is the reading unusual *for this astronaut*, compared
   with their own first 14 mission days?

The second check catches slow change that a range check misses. In the demo
data, resting heart rate creeps up and sleep shortens over several weeks. Every
single reading stays inside the healthy range, yet Forhealth raises a "watch"
flag from about mission day 42.

Screens: **Status** (colour cards with what to do), **Check-in** (enter today's
readings), **Trends** (charts with the personal-normal band), **Learn** (how to
measure, why it matters in space, and sources).

## Run it

```
pip install -r requirements.txt
python simulate.py
streamlit run app.py
```

## Files

| File | Job |
|---|---|
| `indicators.py` | The knowledge table: ranges, NASA risks, sources, advice text |
| `simulate.py` | Creates the simulated mission log `data/mission_log.csv` |
| `checks.py` | The two checks and the green / amber / red rule |
| `app.py` | The Streamlit screens |

## Data statement

**All readings are simulated.** No real astronaut or personal health data is
used. This is a hackathon prototype, not a medical device. The ranges are
general adult reference ranges for people on Earth, and the advice text is
illustrative.

## NASA resources used

- [5 Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/)
- [Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/)
- [Risk of Cardiovascular Adaptations](https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/)
- [Risk of Inadequate Food and Nutrition](https://www.nasa.gov/reference/risk-of-inadequate-food-and-nutrition/)
- [Risk of Altered Immune System Responses](https://www.nasa.gov/reference/risk-of-altered-immune-system-responses/)
- [Risk from Inadequate Sleep and Irregular Schedules](https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/)
- [Risk of Behavioral Conditions and Psychiatric Disorders](https://www.nasa.gov/reference/risk-of-behavioral-conditions-and-psychiatric-disorders/)

## Other sources (healthy ranges)

- Blood pressure: [Mayo Clinic, citing ACC/AHA categories](https://www.mayoclinic.org/tests-procedures/blood-pressure-test/in-depth/blood-pressure/art-20050982)
- Resting heart rate: [Mayo Clinic](https://www.mayoclinic.org/healthy-lifestyle/fitness/expert-answers/heart-rate)
- Fasting blood sugar: [CDC, Testing for Diabetes](https://www.cdc.gov/diabetes/diabetes-testing/index.html) and [CDC, Low Blood Sugar](https://www.cdc.gov/diabetes/about/low-blood-sugar-hypoglycemia.html)
- Body temperature: [MedlinePlus](https://medlineplus.gov/ency/article/001982.htm)
- Sleep: [CDC, About Sleep](https://www.cdc.gov/sleep/about/index.html)

## Tools

Python, Streamlit, pandas, NumPy, Altair.

## Use of AI tools

The code and text in this repository were written with assistance from an AI
tool (Claude, by Anthropic). Each code file says so in its header. No
AI-generated images, video or audio are used. All charts are drawn by the
project's own code from the simulated data.
