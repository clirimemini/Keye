#!/usr/bin/python

import sqlite3

db = sqlite3.connect('keye.db')
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE urls(id INTEGER PRIMARY KEY, url TEXT,
                       contentlength INTEGER)''')
db.commit()
db.close()