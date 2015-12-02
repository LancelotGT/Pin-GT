__author__ = 'Grueo'
import googlemaps
import calendar
import urllib
import urllib2
import json
import re
import pandas as pd
import sys
from database import add_event
reload(sys)
sys.setdefaultencoding('utf-8')

def processGeoInfo(entries):
    baseURL = "https://maps.googleapis.com/maps/api/geocode/json?address="
    l = []
    for entry in entries:
        loc = entry['Location']
        if len(loc) == 0: # drop the event if no location provided
            continue
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

def crawler(start_date,end_date):
    day_list=pd.date_range(start_date, end_date)[1:]
    Activity=[]

    for day in day_list:
        thisurl = "http://www.calendar.gatech.edu/events/day/"+day.strftime('%Y/%m/%d')
        handle = urllib.urlopen(thisurl)
        html_gunk =  handle.readlines()
        k=0
        j=-3
        for line in html_gunk:
            if '<header><a href="/event/' in str(line):
                k=5
                dic={}
                dic['CreatorId'] = 100000000

            if k>0:
                if k==5:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Name']=str(line)
                if k==4:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Date']=str(line)
                    total=dic['Date'].split(",")
                    month_abbr=total[1].split(" ")[1][0:3]
                    month_num=str(list(calendar.month_abbr).index(month_abbr))
                    day = total[1].split(" ")[2]
                    if int(day) < 10:
                        day = "0" + day
                    dic['Date']=total[2][1:]+month_num+day
                if k==3:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=re.search(r'span\>(.*)\<', str(line)).group(1)
                    dic['Time']=str(line)
                if k==2:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Location']=str(line)
                if k==1:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Description']=str(line)
                k=k-1
            if '<div class="tags">' in str(line):
                j=2
                tag=[]
            if j>=0:
                if j==1:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=line.split('/')
                    for i in line:
                        tag.append(i)
                if j!=1 and ('!important;">' in str(line)):
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=line.split('/')
                    for i in line:
                        tag.append(i)
                    j=j+1
                j=j-1
            if j==-1:
                tag2=set(tag)
                tag1=list(tag2)
                dic['Tag']=tag1
                Activity.append(dic)
                j=j-1
    return Activity