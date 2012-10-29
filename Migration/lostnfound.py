import sys
import MySQLdb as mdb

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'kode'
DB_NAME = 'peapancake_live'


def store_settings(setting_id):
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = "SELECT store_id, `value` FROM xstore_setting WHERE `setting_id` = ('%d');" % setting_id  
        cur.execute(sql)
        settings = cur.fetchall()
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()

    queries = []

    for setting in settings:
        queries.append("UPDATE xstore_setting SET `value` = '%s' WHERE store_id = %s AND setting_id = %s;" 
                       % (setting[1], setting[0], setting_id))

        if setting_id == 55:
            queries.append("UPDATE `store` SET logo = '%s' WHERE store_id = %s;" % (setting[1], setting[0]))

    print '\n'.join(queries)


store_settings(90)
        

