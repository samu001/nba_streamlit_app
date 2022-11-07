import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk

url = "https://api-nba-v1.p.rapidapi.com/standings"

headers = {
    "X-RapidAPI-Key": "a60722f048mshde48ca0c6a9d0d8p1099d4jsn973fd638ca0b",
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}

# General Page Configuration
st.set_page_config(
    page_title="The NBA Wire",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': 'https://docs.streamlit.io',
        'About': '#An app created by Samuel Perez, Vanya and Samuel Gras'
    }
)

col1, col2 = st.columns(2, gap="small")
with col1:
    st.title("The NBA Wire")
with col2:
    st.image("media/The_NBA_Wire app logo.jpeg", width=140)

selectedTab = st.sidebar.selectbox("Select a page",
                                   ["Standings", "Map", "Team Stats", "Find Your Team"]
                                   )

if selectedTab == "Standings":
    st.subheader("Standings")
    # Arrays for each data set
    teamNames = []
    wins = []
    losses = []
    winStreak = []
    teamImage = []

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
        response = requests.request \
            ("GET", url, headers=headers, params={"league": "standard", "season": selectedSeason, "conference": conference}).json()
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
        teams = pd.DataFrame(
            {
                "Team Name": teamNames,
                "Wins": wins,
                "Losses": losses,
                "Win Streak": winStreak,
            }
        )
        st.dataframe(teams)

        st.subheader("Team Comparison")

        teamsBarChart = pd.DataFrame(
            data={
                'Wins': wins
            },
            index=teamNames
        )
        st.bar_chart(teamsBarChart)

elif selectedTab == "Map":
    col1, col2 = st.columns(2, gap='small')

    with col1:
        st.subheader("Team List")
        # Read csv file
        teamLocations = pd.read_csv('media/NBA_arena_coordinates.csv')

        # Display data
        st.dataframe(teamLocations)
        st.caption("List of NBA teams and their coordinates.")

    with col2:
        st.subheader("Map")
        zoom_lat = teamLocations["latitude"].mean()
        zoom_long = teamLocations["longitude"].mean()

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=zoom_lat,
                longitude=zoom_long,
                zoom=3,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=teamLocations,
                    get_position='[longitude, latitude]',
                    get_color='[201, 8, 42, 160]',
                    radiusScale=300,
                    radius_min_pixels=5,
                    radius_max_pixels=100,
                    get_radius=50,
                    pickable=True,
                ),
            ],
            tooltip={
                "html": "City: {City} <br/> Team Name: {Team Name} <br/> Lat: {latitude} <br/>"
                        "Long: {longitude} <br/>",
                "style": {
                    "backgroundColor": "darkblue",
                    "color": "white"
                }
            }
        ))

elif selectedTab == "Team Stats":
    st.subheader("Team Stats")

    # Request the Data and turn it to Json
    res = requests.request \
        ("GET", "https://api-nba-v1.p.rapidapi.com/standings", headers=headers, params={"league": "standard", "season": "2021"}).json()
    data = res['response']

    # Teams Data
    teamNames = []
    teamId = []
    teamImage = []
    teamSeasons = [2018, 2019, 2020, 2021, 2022]   # Seasons allowed by the API
    teamWins = []

    for i in range(0, len(data), 1):
        teamNames.append(data[i]['team']['name'])
        teamId.append(data[i]['team']['id'])
        teamImage.append(data[i]['team']['logo'])

    index = st.selectbox("Select a Team", range(len(teamNames)), format_func=lambda x: teamNames[x])
    # ID for the API
    id = index + 1
    # Index of the item should also be the index of teamImage array
    st.image(teamImage[index], width=150)

    # Bug on the api
    if id == 3:
        id = 20
    elif id == 13:
        id = 7

    with st.spinner('Fetching Data...'):
        for season in teamSeasons:
            querystring = {"league": "standard", "season": season, "team": id}
            response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/standings", headers=headers,
                                        params=querystring).json()
            data = response['response'][0]
            teamWins.append(data['win']['total'])

        my_chart = pd.DataFrame(
            data={
                'Wins': teamWins
            },
            index=teamSeasons
        )
        st.line_chart(my_chart)

        st.info('Season 2022 win totals are not final', icon="ℹ")

# Find your Team Tab
else:
    st.subheader("Find Your Team")
    favTeam = ""

    skill = st.radio(
        "What do you prefer?",
        key="skill",
        options=["Dunks", "Three Pointers", "Dribbling"],
    )

    teamType = st.radio(
        "In a movie you would like your team to be",
        key="teamType",
        options=["Underdogs", "Favorites"]
    )

    beachSlider = st.slider('From 1 to 5. How much would you enjoy an afternoon at the beach?', 0, 5, 2)

    # Options for the quiz
    if 4 <= beachSlider <= 5:
        if skill == "Dunks":
            if teamType == "Underdogs":
                favTeam = "Houston Rockets"
            else:
                favTeam = "Boston Celtics"
        elif skill == "Three Pointers":
            if teamType == "Underdogs":
                favTeam = "Miami Heat"
            else:
                favTeam = "Golden State Warriors"
        else:
            favTeam = "Memphis Grizzlies"
    elif 2 <= beachSlider <= 3:
        if skill == "Dunks":
            if teamType == "Underdogs":
                favTeam = "Denver Nuggets"
            else:
                favTeam = "Phoenix Suns"
        elif skill == "Three Pointers":
            if teamType == "Underdogs":
                favTeam = "Minnesota Timberwolves"
            else:
                favTeam = "Milwaukee Bucks"
        else:
            favTeam = "Brooklyn Nets"
    else:
        if teamType == "Underdogs":
            favTeam = "Chicago Bulls"
        else:
            favTeam = "Atlanta Hawks"

    if st.button('Finish Quiz'):
        st.success('Quiz Completed!', icon="✅")
        st.write("Your Favorite Team should be the", favTeam)
