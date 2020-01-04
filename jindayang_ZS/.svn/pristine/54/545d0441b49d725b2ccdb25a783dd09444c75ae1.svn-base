# -*- encoding: utf-8 -*-
import xmlrpclib


class Config(object):
    url = "http://192.168.4.105:8069"
    smartcell_url = "http://192.168.4.110:3000"
    dbname = "SC2"
    username = "123"
    password = "123"
    ignore_fields = ['id',
                     'display_name',
                     '__last_update',
                     'create_uid',
                     'create_date',
                     'write_uid',
                     'write_date'
                     ]

    common = xmlrpclib.ServerProxy(url + "/xmlrpc/common")
    uid = common.login(dbname, username, password)
    models = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

    APP_ID = 'wxb4142490f4b22a11'
    APP_SECRET = '67a85eb3cec3f124fda0b7e2a23c54b7'

    NONCESTR = 'Wm3WZYTPz0wzccnW'

class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    host = "0.0.0.0"
    dbname = "SC2"
    username = '123'
    password = '123'
    url = "http://192.168.4.105:8069"
    smartcell_url = "http://192.168.4.110:3000"
   

