from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import streamlit as st
import osmnx as ox
import folium
from streamlit_folium import st_folium
from datetime import datetime
import math

# ==============================
# --- CONFIG ---
# ==============================
st.set_page_config(layout="wide", page_title="Madrid Mobility App")

GRAPHDB_URL = "url of the graphdb repository"

# ==============================
# --- CACHE FUNCTIONS ---
# ==============================
@st.cache_resource
def get_madrid_data():
    G = ox.graph_from_place("Madrid, Spain", network_type="drive")
    nodes_gdf = ox.graph_to_gdfs(G, edges=False)
    center_point = nodes_gdf.unary_union.centroid
    map_center = [center_point.y, center_point.x]
    edges_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)
    edges_gdf["geometry"] = edges_gdf["geometry"].simplify(tolerance=0.0005)
    return edges_gdf, map_center

@st.cache_resource

#1 Query get all stops to store them with their coordinates
def get_all_stops():
    query = """
    PREFIX ont: <http://crtm-urban-buses.org/opendata/handsOn/group11/ontology#>
    PREFIX schema: <http://schema.org/>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    SELECT ?stop ?stopName ?stopId ?lat ?lon
    WHERE {
        ?stop a ont:Stop ;
              schema:name ?stopName ;
              ont:stopId ?stopId ;
              geo:lat ?lat ;
              geo:long ?lon .
    }
    """
    sparql = SPARQLWrapper(GRAPHDB_URL)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    stops = []
    try:
        results = sparql.query().convert()
        for r in results["results"]["bindings"]:
            stops.append({
                "stopId": r["stopId"]["value"],
                "name": r["stopName"]["value"],
                "lat": float(r["lat"]["value"]),
                "lon": float(r["lon"]["value"])
            })
    except Exception as e:
        st.error(f"Error querying GraphDB: {e}")
    return pd.DataFrame(stops)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
#Calculate de nearest stops with the haversine function
def find_nearby_stops(lat, lon, radius_km=1.0):
    all_stops = st.session_state.all_stops.copy()
    all_stops["distance_km"] = all_stops.apply(lambda row: haversine(lat, lon, row["lat"], row["lon"]), axis=1)
    nearby = all_stops[all_stops["distance_km"] <= radius_km].sort_values("distance_km")
    return nearby

#2 Query, get arrival times of a specific stop
def query_arrival_times(stop_id, time_str):
    query_template = f"""
    PREFIX ont: <http://crtm-urban-buses.org/opendata/handsOn/group11/ontology#>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT ?lineName ?destination ?arrivalTime ?departureTime
    WHERE {{
        ?stop a ont:Stop ;
              ont:stopId "{stop_id}" .
        ?stopTime a ont:StopTime ;
                  ont:refersToStop ?stop ;
                  ont:arrivalTime ?arrivalTime ;
                  ont:departureTime ?departureTime ;
                  ont:belongsToTrip ?trip .
        ?trip a ont:Trip ;
              ont:tripHeadsign ?destination ;
              ont:belongsToRoute ?route .
        ?route a ont:BusRoute ;
               ont:routeShortName ?lineName .
        FILTER(?arrivalTime > "{time_str}")
    }}
    ORDER BY ?arrivalTime
    LIMIT 10
    """
    sparql = SPARQLWrapper(GRAPHDB_URL)
    sparql.setQuery(query_template)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return pd.DataFrame([
            {
                "Line": r["lineName"]["value"],
                "Destination": r["destination"]["value"],
                "Arrival": r["arrivalTime"]["value"],
                "Departure": r["departureTime"]["value"]
            } for r in results["results"]["bindings"]
        ])
    except Exception as e:
        st.error(f"Error querying GraphDB: {e}")
        return pd.DataFrame()

#3 Given a line bus and direction, get route
def get_stops_by_direction(line_id, direction="0"):
    query_template = f"""
    PREFIX ont: <http://crtm-urban-buses.org/opendata/handsOn/group11/ontology#>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT ?stopId ?stopName ?seq ?lat ?lon
    WHERE {{
        ?route a ont:BusRoute ;
               ont:routeShortName "{line_id}" .
        ?trip a ont:Trip ;
              ont:belongsToRoute ?route ;
              ont:directionId "{direction}" .
        ?stopTime a ont:StopTime ;
                  ont:belongsToTrip ?trip ;
                  ont:stopSequence ?seq ;
                  ont:refersToStop ?stop .
        ?stop a ont:Stop ;
              ont:stopId ?stopId ;
              schema:name ?stopName ;
              geo:lat ?lat ;
              geo:long ?lon .
    }}
    ORDER BY ASC(xsd:integer(?seq))
    LIMIT 100
    """
    sparql = SPARQLWrapper(GRAPHDB_URL)
    sparql.setQuery(query_template)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return [
            {
                "Sequence": int(r["seq"]["value"]),
                "Stop_ID": r["stopId"]["value"],
                "Stop_Name": r["stopName"]["value"],
                "Latitude": float(r["lat"]["value"]),
                "Longitude": float(r["lon"]["value"]),
                "Direction": direction
            }
            for r in results["results"]["bindings"]
        ]
    except Exception as e:
        st.error(f"Error querying GraphDB: {e}")
        return []
    
    # ==============================
# --- SESSION STATE ---
# ==============================
if "edges_gdf" not in st.session_state:
    st.session_state.edges_gdf, st.session_state.map_center = get_madrid_data()
if "all_stops" not in st.session_state:
    st.session_state.all_stops = get_all_stops()
edges_gdf = st.session_state.edges_gdf
map_center = st.session_state.map_center

# ==============================
# --- SIDEBAR ---
# ==============================
st.sidebar.title("Navigation Menu")
app_mode = st.sidebar.radio(
    "Choose a tool:",
    ("Find Nearby Stops", "Check Arrival Times", "Get Stop Coordinates by Line")
)

# ==============================
# --- PAGE 1: FIND NEARBY STOPS ---
# ==============================
if app_mode == "Find Nearby Stops":
    st.title("🔍 Find Nearby Stops")
    st.markdown("Click a point on the map, then confirm to search nearby stops.")

    # Initialize session state variables
    if "nearby_map" not in st.session_state:
        st.session_state.nearby_map = folium.Map(
            location=map_center, zoom_start=12, width=1200, height=600, tiles="OpenStreetMap"
        )
        folium.LatLngPopup().add_to(st.session_state.nearby_map)
    
    if "clicked_point_nearby" not in st.session_state:
        st.session_state.clicked_point_nearby = None
    
    if "nearby_results_df" not in st.session_state:
        st.session_state.nearby_results_df = pd.DataFrame()
    
    if "nearby_results_map" not in st.session_state:
        st.session_state.nearby_results_map = None

    # Render map and capture click
    map_data = st_folium(
        st.session_state.nearby_map,  # keep the original folium.Map
        width=1200,
        height=600,
        returned_objects=["last_clicked"],
        key="nearby_map_display"  # unique key
    )

    # Store clicked point
    if map_data and map_data.get("last_clicked"):
        st.session_state.clicked_point_nearby = map_data["last_clicked"]

    # Display selected coordinates
    if st.session_state.clicked_point_nearby:
        lat = st.session_state.clicked_point_nearby["lat"]
        lon = st.session_state.clicked_point_nearby["lng"]
        st.info(f"Selected Coordinates: Lat: {lat:.6f}, Lon: {lon:.6f}")

        # Confirm button
        if st.button("✅ Confirm and search nearby stops") or st.session_state.nearby_results_map is not None:
            # Only compute if not already done
            if st.session_state.nearby_results_df.empty:
                all_stops = st.session_state.all_stops.copy()
                all_stops["distance_km"] = all_stops.apply(lambda row: haversine(lat, lon, row["lat"], row["lon"]), axis=1)
                nearby_df = all_stops[all_stops["distance_km"] <= 1.0].sort_values("distance_km")
                st.session_state.nearby_results_df = nearby_df

                if not nearby_df.empty:
                    # Create new folium map for results
                    m = folium.Map(location=[lat, lon], zoom_start=15, width=1200, height=600, tiles="OpenStreetMap")
                    # Mark clicked point
                    folium.CircleMarker([lat, lon], popup="Selected Point", color="blue", fill=True, fill_color="blue").add_to(m)
                    # Add nearby stops
                    for _, stop in nearby_df.iterrows():
                        folium.CircleMarker(
                            [stop["lat"], stop["lon"]],
                            radius=6,
                            color="red",
                            fill=True,
                            fill_color="red",
                            fill_opacity=0.8,
                            popup=f"{stop['name']} ({stop['stopId']}) {stop['distance_km']:.2f} km"
                        ).add_to(m)
                    st.session_state.nearby_results_map = m

            # Display results table + map
            if not st.session_state.nearby_results_df.empty:
                st.dataframe(st.session_state.nearby_results_df)
                st_folium(st.session_state.nearby_results_map, width=1200, height=600, key="nearby_map_results")
            else:
                st.info("No stops found within 1 km.")

# ==============================
# --- PAGE 2: CHECK ARRIVAL TIMES ---
# ==============================
elif app_mode == "Check Arrival Times":
    st.title("⏱️ Check Arrival Times")
    col1, col2 = st.columns(2)
    with col1:
        stop_id_input = st.text_input("Stop ID")
    with col2:
        time_input = st.time_input("Show arrivals after")

    if st.button("Check Times") and stop_id_input:
        arrivals_df = query_arrival_times(stop_id_input, time_input.strftime("%H:%M:%S"))
        if not arrivals_df.empty:
            st.dataframe(arrivals_df)
        else:
            st.info("No arrivals found.")

# ==============================
# --- PAGE 3: GET STOP COORDINATES BY LINE ---
# ==============================
elif app_mode == "Get Stop Coordinates by Line":
    st.title("🚌 Get Stops by Line")

    # Input box can be used repeatedly
    line_input = st.text_input("Line ID (e.g., 51)", key="line_input_box")
    direction_input = st.radio("Direction", ["0", "1"], horizontal=True, key="direction_radio")

    if "route_map_list" not in st.session_state:
        st.session_state.route_map_list = []  # keep previous route maps if needed
    if "route_df" not in st.session_state:
        st.session_state.route_df = pd.DataFrame()

    map_container = st.container()

    if line_input and st.button("Show Route"):
        stops_list = get_stops_by_direction(line_input, direction_input)
        if stops_list:
            st.session_state.route_df = pd.DataFrame(stops_list)

            m_route = folium.Map(
                location=[stops_list[0]['Latitude'], stops_list[0]['Longitude']],
                zoom_start=13,
                width=1200,
                height=600,
                tiles="OpenStreetMap"
            )
            for stop in stops_list:
                folium.CircleMarker(
                    [stop['Latitude'], stop['Longitude']],
                    radius=5,
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.7,
                    popup=f"{stop['Stop_Name']} ({stop['Stop_ID']}) Seq:{stop['Sequence']}"
                ).add_to(m_route)

            coords = [(s['Latitude'], s['Longitude']) for s in stops_list]
            folium.PolyLine(coords, color="red", weight=3, opacity=0.8).add_to(m_route)

            st.session_state.route_map_list.append(m_route)

    if not st.session_state.route_df.empty:
        st.dataframe(st.session_state.route_df)
        # Show the **last generated map** with unique key
        st_folium(
            st.session_state.route_map_list[-1],
            width=1200,
            height=600,
            key=f"route_map_{len(st.session_state.route_map_list)}"
        )