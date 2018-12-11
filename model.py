import json
import sqlite3
import finalProject as final
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import secrets

plotly.tools.set_credentials_file(username=secrets.PLOTLY_USERNAME, api_key=secrets.PLOTLY_API_KEY)
DBNAME = 'themePark.db'
states = []

def init_states():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    global states
    stm = 'SELECT state, count(*), MAX(roller_coaster), MAX(attraction) '
    stm += 'FROM ThemeParks GROUP BY state ORDER BY count(*) DESC'
    cur.execute(stm)
    states = cur.fetchall()
    conn.close()


def sort_states(sortby='number of park', sortorder='desc'):
    if sortby == 'number of park':
        sortcol = 1
    elif sortby == 'most rollercoasters':
        sortcol = 2
    elif sortby == 'most attractions':
        sortcol = 3
    else:
        sortcol = 0
    rev = (sortorder == 'desc')
    sorted_states = sorted(states, key=lambda row: row[sortcol], reverse=rev)
    return sorted_states

def get_instate(state_chosen):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stm = 'SELECT * from ThemeParks WHERE state = ?'
    cur.execute(stm, (state_chosen,))
    parks_instate = []
    parks_instate = cur.fetchall()
    conn.close()
    return parks_instate

def get_hotel(parkName):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stm = 'SELECT * from Hotels as h JOIN ThemeParks as t '
    stm += 'ON t.park_id = h.park_id WHERE t.park_name = ?'
    cur.execute(stm, (parkName,))
    hotels = []
    hotels = cur.fetchall()
    conn.close()
    return hotels

def statemap(state):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stm = 'SELECT * from ThemeParks WHERE state = ?'
    cur.execute(stm, (state,))
    parks_instate = []
    parks_instate = cur.fetchall()
    conn.close()

    lat_vals = []
    lon_vals = []
    text_vals = []
    for park in parks_instate:
        lat_vals.append(park[11])
        lon_vals.append(park[12])
        text_vals.append(park[2]+'<br>attraction: '+str(park[5])+'<br>rollercoaster: '+str(park[6])+'<br>address: '+park[7])

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000
    for lat in lat_vals:
        v = float(lat)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for lon in lon_vals:
        v = float(lon)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v
    lat_axis = [min_lat - 1, max_lat + 1]
    lon_axis = [min_lon - 1, max_lon + 1]
    center_lat = (max_lat + min_lat)/2
    center_lon = (max_lon + min_lon)/2
    '''
    data = [ dict(
        type = 'scattermapbox',
        lon = lon_vals,
        lat = lat_vals,
        text = text_vals,
        mode = 'markers',
        marker = dict(size = 10, symbol='star', color="rgb(255,165,0)"),
        )
    ]'''
    data = [dict(
        type='scattermapbox',
        lat=lat_vals,
        lon=lon_vals,
        mode='markers',
        marker=dict(
            size=16,
            #symbol = 'star',
            color='rgb(255, 33, 107)',
            opacity=0.85
        ),
        text=text_vals,
        hoverinfo='text'
    )]

    layout = dict(
        title = 'Theme parks in {}<br>(Hover for info)'.format(state),
        autosize = True,
        showlegend = False,

        mapbox = dict(
            accesstoken = secrets.MAPBOX_TOKEN,
            bearing = 0,
            center = dict(
                lat = center_lat,
                lon = center_lon
            ),
            pitch = 0,
            zoom = 6.5
        ),
    )
    fig = dict(data=data, layout=layout)
    py.plot(fig, validate=False, filename='mapbox-{}-photos'.format(state))

def lodgemap(park_name):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stm = 'SELECT * from ThemeParks WHERE park_name = ?'
    cur.execute(stm, (park_name,))
    park = []
    park = cur.fetchall()[0]
    stm2 = 'SELECT * from Hotels as h JOIN ThemeParks as t ON '
    stm2 += 't.park_id = h.park_id WHERE t.park_name = ?'
    cur.execute(stm2, (park_name,))
    hotel_lst = cur.fetchall()
    conn.close()

    park_lat_vals = []
    park_lon_vals = []
    park_text_vals = []
    park_lat_vals.append(park[11])
    park_lon_vals.append(park[12])
    park_text_vals.append(park[2]+'<br>attraction: '+str(park[5])+'<br>rollercoaster: '+str(park[6])+'<br>address: '+park[7])


    lat_vals = []
    lon_vals = []
    text_vals = []
    for hotel in hotel_lst:
        lat_vals.append(hotel[4])
        lon_vals.append(hotel[5])
        text_vals.append(hotel[1]+'<br>rating: '+str(hotel[2])+'<br>address: '+hotel[6]+'<br>distance: '+str(hotel[7]))

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000
    for lat in lat_vals:
        v = float(lat)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for lon in lon_vals:
        v = float(lon)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v
    lat_axis = [min_lat - 1, max_lat + 1]
    lon_axis = [min_lon - 1, max_lon + 1]
    center_lat = (max_lat + min_lat)/2
    center_lon = (max_lon + min_lon)/2

    park_data = dict(
        type='scattermapbox',
        lat=park_lat_vals,
        lon=park_lon_vals,
        mode='markers',
        marker=dict(
            size=18,
            #symbol = 'star',
            color='rgb(255, 33, 107)',
            opacity=0.85
        ),
        text=park_text_vals,
        hoverinfo='text'
    )
    hotel_data = dict(
        type='scattermapbox',
        lat=lat_vals,
        lon=lon_vals,
        mode='markers',
        marker=dict(
            size=16,
            #symbol = 'star',
            color='rgb(0, 160, 105)',
            opacity=0.95
        ),
        text=text_vals,
        hoverinfo='text'
    )
    data = [park_data, hotel_data]

    layout = dict(
        title = 'Hotels near {}<br>(Hover for info)'.format(park_name),
        autosize = True,
        showlegend = False,

        mapbox = dict(
            accesstoken = secrets.MAPBOX_TOKEN,
            bearing = 0,
            center = dict(
                lat = center_lat,
                lon = center_lon
            ),
            pitch = 0,
            zoom = 12
        ),
    )
    fig = dict(data=data, layout=layout)
    py.plot(fig, validate=False, filename='mapbox-hotels-near-{}'.format(park_name))

def rcRanking():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stm = 'SELECT state, SUM(roller_coaster) FROM ThemeParks '
    stm += 'GROUP BY state ORDER BY SUM(roller_coaster) DESC'
    cur.execute(stm)
    rlrank_lst = []
    rlrank_lst = cur.fetchall()
    conn.close()
    x_lst = []
    y_lst = []
    for record in rlrank_lst:
        x_lst.append(record[0])
        y_lst.append(record[1])
    data = [go.Bar(
                x=x_lst,
                y=y_lst
        )]
    layout = go.Layout(
        title='Number of Rollercoaster by State'
    )
    fig=go.Figure(data=data, layout=layout)
    py.plot(data, filename='basic-bar')

def pieChart():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stm = 'SELECT type, count(*) FROM ThemeParks '
    stm += 'GROUP BY type ORDER BY count(*) DESC'
    cur.execute(stm)
    results_lst = cur.fetchall()
    conn.close()
    labels = []
    values = []
    for t in results_lst:
        labels.append(t[0])
        values.append(t[1])
    trace = go.Pie(labels=labels, values=values)
    py.plot([trace], filename='basic_pie_chart')

#rcRanking()
#lodgemap("Donley's Wild West Town")
