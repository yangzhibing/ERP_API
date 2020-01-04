# -*- encoding: utf-8 -*-
import xmlrpclib


class Config(object):
    url = "http://127.0.0.1:8069"
    erp_flask_url = "http://127.0.0.1:5000"
    dbname = "Dairygold_TY"
    username = "odoo"
    password = "zxcvbnm"
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

    data_Json = {
        'success': False,
        'code': "400",
        'message': "数据获取失败",
        'data': {}
    }


class ProdConfig(Config):
    host = "0.0.0.0"
    dbname = "Dairygold_TY"
    username = 'odoo'
    password = 'zxcvbnm'
    url = "http://127.0.0.1:8071"
    erp_flask_url = "http://127.0.0.1:5000"


class DevConfig(Config):
    host = "0.0.0.0"
    dbname = "Dairygold_TY"
    username = 'odoo'
    password = 'zxcvbnm'
    url = "http://127.0.0.1:8071"
    erp_flask_url = "http://127.0.0.1:5000"
