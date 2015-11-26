'''
Helpers functions used by main view controller
'''

import urllib2
import json
from crawler import crawler

def getEventsByDay(start_date, end_date):
    return crawler(start_date, end_date)

'''
given an array of location, make request to Google API and translate
them into longitude and latitude
'''
def getGeoInfo(locations):
    baseURL = "https://maps.googleapis.com/maps/api/geocode/json?address="
    res = []
    for loc in locations:
        url = baseURL + "Georgia%20Tech," + loc
        url = url.replace(" ", "%20")
        raw = urllib2.urlopen(url)
        raw = raw.read()
        resp = json.loads(raw)
        if len(resp["results"]) > 0:
            res.append(resp["results"][0]["geometry"]["location"])
    print res
    return res
