#!/usr/bin/python

import argparse
import requests
import sqlite3
import os
from slackconfig import *
import json
requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--singleurl', help='Single URL to add. E.g: http://google.com', dest='singleurl')
parser.add_argument('-ul', '--urlslist', help='File with new urls to add. E.g: urls.txt', dest='urlslist')
parser.add_argument('-rm', '--remove', help='URL to remove from database. E.g: http://google.com', dest='urltoremove')
parser.add_argument('-d', '--display', help='Display all monitored URLs', required =  False, nargs='?', const="True", dest='displayurls')
args = parser.parse_args()

def db_install():
    if (os.path.isfile('./keye.db')) == False:
        db = sqlite3.connect('keye.db')
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE urls(id INTEGER PRIMARY KEY, url TEXT,
                               reslength INTEGER)''')
        db.commit()
        db.close()
    else:
        pass

def addsingleurl():
    url = args.singleurl
    request(url)

def addurlsfromlist():
    urlslist = open(args.urlslist, "r")
    for url in urlslist:
        url = url.rstrip()
        request(url)

def request(url):
    try:
        if not "http" in url:
            url = "http://" + url
        req = requests.get(url, allow_redirects=True, verify=False, timeout=5)
        reslength = len(req.text)
        try:
            if not check_if_present(url):
                committodb(url, reslength)
                print("We have successfully added the URL to be monitored.")
            else:
                print("This URL already exists on the database.")
        except Exception as e:
            print(e)

    except:
        try:
            url = url.replace("http://", "https://")
            req = requests.get(url, allow_redirects=True, timeout=5)
            reslength = len(req.text)
            if not check_if_present(url):
                committodb(url, reslength)
                print("We have successfully added the URL to be monitored.")
            else:
                print("This URL already exists on the database.")
            print("We have successfully added the URL to be monitored.")
        except Exception as e:
            print("We could not connect to {} due to following error: {}".format(url, e))

def committodb(url, reslength):
    try:
        cursor.execute('''INSERT INTO urls(url, reslength)
                          VALUES(?,?)''', (url, reslength))
        db.commit()
    except Exception as e:
        print(e)

def getfromdb():
    try:
        cursor.execute('''SELECT id, url, reslength FROM urls''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            id = row[0]
            url = row[1]
            reslength = str(row[2])
            connect(id, url, reslength)
    except Exception as e:
        print(e)

def connect(id, url, reslength):
    try:
        req = requests.get(url, allow_redirects=True, verify=False, timeout=5)
        newreslength = len(req.text)
        if int(newreslength) == int(reslength):
            pass
        else:
            notify(url)
            cursor.execute('''UPDATE urls SET reslength = ? WHERE id = ? ''', (newreslength, id))
            db.commit()
    except Exception as e:
        print("We could not connect to {} due to following error: {}".format(url, e))

def removefromdb():
    urltoremove = args.urltoremove
    try:
        cursor.execute('''DELETE FROM urls WHERE url = ? ''', (urltoremove,))
        db.commit()
        print("\nWe have successfully removed the URL from the database.")
    except Exception as e:
        print(e)

def displayurls():
    try:
        cursor.execute('''SELECT url from urls''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            print(row[0])
    except Exception as e:
        print("We couldn't retrieve URLs due to following error {}".format(e))


def check_if_present(url):
    try:
        cursor.execute('''SELECT * from urls where url = ? ''',(url,))
        if cursor.fetchall():
            return True
        else:
            return False
    except Exception as e:
        return False


def notify(url):
    webhook_url = posting_webhook
    slack_data = {'text': 'Changes detected on: ' + url}
    sendnotification = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

db_install()
db = sqlite3.connect('keye.db')
cursor = db.cursor()

if args.singleurl:
    addsingleurl()
elif args.urlslist:
    addurlsfromlist()
elif args.urltoremove:
    removefromdb()
elif args.displayurls:
    displayurls()
else:
    getfromdb()

db.close()
