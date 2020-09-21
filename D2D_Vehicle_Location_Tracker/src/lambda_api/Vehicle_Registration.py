import json
import string
import random
import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    print(event)
    api_body = event["body"]
    api_body = json.loads(api_body)
    print(api_body)
    vehicle_id = api_body["id"]
    # Store vehicle data in the DB #
    table = dynamodb.Table('Vehicle_Tracker')
    item = {"Vehicle_Number" : str(vehicle_id), "Registered": "True"}
    
    try:
        response = table.put_item(Item = item)
        msg = "Vehicle - " + str(vehicle_id) + " is registered."
        result = {"message" : msg}
        print(result)
        return {
            'statusCode': 204,
            'body': json.dumps(result)
        }
    except Exception as e:
        print(e)
        msg = "Unable to register the vehicle due to DB insert error." + str(vehicle_id)
        result = {"message" : msg}
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
