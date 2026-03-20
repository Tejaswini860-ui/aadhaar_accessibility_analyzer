import streamlit as st
import pandas as pd

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("../data/processed/final_merged_data.csv")

# -------------------------------
# CLEAN DATA
# -------------------------------
df = df.dropna()

# -------------------------------
# TITLE
# -------------------------------
st.title("Aadhaar Accessibility Analyzer")

# -------------------------------
# STATE FILTER
# -------------------------------
selected_state = st.selectbox("Select State", df["state"].unique())

filtered_df = df[df["state"] == selected_state].copy()

# -------------------------------
# CREATE TOTAL ACTIVITY
# -------------------------------
filtered_df["total_activity"] = filtered_df[
    ["age_0_5", "age_5_17", "age_18_greater"]
].sum(axis=1)

# -------------------------------
# CREATE LOW ACCESS (STATE-WISE)
# -------------------------------
threshold = filtered_df["total_activity"].median()

filtered_df["low_access"] = filtered_df["total_activity"].apply(
    lambda x: 1 if x <= threshold else 0
)

# -------------------------------
# DATASET PREVIEW
# -------------------------------
st.subheader("Dataset Preview")
st.write(filtered_df.sample(min(20, len(filtered_df))))

# -------------------------------
# LOW ACCESS REGIONS
# -------------------------------
low_regions = filtered_df[filtered_df["low_access"] == 1]

st.subheader("Low Access Regions")

if low_regions.empty:
    st.warning("No low access regions found for this state")
else:
    st.write(low_regions[["state", "district"]].drop_duplicates())

# -------------------------------
# LOW ACCESS COUNT (DISTRICT-WISE)
# -------------------------------
st.subheader("Low Access Count (District-wise)")

if not low_regions.empty:
    count_data = low_regions["district"].value_counts()
    st.bar_chart(count_data)
else:
    st.info("No data to display")

# -------------------------------
# TOP 5 WORST DISTRICTS
# -------------------------------
st.subheader("Top 5 Worst Districts")

if not low_regions.empty:
    top5 = low_regions["district"].value_counts().head(5)
    st.write(top5)

# -------------------------------
# MESSAGE GENERATION
# -------------------------------
st.subheader("Suggested Actions")

def generate_message(state, district):
    return f"Aadhaar enrollment/update is low in {district}, {state}. Awareness campaigns are recommended."

if not low_regions.empty:
    low_regions["message"] = low_regions.apply(
        lambda row: generate_message(row["state"], row["district"]),
        axis=1
    )

    st.write(low_regions[["state", "district", "message"]].drop_duplicates().head(10))
else:
    st.info("No suggestions available")