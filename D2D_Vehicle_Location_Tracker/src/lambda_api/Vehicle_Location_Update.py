import json
import string
import random
import boto3
import datetime
import dateutil.parser
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
vehicle_table = dynamodb.Table('Vehicle_Tracker')

def getItemFromVehicleDB(vehicle_id):
    print("Querying Vehicle DB")
    try:
        response = vehicle_table.get_item(
            Key={ "Vehicle_Number" : str(vehicle_id) }
        )
        print(response)
        if "Item" in response and 'requested_ts' in response["Item"]:
            prev_location_ts = response['Item']['requested_ts']
            return(prev_location_ts)
        else:
            return(None)
    except Exception as e:
        print(e)
        return(None)

def lambda_handler(event, context):
    current_time = datetime.datetime.now()
    print(event)
    api_body = event["body"]
    api_body = json.loads(api_body)
    print(api_body)
    vehicle_id = event["queryStringParameters"]["id"]
    print(vehicle_id)
    # Get vehicle timestamp if already registered #
    prev_location_ts = getItemFromVehicleDB(vehicle_id)
    if(prev_location_ts != None):
        prev_location_ts = dateutil.parser.parse(prev_location_ts)
        print("Converted prev_location_ts")
        print(prev_location_ts)
        print("Current requested time")
        print(current_time)
        print("Get total seconds from 2 date formats")
        delta_seconds = (current_time - prev_location_ts).total_seconds()
        print(delta_seconds)
        print(type(delta_seconds))
        # Check if the requests are coming once in every 3 seconds #
        if(delta_seconds < Decimal(3)):
            msg = "Vehicle location can only be updated once every 3 seconds."
            result = {"message" : msg}
            print(result)
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
    
    # Get latitude, logitude and timestamp data #
    latitude = api_body["lat"]
    longitude = api_body["lng"]
    timestamp = api_body["at"]
    
    # Store vehicle data in Vehicle DB #
    try:
        response = vehicle_table.update_item(
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
        print(response)
        msg = "Vehicle - " + str(vehicle_id) + " location is updated."
        result = {"message" : msg}
        print(result)
        return {
            'statusCode': 204,
            'body': json.dumps(result)
        }
    except Exception as e:
        print(e)
        msg = "Vehicle - " + str(vehicle_id) + " is not registered to update the location."
        result = {"message" : msg}
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }