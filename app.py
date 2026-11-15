"""
app.py - the screens of the Forhealth app, built with Streamlit.

Streamlit turns this Python script into a web page. Every time the user
clicks something, Streamlit re-runs this file from top to bottom and redraws
the page.

Run it from the project folder:
    streamlit run app.py

AI-use note: this file was written with assistance from an AI tool (Claude).
All readings shown are SIMULATED. Prototype only - not a medical device.
"""

import os

import altair as alt        # altair: the charting library Streamlit uses
import pandas as pd
import streamlit as st

from checks import (BASELINE_DAYS, RECENT_DAYS, Z_LIMIT, Z_LIMIT_SINGLE, assess,
                    overall_status)
from indicators import ACTIONS, HAZARDS, HAZARDS_URL, INDICATORS
from simulate import build_log

LOG_PATH = "data/mission_log.csv"

# How each status is shown. A status always has an icon AND a word as well
# as a colour, so it can be read by people who cannot tell colours apart.
STATUS_STYLE = {
    "green": {"colour": "#0ca30c", "icon": "✓", "word": "OK"},
    "amber": {"colour": "#fab219", "icon": "!", "word": "WATCH"},
    "red":   {"colour": "#d03b3b", "icon": "✕", "word": "ACT NOW"},
}
LINE_COLOUR = "#2a78d6"     # the one colour used for the reading line in charts
MUTED = "#898781"           # quiet grey for limits and labels

st.set_page_config(page_title="Forhealth - astronaut self-check", layout="wide")


# ----------------------------------------------------------------------------
# 1. Load the mission log (once per browser session)
# ----------------------------------------------------------------------------
# st.session_state is Streamlit's memory: values stored in it survive re-runs.
if "log" not in st.session_state:
    if os.path.exists(LOG_PATH):
        st.session_state["log"] = pd.read_csv(LOG_PATH)
    else:
        st.session_state["log"] = build_log()      # no file yet: simulate one
    # start by viewing the latest day of the mission
    st.session_state["view_day"] = int(st.session_state["log"]["day"].max())

log = st.session_state["log"]
last_day = int(log["day"].max())


def save_check_in():
    """Runs when the check-in form is submitted: adds one new day to the log."""
    new_row = {"day": last_day + 1}
    for indicator in INDICATORS:
        # each form input stored its value in session_state under "in_<key>"
        new_row[indicator["key"]] = st.session_state["in_" + indicator["key"]]
    st.session_state["log"] = pd.concat(
        [st.session_state["log"], pd.DataFrame([new_row])], ignore_index=True)
    st.session_state["view_day"] = last_day + 1    # jump to the new day
    st.session_state["just_saved"] = True


# ----------------------------------------------------------------------------
# 2. Sidebar: choose which mission day to look at
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("Forhealth")
    st.caption("Daily self-check for astronauts on long missions")
    st.slider("Mission day", min_value=1, max_value=last_day, key="view_day",
              help="Slide back to replay earlier days of the mission.")
    st.info("All readings are simulated. This is a hackathon prototype, "
            "not a medical device.")

view_day = st.session_state["view_day"]
# keep only the rows up to the chosen day: "today" is the last row of `view`
view = log[log["day"] <= view_day]

# run both checks on every indicator
results = [assess(view, indicator) for indicator in INDICATORS]
overall = overall_status(results)


# ----------------------------------------------------------------------------
# 3. Small helper functions that draw parts of the page
# ----------------------------------------------------------------------------
def format_value(value, indicator):
    """Show whole numbers without decimals and others with one or two."""
    if indicator["input_step"] >= 1:
        return f"{value:.0f}"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def draw_card(indicator, result):
    """Draw one status card for one indicator."""
    style = STATUS_STYLE[result["status"]]
    reasons = "<br>".join(result["reasons"])
    # The card is a small piece of HTML so that it can have a coloured edge.
    st.markdown(
        f"""
        <div style="border-left: 8px solid {style['colour']};
                    background: rgba(127,127,127,0.10);
                    border-radius: 6px; padding: 14px 16px; margin-bottom: 6px;">
          <div style="font-size: 0.9rem; opacity: 0.8;">{indicator['label']}</div>
          <div style="font-size: 2rem; font-weight: 600; line-height: 1.3;">
            {format_value(result['today'], indicator)}
            <span style="font-size: 0.9rem; font-weight: 400; opacity: 0.8;">
              {indicator['unit']}</span>
          </div>
          <div style="font-weight: 700; margin: 4px 0 8px 0;">
            <span style="display: inline-block; min-width: 1.5em; text-align: center;
                         background: {style['colour']}; color: #0b0b0b;
                         border-radius: 4px; margin-right: 6px;">{style['icon']}</span>
            {style['word']}
          </div>
          <div style="font-size: 0.92rem;">{reasons}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # the "what to do" text and the NASA link sit under the card
    with st.expander("What to do, and why it matters in space"):
        st.write("**What to do:** " + ACTIONS[result["status"]])
        st.write("**Why it matters in space:** " + indicator["nasa_why"])
        st.markdown(f"NASA: [{indicator['nasa_risk']}]({indicator['nasa_url']})")
        st.caption("Healthy range used: " + indicator["range_text"])


def draw_chart(indicator, result):
    """Draw the trend chart for one indicator, up to the chosen day."""
    key = indicator["key"]
    data = view[["day", key]].rename(columns={key: "reading"})

    # x axis always spans the whole view so charts line up with each other
    x_scale = alt.Scale(domain=[1, max(view_day, 2)], nice=False)
    x = alt.X("day:Q", title="Mission day", scale=x_scale)

    # y axis: tall enough for the readings AND the healthy-range limits
    y_values = list(data["reading"])
    limits = []                          # (value, label) pairs to draw as lines
    if indicator["green_min"] is not None:
        limits.append((indicator["green_min"], f"range min {indicator['green_min']}"))
    if indicator["green_max"] is not None:
        limits.append((indicator["green_max"], f"range max {indicator['green_max']}"))
    y_values += [value for value, _ in limits]
    if result["baseline_ready"]:
        y_values += [result["mean"] - Z_LIMIT * result["std"],
                     result["mean"] + Z_LIMIT * result["std"]]
    pad = (max(y_values) - min(y_values)) * 0.08 or 1
    y_scale = alt.Scale(domain=[min(y_values) - pad, max(y_values) + pad], nice=False)
    y = alt.Y("reading:Q", title=indicator["unit"], scale=y_scale)

    layers = []

    # layer 1: the grey band = this astronaut's personal normal
    if result["baseline_ready"]:
        band = pd.DataFrame({
            "x1": [1], "x2": [max(view_day, 2)],
            "low": [result["mean"] - Z_LIMIT * result["std"]],
            "high": [result["mean"] + Z_LIMIT * result["std"]],
        })
        layers.append(
            alt.Chart(band).mark_rect(color=MUTED, opacity=0.22).encode(
                x=alt.X("x1:Q", scale=x_scale), x2="x2:Q",
                y=alt.Y("low:Q", scale=y_scale), y2="high:Q"))

    # layer 2: dashed lines = the healthy-range limits, each with a text label
    for value, label in limits:
        limit = pd.DataFrame({"y": [value], "x": [max(view_day, 2)], "label": [label]})
        layers.append(
            alt.Chart(limit).mark_rule(color=MUTED, strokeDash=[5, 4]).encode(
                y=alt.Y("y:Q", scale=y_scale)))
        layers.append(
            alt.Chart(limit).mark_text(color=MUTED, align="right", dx=-4, dy=-7,
                                       fontSize=11).encode(
                x=alt.X("x:Q", scale=x_scale), y=alt.Y("y:Q", scale=y_scale),
                text="label:N"))

    # layer 3: the readings themselves (hover over a point to see its value)
    tooltip = [alt.Tooltip("day:Q", title="Mission day"),
               alt.Tooltip("reading:Q", title=indicator["label"])]
    layers.append(
        alt.Chart(data).mark_line(color=LINE_COLOUR, strokeWidth=2).encode(x=x, y=y))
    layers.append(
        alt.Chart(data).mark_circle(color=LINE_COLOUR, size=45, opacity=0.9).encode(
            x=x, y=y, tooltip=tooltip))

    chart = alt.layer(*layers).properties(height=230)
    style = STATUS_STYLE[result["status"]]
    st.markdown(f"**{indicator['label']}** - {style['icon']} {style['word']}")
    st.altair_chart(chart, width='stretch')


# ----------------------------------------------------------------------------
# 4. The page itself: four tabs
# ----------------------------------------------------------------------------
st.title("Forhealth: astronaut daily self-check")

tab_status, tab_checkin, tab_trends, tab_learn = st.tabs(
    ["Status", "Check-in", "Trends", "Learn"])

# ---------------- Status ----------------
with tab_status:
    if st.session_state.pop("just_saved", False):
        st.success(f"Check-in saved as mission day {view_day}.")

    style = STATUS_STYLE[overall]
    flagged = [ind["label"] for ind, res in zip(INDICATORS, results)
               if res["status"] != "green"]
    if overall == "green":
        headline = "All indicators are in range and in line with your usual readings."
    else:
        headline = "Needs attention: " + ", ".join(flagged) + "."
    st.subheader(f"Mission day {view_day}: {style['icon']} {style['word']}")
    st.write(headline)
    if view_day <= BASELINE_DAYS:
        st.caption(f"Still learning your personal normal: this needs the first "
                   f"{BASELINE_DAYS} days. Only the healthy-range check is active.")

    # lay the cards out three to a row
    for start in range(0, len(INDICATORS), 3):
        columns = st.columns(3)
        for column, indicator, result in zip(
                columns, INDICATORS[start:start + 3], results[start:start + 3]):
            with column:
                draw_card(indicator, result)

# ---------------- Check-in ----------------
with tab_checkin:
    st.subheader(f"Check-in for mission day {last_day + 1}")
    st.write("Enter today's readings. The boxes start at your most recent values.")
    latest = log.iloc[-1]                       # the last saved day
    with st.form("check_in"):
        columns = st.columns(2)
        for position, indicator in enumerate(INDICATORS):
            with columns[position % 2]:         # alternate left and right column
                st.number_input(
                    f"{indicator['label']} ({indicator['unit']})",
                    min_value=indicator["input_min"],
                    max_value=indicator["input_max"],
                    value=float(latest[indicator["key"]]),
                    step=indicator["input_step"],
                    key="in_" + indicator["key"],
                    help=indicator["how_to_measure"])
        st.form_submit_button("Save check-in", on_click=save_check_in)

# ---------------- Trends ----------------
with tab_trends:
    st.subheader(f"Trends up to mission day {view_day}")
    st.caption(
        "Blue line: your readings. Grey band: your personal normal, taken from "
        f"your first {BASELINE_DAYS} days. Dashed lines: healthy-range limits. "
        "Hover over a point for its value.")
    for start in range(0, len(INDICATORS), 2):
        columns = st.columns(2)
        for column, indicator, result in zip(
                columns, INDICATORS[start:start + 2], results[start:start + 2]):
            with column:
                draw_chart(indicator, result)
    with st.expander("Show the readings as a table"):
        st.dataframe(view, hide_index=True, width='stretch')

# ---------------- Learn ----------------
with tab_learn:
    st.subheader("How Forhealth decides")
    st.write(
        f"Every reading gets two checks. **Healthy range:** is it inside the "
        f"accepted range for adults? **Personal baseline:** is it unusual for "
        f"you? Your normal is the average of your first {BASELINE_DAYS} mission "
        f"days. The average of your last {RECENT_DAYS} days is flagged when "
        f"it sits {Z_LIMIT:.0f} or more typical day-to-day wobbles away from "
        f"that normal. A single day needs {Z_LIMIT_SINGLE:.0f} or more, because "
        f"one odd day often happens by chance. The second check can catch a slow change "
        f"while every single reading is still inside the healthy range.")

    st.subheader("NASA's five hazards of human spaceflight")
    for name, text in HAZARDS:
        st.markdown(f"- **{name}.** {text}")
    st.markdown(f"Source: [NASA Human Research Program]({HAZARDS_URL})")

    st.subheader("The indicators")
    for indicator in INDICATORS:
        with st.expander(indicator["label"]):
            st.write("**How to measure:** " + indicator["how_to_measure"])
            st.write("**Why it matters in space:** " + indicator["nasa_why"])
            st.markdown(f"NASA: [{indicator['nasa_risk']}]({indicator['nasa_url']})")
            st.write("**Healthy range:** " + indicator["range_text"])
            if indicator["range_url"]:
                st.markdown(
                    f"Range source: [{indicator['range_source']}]({indicator['range_url']})")

    st.subheader("Limits of this prototype")
    st.write(
        "All readings are simulated. The ranges are general adult reference "
        "ranges for people on Earth, and the advice text is illustrative. A "
        "flight version would use each astronaut's own limits and the "
        "mission's medical procedures. The baseline uses the first "
        f"{BASELINE_DAYS} mission days; a real one would be set by flight "
        "surgeons, because the body keeps adapting in space.")
