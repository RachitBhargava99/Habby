# Eventster
Welcome to Eventster - time to see only the events you love, only the ones around you!

This is the supporting API for the main application and must not be confused with the client module.

Below mentioned are the endpoints that can be publicly called to get information or feed in the required information.

## Endpoints
### <pre>/test              GET</pre>
Checker to see if the server is up and running
<hr>

### <pre>/search            POST</pre>
Accepts up to three categories that the user wants to search events in.
Optional parameters:
page_number (defaults to 1)
zip_code
loc_radius (required with zip_code) - Specifies the radius of search from given location
Return Format: Status (Int), List of Maps (each map representing an event), Current Page Number (Int),
Last Page of Result - Maximum Number of Pages in Result (Int)
Event Info Dictionary Format:
<code>{
    'id': Int,
    'image': String,
    'name': String,
    'description': String,
    'start_date': String,
    'start_month': String
}</code>
<hr>

### <pre>/cat/list          GET</pre>
Returns a list of categories accepted by Eventbrite along with their Eventbrite ID's
Return Format: Status (Int), List of Maps (each map representing a category)
Category Info Dictionary Format:
<code>{
   'id': Int),
   'name': String
}</code>
<hr>

### <pre>/event/<local_id>  GET</pre>
Returns details of the event based on the local ID provided
Return Format: Status and (Error / Event Info)
Event Info Map Format:
<code>{
    'name': String,
    'small_text': String,
    'eb_url': String,
    'description': String,
    'lat': Float,
    'lng': Float,
    'address': String
}</code>
<hr>

## Google App Engine Requirements
This server was initially built to be deployed using Google App Engine.
As a result, there are several environment variables that were added to a <code>app.yaml</code> file.
Here are some that you might need to add while deploying this.
Also, please note that several are required for adding Google Cloud SQL support.
You may remove them if you are planning to use a different database.

<pre>
PROJECT_ID: enter_project_id
DATA_BACKEND: 'cloudsql'
CLOUDSQL_USER: enter_username
CLOUDSQL_PASSWORD: enter_password
CLOUDSQL_DATABASE: enter_database_name
CLOUDSQL_CONNECTION_NAME: enter_connection_name
EVENTBRITE_OAUTH_TOKEN: enter_eventbrite_oauth_token
</pre>
<hr>

## Contact Info
In case of any queries, please feel free to contact Rachit Bhargava (developer) at rachitbhargava99@gmail.com.

## Third-Party Use
This application cannot be used for any unauthorized uses.
If you are interested in using the application for any purposes, please contact the developer for permissions.