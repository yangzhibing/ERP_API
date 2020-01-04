# -*- encoding: utf-8 -*-
from flask import jsonify, request, json
from os import path
from flask import Blueprint
from ..config import Config

# 报修
apply_blueprint = Blueprint(
    'apply',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'apply'),
    url_prefix="/apply"
)


@apply_blueprint.route('/get_apply_record', methods=['GET'])
def get_apply_record():
    user_id = request.args.get('user_id', None)
    state = request.args.get('state', None)
    result = {}
    if user_id:

        odoo_uids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'res.users', 'search',
                                             [[['id', '=', user_id]]])
        print("odoo_uids: " + str(odoo_uids))
        if odoo_uids:
            result = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                              'afc.repair.apply', 'search_read',
                                              [],
                                              )
            for r in result:
                if r['deviceId'] is not None:
                    device_info = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                           'afc.device', 'search_read',
                                                           [[['id', '=', int(r['deviceId'][0])]]]
                                                           )
                    if device_info is not None and len(device_info) != 0:
                        r['device_info'] = device_info[0]
    return jsonify({'data': result})


@apply_blueprint.route('/get_device_info', methods=['GET'])
def get_device_info():
    user_id = request.args.get('user_id', None)
    code = request.args.get('code', None)
    model_name = 'afc.device'

    # 构建一个model层列表
    data_model = []

    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])
        if user_ids:
            # 对model数据查询
            dict_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                model_name, 'fields_get',
                                                [],
                                                {'attributes': ['string', 'type', 'help']})

            value_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                 model_name, 'search_read',
                                                 [[['deviceCode', '=', code]]])
            if value_res is not None and value_res != []:
                # 遍历赋值过程
                for i in dict_res:
                    if i in Config.ignore_fields:
                        continue
                    else:
                        if i == "state":
                            print "工作流暂不处理"
                        else:
                            if value_res != [] and value_res[0][i] != '' and dict_res[i].has_key('help'):
                                # 构建一个model层下的字典,并赋值
                                dict_model = {'field_name': i,
                                              'is_readonly': True,
                                              'display_name': dict_res[i]['string'],
                                              'field_type': dict_res[i]['type'],
                                              'field_value': value_res[0][i],
                                              "field_order": dict_res[i]['help'],
                                              'field_params': {}}
                                # 设备参数
                                if str(dict_model['field_type']) == "one2many":
                                    dict_model['field_params'] = {'data': []}

                                    ids = value_res[0][i]
                                    for id in ids:
                                        item_data = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                             'afc.device.item', 'read', [id],
                                                                             {'fields': ['name', 'value']})

                                        dict_item_model = [{'field_name': "name",
                                                            'is_readonly': True,
                                                            'display_name': "参数名",
                                                            'field_type': 'char',
                                                            'field_value': item_data[0]['name'],
                                                            'field_params': {}
                                                            },
                                                           {'field_name': "value",
                                                            'is_readonly': True,
                                                            'display_name': "参数值",
                                                            'field_type': 'char',
                                                            'field_value': item_data[0]['value'],
                                                            'field_params': {},
                                                            }
                                                           ]
                                        dict_model['field_params']['data'].append(dict_item_model)

                                data_model.append(dict_model)
                # 冒泡排序
                for i in range(len(data_model) - 1):
                    for j in range(len(data_model) - i - 1):
                        if data_model[j]['field_order'] > data_model[j + 1]['field_order']:
                            data_model[j], data_model[j + 1] = data_model[j + 1], data_model[j]

    return jsonify({'data': data_model})


@apply_blueprint.route('/get_device_fault_info', methods=['GET'])
def get_device_fault_info():
    user_id = request.args.get('user_id', None)
    code = request.args.get('code', None)
    model_name = 'afc.fault'
    data = [
        # 构建一个下拉选项列表
        {
            'field_name': 'list_fault',
            'is_readonly': False,
            'display_name': "设备故障列表",
            'field_type': 'selection',
            'field_value': '',
            "field_order": -1,
            'field_params': {
                'device_id': -1,
                'selection_type': {}
            }
        }
    ]

    # 验证当前登录用户
    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])
        # 用户存在
        if user_ids:
            # 查询设备
            res_device = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                  'afc.device', 'search',
                                                  [[['deviceCode', '=', code]]])
            # 非空判断
            if res_device is not None and res_device != []:
                # 设备ID(整机类故障查询参数)
                device_id = res_device[0]

                res_fault = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                     model_name, 'search_read',
                                                     [[['deviceID', '=', device_id]]])
                data = [
                    {
                        'field_name': 'list_fault',
                        'is_readonly': False,
                        'display_name': "设备故障列表",
                        'field_type': 'selection',
                        'field_value': '',
                        "field_order": -1,
                        'field_params': {
                            'device_id': device_id,
                            'module_id': False,
                            'selection_type': {}
                        }
                    }
                ]
                for res in res_fault:
                    fault_id = res['id']
                    fault_name = res['name']
                    selection_type = str(fault_id)
                    data[0]['field_params']['selection_type'][selection_type] = fault_name
                    # 构建故障描述字段
    fault_content = {
        'field_name': 'fault_content',
        'is_readonly': False,
        'display_name': "故障内容描述",
        'field_type': 'text',
        'field_value': '',
        "field_order": -1,
        'field_params': {}
    }
    data.append(fault_content)
    return jsonify({'data': data})


@apply_blueprint.route('/get_device_module_info', methods=['GET'])
def get_device_module_info():
    user_id = request.args.get('user_id', None)
    code = request.args.get('code', None)
    model_name = 'afc.module'
    data = [
        # 构建一个下拉选项列表
        {
            'field_name': 'list_module',
            'is_readonly': False,
            'display_name': "设备模块列表",
            'field_type': 'selection',
            'field_value': '',
            "field_order": -1,
            'field_params': {
                'device_id': -1,
                'selection_type': {}
            }
        }
    ]
    # 验证当前登录用户
    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])
        # 用户存在
        if user_ids:
            # 查询设备
            res_device = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                  'afc.device', 'search',
                                                  [[['deviceCode', '=', code]]])
            # 非空判断
            if res_device is not None and res_device != []:
                # 设备ID(设备模块查询参数)
                device_id = res_device[0]

                res_module = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                      model_name, 'search_read',
                                                      [[['deviceID', '=', device_id]]])
                data = [
                    {
                        'field_name': 'list_module',
                        'is_readonly': False,
                        'display_name': "设备模块列表",
                        'field_type': 'selection',
                        'field_value': '',
                        "field_order": -1,
                        'field_params': {
                            'device_id': device_id,
                            'selection_type': {}
                        }
                    }
                ]
                for res in res_module:
                    module_id = res['id']
                    module_name = res['name']
                    selection_type = str(module_id)
                    data[0]['field_params']['selection_type'][selection_type] = module_name
                    # 构建故障描述字段

    return jsonify({'data': data})


@apply_blueprint.route('/get_module_fault_info', methods=['GET'])
def get_module_fault_info():
    user_id = request.args.get('user_id', None)
    code = request.args.get('code', None)
    module_id = request.args.get('module_id', None)

    model_name = 'afc.fault'
    data = [
        # 构建一个下拉选项列表
        {
            'field_name': 'list_fault',
            'is_readonly': False,
            'display_name': "模块故障列表",
            'field_type': 'selection',
            'field_value': '',
            "field_order": -1,
            'field_params': {
                'selection_type': {}
            }
        }
    ]

    # 验证当前登录用户
    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', int(user_id)]]])
        # 用户存在
        if user_ids and module_id is not None:

            res_fault = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                 model_name, 'search_read',
                                                 [[['moduleID', '=', int(module_id)]]])

            data = [
                {
                    'field_name': 'list_fault',
                    'is_readonly': False,
                    'display_name': "模块故障列表",
                    'field_type': 'selection',
                    'field_value': '',
                    "field_order": -1,
                    'field_params': {
                        'device_code': code,
                        'device_id': False,
                        'module_id': int(module_id),
                        'selection_type': {}
                    }
                }
            ]
            for res in res_fault:
                fault_id = res['id']
                fault_name = res['name']
                selection_type = str(fault_id)
                data[0]['field_params']['selection_type'][selection_type] = fault_name

    # 构建故障描述字段
    fault_content = {
        'field_name': 'fault_content',
        'is_readonly': False,
        'display_name': "故障内容描述",
        'field_type': 'text',

        'field_value': '',
        "field_order": -1,
        'field_params': {}
    }
    data.append(fault_content)
    return jsonify({'data': data})


@apply_blueprint.route('/post_repair_apply_info', methods=['POST'])
def post_repair_apply_info():
    # 固定参数
    model_name = 'afc.repair.apply'
    # 接收参数
    post_data = request.json
    # 非空处理
    if post_data is None:
        return jsonify({'data': False})
    else:
        user_id = post_data['user_id']
        # 验证当前登录用户
        if user_id is None:
            return jsonify({'data': False})
        else:
            user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'res.users', 'search',
                                                [[['id', '=', user_id]]])
            # 用户存在
            if user_ids != []:
                if str(post_data['apply_type']) == "type_1":
                    model_data = {
                        'deviceId': int(post_data['device_id']),
                        'applyType': str(post_data['apply_type']),
                        'userId': int(post_data['user_id']),
                        'fault_type_1': int(post_data['field_value']),
                        'recordContent': post_data['fault_content']
                    }
                elif str(post_data['apply_type']) == "type_2":
                    module_id = int(post_data['module_id'])
                    res_module = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                          'afc.module', 'read',
                                                          [module_id],
                                                          {'fields': ['deviceID']})
                    model_data = {
                        'deviceId': int(res_module[0]['deviceID'][0]),
                        'module': module_id,
                        'applyType': str(post_data['apply_type']),
                        'userId': int(post_data['user_id']),
                        'fault_type_2': int(post_data['field_value']),
                        'recordContent': post_data['fault_content']
                    }
                else:
                    return jsonify({'data': False})

                model_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                    model_name, 'create',
                                                    [model_data])
                if type(model_id) == int:
                    return jsonify({'data': True})

    return jsonify({'data': False})
