
import streamlit as st
import pandas as pd
import altair as alt

# Load data
df = pd.read_csv("rumor_dashboard_with_status_cleaned.csv", parse_dates=['Date'])

st.set_page_config(page_title="Transfer Rumor Tracker", layout="wide")
st.title("📦 Transfer Rumor Dashboard (Powered by MITCHARD)")

# Sidebar filters
st.sidebar.header("Filters")

# Filter by status
statuses = sorted(df["Status"].dropna().unique())
selected_statuses = st.sidebar.multiselect("Status", options=statuses, default=statuses)

# Filter by club
clubs = sorted(df["To Club"].dropna().unique())
club_choice = st.sidebar.selectbox("Destination Club", options=["All"] + clubs)

# Filter by date range
min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
filtered_df = df[df["Status"].isin(selected_statuses)]
if club_choice != "All":
    filtered_df = filtered_df[filtered_df["To Club"] == club_choice]

filtered_df = filtered_df.copy()
filtered_df["Date"] = filtered_df["Date"].dt.tz_localize(None)
filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
    (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
]

# Probability-based top 10 bar chart
st.subheader("🔝 Top 10 Most Likely Transfers")
top_10 = filtered_df.sort_values("Probability", ascending=False).head(10).copy()
top_10["Label"] = top_10["Player"] + " → " + top_10["To Club"].fillna("Unknown")

bar = alt.Chart(top_10).mark_bar().encode(
    x=alt.X("Probability", scale=alt.Scale(domain=[0, 1])),
    y=alt.Y("Label", sort="-x", axis=alt.Axis(labelLimit=300)),
    tooltip=["Player", "To Club", "Status", "Probability"]
).properties(height=400)

st.altair_chart(bar, use_container_width=True)

# Display filtered data
df_display = filtered_df.sort_values("Probability", ascending=False)
st.subheader(f"📋 {len(df_display)} Rumors Matching Filters")
st.dataframe(df_display, use_container_width=True)

# Download button
csv = df_display.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", csv, "filtered_rumors.csv", "text/csv")
