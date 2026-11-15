"""
indicators.py - the single "knowledge table" for the Forhealth app.

Every fact the app shows about a health indicator lives here: its name, unit,
healthy range, the NASA risk it relates to, and where each number came from.
Keeping it in one place means the screens (app.py) and the logic (checks.py)
never contain medical numbers of their own.

AI-use note: this file was written with assistance from an AI tool (Claude).
The ranges were looked up from the cited public sources on 15 Nov 2026.

PROTOTYPE ONLY - not a medical device. Ranges are general adult reference
ranges for people on Earth; a real flight version would use each astronaut's
flight-surgeon-approved limits.
"""

# The order of this list is the order the app shows the indicators in.
# Each indicator is a dictionary (a set of name -> value pairs).
#
# Range fields (any of them can be None, meaning "the source gives no number"):
#   green_min / green_max : readings inside this band count as "in range"
#   red_below / red_above : readings beyond these count as "act now"
#   anything between green and red counts as "watch"
#
# watch_direction: which way a change from personal baseline matters.
#   "both" = higher OR lower than usual is worth a look
#   "low"  = only a drop is worth a look (for example, less sleep)
INDICATORS = [
    {
        "key": "systolic",                      # column name in the mission log
        "label": "Blood pressure - systolic",   # name shown on screen
        "unit": "mm Hg",
        "green_min": None,
        "green_max": 119,       # "Normal: systolic below 120"
        "red_below": None,
        "red_above": 140,       # "Stage 2: systolic 140 or higher"
        "watch_direction": "both",
        "input_min": 70.0, "input_max": 220.0, "input_step": 1.0,
        "range_text": "In range below 120. Watch 120-139. Act at 140 or higher.",
        "range_source": "Mayo Clinic, citing the American College of Cardiology "
                        "and American Heart Association categories",
        "range_url": "https://www.mayoclinic.org/tests-procedures/blood-pressure-test/"
                     "in-depth/blood-pressure/art-20050982",
        "nasa_risk": "Risk of Cardiovascular Adaptations",
        "nasa_url": "https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/",
        "nasa_why": "NASA reports that weightlessness changes how blood circulates, "
                    "which may raise the chance of cardiovascular events.",
        "how_to_measure": "Sit still for five minutes, cuff on the upper arm at "
                          "heart level, and record the top (systolic) number.",
    },
    {
        "key": "diastolic",
        "label": "Blood pressure - diastolic",
        "unit": "mm Hg",
        "green_min": None,
        "green_max": 79,        # "Normal: diastolic below 80"
        "red_below": None,
        "red_above": 90,        # "Stage 2: diastolic 90 or higher"
        "watch_direction": "both",
        "input_min": 40.0, "input_max": 140.0, "input_step": 1.0,
        "range_text": "In range below 80. Watch 80-89. Act at 90 or higher.",
        "range_source": "Mayo Clinic, citing the American College of Cardiology "
                        "and American Heart Association categories",
        "range_url": "https://www.mayoclinic.org/tests-procedures/blood-pressure-test/"
                     "in-depth/blood-pressure/art-20050982",
        "nasa_risk": "Risk of Cardiovascular Adaptations",
        "nasa_url": "https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/",
        "nasa_why": "NASA reports that weightlessness changes how blood circulates, "
                    "which may raise the chance of cardiovascular events.",
        "how_to_measure": "Same reading as systolic: record the bottom (diastolic) number.",
    },
    {
        "key": "heart_rate",
        "label": "Resting heart rate",
        "unit": "beats/min",
        "green_min": 60,        # "normal resting heart rate ranges from 60 to 100"
        "green_max": 100,
        "red_below": None,      # the source gives no single "emergency" number
        "red_above": None,
        "watch_direction": "both",
        "input_min": 30.0, "input_max": 200.0, "input_step": 1.0,
        "range_text": "In range 60-100. Outside that range: watch. "
                      "Very fit people can sit below 60 normally.",
        "range_source": "Mayo Clinic",
        "range_url": "https://www.mayoclinic.org/healthy-lifestyle/fitness/"
                     "expert-answers/heart-rate",
        "nasa_risk": "Risk of Cardiovascular Adaptations",
        "nasa_url": "https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/",
        "nasa_why": "NASA reports that weightlessness changes how blood circulates, "
                    "which may raise the chance of cardiovascular events.",
        "how_to_measure": "Measure after waking, before exercise or caffeine. "
                          "Count the pulse for 60 seconds or use the monitor.",
    },
    {
        "key": "glucose",
        "label": "Fasting blood sugar",
        "unit": "mg/dL",
        "green_min": 70,        # CDC: low blood sugar is "below 70 mg/dL"
        "green_max": 99,        # CDC fasting test: "Normal: 99 or lower"
        "red_below": 54,        # CDC: "Severe low blood sugar is below 54 mg/dL"
        "red_above": 126,       # CDC fasting test: "Diabetes: 126 or higher"
        "watch_direction": "both",
        "input_min": 30.0, "input_max": 400.0, "input_step": 1.0,
        "range_text": "In range 70-99. Watch 54-69 or 100-125. "
                      "Act below 54, or at 126 or higher.",
        "range_source": "US Centers for Disease Control and Prevention (CDC)",
        "range_url": "https://www.cdc.gov/diabetes/diabetes-testing/index.html",
        "nasa_risk": "Risk of Inadequate Food and Nutrition",
        "nasa_url": "https://www.nasa.gov/reference/risk-of-inadequate-food-and-nutrition/",
        "nasa_why": "NASA treats a healthy, balanced diet as essential to crew "
                    "health and performance on long missions.",
        "how_to_measure": "Finger-prick test before the first meal of the day, "
                          "after at least eight hours without food.",
    },
    {
        "key": "temperature",
        "label": "Body temperature",
        "unit": "deg C",
        "green_min": 36.1,      # MedlinePlus: normal range 36.1 to 37.2 deg C
        "green_max": 37.2,
        "red_below": None,
        "red_above": 38.1,      # MedlinePlus: OVER 38 deg C most often means fever,
                                # so 38.0 itself is "watch" and 38.1 is "act"
        "watch_direction": "both",
        "input_min": 33.0, "input_max": 42.0, "input_step": 0.1,
        "range_text": "In range 36.1-37.2. Watch outside that range. Act above 38.0.",
        "range_source": "MedlinePlus, US National Library of Medicine",
        "range_url": "https://medlineplus.gov/ency/article/001982.htm",
        "nasa_risk": "Risk of Altered Immune System Responses",
        "nasa_url": "https://www.nasa.gov/reference/risk-of-altered-immune-system-responses/",
        "nasa_why": "NASA reports that the stresses of spaceflight can reactivate "
                    "dormant viruses in astronauts, so signs of infection matter.",
        "how_to_measure": "Use the same thermometer and the same body site each "
                          "day, at the same time of day.",
    },
    {
        "key": "sleep_hours",
        "label": "Sleep last night",
        "unit": "hours",
        "green_min": 7.0,       # CDC: adults 18-60 need "7 or more hours"
        "green_max": None,
        "red_below": None,      # the source gives no "emergency" number
        "red_above": None,
        "watch_direction": "low",
        "input_min": 0.0, "input_max": 14.0, "input_step": 0.25,
        "range_text": "In range at 7 hours or more. Watch below 7.",
        "range_source": "US Centers for Disease Control and Prevention (CDC)",
        "range_url": "https://www.cdc.gov/sleep/about/index.html",
        "nasa_risk": "Risk from Inadequate Sleep and Irregular Schedules",
        "nasa_url": "https://www.nasa.gov/reference/"
                    "risk-from-inadequate-sleep-and-irregular-schedules/",
        "nasa_why": "NASA lists chronic sleep loss, constant work demands and "
                    "disrupted body clocks as stressors on crew.",
        "how_to_measure": "Record total hours actually asleep, not hours in the "
                          "sleep station.",
    },
    {
        "key": "mood",
        "label": "Mood (self-rating)",
        "unit": "out of 10",
        "green_min": None,      # no clinical range: mood is judged ONLY against
        "green_max": None,      # the astronaut's own baseline
        "red_below": None,
        "red_above": None,
        "watch_direction": "low",
        "input_min": 1.0, "input_max": 10.0, "input_step": 1.0,
        "range_text": "No fixed range. This is a personal 1-10 rating, compared "
                      "only with your own usual scores. It is not a clinical scale.",
        "range_source": "None - personal baseline only",
        "range_url": None,
        "nasa_risk": "Risk of Behavioral Conditions and Psychiatric Disorders",
        "nasa_url": "https://www.nasa.gov/reference/"
                    "risk-of-behavioral-conditions-and-psychiatric-disorders/",
        "nasa_why": "NASA notes that isolation, radiation, distance from Earth "
                    "and other stressors may affect crew mental health.",
        "how_to_measure": "Rate your overall mood today from 1 (very low) to "
                          "10 (very good). Answer quickly and honestly.",
    },
]

# What the astronaut should do for each status colour.
# These are ILLUSTRATIVE prototype wording, not medical protocol. A flight
# version would load the mission's own flight-surgeon procedures here.
ACTIONS = {
    "green": "No action needed. Keep your normal routine and check in again tomorrow.",
    "amber": "Rest for five minutes and measure again. If it is still flagged, "
             "note it in your log and raise it at your next scheduled medical call.",
    "red":   "Measure again now to confirm. If confirmed, tell your Crew Medical "
             "Officer and contact the flight surgeon on the ground.",
}

# NASA's five hazards of human spaceflight, used on the Learn screen.
HAZARDS_URL = "https://www.nasa.gov/hrp/hazards/"
HAZARDS = [
    ("Space radiation", "Described by NASA as one of the most hazardous aspects of spaceflight."),
    ("Isolation and confinement", "Small crews living together for months can show behavioural changes."),
    ("Distance from Earth", "Instructions, supplies and medical care get harder to receive, so crews must be self-reliant. This is why self-assessment matters."),
    ("Gravity fields", "Muscles, bones, the inner ear and organs have to adjust as gravity changes."),
    ("Hostile and closed environments", "Temperature, pressure, lighting, noise and microbes inside the spacecraft all affect health."),
]
