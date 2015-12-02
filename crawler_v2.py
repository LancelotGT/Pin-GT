__author__ = 'Grueo'
import googlemaps
import calendar
import urllib
import urllib2
import json
import re
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
file=open("crawler1.txt","w")
API_KEY = 'AIzaSyDtaF7VqFqOIQaS0N-gSiWRPfOTI8UXN7Q'

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

def crawler(start_date,end_date):
    day_list=pd.date_range(start_date, end_date)[1:]
    Activity=[]
    location=[]
    tag_set=[]
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

            if k>0:
                if k==5:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Name']=str(line)
                if k==4:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Date']=str(line)
                if k==3:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=re.search(r'span\>(.*)\<', str(line)).group(1)
                    dic['Time']=str(line)
                if k==2:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic['Location']=str(line)
                    location.append(str(line))
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
                for i in tag2:
                    tag_set.append(i)
                Activity.append(dic)
                file.write('%s' %dic)
                file.write('\n')
                j=j-1
    tag_set=list(set(tag_set))
    return Activity, tag_set

def database_format(dic):
    activitylist=[]
    locationlist=[]
    for i in dic:
        tup=(i['Name'],)
        tup=tup+(100000000,)
        Todeal=i['Date'].split(",")
        month_abbr=Todeal[1].split(" ")[1][0:3]
        month_num=str(list(calendar.month_abbr).index(month_abbr))
        Date_change=Todeal[2][1:]+month_num+Todeal[1].split(" ")[2]
        tup=tup+(Date_change,)
        tup=tup+(i['Time'],)
        tup=tup+(i['Description'],)
        activitylist.append(tup)
        tup1=(i['latlon']['lng'],)
        tup1=tup1+(i['latlon']['lat'],)
        tup1=tup1+(i['Location'],)
        locationlist.append(tup1)
    return activitylist,locationlist

def tag_format(tag_set):
    taglist=[]
    for i in tag_set:
        tup=(i,)
        taglist.append(tup)
    return taglist

if __name__=="__main__":
    start_date='2015/11/17'
    end_date='2015/11/18'
    a,c=crawler(start_date,end_date)
    a1=processGeoInfo(a)
    activitylist,locationlist=database_format(a1)
    taglist=tag_format(c)
    print activitylist
    print locationlist
    print taglist




