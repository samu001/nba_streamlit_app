import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk

# General Page Configuration
st.set_page_config(
    page_title="The NBA Wire",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': 'https://docs.streamlit.io',
        'About': '#An app created by Samuel Perez, Vanya Farzamipour and Samuel Gras'
    }
)

# API Configuration
url = "https://api-nba-v1.p.rapidapi.com/standings"
headers = {
    "X-RapidAPI-Key": "a60722f048mshde48ca0c6a9d0d8p1099d4jsn973fd638ca0b",
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}


# App title and logo
col1, col2 = st.columns(2, gap="small")
with col1:
    st.title("The NBA Wire")
with col2:
    st.image("media/The_NBA_Wire app logo.jpeg", width=140)

selectedTab = st.sidebar.selectbox("Select a page", ["Standings", "Map", "Team Stats", "Find Your Team"])

# Season Standings Section
if selectedTab == "Standings":
    st.subheader("Standings")
    # Data for the tables
    teamNames = []
    wins = []
    losses = []
    winStreak = []
    teamImage = []
    winPct = []

    selectedSeason = st.selectbox('Select Season', ('2022', '2021', '2020', '2019', '2018'), index=1)
    conference = st.radio("Select Conference", ("East", "West"))

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
            wins.append(data[i]['win']['total'])
            losses.append(data[i]['loss']['total'])
            winPct.append(data[i]['win']['percentage'])

        # Construct the Standings Table
        teams = pd.DataFrame(
            {
                "Team Name": teamNames,
                "Wins": wins,
                "Losses": losses,
                "Win Streak": winStreak,
                "Win Percentage": winPct
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

# Franchise Map Section
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
        satelliteView = st.checkbox("Satellite View", value=True)

        if satelliteView:
            mapStyle = 'mapbox://styles/mapbox/satellite-streets-v11'
        else:
            mapStyle = 'mapbox://styles/mapbox/light-v10'

        st.pydeck_chart(pdk.Deck(
            map_style=mapStyle,
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

# Team Statistics Section
elif selectedTab == "Team Stats":
    st.subheader("Team Stats")

    # Request the Data and turn it to Json
    res = requests.request \
        ("GET", "https://api-nba-v1.p.rapidapi.com/standings", headers=headers, params={"league": "standard", "season": "2021"}).json()
    data = res['response']

    # Data for the tables
    teamNames = []
    teamId = []
    teamImage = []
    teamSeasons = [2018, 2019, 2020, 2021, 2022]   # Seasons allowed by the API
    teamWins = []

    for i in range(0, len(data), 1):
        teamNames.append(data[i]['team']['name'])
        teamId.append(data[i]['team']['id'])
        teamImage.append(data[i]['team']['logo'])

    teamNames.sort()

    # Get the index of the selected item
    index = st.selectbox("Select a Team", range(len(teamNames)), format_func=lambda x: teamNames[x])


    # ID for the API call
    id = index + 1
    st.image(teamImage[index], width=150)

    # Bug on the API
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

# Find your team Section
else:
    st.subheader("Find Your Team")
    favTeam = ""

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input('Enter your name')
    with col2:
        age = st.number_input('Enter your age', value=18, max_value=100, min_value=1)

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

    # All the options for the quiz
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
        if age > 26:
            if teamType == "Underdogs":
                favTeam = "Chicago Bulls"
            else:
                favTeam = "Atlanta Hawks"
        else:
            if skill == "Dunks":
                favTeam = "Orlando Magic"
            else:
                favTeam = "Indiana Pacers"

    if st.button('Finish Quiz'):
        st.success('Quiz Completed!', icon="✅")
        st.write("Congrats", name, "!   Your Favorite Team should be the", favTeam)
