#!/usr/bin/python
from xlrd import open_workbook
from glob import glob
import os
import re
import HTMLParser
import json
from bs4 import BeautifulSoup


EMAIL_XLS_PATH = '/home/vineet/Documents/projects/peapancake/EmailDetails.xls'
LOGIN_XLS_PATH = '/home/vineet/Documents/projects/peapancake/LoginDetails.xls'
STORE_DIRS_PATH = '/home/vineet/Desktop/b12_data'


def main(path):
    login_dict = create_login_dict()

    user_dict = create_user_dict()
    files = glob(path)
    for f in files:
        try:
            store_dict = create_store_dict(f)

            # get email, firstname, last name and password for the store from
            # the dictionary created from excel files
            username = store_dict['username']
            email = login_dict[username]['email']
            password = login_dict[username]['password']
            firstname = user_dict[email]['firstname']
            lastname = user_dict[email]['lastname']

            #update the store dictionary with the above values
            store_dict['firstname'] = firstname
            store_dict['lastname'] = lastname
            store_dict['email'] = email
            store_dict['password'] = password

            #append to store list
            #store_list.append(store_dict)
        except LookupError, e:
            print 'file :', f, e
            continue

        #convert store list into json format
        stores = json.dumps(store_dict, indent=4)
        dir_name = os.path.dirname(f)
        f = open(dir_name+'/stores.json', 'w')
        f.write(stores)
        f.close()


def create_login_dict():
    xls_source = LOGIN_XLS_PATH
    wb = open_workbook(xls_source)
    sheet = wb.sheet_by_index(0)

    login_dict = {}
    p = re.compile('[^a-z0-9_\-]+')
    for row in range(1,sheet.nrows):
        username = sheet.cell(row,0).value
        email = sheet.cell(row,1).value
        password = sheet.cell(row,2).value
        username = username.lower().rstrip().replace('&', 'n')
        username = p.sub('_', username)
        login_dict[username] = {'email': email, 'password': password}

    return login_dict

def create_user_dict():
    xls_source = EMAIL_XLS_PATH
    wb = open_workbook(xls_source)
    sheet = wb.sheet_by_index(0)

    user_dict = {}
    for row in range(1,sheet.nrows):
        email = sheet.cell(row,1).value
        firstname = sheet.cell(row,2).value
        lastname = sheet.cell(row,3).value
        user_dict[email] = {'firstname': firstname, 'lastname': lastname}

    return user_dict

def create_store_dict(file_name):
    dir_name = os.path.basename(os.path.dirname(file_name))
    with open(file_name, 'rw') as fp:
        text = fp.read().decode('utf-8')
        fp.close()

    html_escaped_text = HTMLParser.HTMLParser().unescape(text)
    soup = BeautifulSoup(html_escaped_text, 'html5lib')

    username = dir_name.rstrip('_').replace('.', '_')
    store_name = dir_name.replace('_', ' ').rstrip(' ').lower()
    try:
        region = soup.find('input', {'id':'ContentPlaceHolder1_txtCounty'}).get('value','')

        #address part
        add1 = soup.find('input', {'id':'ContentPlaceHolder1_txtAddress1'}).get('value','')
        add2 = soup.find('input', {'id':'ContentPlaceHolder1_txtAddress2'}).get('value','')
        add3 = soup.find('input', {'id':'ContentPlaceHolder1_txtAddress3'}).get('value','')
        city = soup.find('input', {'id':'ContentPlaceHolder1_txtCity'}).get('value','')
        address = add1 + add2 + add3 + city

        telephone = soup.find('input', {'id':'ContentPlaceHolder1_txtTelephone'}).get('value','')
        meta_tag_description = soup.find('input', {'id':'ContentPlaceHolder1_txtLongName'}).get('value','')

        #custom field description
        company_no = soup.find('input', {'id':'ContentPlaceHolder1_txtCompanyNo'}).get('value','')
        # vat registered or not. value should be 0 or 1
        vat_registered_select = soup.find('select',{'id':'ContentPlaceHolder1_ddlVatRegistered'})

        vat_registered = vat_registered_select.find('option', {'selected':'selected'}).get('value','')
        try:
            vat_no = soup.find('input', {'id':'ContentPlaceHolder1_txtVatNo'}).get('value','')
        except AttributeError:
            vat_no = ''

        profile_description = soup.find('textarea', {'id':'ContentPlaceHolder1_txtProfileDescription'}).contents
        profile_description = '' if len(profile_description) == 0 else profile_description[0]
        
    except (KeyError, TypeError):
        raise LookupError

    store_dict = {
            'store_name': store_name,
            'username':username,
            'url':'http://peapancake.kp/'+username+'/',
            'region':region,
            'address': address,
            'country': 'UK',
            'telephone': telephone,
            'meta_description': meta_tag_description,
            'url_mode': 'subdir',
            'plan_id':1,
            "mall_category_id": "0",
            'custom_fields':{
                    'company_no': company_no,
                    'vat_registered':vat_registered,
                    'vat_no': vat_no,
                    'profile_description': profile_description
                    }
            }
    return store_dict


if __name__ == '__main__':
    path = STORE_DIRS_PATH + '/*/03-account_details.html'
    main(path)

