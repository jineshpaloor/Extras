from glob import glob
import os
import json
import sys

import MySQLdb as mdb

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'kode'
DB_NAME = 'peapancake'

STORE_DIRS_PATH = '/home/vineet/Desktop/b12_data'


def main(path):
    files = glob(path)
    for f in files:
        create_store_id(f)

def create_store_id(file_name):
    dir_name = os.path.dirname(file_name)

    fp = open(file_name)
    data = json.load(fp)
    fp.close()

    url = data['url']
    store_id = get_store_id(url)
    f = open(dir_name+'/store_id.txt', 'w')
    print 'id  :',store_id
    f.write(store_id)
    f.close()

def get_store_id(url):
    con = None
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = "SELECT store_id FROM store WHERE url = ('%s');" % url        
        cur.execute(sql)
        store_id = cur.fetchall()
    except mdb.Error, e:
        store_id = None
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()

    if not store_id:
        print 'error in file :', url
        return 'unknown'
    else:
        return str(store_id[0][0])

if __name__ == '__main__':
    path = STORE_DIRS_PATH + '/*/stores.json'
    main(path)

