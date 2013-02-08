#!/usr/bin/python

"""
script to create agent for store user.
take user_id, seller_jid, store_id from another mysql table and display_name from mongodb table

"""
import pymongo
import MySQLdb as mdb

db = mdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="kodeplay", # your password
                      db="kodecrm_dev") # name of the data base

mongo_conn = pymongo.Connection("mongodb://localhost", safe=True)
mongo_db = mongo_conn.kodecrm
mongo_db.authenticate('kodecrm', 'passForKodecrm')
storeflags = mongo_db.storeflags


with db:
    # you must create a Cursor object. It will let
    #  you execute all the query you need
    cur = db.cursor(mdb.cursors.DictCursor)
    cur.execute('SELECT * FROM account_store')

    rows = cur.fetchall()
    for row in rows:
        user_id = row["user_id"]
        seller_jid = row["seller_jid"]
        store_id = row["id"]
        display_name = 'Seller'

        #get nickname from mongodb
        query = {'store_id': str(store_id)}
        docs = storeflags.find(query)
        for doc in docs:
            display_name = doc.get('seller_nickname', 'Seller')

        create_agent_query = "insert into account_agent (user_id,priority,max_chat_count,agent_jid, store_id,display_name) values (%s, %d, %d, '%s', %d, '%s')" % (user_id, 1, 1, str(seller_jid), store_id, str(display_name))
        cur.execute(create_agent_query)

