#!/usr/bin/python

import argparse
import requests
import urllib3
import sqlite3
from slackconfig import *
import json

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--singleurl', help='Single url to add. E.g: http://google.com', dest='singleurl')
parser.add_argument('-ul', '--urlslist', help='File with new urls to add. E.g: urls.txt', dest='urlslist')
parser.add_argument('-rm', '--remove', help='Url to remove from database. E.g: http://google.com', dest='urltoremove')
args = parser.parse_args()

db = sqlite3.connect('keye.db')
cursor = db.cursor()

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
            url = "https://" + url
        requests.packages.urllib3.disable_warnings()
        contentlength = requests.get(url, allow_redirects=True, verify=False, timeout=5).headers['content-length']
        committodb(url, contentlength)
    except requests.ConnectionError:
        print("Could not connect to: " + url)
        try:
            url = url.replace("https://", "http://")
            contentlength = requests.get(url, allow_redirects=True, timeout=5).headers['content-length']
            committodb(url, contentlength)
        except requests.ConnectionError:
            print("Could not connect to: " + url)
        except requests.exceptions.ReadTimeout:
            pass
    except requests.exceptions.InvalidURL:
        pass
    except KeyError:
        pass
    except requests.exceptions.ReadTimeout:
        pass


def committodb(url, contentlength):
    cursor.execute('''INSERT INTO urls(url, contentlength)
                      VALUES(?,?)''', (url, contentlength))
    db.commit()


def getfromdb():
    cursor.execute('''SELECT id, url, contentlength FROM urls''')
    all_rows = cursor.fetchall()
    for row in all_rows:
        id = row[0]
        url = row[1]
        contentlength = str(row[2])
        connect(id, url, contentlength)


def connect(id, url, contentlength):
    try:
        requests.packages.urllib3.disable_warnings()
        newcontentlength = requests.get(url, allow_redirects=True, verify=False, timeout=5).headers['content-length']
        if newcontentlength == contentlength:
            pass
        else:
            notify(url)
            cursor.execute('''UPDATE urls SET contentlength = ? WHERE id = ? ''', (newcontentlength, id))
            db.commit()
    except requests.ConnectionError:
        print("Could not connect to the target host! ")
    except KeyError:
        pass
    except requests.exceptions.ReadTimeout:
        pass


def removefromdb():
    urltoremove = args.urltoremove
    cursor.execute('''DELETE FROM urls WHERE url = ? ''', (urltoremove,))
    db.commit()

def notify(url):
    webhook_url = posting_webhook
    slack_data = {'text': 'Changes detected on: ' + url}
    sendnotification = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})


if args.singleurl:
    addsingleurl()
elif args.urlslist:
    addurlsfromlist()
elif args.urltoremove:
    removefromdb()
else:
    getfromdb()

db.close()