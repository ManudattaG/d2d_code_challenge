# Vehicle GPS Location Tracking

Overview:
------------------------------------------------------------------------------------

This software will register all the vehicles, collects the live position and updates the location to the system and also de-registers the vehicle as and when the location updates are completed. The solution of this software is expected to visualize all the registered vehicle's real-time location data on Google Maps.

There are 2 types of solutions in this repository:
1. Module --> "D2D_Vehicle_Location_API"
2. Module --> "D2D_Vehicle_Location_Tracker"

Overview of "D2D_Vehicle_Location_API" Workflow:
------------------------------------------------------------------------------------

1. Register API (POST /vehicles)
    * Registers a vehicle and stores in DynamoDB table with the registered status set to "True"
    * This vehicle is eligible to start emitting location updates
    
2. Location Update API (POST /vehicles/:id/locations)
    * Checks if vehicle is registered to send location updates
    * If registered, it verifies if the vehicle is sending updates no more than once every 3secs
    * If registered and the requests are once every 3secs, then vehicle latitude, longitude coordinates are stored in DynamoDB table
    * It plots the map according to the coordinates of the vehicle
    * Saves the map in an S3 bucket for the visualization
    
3. De-Register API (DELETE /vehicles/:id)
    * De-Register's the vehicle and the registered status is set to "False" in DynamoDB table
    * Map is updated by removing the de-registered vehicle from the plot
    * Saves the updated map in S3 bucket for the visualization
    
    
Project Structure:
--------------------------------------------------------------------------------------

1. _lambda_function.py_ -- Main function for "D2D_Vehicle_Location_API" workflow
2. _requirements.txt_ -- Requirements file which contains the dependencies
3. _api_creds.yml_ -- API key credentials to call REST APIs


Pre requisites:
---------------------------------------------------------------------------------------

* Python 3.7
* AWS Lambda with Layers
* Amazon API Gateway
* Amazon DynamoDB
* Amazon S3 Bucket

REST API endpoints:
---------------------------------------------------------------------------------------

1. Register -- https://03fc0pnobj.execute-api.us-east-1.amazonaws.com/visualize-location/vehicles (POST)
2. Location Update -- https://03fc0pnobj.execute-api.us-east-1.amazonaws.com/visualize-location/vehicles/{id}/locations (POST)
3. De-Register -- https://03fc0pnobj.execute-api.us-east-1.amazonaws.com/visualize-location/vehicles/{id} (DELETE)
  
  
DynamoDB table structure:
---------------------------------------------------------------------------------------

* Table Name - Vehicle_Data
* Primary Key - Vehicle_Number
* Attributes - latitude, longitude, Registered, requested_ts, timestamp


Solution:
---------------------------------------------------------------------------------------

Visualize all the vehicles on a map (in browser) which are registered and sent the location updates to the system
URL --> https://vehicle-visual-map.s3.amazonaws.com/map/visual_map.html

** NOTE: To register a new vehicle and start sending location updates, call the REST endpoints and view the result by clicking the above URL **

PS: DEMO screenshots available in demo.md file


Overview of "D2D_Vehicle_Location_Tracker" Workflow:
------------------------------------------------------------------------------------

1. Register API (POST /vehicles)
    * Registers a vehicle and stores in DynamoDB table with the registered status set to "True"
    * This vehicle is eligible to start emitting location updates
    
2. Location Update API (POST /vehicles/:id/locations)
    * Updates the location on map until the destination is reached (nodes provides in vehicle.json file)
    * Gets the nodes to update each step from the JSON file
    * Calculates vehicle's distance if it is within 3.5km radius (as per requirement)
    * Plots all the nodes and forms a cluster within the boundaries
    * Saves the map in an HTML file for the visualization
    
3. De-Register API (DELETE /vehicles/:id)
    * De-Register's the vehicle and the registered status is set to "False" in DynamoDB table
    * Map is updated by removing the de-registered vehicle from the plot
    * Saves the updated map in S3 bucket for the visualization
    
    
Project Structure:
--------------------------------------------------------------------------------------

1. _src/main.py_ -- Main function for "D2D_Vehicle_Location_API" workflow
2. _src/vehicle_location_mapping.py_ -- Function which updates the vehicle's location by calculating the distance
3. _src/api_url.py_ -- File which contains all the endpoints
4. _src/load_json_file_ -- Generic file which loads JSON file and returns the data
5. _src/vehicle.json_ -- JSON file which contains vehicle data
6. _src/visual_map.html_ -- HTML file for the map visualization


Pre requisites:
---------------------------------------------------------------------------------------

* Python 3.7 or Python 3.8
* AWS Lambda
* Amazon API Gateway
* Amazon DynamoDB

REST API endpoints:
---------------------------------------------------------------------------------------

1. Register -- https://vpoe02xgyh.execute-api.us-east-1.amazonaws.com/dev/vehicles (POST)
2. Location Update -- https://hgge3eylqg.execute-api.us-east-1.amazonaws.com/dev/vehicles (POST)
3. De-Register -- https://245um5jz9c.execute-api.us-east-1.amazonaws.com/dev/vehicles(DELETE)
  
  
DynamoDB table structure:
---------------------------------------------------------------------------------------

* Table Name - Vehicle_Tracker
* Primary Key - Vehicle_Number
* Attributes - latitude, longitude, Registered, requested_ts, timestamp


Solution:
---------------------------------------------------------------------------------------

Visualize all the vehicle nodes as a cluster on a map
Clone the module from the repo and run "visual_map.html" to view the result

PS: DEMO screenshots available in demo.md file
