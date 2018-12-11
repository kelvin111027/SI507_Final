# 507 Final Project: Theme Park Base


## Data Source Used:

### Ultimate Rollercoaster website
- https://www.ultimaterollercoaster.com/
- The program collects the data of theme parks across the States,  crawl and scrape all the links of difference states and parks on this site.
- There are two levels for crawling and scraping, the state level and park level.

### Yelp Fusion
- Documentation of Yelp Fusion Business Search: https://www.yelp.com/developers/documentation/v3/business_search
- Yelp API key is required, please refer to: https://www.yelp.com/developers/documentation/v3/authentication
- This program uses Yelp Fusion to search for the coordinates of parks searched from ultimate rollercoaster and base of that, search for nearby lodges' data.

### Plotly
- http://plot.ly/
- Instructions on signing up, acquirng api key and installation: https://plot.ly/python/getting-started/
- Documentation of Plotly python open source graphing library: https://plot.ly/python/
- In python file, after import plotly, set up the credentials using:
    plotly.tools.set_credentials_file(username=<USERNAME>, api_key=<APIKEY>)
- This program use Plotly as visualization tool to map the data and create charts.

### Mapbox
- https://www.mapbox.com/
- Mapbox used combined with Plotly to create maps.
- MAPBOX_TOKEN required. Please refer to https://www.mapbox.com/help/how-to-use-mapbox-securely/


## Program's Structure

- The program used web crawling and scraping as well as Yelp API to collect data then populate a database.
- The processing and interation part of the program is implemented with Flask and Model View Controller (MVC) framework.
- The finalProject.py is responsible for collecting, organizing and caching data as well as building database
- The app.py is the controller file, which sets up routes and logic of the main program.
- The model.py is the file handling data retrieval from database and containing a set of functions created for processing data.
- The html files in templates folder are the View part of the program, which decides how the interface looks like.
- A file called "secrets.py" is needed which has all the api keys and token needed.

### Functions & Classes
**retrieveData()**
- This function execute web crawling, scraping and Yelp API calling.

**sort_states(sortby='number of park', sortorder='desc')**
- This function take the user choice and sort the main table in the program accordingly

**statemap()**
**lodgemap()**
- These functions call for required data from database then visualize it

**Class_Definitions**
ThemePark()
NearbyHotel()
- These classes were initiazed to organize the raw data before building the database


## User Guide

- Download files
  First for this repository, download all the files and foler  
- Set up secrets.py
  Acquire all the keys required following previous links. Put them in a python fil named "secrets", below is a sample secrets.py content, same format should be followed:
        yelp_api_key = <yelp_api_key>
        PLOTLY_USERNAME = <plotly_username>
        PLOTLY_API_KEY = <plotly_api_key>
        MAPBOX_TOKEN = <map_box_token>
- Set up virtual environment
  Use requirements.txt to set up an environment including packages needed, then activate it.
- Build database
  Open finalProject.py, uncomment line333, run it.
- Run the Program
  After the database (themePark.db) is built, comment out the line333 in finalProject.py, then execute app.py, open the url returned from the terminal or gitbash (whatever is used) in the browser. That's it!
- Enjoy playing with it :)
  Follow the prompt on the interface to choose presentation options.
- Kind reminder
  If using a free plotly account, it's suggested to remove the needless graphs in account regularly (log in first), if the number of files exceeded the limit, the mapping and graphing functions of this program could be down.
