import folium
from folium.plugins import MarkerCluster
import webbrowser
import load_json_file
import logging
from geopy import distance
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RADIUS = 3500

# Check if vehicle is within the radius #
def calculateVehicleDistance(center_location, vehicle_coordinate):
    vehicle_dist = distance.distance(center_location, vehicle_coordinate).meters
    if vehicle_dist <= RADIUS:
        return(True)
    else:
        return(False)

# Plot map according to lat, long of the vehicle #
def updateLocationOnMap():
    map_loc = "src/visual_map.html"
    center_location = (52.53, 13.403) # As per door2door's office location
    plot_map = folium.Map(location=center_location, zoom_start=13)
    folium.Circle(center_location, radius=RADIUS).add_to(plot_map)
    marker_cluster = MarkerCluster().add_to(plot_map)

    # Mark the location coordinates for each vehicle's nodes #
    json_file = open('src/vehicle.json')
    data = json.load(json_file)
    for vehicle in data:
        for nodes in vehicle['nodes']:
            is_within_radius = calculateVehicleDistance(center_location, nodes)
            if(is_within_radius):
                folium.Marker(location=nodes, tooltip=str(vehicle["id"])).add_to(marker_cluster)
    plot_map.save(map_loc)