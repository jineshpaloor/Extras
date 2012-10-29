#!/usr/bin/env python

import sys
import MySQLdb as mdb
import xlrd
import xlwt

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'kode'
DB_NAME = 'peapancake'

# EXCEL_PATH = '/home/vineet/Documents/projects/peapancake/product_category.xls'
# CAT_INDEX = 1
# PROD_INDEX = 3

EXCEL_PATH = '/home/vineet/Documents/projects/peapancake/missing_categories.xls'

CAT_INDEX = 3
PROD_INDEX = 0 


def product_map():
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = "SELECT product_id, model FROM product"
        cur.execute(sql)
        products = cur.fetchall()
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    return dict([(m, int(i)) for i, m in products]) 


def category_map():
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = "SELECT category_id, name FROM xmall_category"
        cur.execute(sql)
        categories = cur.fetchall()
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    return dict([(n.replace('&amp;', '&'), int(i)) for i, n in categories])


def product_store_map():
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = "SELECT product_id, store_id FROM product_to_store"
        cur.execute(sql)
        ps = cur.fetchall()
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    return dict([(int(p), int(s)) for p, s in ps])


def enum_report(msg, li):
    print '\n%s\n%s\n%s' % (msg, '-' * len(msg), '\n'.join(['%d. %s' % (n, c) for (n, c) in zip(range(1, len(li)+1), li)]))

def data_diff():
    products = product_map()
    categories = category_map()
    wb = xlrd.open_workbook(EXCEL_PATH)
    sheet = wb.sheet_by_index(0)

    cats = set([str(sheet.row_values(r)[CAT_INDEX]).strip() for r in range(1, sheet.nrows)])
    prods = set([str(sheet.row_values(r)[PROD_INDEX]).rstrip('.00') for r in range(1, sheet.nrows)])

    print enum_report('Categories present in Excel that are found missing in these database', 
                      cats - set(categories))

    print enum_report('Products present in Excel that are found missing in the database', 
                      prods - set(products))

    print enum_report('Categories present in database that are found missing in the excel', 
                      set(categories) - cats)

    print enum_report('Products present in database that are found missing in the excel', 
                      set(products) - prods)


def get_excel_dict():
    products = product_map()
    categories = category_map()
    wb = xlrd.open_workbook(EXCEL_PATH)
    sheet = wb.sheet_by_index(0)
    new_mappings = []
    
    for r in range(1, sheet.nrows):
        row = sheet.row_values(r)
        catName = str(row[CAT_INDEX]).strip(' ')
        itemCode = str(row[PROD_INDEX])

        try:
            cat = categories[catName]
        except KeyError:
            print 'Category mapping not found for %s' % row[CAT_INDEX]
            continue

        try:
            prod = products[itemCode]
        except KeyError:
            print 'Product mapping not found for %s' % itemCode
            continue

        new_mappings.append((prod, cat))

    return new_mappings


def save_new_mappings(new_mappings):    
    ps_map = product_store_map()
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        values = []
        for p, c in new_mappings:
            s = ps_map[p]
            values.append("'%s', '%s', '%s'" % (s, p, c))

        cur.execute("INSERT INTO xproduct_mall_category (store_id, product_id, mall_category_id) VALUES (%s)" % '), ('.join(values))
        con.commit()
        con.close()

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)    

    print "Number of rows updated: %d" % cur.rowcount


def detailed_report():
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = """SELECT p.model, pd.name, s.name as store_name FROM product p 
INNER JOIN product_description pd ON (p.product_id = pd.product_id)
INNER JOIN product_to_store p2s ON (p.product_id = p2s.product_id)
INNER JOIN store s ON (p2s.store_id = s.store_id) 
WHERE p.product_id NOT IN (SELECT product_id FROM xproduct_mall_category) GROUP BY p.model"""
        cur.execute(sql)
        products = cur.fetchall()
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    # print '\n'.join([' | '.join(p) for p in products])
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('no_assoc')
    for r in range(len(products)):
        for c in range(1, 4):
            cellval = products[r][c-1]
            if c == 2:
                cellval = unicode(cellval, errors='replace')
            sheet.write(r, c, cellval)
    wb.save('detailed_no_assoc2.xls')


def prod_no_assoc():
    pmap = dict((v, k) for k, v in product_map().iteritems())
    products = set(pmap.keys())
    try:
        con = mdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        cur = con.cursor()
        sql = "SELECT product_id FROM xproduct_mall_category"
        cur.execute(sql)
        mallprod = cur.fetchall()
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)        
    mpa = set([int(mp[0]) for mp in mallprod])
    no_assoc = products - mpa    

    print enum_report('Products in database that are not associated with any categories', 
                      [pmap[p] for p in no_assoc])


def to_delete():
    products = product_map()
    ps_map = product_store_map()
    wb = xlrd.open_workbook(EXCEL_PATH)
    sheet = wb.sheet_by_index(0)
    tobedel = []
    for r in range(1, sheet.nrows):
        row = sheet.row_values(r)
        catName = str(row[CAT_INDEX]).strip(' ')
        if catName in ['(delete product please)', '(delete product)']:
            try:
                ps_map[str(row[PROD_INDEX])]
                tobedel.append()
            except KeyError:
                continue
    print enum_report('Products to be deleted', tobedel)



if __name__ == '__main__':
    # new_mappings = get_excel_dict()
    # print len(new_mappings)
    # save_new_mappings(new_mappings)

    data_diff()

    # prod_no_assoc()
    
    # detailed_report()

    # to_delete()

