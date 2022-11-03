import streamlit as st
import pandas as pd
import numpy as np
import http.client
import requests
import altair as alt

st.title("Team Stats")

headers = {
    "X-RapidAPI-Key": "a60722f048mshde48ca0c6a9d0d8p1099d4jsn973fd638ca0b",
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}

# Get all the teams Data
res = requests.request \
    ("GET", "https://api-nba-v1.p.rapidapi.com/standings", headers=headers,
     params={"league": "standard", "season": "2021"}).json()
data = res['response']

teamNames = []
teamId = []
for i in range(0, len(data), 1):
    teamNames.append(data[i]['team']['name'])
    teamId.append(data[i]['team']['id'])

teamNames.sort()

# Pass the team names as option for selectbox, get the index instead of the label for the API call
index = st.selectbox("Select a Team", range(len(teamNames)), format_func=lambda x: teamNames[x])
id = index + 1

# Bug on the api
if id == 3:
    id = 20

# Seasons allowed by the API
teamSeasons = [2018, 2019, 2020, 2021, 2022]
teamWins = []

with st.spinner('Fetching Data...'):
    for season in teamSeasons:
        querystring = {"league": "standard", "season": season, "team": id}
        response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/standings", headers=headers,
                                    params=querystring).json()
        data = response['response'][0]
        teamWins.append(data['win']['total'])

    df = pd.DataFrame(
        {
            'Season': [f"{d} Season" for d in teamSeasons],
            'Wins': teamWins,
        },
        columns=['Season', 'Wins']
    )

    df = df.melt('Season', var_name='Legend', value_name='Wins')

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Season:N'),
        y=alt.Y('Wins:Q'),
        color=alt.Color("Legend:N")
    ).properties(title="Wins per year")
    st.altair_chart(chart, use_container_width=True)

    st.info('Season 2022 win totals are not final', icon="ℹ")
