import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import ssl
from sqlalchemy import create_engine
from datetime import timedelta
from threading import Event
import datetime

# RETRIEVE DATA FROM DATABASE

engine = create_engine("postgresql+psycopg2://postgres:DSIholiday@localhost:5432/dsi_postgres")

# Flight data
def load_flight_data():
    refDate = (datetime.date.today()).strftime("%Y-%m-%d")
    query = "SELECT f.date, time, arrival_time, duration, f.origin, f.destination, company, price, n_connections \
             FROM flight f \
             INNER JOIN (SELECT date, origin, destination, max(import_date) as last_import \
                         FROM flight \
                         GROUP BY date,origin, destination) sel \
                ON (f.origin = sel.origin) \
                    AND (f.destination = sel.destination) \
                    AND (f.date = sel.date) \
             WHERE import_date = last_import \
             AND sel.date::date < ('{0}'::date + INTERVAL '4 DAYS') \
             AND sel.date::date >= ('{0}'::date)".format(refDate)
    
    return pd.read_sql_query(query, con = engine)

# Country data
def load_country_data():
    query = """ SELECT capital, country
                FROM capital"""

    return pd.read_sql_query(query, con = engine)

# Hotel data
def load_hotel_data():
    refDate = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    query = "SELECT h.checkin_date, h.city, h.name, h.price, h.longitude, h.latitude, h.rating, h.import_date \
             FROM hotelday h \
             INNER JOIN (SELECT checkin_date, city, max(import_date) as last_import \
                         FROM hotelday \
                         GROUP BY checkin_date, city) sel \
             ON (h.checkin_date = sel.checkin_date) \
                 AND (h.city = sel.city) \
             WHERE import_date = last_import \
                 AND sel.checkin_date < ('{0}'::date + INTERVAL '4 DAYS') \
                 AND sel.checkin_date >= ('{0}'::date)".format(refDate)
    
    return pd.read_sql_query(query, con = engine)

# Monument data
def load_monument_data():
    query = """ SELECT *
                FROM monument """
    return pd.read_sql_query(query, con = engine)

# FILTERS AND INTRO PAGE

# Page title
def render_info():
    st.title('Holiday Planner App')

# Country Filter Widget
def create_country_filter(countryData):
    st.sidebar.markdown("### Select a country:")
    value = st.sidebar.selectbox('Filter by country:', [''] + list(countryData['country']))
    if value != "":
        st.session_state["countryState"] = value
    return value
        
# Day Filter Widget
def create_day_filter():
    st.sidebar.markdown("### Select a day:")
    refDate = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    options = [''] + [pd.to_datetime(refDate).normalize() + timedelta(days=x) for x in range(4)]
    value = st.sidebar.selectbox('Filter by day:', options)
    if value != "":
        st.session_state["dayState"] = value
    return value

# FILTER FUNCTIONS

# Filter flight and hotel data based on a day
def filter_by_day(selDay, data):
    if 'date' in data.columns:
        data = data[data["date"] == selDay]
    elif 'checkin_date' in data.columns:
        data = data[data["checkin_date"] == selDay]
    return data

# Filter flight and hotel data based on a country (or city)
def filter_by_country(selCountry, data, countryData):
    capitals = countryData[countryData["country"] == selCountry][["capital"]]
    if 'destination' in data.columns:
        data = data[data.destination.isin(capitals.capital)]
    elif 'country' in data.columns:
        data = data[data["country"] == selCountry]
    elif 'city' in data.columns:
        data = data[data.city.isin(capitals.capital)]
    return data

# RESULT PAGES

# Page 1: Flight Info
def render_table(selCountry, flightData):
    if (flightData.empty):
        st.header("No flights for the selected destination")
        st.markdown("Please choose another one")
    else:
        st.subheader(flightData.iloc[0]["origin"] + " -> " + flightData.iloc[0]["destination"])
        flightData.set_index("date", inplace=True)
        flightData["time"] = [time.strftime("%H:%M:%S") for time in flightData["time"]]
        flightData["n_connections"] = [int(x) for x in flightData["n_connections"]]
        
        st.markdown("Overview")
        st.bar_chart(data = flightData, y = "price")
        def color_coding(row):
            return ['background-color:IndianRed'] * len(
                row) if row.price == round(max(flightData["price"]),2) else ['background-color:DarkSeaGreen'] * len(
                row) if row.price == round(min(flightData["price"]),2) else ['background-color:white'] * len(row)
        st.markdown("------------------------------------")
        st.markdown("Detail data")
        st.dataframe(flightData.style.apply(color_coding, axis=1))

        
# Page 2: Detail info abour trip + map
def render_trip(selCountry, selDay, flightData, hotelData, monumentData):

    st.header("Trip to " + selCountry + " on " + str(selDay))
    
    st.subheader("Flight Information:")
    if (selCountry == "Austria"):
        st.markdown("Already in Austria -> No flight needed")
    elif (flightData.empty):
        st.markdown("No flights available for " + selCountry + " on " + str(selDay))
    else:
        subrender_flight(flightData.iloc[0])

    st.subheader("Hotel Information:")
    if (hotelData.empty):
        st.markdown("No hotels available for " + selCountry + " on " + str(selDay))
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            subrender_hotel(hotelData.iloc[0], 1)
        with col2:
            subrender_hotel(hotelData.iloc[1], 2)
        with col3:
            subrender_hotel(hotelData.iloc[2], 3)
    
    st.subheader("Monument Information:")
    if (monumentData.empty):
        st.markdown("No monuments available")
    else:
        monumentData.index = np.arange(1, len(monumentData) + 1)
        for index, m in monumentData.iterrows():
            subrender_monument(m, index)
        
def subrender_flight(f):
    st.markdown("**" + f["origin"] + " -> " + f["destination"] + "**")
    st.markdown("Date: " + str(f["date"]) + " at: " + str(f["time"]) + " -> " + str(f["arrival_time"]))
    st.markdown("Duration: " + str(f["duration"]) + "min (" + str(int(f["n_connections"])) + " changes)")
    st.markdown(f["company"] + " for " + str(f["price"]) + " EUR")

def subrender_hotel(h, index):
    st.markdown("**Hotel " + str(index) + "**")
    st.markdown(h["name"])
    st.markdown(str(h["price"]) + " EUR / night")
    st.markdown("Rating: " + str(h["rating"]))
    
def subrender_monument(m, index):
    st.markdown(str(index) + ". " + m["name"])

def render_map(hotelData, monumentData):
    lonMid = (monumentData["longitude"].max() + monumentData["longitude"].min()) / 2
    latMid = (monumentData["latitude"].max() + monumentData["latitude"].min()) / 2
    
    hotelData = hotelData[["name", "longitude","latitude"]].dropna()
    hotelData = hotelData.rename(columns={"latitude": "lat", "longitude":"lon"})
    
    if (hotelData.empty and monumentData.empty):
        return
    
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state={
                "latitude": latMid,
                "longitude": lonMid,
                "zoom": 4,
                "pitch": 0,
            },
            layers = [
                pdk.Layer(
                    "ScatterplotLayer",
                    data = monumentData,
                    auto_highlight = True,
                    get_position = ["longitude", "latitude"],
                    get_color=[200, 30, 0, 160],
                    get_radius = 200,
                    radius_min_pixels = 3,
                ),
                pdk.Layer(
                    "TextLayer",
                    data = monumentData,
                    get_position = ["longitude", "latitude"],
                    get_text = "name",
                    get_color=[0, 0, 0, 200],
                    get_size = 11,
                    get_alignment_baseline="'bottom'",
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data = hotelData,
                    auto_highlight = True,
                    get_position = ["lat", "lon"],
                    get_color=[0, 0, 10, 180],
                    get_radius = 100,
                    radius_min_pixels = 3,
                ),
                pdk.Layer(
                    "TextLayer",
                    data = hotelData,
                    get_position = ["lat", "lon"],
                    get_text = "name",
                    get_color=[0, 0, 10, 180],
                    get_size = 11,
                    get_alignment_baseline="'bottom'",
                ),
            ],
        )
    )

# SCRIPT USING PREVIOUSLY DEFINED FUNCTIONS

# get all data
flightData = load_flight_data()
hotelData = load_hotel_data()
countryData = load_country_data()
monumentData = load_monument_data()

# display page title
render_info()

# create refresh button to get latest data
if st.sidebar.button('Refresh'):
    st.experimental_rerun()

# Create Country filter widget and save country in session variables
selCountry = create_country_filter(countryData)
if selCountry == "" and "countryState" in st.session_state:
    selCountry = st.session_state["countryState"]
    
# If user has selected a country proceed:
if (selCountry):
    # Create Day filter widget and data filtering by country
    flightData = filter_by_country(selCountry, flightData, countryData)
    selDay = create_day_filter()
    # If user has selected a day: save result in session variables
    if selDay == "" and "dayState" in st.session_state:
        selDay = st.session_state["dayState"]
    # If user has selected a day: filter flight data by day, filter hotel data by day and country, display map
    if (selDay):
        flightData = filter_by_day(selDay, flightData)
        hotelData = filter_by_country(selCountry, hotelData, countryData)
        hotelData = filter_by_day(selDay, hotelData)
        monumentData = filter_by_country(selCountry, monumentData, countryData)
        render_map(hotelData, monumentData)
        render_trip(selCountry, selDay, flightData, hotelData, monumentData)
    # If user has not selected a day, display only the flight info
    else:
        render_table(selCountry, flightData)
# If user has not selected a country, display placeholder text
else:
    st.header('Please select the destination of your trip.')

