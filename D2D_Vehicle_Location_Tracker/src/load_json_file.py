import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def loadJsonFile():
    json_file = open('src/vehicle.json')
    data = json.load(json_file)
    logger.info(data)
    return(data)