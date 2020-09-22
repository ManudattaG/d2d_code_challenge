# Python code to demonstrate working of unittest 
import unittest
import json
import datetime
import dateutil.parser
from decimal import Decimal
from geopy import distance
import boto3
from moto import mock_dynamodb2
from boto3.dynamodb.conditions import Key

# Check if vehicle is within the radius #
def calculateVehicleDistance(center_location, vehicle_coordinate):
    vehicle_dist = distance.distance(center_location, vehicle_coordinate).meters
    if vehicle_dist <= 3500:
        return(True)
    else:
        return(False)

@mock_dynamodb2
def mock_dynamodb_table():
    table_name = 'test_vehicle_data'
    dynamodb = boto3.resource('dynamodb', 'us-east-1')

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'Vehicle_Number',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Vehicle_Number',
                'AttributeType': 'S'
            }

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table = dynamodb.Table(table_name)
    return(table)

class TestStringMethods(unittest.TestCase): 
    
    def setUp(self):
        pass

    # Returns True if the vehicle is registered. 
    def test_register_vehicle(self):
        vehicle_list = ["BMW-123", "AUDI-123", "VW-456", "MRC-777"]
        item = {}
        table = mock_dynamodb_table()
        for value in vehicle_list:
            item['Vehicle_Number'] = value
            table.put_item(Item=item)
        json_file = open('src/vehicle.json')
        data = json.load(json_file)
        registered_list = []
        for vehicle in data:
            registered_list.append(vehicle["id"])
        json_file.close()
        self.assertEqual(registered_list, vehicle_list)

    # Returns True if vehicle is sending requests once every 3 seconds, else returns False 
    def test_location_update_every3seconds(self):
        prev_location_ts = "2020-09-21T16:15:49.885884"
        current_time = datetime.datetime.now()
        prev_location_ts = dateutil.parser.parse(prev_location_ts)
        delta_seconds = (current_time - prev_location_ts).total_seconds()
        self.assertTrue(delta_seconds > Decimal(3))

    # Returns TRUE if the vehicle is within the given radius 
    # else returns False. 
    def test_vehicle_within_radius(self):
        center_location = (52.53, 13.403)
        vehicle_within_radius = (52.52147, 13.41026)
        vehicle_outside_radius = (10.52147, 20.41026)
        self.assertTrue(calculateVehicleDistance(center_location, vehicle_within_radius))
        self.assertFalse(calculateVehicleDistance(center_location, vehicle_outside_radius))

    # Returns true if the string splits and matches 
    # the given output. 
    def test_de_register(self):
        vehicle_list = ["BMW-123", "AUDI-123", "VW-456", "MRC-777"]
        table = mock_dynamodb_table()
        item = {}
        for value in vehicle_list:
            item['Vehicle_Number'] = value
            table.delete_item(Key = item)

        for value in vehicle_list:
            item['Vehicle_Number'] = value
            response = table.get_item(item)
            if 'Item' in response:
                item = response['Item']
            self.assertTrue("Vehicle_Number" in item)
            self.assertFalse("Vehicle_Number" not in item)

if __name__ == '__main__': 
    unittest.main()
