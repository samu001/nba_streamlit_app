import streamlit as st
import pandas as pd
import numpy as np
import requests
import altair as alt

url = "https://api-nba-v1.p.rapidapi.com/standings"

headers = {
    "X-RapidAPI-Key": "a60722f048mshde48ca0c6a9d0d8p1099d4jsn973fd638ca0b",
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}

# General Page Configuration
st.set_page_config(
    page_title="NBA Data Hub",
    layout="wide"
)

st.title("Standings")

st.sidebar.success("Select a page")

# Arrays for each data set (maybe change to object later)
teamNames = []
wins = []
losses = []
winStreak = []

# Season Selector
selectedSeason = st.selectbox(
    'Select Season',
    ('2022', '2021', '2020', '2019', '2018'),
    index=1
)

conference = st.radio(
    "Select Conference",
    ("East", "West")
)

with st.spinner('Fetching Data...'):
    # Call API when user selects a new season, Get the response and convert it to Json
    response = requests.request\
        ("GET", url, headers=headers, params={"league": "standard", "season": selectedSeason, "conference": conference}).json()
    # Put response array on data
    data = response['response']

    # Distribute the data to use on the Table
    for i in range(0, len(data), 1):
        # If the team has a win streak append it, else no streak
        if data[i]['winStreak']:
            winStreak.append(data[i]['streak'])
        else:
            winStreak.append("0")
        teamNames.append(data[i]['team']['name'])
        wins.append(data[i]['conference']['win'])
        losses.append(data[i]['conference']['loss'])

    # Construct the Standings Table
    col1, = st.columns(1)
    with col1:
        teams = pd.DataFrame(
            {
                "Team Name": teamNames,
                "Wins": wins,
                "Losses": losses,
                "Win Streak": winStreak
            }
        )
        st.dataframe(teams)

    st.subheader("Team Comparison")

    bar_chart = alt.Chart(teams).mark_bar().encode(
        y='Wins:Q',
        x='Team Name:O',
    )
    st.altair_chart(bar_chart, use_container_width=True)




















# Object to store needed team data (not being used now)
class Team:
    # Constructor function
    def __init__(self, name, city, conference, wins, losses):
        self.name = name
        self.city = city
        self.conference = conference
        self.wins = wins
        self.losses = losses

    # To str function to print to console
    def __str__(self):
        return "Name: " + self.name + "\nCity: " + self.city