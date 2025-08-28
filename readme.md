<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/f4a16b97-3394-4f2d-8490-adda28e4ecd4" /># Fleet Resource Optimization with AI Agents

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B.svg)

This project is a real-time simulation and visualization of an AI-powered fleet management system, developed for the DSIG 7 Hackathon. Our prototype, demonstrated here in the Chennai region, shows how AI agents can dynamically reallocate vehicles to optimize for efficiency, reduce wait times, and increase overall fleet productivity.

### The Problem Statement

Fleet management in dense urban areas suffers from major inefficiencies. Systems are often **reactive**, leading to a poor experience for customers (long wait times, surge pricing) and high operational costs for businesses (wasted fuel, underutilized vehicles). The core challenge is that vehicles are frequently in the wrong place at the wrong time, unable to anticipate the dynamic flow of demand.

### Our Solution

Our solution is an AI agent that operates on a dual-strategy to combat this inefficiency:

1.  **Optimal Reactive Dispatching:** Using the Hungarian algorithm, the agent assigns idle vehicles to new requests in a globally optimal way, minimizing the entire fleet's travel time.
2.  **Proactive Predictive Rebalancing:** Using a Kernel Density Estimation model, the agent learns from historical ride data to predict "demand hotspots" and proactively repositions idle vehicles to these areas *before* new requests even arrive.

--


---

### Key Features

* **Real-Time Map Visualization:** An interactive Folium map displays the live location and status of all vehicles and customer requests.
* **Dynamic Event Simulation:** The simulation generates new requests based on configurable demand rates, mimicking a real-world environment.
* **Dual-Strategy AI Agent:** The core of the project, making intelligent decisions every tick of the simulation.
* **Live KPI Dashboard:** Key metrics like Vehicle Utilization, Average Wait Time, and Completed Rides are tracked and displayed in real-time.
* **Interactive Controls:** The user can configure the simulation parameters (number of vehicles, demand rate, etc.) via a simple sidebar.

### Tech Stack

* **Language:** Python 3.9+
* **Web Framework / UI:** Streamlit
* **Mapping:** Folium & Streamlit-Folium
* **AI / Machine Learning:** Scikit-learn
* **Optimization & Computation:** SciPy, NumPy

### How It Works

Our system's intelligence is encapsulated in the `FleetAI` agent, which operates in two modes:

1.  **Reactive Dispatching (`_make_dispatch_decisions`)**
    When new customer requests are made, the agent builds a cost matrix of travel times between every idle vehicle and every new request. It then uses `scipy.optimize.linear_sum_assignment` (the Hungarian algorithm) to find the most efficient possible pairings, minimizing the total time-to-pickup for the entire fleet.

2.  **Proactive Rebalancing (`_make_rebalancing_decisions`)**
    The agent continuously learns from the pickup locations of all completed rides. It feeds this historical data into a `KernelDensity` model from Scikit-learn to create a probability heatmap of the city. This map predicts where future demand is most likely to occur. The agent then commands the nearest idle vehicle to move towards the center of these "hotspots," ensuring the fleet is prepared for future demand.

---

### Setup and Installation

To run this project locally, please follow these steps.

**1. Clone the repository:**
```bash
git clone <https://github.com/alonek007/ReallocateFleetVehicle>
cd </pathdirectory/https://github.com/alonek007/ReallocateFleetVehicle>```

**2. Create a requirements.txt file:**
```bash
streamlit
folium
streamlit-folium
numpy
scipy
scikit-learn
geopy```

**3. Install the dependencies:**
```bash
pip install -r requirements.txt```

**How to Run**
Once the setup is complete, launch the Streamlit application from your terminal:
```bash
streamlit run visualizer.py```
