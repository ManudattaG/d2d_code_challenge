import json
import string
import load_json_file
import requests
import logging
import api_url
import time
import datetime
import vehicle_location_mapping

current_time = datetime.datetime.now().isoformat()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def register():
    # Register the vehicle #
    url = api_url.registerVehicle_API
    data = load_json_file.loadJsonFile()
    for vehicle in data:
        vehicle_id = vehicle["id"]
        payload = {"id": str(vehicle_id)}
        try:
            response = requests.request("POST", url, data = json.dumps(payload), timeout=10)
            logger.info(response.text)
            logger.info(response.status_code)
        except Exception as e:
            logger.error(e)
    else:
        logger.info("Vehicle registration completed")

    # After registering, update vehicle location on maps until destination is reached #
    location_url = api_url.updateVehicleLocation_API
    json_file = open('src/vehicle.json')
    data = json.load(json_file)
    for vehicle in data:
        vehicle_id = vehicle["id"]
        url = location_url + "?id=" + vehicle_id
        for nodes in vehicle['nodes']:
            payload = {"lat": nodes[0], "lng": nodes[1], "at": str(current_time)}
            try:
                response = requests.request("POST", url, data = json.dumps(payload), timeout=10)
                logger.info(response.text)
                logger.info(response.status_code)
                vehicle_location_mapping.updateLocationOnMap()
            except Exception as e:
                logger.error(e)
    else:
        logger.info("Vehicle location updates completed")


    # De-registers the vehicle once the updates are completed #
    url = api_url.deRegisterVehicle_API
    data = load_json_file.loadJsonFile()
    for vehicle in data:
        vehicle_id = vehicle["id"]
        url = location_url + "?id=" + vehicle_id
        try:
            response = requests.request("DELETE", url, timeout=10)
            logger.info(response.text)
            logger.info(response.status_code)
        except Exception as e:
            logger.error(e)
    else:
        logger.info("Vehicle registration completed")


if __name__ == '__main__':
    register()