#!/usr/bin/python
from glob import glob
import HTMLParser
from bs4 import BeautifulSoup
import os

import MySQLdb as mdb

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'peapancake'

STORE_DIRS_PATH = '/home/manty/Desktop/b12_data'

def main(path):
    files = glob(path)
    for f in files:
        try:
            terms_dict = get_textarea_data(f)
            dir_name = os.path.dirname(f)
            fp = open(dir_name+'/store_id.txt','r')
            store_id = fp.read()
            if store_id == 'unknown':
                continue
            store_id = int(store_id)
            fp.close()
            save_to_database(terms_dict, store_id)
        except (IOError, LookupError):
            print 'error in file:',f
            # exit(0)
            continue

def get_textarea_data(file_name):
    with open(file_name, 'r') as fp:
        text = fp.read().decode('utf-8')
        fp.close()

    html_escaped_text = HTMLParser.HTMLParser().unescape(text)
    soup = BeautifulSoup(html_escaped_text, 'html5lib')

    (business, shipping, refund, profile) = map(lambda x: soup.find('textarea', {'id': 'ContentPlaceHolder1_%s' % x}).contents[0].encode('utf-8'),
                                                ['txtTerms', 'txtShipping', 'txtRefund', 'txtProfileDescription'])


    return {
            'business': business,
            'shipping': shipping,
            'refund': refund,
            'profile': profile
            }

def save_to_database(terms_dict, store_id):

    # connect to database
    con = None
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        #saving to database
        save_shipping_terms(con, cur, terms_dict, store_id)
        save_refund_terms(con, cur, terms_dict, store_id)
        save_business_terms(con, cur, terms_dict, store_id)
        save_profile_description(con, cur, terms_dict, store_id)


    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        raise LookupError
    finally:
        if con:
            con.close()

def save_shipping_terms(con, cur, terms_dict, store_id):
    sql1 =  information_sql(4)
    cur.execute(sql1)
    info_id = con.insert_id()
    desc = str(mdb.escape_string(terms_dict['shipping']))
    sql2 = info_desc_sql(info_id, 'Shipping Policy', desc)
    cur.execute(sql2)
    sql3 = info_store_sql(info_id, store_id)
    cur.execute(sql3)

def save_refund_terms(con, cur, terms_dict, store_id):
    sql1 =  information_sql(5)
    cur.execute(sql1)
    info_id = con.insert_id()
    desc = str(mdb.escape_string(terms_dict['refund']))
    sql2 = info_desc_sql(info_id, 'Return Policy', desc)
    cur.execute(sql2)
    sql3 = info_store_sql(info_id, store_id)
    cur.execute(sql3)

def save_business_terms(con, cur, terms_dict, store_id):
    desc = str(mdb.escape_string(terms_dict['business']))
    update_desc(con, cur, 'Terms &amp; Conditions', desc, store_id)


def save_profile_description(con, cur, terms_dict, store_id):
    desc = str(mdb.escape_string(terms_dict['profile']))
    update_desc(con, cur, 'About Us', desc, store_id)


def update_desc(con, cur, title, desc, store_id):
    sql = "SELECT id.information_id FROM information_description id INNER JOIN information_to_store i2s ON (id.information_id = i2s.information_id) WHERE id.title = '%s' AND i2s.store_id = '%d'" % (title, store_id)
    cur.execute(sql)
    info_id = cur.fetchall()
    desc = str(mdb.escape_string(desc))
    sql2 = "UPDATE information_description SET description = '%s' WHERE information_id = '%d'" % (desc, info_id[0][0])
    cur.execute(sql2)



def information_sql(sort_order):
    return "INSERT INTO information (sort_order, status) VALUES ('%d', '1')" % (sort_order)


def info_desc_sql(info_id, title, desc):
    return """INSERT INTO information_description (information_id, language_id, title, meta_keywords, meta_description, description)\
            VALUES ('%d', '1', '%s', '', '', '%s')""" % (info_id, title, desc)


def info_store_sql(info_id, store_id):
    return """INSERT INTO information_to_store (information_id, store_id)\
            VALUES ('%d', '%d')""" %(info_id, store_id)


if __name__ == '__main__':
    path = STORE_DIRS_PATH + '/*/03-account_details.html'
    main(path)

