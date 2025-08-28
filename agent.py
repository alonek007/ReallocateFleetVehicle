# File: agent.py
import numpy as np
import math
from scipy.optimize import linear_sum_assignment
from sklearn.neighbors import KernelDensity

# --- Data Classes and Helpers ---
class Vehicle:
    def __init__(self, vid, location):
        self.vid = vid
        self.location = location
        self.status = "idle"  # idle, to_pickup, to_drop, rebalancing
        self.target = None
        self.request = None

class Request:
    def __init__(self, rid, pickup, dropoff, request_time):
        self.rid = rid
        self.pickup = pickup
        self.dropoff = dropoff
        self.request_time = request_time
        self.pickup_time = None
        self.completed_time = None
        self.assigned = False

def haversine(a, b):
    lat1, lon1 = np.radians(a)
    lat2, lon2 = np.radians(b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 6371 * 2 * np.arcsin(np.sqrt(h))

def get_travel_time(a, b, speed=30):
    return haversine(a, b) / speed * 60

# --- The AI Agent ---
class FleetAI:
    """ An AI agent that makes optimal dispatch and rebalancing decisions for a vehicle fleet. """
    
    # FIX: The constructor now correctly takes map_bounds as an argument.
    def __init__(self, map_bounds):
        self.pickup_history = []
        self.map_bounds = map_bounds

    def log_completed_ride(self, pickup_location):
        self.pickup_history.append(pickup_location)

    def update(self, vehicles, requests):
        dispatch_commands = self._make_dispatch_decisions(vehicles, requests)
        rebalance_commands = self._make_rebalancing_decisions(vehicles)
        return dispatch_commands, rebalance_commands

    def _make_dispatch_decisions(self, vehicles, requests):
        idle_vehicles = [v for v in vehicles if v.status == "idle"]
        unassigned_requests = [r for r in requests if not r.assigned]
        commands = []
        if not idle_vehicles or not unassigned_requests:
            return commands
        cost_matrix = np.array([[get_travel_time(v.location, r.pickup) for r in unassigned_requests] for v in idle_vehicles])
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        assigned_vehicles = set()
        assigned_requests = set()
        for i, j in zip(row_ind, col_ind):
            if i < len(idle_vehicles) and j < len(unassigned_requests):
                vehicle = idle_vehicles[i]
                request = unassigned_requests[j]
                if vehicle not in assigned_vehicles and request not in assigned_requests:
                    commands.append((vehicle, request, "DISPATCH"))
                    assigned_vehicles.add(vehicle)
                    assigned_requests.add(request)
        return commands

    def _make_rebalancing_decisions(self, vehicles):
        idle_vehicles = [v for v in vehicles if v.status == "idle"]
        commands = []
        if len(self.pickup_history) < 10 or len(idle_vehicles) < 2:
            return commands
        kde = KernelDensity(bandwidth=0.01, kernel='gaussian')
        kde.fit(np.array(self.pickup_history))
        
        # Use the map_bounds passed during initialization
        lat_range = np.linspace(self.map_bounds["min_lat"], self.map_bounds["max_lat"], 50)
        lon_range = np.linspace(self.map_bounds["min_lon"], self.map_bounds["max_lon"], 50)
        grid = np.array(np.meshgrid(lat_range, lon_range)).T.reshape(-1, 2)
        
        log_density = kde.score_samples(grid)
        hotspot_location = tuple(grid[np.argmax(log_density)])
        
        distances = [haversine(v.location, hotspot_location) for v in idle_vehicles]
        closest_vehicle = idle_vehicles[np.argmin(distances)]
        
        commands.append((closest_vehicle, hotspot_location, "REBALANCE"))
        return commands