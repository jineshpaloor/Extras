#!/usr/bin/python

from glob import glob
import HTMLParser
from bs4 import BeautifulSoup
import json
import os


STORE_DIRS_PATH = '/home/jinesh/Desktop/homestead_n_garden'


def main(path):
    files = glob(path)
    failed = []
    for f in files:
        try:
            format_file(f)
        except LookupError, e:
            print e
            failed.append(f)
            continue
    print 'Failed dirs - '
    print '\n'.join(failed)

def format_file(file_name):
    dir_name = os.path.dirname(file_name)
    with open(file_name, 'rw') as fp:
        text = fp.read().decode('utf-8')
        fp.close()

    html_escaped_text = HTMLParser.HTMLParser().unescape(text)
    soup = BeautifulSoup(html_escaped_text, 'html5lib', fromEncoding='utf-8')

    table = soup.find('table', {'id': 'ContentPlaceHolder1_dg_excel'})

    if table is None:
        raise LookupError

    product_list = []    
    # rows = [r for r in table.find_all('tr')[1:] if r.attrs.get('class', [''])[0] != 'dontTakethis']
    rows = table.find_all('tr')[1:]

    for row in rows:
        row_data = row.find_all('td')        
        if len(row_data) != 8:
            print '    Failed for "%s" in store "%s"' % (row_data[0].string, os.path.basename(dir_name))
            continue
        if row_data:
            # remove pound symbol from price
            s = row_data[6].string
            if s:
                price = s.encode('utf-8').replace('\xc2\xa3', '')
            else:
                price = 0

            status = row_data[7].string.strip()
            status = "1" if status == "Yes" else "0"

            product_dict = {
                    'name' : row_data[1].string,
                    'meta_description' : row_data[3].string,
                    'description' : ' '.join([str(c) for c in row_data[4].findChildren()]),
                    'model' : row_data[0].string,
                    'seo_keyword': row_data[2].string,
                    'status': status,
                    'price': price,
                    'sku': row_data[5].string
                    }
            #print product_dict
            #exit(1)
            product_list.append(product_dict)
            
    products = json.dumps(product_list, indent=4)

    #print 'this is the product list      :',products

    #exit(1)

    f = open(dir_name+'/products.json', 'w')
    f.write(products)
    f.close()


if __name__ == '__main__':
    path = STORE_DIRS_PATH + '/items.xls'
    main(path)
