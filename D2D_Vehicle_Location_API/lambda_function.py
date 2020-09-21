import json
import logging
import datetime
import boto3
import folium
from folium.plugins import MarkerCluster
from geopy import distance
import dateutil.parser
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3', region_name='us-east-1')
table = dynamodb.Table('Vehicle_Data')
coordinates_table = dynamodb.Table('Location_Coordinate_Data')
S3_BUCKET = "vehicle-visual-map"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# City Boundaries #
center_location = (52.53, 13.403)
RADIUS = 3500

# Get registered vehicle from the DB #
def getItemFromVehicleDB(vehicle_id):
    logger.info("Querying Vehicle DB")
    try:
        response = table.get_item(
            Key={ "Vehicle_Number" : str(vehicle_id) }
        )
        logger.info(response)
        if "Item" in response and 'requested_ts' in response["Item"]:
            prev_location_ts = response['Item']['requested_ts']
            return(prev_location_ts)
        else:
            return(None)
    except Exception as e:
        logger.error(e)
        return(None)
        
# Store Vehicle Location Coordinates Data in DB #
def storeVehicleLocationData(latitude, longitude, vehicle_id):
    logger.info("Storing Vehicle Location Coordinates in DB")
    item = {"Vehicle_Number" : str(vehicle_id), "latitude": Decimal(str(latitude)), "longitude": Decimal(str(longitude))}
    try:
        response = coordinates_table.put_item(Item = item)
        msg = "Vehicle - " + str(vehicle_id) + " updated the location to map the coordinates."
        result = {"message" : msg}
        logger.info(result)
    except Exception as e:
        print(e)
        msg = "Unable to updated the location to map the coordinates due to DB insert error." + str(vehicle_id)
        result = {"message" : msg}
        logger.info(result)

# Check if vehicle is within the radius #
def calculateVehicleDistance(center_location, vehicle_coordinate):
    vehicle_dist = distance.distance(center_location, vehicle_coordinate).meters
    logger.info(vehicle_dist)
    if vehicle_dist <= RADIUS:
        return(True)
    else:
        return(False)
        
# Get all vehicle data from DB #
def queryAllItemsFromVehicleDB():
    logger.info("Querying Vehicle DB to fetch all items")
    try:
        response = table.query(
            IndexName="Registered-index",
            KeyConditionExpression=Key('Registered').eq('True')
        )
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.query(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.update(response['Items'])
        logger.info(data)
        return(data)
    except Exception as e:
        logger.error(e)
        return(None)

# Plot map according to lat, long of the vehicle #
def updateLocationOnMap():
    map_loc = "/tmp/visual_map.html"
    center_location = (52.53, 13.403) # As per door2door's office location
    plot_map = folium.Map(location=center_location, zoom_start=13)
    folium.Circle(center_location, radius=RADIUS).add_to(plot_map)
    marker_cluster = MarkerCluster().add_to(plot_map)

    # Mark the location coordinates for each vehicle's node  #
    data = queryAllItemsFromVehicleDB()
    for vehicle in data:
        vehicle_id = vehicle["Vehicle_Number"]
        latitude = vehicle["latitude"]
        longitude = vehicle["longitude"]
        nodes = (latitude, longitude)
        is_within_radius = calculateVehicleDistance(center_location, nodes)
        if(is_within_radius):
            folium.Marker(location=nodes, tooltip=str(vehicle_id)).add_to(marker_cluster)
    plot_map.save(map_loc)
    uploadHTMLToS3(map_loc)
    
def uploadHTMLToS3(map_loc):
    try:
        s3_client.upload_file(map_loc, S3_BUCKET, 'map/visual_map.html')
        logger.info("Map uploaded to S3 successfully...")
    except Exception as e:
        logger.error(e)

def lambda_handler(event, context):
    logger.info(event)
    api_path = event["resource"]
    api_method = event["httpMethod"]
    
    # Register a vehicle --> POST /vehicles #
    if(api_path == "/vehicles" and api_method == "POST"):
        api_body = event["body"]
        api_body = json.loads(api_body)
        logger.info(api_body)
        vehicle_id = api_body["id"]
        item = {"Vehicle_Number" : str(vehicle_id), "Registered": "True"}
        try:
            response = table.put_item(Item = item)
            msg = "Vehicle - " + str(vehicle_id) + " is registered."
            result = {"message" : msg}
            logger.info(result)
            return {
                'statusCode': 204,
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(e)
            msg = "Unable to register the vehicle due to DB insert error." + str(vehicle_id)
            result = {"message" : msg}
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
            
    # Update the location data of the vehicle --> POST /vehicles/:id/locations #
    if(api_path == "/vehicles/{id}/locations" and api_method == "POST"):
        current_time = datetime.datetime.now()
        vehicle_id = event["pathParameters"]["id"]
        prev_location_ts = getItemFromVehicleDB(vehicle_id)
        if(prev_location_ts != None):
            prev_location_ts = dateutil.parser.parse(prev_location_ts)
            logger.info("Converted prev_location_ts")
            logger.info(prev_location_ts)
            logger.info("Current requested time")
            logger.info(current_time)
            logger.info("Get total seconds from 2 date formats")
            delta_seconds = (current_time - prev_location_ts).total_seconds()
            logger.info(delta_seconds)
            # Check if the location updates are coming not more than once in every 3 seconds #
            if(delta_seconds < Decimal(3)):
                msg = "Vehicle location can only be updated once every 3 seconds."
                result = {"message" : msg}
                logger.info(result)
                return {
                    'statusCode': 200,
                    'body': json.dumps(result)
                }
                
        # Get lat, lng and timestamp data from API #
        api_body = event["body"]
        api_body = json.loads(api_body)
        logger.info(api_body)
        latitude = api_body["lat"]
        longitude = api_body["lng"]
        timestamp = api_body["at"]
        
        try:
            response = table.update_item(
                Key={
                    "Vehicle_Number" : str(vehicle_id)
                },
                UpdateExpression="set latitude=:la, longitude=:lo, #timestamp=:ts, requested_ts=:rt",
                ExpressionAttributeNames={'#timestamp': 'timestamp'},
                ConditionExpression = "attribute_exists(Vehicle_Number) AND Registered = :reg_flag",
                ExpressionAttributeValues={
                    ':la': Decimal(str(latitude)),
                    ':lo': Decimal(str(longitude)),
                    ':ts': str(timestamp),
                    ':rt': str(current_time),
                    ':reg_flag': "True"
                },
                ReturnValues="UPDATED_NEW"
            )
            logger.info(response)
            msg = "Vehicle - " + str(vehicle_id) + " location updated with coordinates: [" + str(latitude) + "," + str(longitude) + "]"
            result = {"message" : msg}
            logger.info(result)
            updateLocationOnMap()
            return {
                'statusCode': 204,
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(e)
            msg = "Vehicle - " + str(vehicle_id) + " is not registered to update the location."
            result = {"message" : msg}
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
            
    # De-register all vehicles when location updates are completed --> DELETE /vehicles/:id #
    if(api_path == "/vehicles/{id}" and api_method == "DELETE"):
        vehicle_id = event["pathParameters"]["id"]
        
        try:
            response = table.update_item(
                Key={
                    "Vehicle_Number" : str(vehicle_id)
                },
                UpdateExpression="set Registered=:r",
                ExpressionAttributeValues={
                    ':r': "False"
                },
                ConditionExpression = "attribute_exists(Vehicle_Number)",
                ReturnValues="UPDATED_NEW"
            )
            msg = "Vehicle - " + str(vehicle_id) + " is de-registered."
            result = {"message" : msg}
            logger.info(result)
            updateLocationOnMap()
            return {
                'statusCode': 204,
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(e)
            msg = "Vehicle - " + str(vehicle_id) + " is not registered."
            result = {"message" : msg}
            logger.info(result)
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }