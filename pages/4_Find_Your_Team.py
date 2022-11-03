import streamlit as st
import pandas as pd
import numpy as np
import http.client
import requests
import altair as alt

favTeam = ""
skill = st.radio(
    "What is your preferred skill",
    key="skill",
    options=["Dunks", "Three Pointers", "Ally-ups", "Speed"],
)

teamType = st.radio(
    "In a movie you would like your team to be",
    key="teamType",
    options=["Underdogs", "Favorites", "Young Team", "Experienced"]
)

beachSlider = st.slider('From 1 to 5. How much would you enjoy an afternoon at the beach?', 0, 5, 2)

if skill == "Dunks" and teamType == "Underdogs":
    favTeam = "Milwaukee Bucks"
elif skill == "Dunks" and teamType == "Favorites":
    favTeam = "Heat"
else:
    favTeam = "Working On it"


if st.button('Finish Quiz'):
    st.success('Quiz Completed!', icon="✅")
    st.write("Your Favorite Team should be the", favTeam)


