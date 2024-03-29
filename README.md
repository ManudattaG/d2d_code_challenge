# Visualize Vehicle Real-Time Locations #

Problem Statement:
------------------------------------------------------------------------------------
door2door service collects the live position of all vehicles in its fleet in real-time via a GPS sensor in each vehicle. To manage the service, door2door needs to be able to visualize the location and bearing of all vehicles in real-time.


Approach:
------------------------------------------------------------------------------------

* Create an API to register a vehicle
* Create an API to collect vehicle location details
* Create an API to de-register a vehicle
* Store and update vehicle data in a database table
* Call the endpoint to register the vehicle
* Call the endpoint to start updating vehicle location data
* Plot the location coordinates on a map for the visualization
* Derive the routes by calling update enpoint for updating vehicle location data
* Call the endpoint to de-register the vehicle after the destination is reached
* Test the solution with vehicle.json file which contains all the vehicle location data
* Visualize the cluster map with vehicle locations


Tech Stack:
------------------------------------------------------------------------------------

1. Python 3.7
2. AWS


Solution:
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
    
    
Architecture Diagram
--------------------------------------------------------------------------------------

![Alt text](/D2D_Vehicle_Location_API/architecture_diagram.png?raw=true "Architecture Diagram")
    
    
Project Structure:
--------------------------------------------------------------------------------------

1. lambda_function.py -- _Main function for "D2D_Vehicle_Location_API" workflow_
2. requirements.txt -- _Requirements file which contains the project dependencies_
3. api_creds.yml -- _API key credentials to call REST APIs_
4. vehicle_data.csv -- _An extract of Vehicle's valid position data stored in DynamoDB table for future analysis_


Pre requisites:
---------------------------------------------------------------------------------------

* Python 3.7 or Python 3.8
* AWS Lambda with Layers
* Amazon API Gateway
* Amazon DynamoDB
* Amazon S3

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

Visualize the location of all the vehicles on a map (in any browser) by clicking the below web URL.

URL --> https://vehicle-visual-map.s3.amazonaws.com/map/visual_map.html

** NOTE: To register a new vehicle and start sending location updates, call the REST endpoints and view the result by clicking on the same website URL **

PS: DEMO screenshots available in D2D_Vehicle_Location_API/README.md


Libraries Used:
---------------------------------------------------------------------------------------

1. _folium_ -- A python package for visualizing maps that makes it easy to visualize data that's been manipulated in Python on an interactive leaflet map. It enables both the binding of data to a map for choropleth visualizations as well as passing rich vector/raster/HTML visualizations as markers on the map.

2. _requests_ -- A python package to call REST APIs securely and easily

3. _geopy_ -- A python client for several popular geocoding web services which makes it easy to locate the coordinates of addresses, cities, countries, and landmarks across the globe using third-party geocoders and other data sources.

4. _boto3_ -- An AWS SDK Client used to call different AWS resources via APIs

5. _unittest_ -- An unit test library used to mock test scenarios and validate assertions

6. _moto_ -- A mocking framework used in test functions to mock AWS resources such as DynamoDB, S3 etc..


Overview of "D2D_Vehicle_Location_Tracker" Workflow:
------------------------------------------------------------------------------------

1. Register API (POST /vehicles)
    * Registers a vehicle and stores in DynamoDB table with the registered status set to "True"
    * This vehicle is eligible to start emitting location updates
    
2. Location Update API (POST /vehicles/:id/locations)
    * Updates the location on map until the destination is reached (nodes provided in vehicle.json file)
    * Gets the nodes to update each step from the JSON file
    * Calculates vehicle's distance if it is within 3.5km radius (as per requirement)
    * Plots all the nodes and forms a cluster within the boundaries
    * Saves the map in an HTML file for the visualization
    
3. De-Register API (DELETE /vehicles/:id)
    * De-Register's the vehicle and the registered status is set to "False" in DynamoDB table
    * Map is updated by removing the de-registered vehicle from the plot
    * Saves the updated map in an HTML file for the visualization
    
    
Architecture Diagram
--------------------------------------------------------------------------------------

![Alt text](/D2D_Vehicle_Location_Tracker/src/architecture_diagram.png)
    
    
Project Structure:
--------------------------------------------------------------------------------------

1. src/main.py -- _Main function for "D2D_Vehicle_Location_Tracker" workflow_
2. src/vehicle_location_mapping.py -- _Function which updates the vehicle's location by calculating the distance_
3. src/api_url.py -- _File which contains all the endpoints_
4. src/load_json_file.py -- _Generic file which loads JSON file and returns the data_
5. src/vehicle.json -- _JSON file which contains vehicle data_
6. src/visual_map.html -- _HTML file for the map visualization_
7. src/tests/vehicle_location_test.py -- _Test file where all the unit test cases related to the project are written_
8. src/lambda_api/Vehicle_Registration.py -- _API lambda to register the vehicle_
9. src/lambda_api/Vehicle_Location_Update.py -- _API lambda to update the location coordinates of the vehicle_
10. src/lambda_api/Vehicle_DeRegistration.py -- _API lambda to de-register the vehicle_
11. src/screenshots -- _Screenshots of the visual map_
12. src/requirements.txt -- _Requirements file which contains the project dependencies_


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

To visualize all the vehicle nodes as a cluster within the city boundaries on a map, run "main.py" file and open "visual_map.html" to view the result

PS: DEMO screenshots available in D2D_Vehicle_Location_Tracker/src/screenshots/README.md
