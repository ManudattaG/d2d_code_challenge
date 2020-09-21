import json
import string
import random
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    print(event)
    vehicle_id = event["queryStringParameters"]["id"]
    print(vehicle_id)
    # Store vehicle data in the DB #
    table = dynamodb.Table('Vehicle_Tracker')
    item = {"Vehicle_Number" : str(vehicle_id), "Registered": "True"}
    print(item)
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
        print(result)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        print(e)
        msg = "Vehicle - " + str(vehicle_id) + " is not registered."
        result = {"message" : msg}
        print(result)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
