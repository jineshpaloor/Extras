#!/usr/bin/python

"""
script to read all tables in a database and change its 'collate'
settings to 'utf8_unicode_ci'.

"""

import MySQLdb

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="kodeplay", # your password
                      db="kodecrm_dev") # name of the data base

# you must create a Cursor object. It will let
#  you execute all the query you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("USE kodecrm_dev")

cur.execute("SHOW TABLES")

tables = cur.fetchall()

for (table_name,) in cur:
    print 'changing collate of table ',table_name
    cur.execute("ALTER TABLE %s COLLATE utf8_unicode_ci" % table_name)
