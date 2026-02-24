import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("✈️ Juanda Live Radar")
st.caption("Mini FlightRadar - Fokus Bandara Juanda (WARR)")

# =========================
# KOORDINAT JUANDA
# =========================
JUANDA_LAT = -7.379
JUANDA_LON = 112.787

# Bounding Box Jawa Timur
LAT_MIN = -8
LAT_MAX = -6
LON_MIN = 111
LON_MAX = 114


# =========================
# FETCH DATA OPEN SKY
# =========================
@st.cache_data(ttl=20)
def get_flights():
    try:
        url = (
            "https://opensky-network.org/api/states/all"
            f"?lamin={LAT_MIN}&lomin={LON_MIN}"
            f"&lamax={LAT_MAX}&lomax={LON_MAX}"
        )
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()
        flights = []

        if data.get("states"):
            for s in data["states"]:
                if s[5] and s[6]:
                    flights.append({
                        "callsign": s[1].strip() if s[1] else "N/A",
                        "lat": s[6],
                        "lon": s[5],
                        "altitude": s[7],
                        "velocity": s[9],
                        "heading": s[10],
                    })

        return flights

    except:
        return []


# =========================
# MAP
# =========================
m = folium.Map(location=[JUANDA_LAT, JUANDA_LON], zoom_start=9)

# Marker Juanda
folium.Marker(
    [JUANDA_LAT, JUANDA_LON],
    tooltip="Juanda Airport (WARR)",
    icon=folium.Icon(color="red", icon="plane")
).add_to(m)

flights = get_flights()

for f in flights:
    folium.CircleMarker(
        location=[f["lat"], f["lon"]],
        radius=5,
        popup=f"""
        Callsign: {f['callsign']} <br>
        Altitude: {f['altitude']} m <br>
        Speed: {f['velocity']} m/s
        Heading: {f['heading']}
        """,
        color="blue",
        fill=True,
    ).add_to(m)

st_folium(m, width=1400, height=700)

st.success(f"Pesawat terdeteksi: {len(flights)}")
