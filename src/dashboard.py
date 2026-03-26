import streamlit as st
import pandas as pd

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("../data/processed/final_merged_data.csv")

st.title("Aadhaar Accessibility Analyzer")

# -------------------------------
# STATE SELECTOR
# -------------------------------
states = df["state"].dropna().unique()
selected_state = st.selectbox("Select State", states)

filtered_df = df[df["state"] == selected_state].copy()

# -------------------------------
# TOTAL CALCULATION (FIXED)
# -------------------------------
all_cols = filtered_df.columns

demo_cols = [col for col in all_cols if "demo" in col.lower()]
bio_cols = [col for col in all_cols if "bio" in col.lower()]

exclude_cols = [
    "state", "district", "date", "pincode",
    "low_access", "risk_score", "confidence",
    "future_risk", "total_activity"
]

enroll_cols = [
    col for col in all_cols
    if col not in demo_cols + bio_cols + exclude_cols
    and filtered_df[col].dtype != "object"
]

filtered_df["demographic_total"] = filtered_df[demo_cols].sum(axis=1) if demo_cols else 0
filtered_df["biometric_total"] = filtered_df[bio_cols].sum(axis=1) if bio_cols else 0
filtered_df["enrollment_total"] = filtered_df[enroll_cols].sum(axis=1) if enroll_cols else 0

# -------------------------------
# NORMALIZATION
# -------------------------------
filtered_df["enroll_norm"] = filtered_df["enrollment_total"] / (filtered_df["enrollment_total"].max() + 1)
filtered_df["demo_norm"] = filtered_df["demographic_total"] / (filtered_df["demographic_total"].max() + 1)
filtered_df["bio_norm"] = filtered_df["biometric_total"] / (filtered_df["biometric_total"].max() + 1)

# -------------------------------
# LOW ACCESS CALCULATION
# -------------------------------
threshold = filtered_df["total_activity"].median()

filtered_df["low_access"] = filtered_df["total_activity"].apply(
    lambda x: 1 if x <= threshold else 0
)

low_regions = filtered_df[filtered_df["low_access"] == 1]

# -------------------------------
# LOW ACCESS REGIONS
# -------------------------------
st.subheader("Low Access Regions")

if low_regions.empty:
    st.success("No low access regions found for this state")
else:
    st.dataframe(
        low_regions[["state", "district", "confidence"]]
        .drop_duplicates()
        .head(20)
    )

# -------------------------------
# LOW ACCESS COUNT
# -------------------------------
st.subheader("Low Access Count (District-wise)")

if low_regions.empty:
    st.info("No data to display")
else:
    count_df = (
        low_regions.groupby("district")
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    st.bar_chart(count_df.set_index("district"))

# -------------------------------
# TOP 5 WORST DISTRICTS
# -------------------------------
st.subheader("Top 5 Worst Districts")

if low_regions.empty:
    st.info("No data available")
else:
    worst = (
        low_regions.groupby("district")
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
        .head(5)
    )

    st.dataframe(worst)

# -------------------------------
# RISK SCORE
# -------------------------------
st.subheader("Risk Score (Top Risk Areas)")

risk_df = filtered_df.sort_values(by="risk_score", ascending=False)

st.dataframe(
    risk_df[["state", "district", "risk_score"]]
    .drop_duplicates()
    .head(10)
)

# -------------------------------
# FUTURE RISK ALERT
# -------------------------------
st.subheader("Future Risk Alerts")

future_df = filtered_df[filtered_df["future_risk"] == 1]

if future_df.empty:
    st.success("No future risks detected")
else:
    st.warning("Regions likely to become low access soon")

    st.dataframe(
        future_df[["state", "district"]]
        .drop_duplicates()
        .head(10)
    )

# -------------------------------
# SMART INSIGHT
# -------------------------------
st.subheader("Smart Insight")

if low_regions.empty:
    st.info("No major issues detected in this state")
else:
    worst_series = (
        low_regions.groupby("district")
        .size()
        .sort_values(ascending=False)
    )

    worst_district = worst_series.index[0]
    count = worst_series.iloc[0]

    st.info(
        f"⚠️ {worst_district}, {selected_state} has {count} low access records. Immediate action recommended."
    )

# -------------------------------
# SMART SUGGESTIONS (FINAL 🔥)
# -------------------------------
st.subheader("Suggested Actions")

if low_regions.empty:
    st.info("No suggestions available")
else:
    suggestions = low_regions.drop_duplicates(subset=["district"]).head(5)

    def generate_suggestion(row):
        values = {
            "enrollment": row["enroll_norm"],
            "demographic": row["demo_norm"],
            "biometric": row["bio_norm"]
        }

        sorted_issues = sorted(values, key=values.get)

        primary_issue = sorted_issues[0]
        secondary_issue = sorted_issues[1]

        if primary_issue == "enrollment":
            return f"Increase Aadhaar enrollment centers in {row['district']}, {row['state']}"

        elif primary_issue == "demographic":
            return f"Improve demographic services in {row['district']}, {row['state']} and monitor {secondary_issue} updates"

        else:
            return f"Enhance biometric facilities in {row['district']}, {row['state']} and strengthen {secondary_issue} services"

    suggestions["suggestion"] = suggestions.apply(generate_suggestion, axis=1)

    st.dataframe(
        suggestions[["state", "district", "suggestion"]]
    )
    # -------------------------------
# PRIORITY SCORE (🔥 NEW FEATURE)
# -------------------------------
st.subheader("Priority Regions (High Attention Required)")

filtered_df["priority_score"] = (
    filtered_df["low_access"] * 0.5 +
    filtered_df["risk_score"] * 0.3 +
    filtered_df["future_risk"] * 0.2
)

priority_df = filtered_df.sort_values(by="priority_score", ascending=False)

st.dataframe(
    priority_df[[
        "state",
        "district",
        "priority_score"
    ]].drop_duplicates().head(10)
)

# -------------------------------
# RESOURCE ALLOCATION (🔥 NEW FEATURE)
# -------------------------------
st.subheader("Recommended Resource Allocation")

def resource_suggestion(row):
    if row["priority_score"] > 0.7:
        return "High Priority: Add 3-5 Aadhaar centers"
    elif row["priority_score"] > 0.4:
        return "Medium Priority: Add 1-2 Aadhaar centers"
    else:
        return "Low Priority: Monitor region"

resource_df = priority_df.drop_duplicates(subset=["district"]).head(10).copy()

resource_df["resource_plan"] = resource_df.apply(resource_suggestion, axis=1)

st.dataframe(
    resource_df[[
        "state",
        "district",
        "priority_score",
        "resource_plan"
    ]]
)
# existing code...

# LOW ACCESS
# RISK SCORE
# GRAPH
# SUGGESTIONS

# -----------------------------------
# ADD THIS AT THE END 👇
# -----------------------------------

import json
import os

OUTPUT_FILE = "output.json"

st.subheader("Real-Time Producer-Consumer Output")

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r") as f:
        data = json.load(f)

    if data:
        st.dataframe(data)
    else:
        st.info("No data yet")
else:
    st.warning("No output file found")
