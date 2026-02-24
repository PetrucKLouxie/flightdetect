import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("✈️ Juanda Live Radar (OpenSky Login)")
st.caption("Mini FlightRadar - Fokus Juanda (WARR)")

JUANDA_LAT = -7.379
JUANDA_LON = 112.787

# Bounding box lebih luas supaya pasti ada pesawat
LAT_MIN = -10
LAT_MAX = -5
LON_MIN = 109
LON_MAX = 116


@st.cache_data(ttl=30)
def get_flights():
    url = "https://opensky-network.org/api/states/all"
    try:
        r = requests.get(
            url,
            auth=(st.secrets["OPENSKY_USER"], st.secrets["OPENSKY_PASS"]),
            timeout=15
        )

        if r.status_code != 200:
            st.error(f"API Error Code: {r.status_code}")
            st.write(r.text)
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
                        "altitude": s[7],      # meter
                        "velocity": s[9],      # m/s
                        "heading": s[10],
                        "vertical_rate": s[11]
                    })

        return flights

    except Exception as e:
        st.error(str(e))
        return []


# =========================
# MAP
# =========================
m = folium.Map(
    location=[JUANDA_LAT, JUANDA_LON],
    zoom_start=13
)

# Marker Juanda
folium.Marker(
    [JUANDA_LAT, JUANDA_LON],
    tooltip="Juanda Airport (WARR)",
    icon=folium.Icon(color="red")
).add_to(m)

folium.Circle(
    location=[JUANDA_LAT, JUANDA_LON],
    radius=3000,  # 30 km
    color="red",
    fill=False
).add_to(m)

flights = get_flights()

# DEBUG
st.write("RAW STATES:", data.get("states"))
st.write("USER:", st.secrets.get("OPENSKY_USER"))
st.write("PASS LENGTH:", len(st.secrets.get("OPENSKY_PASS", "")))
st.write("Total aircraft detected:", len(flights))

for f in flights:
    folium.CircleMarker(
        location=[f["lat"], f["lon"]],
        radius=4,
        popup=f"""
        Callsign: {f['callsign']} <br>
        Altitude: {round(f['altitude'] or 0)} m <br>
        Speed: {round(f['velocity'] or 0)} m/s <br>
        Vertical rate: {f['vertical_rate']}
        """,
        color="blue",
        fill=True
    ).add_to(m)

st_folium(m, width=1400, height=700)
