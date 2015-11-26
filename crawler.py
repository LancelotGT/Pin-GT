__author__ = 'Grueo'
import urllib
import re
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
file=open("crawler.txt","w")
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
            if k>0:
                if k==5:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic["Name"]=str(line)
                if k==4:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic["Date"]=str(line)
                if k==3:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    line=re.search(r'span\>(.*)\<', str(line)).group(1)
                    dic["Time"]=str(line)
                if k==2:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic["Location"]=str(line)
                if k==1:
                    line=re.search(r'\>(.*)\<', str(line)).group(1)
                    dic["Description"]=str(line)
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
                tag1=list(set(tag))
                dic["Tag"]=tag1
                Activity.append(dic)
                file.write('%s' %dic)
                file.write('\n')
                j=j-1
    return Activity
if __name__=="__main__":
    start_date='2015/11/17'
    end_date='2015/11/20'
    crawler(start_date,end_date)




