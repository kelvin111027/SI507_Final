import unittest
from finalProject import *
from model import *
import random

class TestPlaceSearch(unittest.TestCase):
    def setUp(self):
        self.ca_park_lst = get_park_by_state("california")
    def test_park_search(self):
        #park_ca = get_park_by_state("california")
        index = random.randrange(0,len(self.ca_park_lst))
        parkContainer = []
        for park in self.ca_park_lst:
            if park.name == "Pacific Park":
                parkContainer.append(park)

        self.assertEqual(len(parkContainer),1)
        self.assertNotEqual(len(parkContainer[0].address),0)
        self.assertIsNotNone(self.ca_park_lst[index].lat)
        self.assertIsNotNone(self.ca_park_lst[index].lng)

    def test_hotel_search(self):
        hotel_lst = []
        for park in self.ca_park_lst:
            if park.name == "Pacific Park":
                hotel_lst = get_hotels_lst_for_park(park)
        found = False
        try:
            for h in hotel_lst:
                if h.name == "Loews Santa Monica":
                    found = True
        except:
            self.fail()

        coorNotFound = False
        for h in hotel_lst:
            if h.lat == None or h.lng == None:
                coorNotFound = True

        self.assertFalse(coorNotFound)
        self.assertTrue(found)
        self.assertTrue(len(hotel_lst)<=5 and len(hotel_lst)!=0) #

class TestDatabase(unittest.TestCase):
    def test_ThemeParks_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT park_name FROM ThemeParks'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('EPCOT',), result_list)
        self.assertEqual(len(result_list), 252)
        sql = 'SELECT type, park_name, city, state FROM '
        sql += 'ThemeParks WHERE state="Maryland" ORDER BY park_id'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 6)
        self.assertEqual(result_list[1][2], "West Ocean City")
        conn.close()

    def test_Hotels_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT hotel_name FROM Hotels'
        results = cur.execute(sql)
        results_lst = results.fetchall()
        self.assertEqual(len(results_lst),1182)
        self.assertIn(("Cedar Point's Express Hotel",), results_lst)
        sql = 'SELECT hotel_name, rating FROM Hotels WHERE park_id = '
        sql += '"220" ORDER BY hotel_id'
        results = cur.execute(sql)
        results_lst = results.fetchall()
        self.assertEqual(len(results_lst),5)
        self.assertEqual(results_lst[0][1], 4.0)
        conn.close()

    def test_table_join(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT park_name FROM ThemeParks as t JOIN Hotels as h '
        sql += 'ON t.park_id = h.park_id WHERE h.hotel_name = '
        sql += '"Holiday Inn Express & Suites Minneapolis Sw - Shakopee"'
        cur.execute(sql)
        results_lst = cur.fetchall()
        self.assertEqual(results_lst[0][0], "Valleyfair")
        conn.close()

    def test_table_search(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        stm = 'SELECT state, count(*), MAX(roller_coaster), MAX(attraction) '
        stm += 'FROM ThemeParks GROUP BY state ORDER BY count(*) DESC'
        cur.execute(stm)
        states = cur.fetchall()
        self.assertEqual(states[4][1], 15)
        self.assertEqual(states[-1][2], 3)
        self.assertEqual(states[10][3], 25)
        stm = 'SELECT * from Hotels as h JOIN ThemeParks as t '
        stm += 'ON t.park_id = h.park_id WHERE t.park_name = "Worlds of Fun"'
        cur.execute(stm)
        hotels = cur.fetchall()
        self.assertEqual(hotels[0][7], 8227)
        cur.close()

class TestMapping(unittest.TestCase):
    def test_show_state_map(self):
        try:
            statemap('Florida')
        except:
            self.fail()
    def test_show_lodge_map(self):
        try:
            lodgemap('Cedar Point')
        except:
            self.fail()


unittest.main()
