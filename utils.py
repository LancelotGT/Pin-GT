'''
Helpers functions used by main view controller
'''

import urllib2
import json, math
from crawler import crawler

def getEventsByDay(start_date, end_date, tag):
    results = crawler(start_date, end_date)
    if tag == 'all':
        return results
    entries = [e for e in results if tag in e['Tag']]
    return entries

'''
given an array of location, make request to Google API and translate
them into longitude and latitude
'''
def processGeoInfo(entries):
    baseURL = "https://maps.googleapis.com/maps/api/geocode/json?address="
    l = []
    for entry in entries:
        loc = entry['Location']
        url = baseURL + "Georgia%20Tech,%20" + loc
        url = url.replace(" ", "%20")
        raw = urllib2.urlopen(url)
        raw = raw.read()
        resp = json.loads(raw)
        if len(resp["results"]) > 0:
            entry['latlon'] = resp["results"][0]["geometry"]["location"]
            ndigit = 7
            entry['latlon']['lat'] = round(entry['latlon']['lat'], ndigit)
            entry['latlon']['lng'] = round(entry['latlon']['lng'], ndigit)
            l.append(entry)
    return l