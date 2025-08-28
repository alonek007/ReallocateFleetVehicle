# File: visualizer.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import time
import random

# Import the agent and its dependencies from the other file
from agent import FleetAI, Vehicle, Request, haversine

# --- Helper Function for Spawning (with Land-Only Check) ---
def random_point_in_bounds(bounds):
    """
    Generates a random point within the given bounds, but rejects points
    that are likely in the sea by using a simple longitude check.
    """
    # For the Chennai/Mambakkam area, a longitude greater than ~80.28 is almost certainly the sea.
    SEA_LONGITUDE_BOUNDARY = 80.28 
    
    while True: # Loop until a valid point on land is found
        lat = random.uniform(bounds["min_lat"], bounds["max_lat"])
        lon = random.uniform(bounds["min_lon"], bounds["max_lon"])
        
        if lon < SEA_LONGITUDE_BOUNDARY:
            # This point is west of the boundary, so it's likely on land.
            return (lat, lon)
        # Otherwise, the loop continues and tries to generate a new point.

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="AI Fleet Visualization")
st.title("🤖 AI Fleet Agent Visualization")

st.sidebar.header("⚙️ Controls")
# Use a fixed city area for this demo for simplicity and define MAP_BOUNDS
CITY_CENTER = (12.84, 80.22) # Centered near Mambakkam
MAP_BOUNDS = {"min_lat": CITY_CENTER[0]-0.15, "max_lat": CITY_CENTER[0]+0.15, 
              "min_lon": CITY_CENTER[1]-0.15, "max_lon": CITY_CENTER[1]+0.15}

num_vehicles = st.sidebar.slider("Number of Vehicles", 5, 50, 15)
demand_rate = st.sidebar.slider("Demand Rate (requests/tick)", 0.1, 1.0, 0.7)
tick_speed = st.sidebar.slider("Simulation Speed (sec/tick)", 0.1, 2.0, 0.5)

col_start, col_stop, col_reset = st.sidebar.columns([1,1,1])
start_button = col_start.button("▶️ Start")
stop_button = col_stop.button("⏹️ Stop")
reset_button = col_reset.button("🔄 Reset")

# --- Initialize / Reset Session State ---
if reset_button or "vehicles" not in st.session_state:
    st.session_state.vehicles = [
        Vehicle(i, random_point_in_bounds(MAP_BOUNDS)) for i in range(num_vehicles)
    ]
    st.session_state.requests = []
    # FIX: This line now correctly creates the agent by passing the defined MAP_BOUNDS
    st.session_state.agent = FleetAI(map_bounds=MAP_BOUNDS)
    st.session_state.time = 0
    st.session_state.rid_counter = 0
    st.session_state.stats = {"completed_rides": 0, "wait_times": [], "ride_times": []}
    st.session_state.running = False
    st.info("Simulation reset. Press Start to begin.")

if start_button: st.session_state.running = True
if stop_button: st.session_state.running = False

vehicles = st.session_state.vehicles
requests = st.session_state.requests
agent = st.session_state.agent

# --- Main Simulation Loop ---
if st.session_state.running:
    if random.random() < demand_rate:
        req = Request(st.session_state.rid_counter, 
                      random_point_in_bounds(MAP_BOUNDS), 
                      random_point_in_bounds(MAP_BOUNDS), 
                      st.session_state.time)
        requests.append(req)
        st.session_state.rid_counter += 1

    dispatch_cmds, rebalance_cmds = agent.update(vehicles, requests)

    for v, r, action in dispatch_cmds:
        v.status = "to_pickup"
        v.target = r.pickup
        v.request = r
        r.assigned = True
        st.session_state.stats["wait_times"].append(st.session_state.time - r.request_time)

    for v, target, action in rebalance_cmds:
        if v.status == 'idle': # Only rebalance idle vehicles
            v.status = "rebalancing"
            v.target = target
        
    for v in vehicles:
        if v.status not in ["idle"]:
            direction = (v.target[0] - v.location[0], v.target[1] - v.location[1])
            dist = (direction[0]**2 + direction[1]**2)**0.5
            if dist < 0.01: 
                if v.status == "to_pickup":
                    v.status = "to_drop"
                    v.target = v.request.dropoff
                    v.request.pickup_time = st.session_state.time
                elif v.status == "to_drop":
                    st.session_state.stats["completed_rides"] += 1
                    st.session_state.stats["ride_times"].append(st.session_state.time - v.request.pickup_time)
                    agent.log_completed_ride(v.request.pickup)
                    v.status = "idle"
                    v.target = None
                    v.request = None
                elif v.status == "rebalancing":
                    v.status = "idle"
                    v.target = None
            else:
                 move_fraction = 0.05
                 v.location = (v.location[0] + move_fraction * direction[0], v.location[1] + move_fraction * direction[1])

    st.session_state.time += 1

# --- Dashboard & Map Display ---
stats = st.session_state.stats
avg_wait = np.mean(stats["wait_times"]) if stats["wait_times"] else 0
utilization = (len([v for v in vehicles if v.status != "idle"]) / len(vehicles)) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Simulation Time (min)", st.session_state.time)
col2.metric("Completed Rides", stats["completed_rides"])
col3.metric("Vehicle Utilization", f"{utilization:.1f}%")

m = folium.Map(location=CITY_CENTER, zoom_start=12)

colors = {"idle": "green", "to_pickup": "orange", "to_drop": "blue", "rebalancing": "purple"}

for v in vehicles:
    folium.Marker(
        location=v.location, 
        popup=f"Vehicle {v.vid} ({v.status})",
        icon=folium.Icon(color=colors.get(v.status, "gray"), icon="truck", prefix="fa")
    ).add_to(m)

for r in requests:
    if not r.assigned:
        folium.Marker(
            location=r.pickup, 
            popup=f"Request {r.rid}",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

st_folium(m, width=1400, height=600, key="map1")

# --- Animation Loop ---
if st.session_state.running:
    time.sleep(tick_speed)
    st.rerun()