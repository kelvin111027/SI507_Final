from bs4 import BeautifulSoup
import requests
import json
import secrets
import sqlite3

CACHE_FNAME = 'final_proj_cache.json'
header = {}
header = {"Authorization": "Bearer {}".format(secrets.yelp_api_key)}
state_dict = {'al' : 'Alabama','az' : 'Arizona','ar' : 'Arkansas','ca' : 'California','co' : 'Colorado','ct' : 'Connecticut','fl' : 'Florida','ga' : 'Georgia','id' : 'Idaho','il' : 'Illinois','in' : 'Indiana','ia' : 'Iowa','ks' : 'Kansas','ky' : 'Kentucky','la' : 'Louisiana','me' : 'Maine','md' : 'Maryland','ma' : 'Massachusetts','mi' : 'Michigan','mn' : 'Minnesota','mo' : 'Missouri','nv' : 'Nevada','nh' : 'New Hampshire','nj' : 'New Jersey','nm' : 'New Mexico','ny' : 'New York','nc' : 'North Carolina','oh' : 'Ohio','ok' : 'Oklahoma','or' : 'Oregon','pa' : 'Pennsylvania','sc' : 'South Carolina','tn' : 'Tennessee','tx' : 'Texas','ut' : 'Utah','va' : 'Virginia','wa' : 'Washington','wv' : 'West Virginia','wi' : 'Wisconsin'}

class ThemePark():
    def __init__(self, name, desc, url=None, type=None, openYear=None, size=None, attractions=0, rollerCoaster=0):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url
        self.open = openYear
        self.size = size
        self.attraction = attractions
        self.rollerCoaster = rollerCoaster

        self.address = ""
        self.city = ""
        self.state = ""
        self.lat = None
        self.lng = None
        self.imgurl = None
    def __str__(self):
        return("{}: {}\nDescription: {}\nOpen year: {}\nSize: {}\nAttractions: {}\nRoller Coasters: {}\n").format(self.type, self.name, self.description, self.open, self.size, self.attraction, self.rollerCoaster)

class NearbyHotel():
    def __init__(self, name, lat, lng, id, rating, park, address, url, distance):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.id = id
        self.rating = rating
        self.nearPark = park
        self.address = address
        self.url = url
        self.distance = distance
    def __str__(self):
        return "{}\nnear park: {}\nrating: {}\nlng: {}\nlat: {}\nid: {}".format(self.name, self.nearPark, self.rating, self.lng, self.lat, self.id)

def get_park_by_state(state_name):
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    lst = []
    formated_state_name = "_".join(state_name.split(' '))
    state_url = "https://www.ultimaterollercoaster.com/themeparks/{}/".format(formated_state_name)
    if state_url in CACHE_DICTION:
        state_html = CACHE_DICTION[state_url]
        #print("using cached data................................")
    else:
        #print("Getting new data!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        state_html = requests.get(state_url).text
        CACHE_DICTION[state_url] = state_html
    soup = BeautifulSoup(state_html, 'html.parser')
    ul_id = soup.find_all("div", class_="tpIdx")
    li_lst = ul_id[0].find_all("li")

    for i in li_lst:
        name = i.find("a").text
        city = i.find("i").text
        url_add = i.find("a")['href']
        park_url = "https://www.ultimaterollercoaster.com{}".format(url_add)
        if park_url in CACHE_DICTION:
            park_html = CACHE_DICTION[park_url]
            #print("using cached data................................")
        else:
            #print("Getting new data!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            park_html = requests.get(park_url).text
            CACHE_DICTION[park_url] = park_html
        soup_park = BeautifulSoup(park_html, "html.parser")
        #parse park description
        try:
            park_desc = soup_park.find('div', class_='tpContent')
            desc = park_desc.find('p').get_text(strip=True, separator='\n').split('\n')[0] #only use first paragraph
        except:
            desc = None

        #parse park info
        park_info_dct = {}
        park_info_raw = soup_park.find('div', class_='tpSidebar')
        park_info_lst = park_info_raw.find_all('tr')
        for row in park_info_lst:
            infoKey = row.find('th').text
            infoValue = row.find('td').text
            park_info_dct[infoKey] = infoValue
        try:
            type = park_info_dct['Park type:']
        except:
            type = None
        try:
            openYear = park_info_dct['Opening year:']
        except:
            openYear = None
        try:
            size = park_info_dct['Park size:'].split(' ')[0]
        except:
            size = None
        try:
            attractions = park_info_dct['Attractions:']
        except:
            attractions = 0
        try:
            rollerCoaster = park_info_dct['Roller Coasters:']
        except:
            rollerCoaster = 0

        #Now use parameters to create a park object
        parkX = ThemePark(name, desc, park_url, type, openYear, size, attractions, rollerCoaster)
        #Now find the address
        sidebar_children = park_info_raw.findChildren()
        h3_lst = park_info_raw.find_all('h3')
        for h in h3_lst:
            if h.text == "Park Location":
                ind = sidebar_children.index(h)
        address = sidebar_children[ind+1].get_text(strip=True, separator='\n')
        parkX.address = ", ".join(address.split('\n'))
        zipcode = parkX.address.split(' ')[-1]
        parkX.city = city
        parkX.state = state_name

        #now request lat and lon of site using yelp api
        place_search_baseurl = "https://api.yelp.com/v3/businesses/search"
        params = {'term':parkX.name, 'location':parkX.address, 'radius':1000, 'categories': 'active, All', 'limit':1}

        alphabetized_keys = sorted(params.keys())
        res = []
        uniqId = ""
        for k in alphabetized_keys:
            res.append("{}-{}".format(k, params[k]))
        uniqId = place_search_baseurl + "_".join(res)


        if uniqId in CACHE_DICTION:
            site_geo = CACHE_DICTION[uniqId]
            #print("using cached data................................")

        else:
            #print("Getting new data!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            resp = requests.get(place_search_baseurl, headers = header, params=params)
            site_geo = json.loads(resp.text)
            CACHE_DICTION[uniqId] = site_geo

        try:
            parkX.lat = site_geo['businesses'][0]['coordinates']['latitude']
            parkX.lng = site_geo['businesses'][0]['coordinates']['longitude']
            parkX.imgurl = site_geo['businesses'][0]['image_url']
        except:
            parkX.lat = site_geo['region']['center']['latitude']
            parkX.lng = site_geo['region']['center']['longitude']

        lst.append(parkX)

    dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys = True, indent = 5)
    fw = open(CACHE_FNAME, 'w')
    fw.write(dumped_json_cache)
    fw.close()
    return lst

def get_hotels_lst_for_park(park):
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    lst_nearHotels = []
    nearby_search_baseurl = "https://api.yelp.com/v3/businesses/search"
    params = {'location':park.address, 'radius':10000, 'categories':'hotels, All', 'limit':5}

    alphabetized_keys = sorted(params.keys())
    res = []
    uniqId = ""
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    uniqId = nearby_search_baseurl + "_".join(res)

    if uniqId in CACHE_DICTION:
        nearby_places = CACHE_DICTION[uniqId]
        #print("using cached data................................")

    else:
        #print("Getting new data!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        resp = requests.get(nearby_search_baseurl, headers = header, params=params)
        nearby_places = json.loads(resp.text)
        CACHE_DICTION[uniqId] = nearby_places

    nearby_print = json.dumps(nearby_places, indent = 5)
    results_lst = []
    results_lst = nearby_places['businesses']
    for h in results_lst:
        name = h['name']
        try:
            lat = h['coordinates']['latitude']
            lng = h['coordinates']['longitude']
        except:
            lat = None
            lng = None
        id = h['id']
        address = h['location']['address1']+", "+h['location']['city']+", "+h['location']['state']+", "+h['location']['zip_code']
        url = h['image_url']
        distance = h['distance']
        try:
            rating = h['rating']
        except:
            continue
        nearPark = park.name
        hotelX = NearbyHotel(name, lat, lng, id, rating, nearPark, address, url, distance)
        lst_nearHotels.append(hotelX)
    dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys = True, indent = 5)
    fw = open(CACHE_FNAME, 'w')
    fw.write(dumped_json_cache)
    fw.close()
    lst_nearHotels.sort(reverse=True, key=lambda x:x.rating) #sory by rating from top
    lst_near_ten = lst_nearHotels[:5] #only choose top 5
    return lst_near_ten


def retrieveData():
    dataset = {}
    state_dict = {'al' : 'Alabama','az' : 'Arizona','ar' : 'Arkansas','ca' : 'California','co' : 'Colorado','ct' : 'Connecticut','fl' : 'Florida','ga' : 'Georgia','id' : 'Idaho','il' : 'Illinois','in' : 'Indiana','ia' : 'Iowa','ks' : 'Kansas','ky' : 'Kentucky','la' : 'Louisiana','me' : 'Maine','md' : 'Maryland','ma' : 'Massachusetts','mi' : 'Michigan','mn' : 'Minnesota','mo' : 'Missouri','nv' : 'Nevada','nh' : 'New Hampshire','nj' : 'New Jersey','nm' : 'New Mexico','ny' : 'New York','nc' : 'North Carolina','oh' : 'Ohio','ok' : 'Oklahoma','or' : 'Oregon','pa' : 'Pennsylvania','sc' : 'South Carolina','tn' : 'Tennessee','tx' : 'Texas','ut' : 'Utah','va' : 'Virginia','wa' : 'Washington','wv' : 'West Virginia','wi' : 'Wisconsin'}
    parks_lst = [] #list of all the park object
    parks_dct = {} #key:state; value:list of parks in that state
    hotels_lst = [] #list of all the nearby hotels
    for abbr in list(state_dict.keys())[:]:
        parks_state = get_park_by_state(state_dict[abbr])
        parks_lst.extend(parks_state)
        parks_dct[abbr] = parks_state

    for pk in parks_lst:
        nearht = []
        nearht = get_hotels_lst_for_park(pk)
        hotels_lst.extend(nearht)

    dataset['parks_dct'] = parks_dct
    dataset['parks_lst'] = parks_lst
    dataset['hotels_lst'] = hotels_lst

    return dataset


def create_populate_ThemeParks(dataset):
    conn = sqlite3.connect('themePark.db')
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'ThemeParks';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'ThemeParks'(
            'park_id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'type' TEXT,
            'park_name' TEXT,
            'open_year' INTEGER,
            'size(acre)' INTEGER,
            'attraction' INTEGER,
            'roller_coaster' INTEGER,
            'address' TEXT,
            'city' TEXT,
            'state' TEXT,
            'description' TEXT,
            'latitude' REAL,
            'longitutde' REAL,
            'image_url' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    for p in dataset['parks_lst']:
        insertion = (None, p.type, p.name, p.open, p.size, p.attraction, p.rollerCoaster, p.address, p.city, p.state, p.description, p.lat, p.lng, p.imgurl)
        statement = 'INSERT INTO "ThemeParks"'
        statement += 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        cur.execute(statement, insertion)
    conn.commit()
    conn.close()

def create_populate_Hotels(dataset):
    conn = sqlite3.connect('themePark.db')
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Hotels';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Hotels'(
            'hotel_id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'hotel_name' TEXT,
            'rating' REAL,
            'park_id' INTEGER,
            'latitude' REAL,
            'longitude' REAL,
            'address' TEXT,
            'distance' INTEGER,
            'image_url' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()

    for h in dataset['hotels_lst']:
        querry = 'SELECT park_id FROM ThemeParks WHERE park_name = ?'
        cur.execute(querry, (h.nearPark,))
        parkId = cur.fetchone()[0]
        insertion = (None, h.name, h.rating, parkId, h.lat, h.lng, h.address, round(h.distance), h.url)
        statement = 'INSERT INTO "Hotels"'
        statement += 'VALUES (?,?,?,?,?,?,?,?,?)'
        cur.execute(statement, insertion)
    conn.commit()
    conn.close()


def main():
    #pass
    dset = {}
    dset = retrieveData()
    create_populate_ThemeParks(dset)
    create_populate_Hotels(dset)

#main()
