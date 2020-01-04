# -*- encoding: utf-8 -*-
from flask import jsonify, request, json
from os import path
from flask import Blueprint
from ..config import Config
import redis

import sys

reload(sys)
sys.setdefaultencoding('utf8')

repair_blueprint = Blueprint(
    'repair',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'repair'),
    url_prefix="/repair"
)


@repair_blueprint.route('/get_repair_record', methods=['GET'])
def get_repair_record():
    user_id = request.args.get('user_id', None)
    state = request.args.get('state', None)
    result = {}
    if user_id:

        odoo_uids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'res.users', 'search',
                                             [[['id', '=', user_id]]])
        if odoo_uids:
            result = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                              'afc.repair.form', 'search_read',
                                              [],
                                              {'fields': ['deviceId', 'userId', 'userName', 'faultReason', 'solutions',
                                                          'repairParts', 'delayReason', 'remarks']})

    return jsonify({'data': result})


@repair_blueprint.route('/upload_repair_form', methods=['POST'])
def upload_repair_form():
    post_data = request.values.get('data', None)
    result = {}
    if post_data:
        post_dict = json.loads(post_data)
        odoo_uids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'res.users', 'search',
                                             [[['id', '=', post_dict['user_id']]]])
        if odoo_uids:
            result = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                              'afc.apply.record', 'search_read',
                                              [[['deviceCode', '=', post_dict['code']]]],
                                              {'fields': ['deviceId', 'deviceType', 'deviceCountry', 'deviceCity',
                                                          'deviceLine', 'deviceStation']})

    return jsonify({'data': result})


@repair_blueprint.route('/update_repair_state', methods=['POST'])
def update_repair_state():
    post_data = request.values.get('data', None)
    result = {}
    if post_data:
        post_dict = json.loads(post_data)
        odoo_uids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'res.users', 'search',
                                             [[['id', '=', post_dict['user_id']]]])
        if odoo_uids:
            result = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                              'afc.apply.record', 'search_read',
                                              [[['device_id', '=', post_dict['code']]]],
                                              {'fields': ['device_id', 'device_type', 'device_country', 'device_city',
                                                          'device_line', 'device_station']})

    return jsonify({'data': result})


@repair_blueprint.route('/get_apply_record', methods=['GET'])
def get_apply_record():
    user_id = request.args.get('user_id', None)
    model_name = 'afc.repair.apply'

    # 构建一个model层列表
    data = []

    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])
        if user_ids:
            res_model = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                 model_name, 'search_read',
                                                 [[['is_allocation', '=', False]]],
                                                 {'fields': ['deviceId', 'applyType', 'create_date']})
            if res_model:
                for res in res_model:
                    # 构建一个model层下的字典,并赋值
                    repair_apply_id = str(res['id'])
                    device_id = res['deviceId'][0]
                    type_apply = str(res['applyType'])
                    if type_apply == 'type_1':
                        apply_type = u'整机报修'
                    elif type_apply == 'type_2':
                        apply_type = u'模块报修'
                    else:
                        apply_type = u'无类型'
                    create_date = res['create_date'][0:10]

                    # 查询设备
                    if device_id is not None:
                        res_device = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                              'afc.device', 'search_read',
                                                              [[['id', '=', device_id]]],
                                                              {'fields': ['city', 'line', 'station', 'name']})
                        city = res_device[0]['city']
                        line = res_device[0]['line']
                        station = res_device[0]['station']
                        name = res_device[0]['name']

                        context = create_date + " " + city + line + station + name + " " + apply_type

                        dict_model = {'field_name': 'name',
                                      'display_name': context,
                                      'field_type': 'checkbox',
                                      'is_readonly': False,
                                      'field_value': False,
                                      "field_order": '',
                                      'field_params': {
                                          'field_id': repair_apply_id
                                      }}

                        data.append(dict_model)

    return jsonify({'data': data, 'user_id': -1})


@repair_blueprint.route('/post_data_to_session', methods=['POST'])
def post_data_to_session():
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    # 接收参数
    post_data = request.json
    # 非空处理
    if post_data is not None and post_data.has_key('user_id'):
        user_id = post_data['user_id']
        # 验证当前登录用户
        if user_id is not None:
            user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'res.users', 'search',
                                                [[['id', '=', user_id]]])
            # 用户存在
            if user_ids:
                repair_apply_ids_str = post_data['repair_apply_ids']
                # 处理数据格式问题：去u
                repair_apply_ids = json.dumps(repair_apply_ids_str)
                r.set('repair_apply_ids', repair_apply_ids)
                if r.get('repair_apply_ids') and r.get('repair_apply_ids') is not None:
                    redis_repair_apply_ids = r.get('repair_apply_ids')
                    if redis_repair_apply_ids == str(repair_apply_ids):
                        return jsonify({'data': True})
    return jsonify({'data': False})


@repair_blueprint.route('/get_user_name', methods=['GET'])
def get_user_name():
    # 接收参数
    user_id = request.args.get('user_id', None)
    model_name = 'res.users'

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
                'selection_type': {}
            }
        }
    ]

    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            model_name, 'search',
                                            [[['id', '=', user_id]]])
        if user_ids:
            res_user = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                model_name, 'search_read',
                                                [],
                                                {'fields': ['name']})
            data = [
                {
                    'field_name': 'list_user',
                    'is_readonly': False,
                    'display_name': "用户列表",
                    'field_type': 'selection',
                    'field_value': '',
                    "field_order": -1,
                    'field_params': {
                        'selection_type': {}
                    }
                }
            ]
            for res in res_user:
                user_id = res['id']
                user_name = res['name']
                selection_type = str(user_id)
                data[0]['field_params']['selection_type'][selection_type] = user_name
                # 构建故障描述字段

        return jsonify({'data': data})


@repair_blueprint.route('/post_apply_allocation', methods=['POST'])
def post_apply_allocation():
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    # 固定参数
    model_name = 'afc.repair.task'
    # 接收参数
    post_data = request.json

    # 非空处理
    if post_data is not None and post_data.has_key('user_id') and post_data.has_key('repair_user_id'):
        user_id = post_data['user_id']
        post_repair_user_id = post_data['repair_user_id']

        # 验证当前登录用户
        if user_id is not None:
            user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'res.users', 'search',
                                                [[['id', '=', user_id]]])
            repair_user_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                      'res.users', 'search',
                                                      [[['id', '=', post_repair_user_id]]])
            # 用户存在
            if user_ids and repair_user_id:
                # 从服务端redis中获取存入的已指定分配的报修任务
                if r.get('repair_apply_ids') and r.get('repair_apply_ids') is not None:
                    model_ids_str = r.get('repair_apply_ids')
                    model_ids = json.loads(model_ids_str)
                else:
                    model_ids = []

                # 测量参数
                ids_len = len(model_ids)
                num = 0

                if model_ids:
                    for model_id in model_ids:
                        if model_id is not None:
                            # 验证报修单据是否存在
                            repair_apply_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                        'afc.repair.apply', 'search',
                                                                        [[['id', '=', int(model_id)]]])
                            if repair_apply_ids:
                                # 创建维修任务表单
                                model_data = {
                                    'RepairApplyId': int(model_id),
                                    'repair_user_id': int(post_repair_user_id)
                                }
                                task_model_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                         model_name, 'create',
                                                                         [model_data])
                                if task_model_id:
                                    # 修改报修单任务分配状态
                                    is_success = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                          'afc.repair.apply', 'write',
                                                                          [[int(model_id)],
                                                                           {'is_allocation': True}])
                                    if is_success:
                                        num = num + 1
                if ids_len == num:
                    return jsonify({'data': True})

    return jsonify({'data': False})


@repair_blueprint.route('/get_repair_task', methods=['GET'])
def get_repair_task():
    # 接收参数
    user_id = request.args.get('user_id', None)
    model_name = 'afc.repair.apply'

    data = []

    if user_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', int(user_id)]]])
        if user_ids:
            started_model = {'field_name': 'started_task',
                             'display_name': '报修记录',
                             'field_type': 'radio',
                             'is_readonly': False,
                             'field_value': False,
                             'field_order': '',
                             'field_params': {
                                 'radio_type': {}
                             }}
            # 当前用户分配的任务(未完成)
            res_task_started = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                        'afc.repair.task', 'search_read',
                                                        [[['repair_user_id', '=', int(user_id)],
                                                          ['is_confirm', '=', True],
                                                          ['is_confirm', '=', False]]],
                                                        {'fields': ['RepairApplyId']})
            # 收集已分配的报修表ID
            started_repair_task_ids = []
            for res_1 in res_task_started:
                started_repair_task_id = res_1['RepairApplyId'][0]
                started_repair_task_ids.append(started_repair_task_id)

            res_1_model = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                   model_name, 'search_read',
                                                   [[['is_allocation', '=', True],
                                                     ['id', 'in', started_repair_task_ids]]],
                                                   {'fields': ['deviceId', 'applyType', 'create_date']})
            if res_1_model:
                for model_1 in res_1_model:
                    # 构建一个model层下的字典,并赋值
                    repair_apply_id = str(model_1['id'])
                    device_id = model_1['deviceId'][0]
                    type_apply = str(model_1['applyType'])
                    if type_apply == 'type_1':
                        apply_type = u'整机报修'
                    elif type_apply == 'type_2':
                        apply_type = u'模块报修'
                    else:
                        apply_type = u'无类型'
                    create_date = model_1['create_date'][0:10]

                    # 查询设备
                    if device_id is not None:
                        res_1_device = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                'afc.device', 'search_read',
                                                                [[['id', '=', device_id]]],
                                                                {'fields': ['city', 'line', 'station', 'name']})
                        city = res_1_device[0]['city']
                        line = res_1_device[0]['line']
                        station = res_1_device[0]['station']
                        name = res_1_device[0]['name']
                        handle_state = '【未完成】'
                        context = handle_state + create_date + " " + city + line + station + name + " " + apply_type
                        started_model['field_params']['radio_type'][repair_apply_id] = context

            # 未处理任务查询过程
            res_task_not_started = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                            'afc.repair.task', 'search_read',
                                                            [[['repair_user_id', '=', int(user_id)],
                                                              ['is_confirm', '=', False],
                                                              ['is_complete', '=', False]]],
                                                            {'fields': ['RepairApplyId']})
            not_started_repair_task_ids = []
            for res_2 in res_task_not_started:
                not_started_repair_task_id = res_2['RepairApplyId'][0]
                not_started_repair_task_ids.append(not_started_repair_task_id)

                res_model = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                     model_name, 'search_read',
                                                     [[['is_allocation', '=', True],
                                                       ['id', 'in', not_started_repair_task_ids]]],
                                                     {'fields': ['deviceId', 'applyType', 'create_date']})
                if res_model:
                    for model_2 in res_model:
                        # 构建一个model层下的字典,并赋值
                        repair_apply_id = str(model_2['id'])
                        device_id = model_2['deviceId'][0]
                        type_apply = str(model_2['applyType'])
                        if type_apply == 'type_1':
                            apply_type = u'整机报修'
                        elif type_apply == 'type_2':
                            apply_type = u'模块报修'
                        else:
                            apply_type = u'无类型'
                        create_date = model_2['create_date'][0:10]

                        # 查询设备
                        if device_id is not None:
                            res_2_device = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                    'afc.device', 'search_read',
                                                                    [[['id', '=', device_id]]],
                                                                    {'fields': ['city', 'line', 'station', 'name']})
                            city = res_2_device[0]['city']
                            line = res_2_device[0]['line']
                            station = res_2_device[0]['station']
                            name = res_2_device[0]['name']
                            handle_state = '【未处理】'
                            context = handle_state + create_date + " " + city + line + station + name + " " + apply_type
                            started_model['field_params']['radio_type'][repair_apply_id] = context

            data.append(started_model)

    return jsonify({'data': data})


@repair_blueprint.route('/get_info_handle', methods=['GET'])
def get_info_handle():
    user_id = request.args.get('user_id', None)
    repair_apply_id = request.args.get('repair_apply_id', None)
    model_name = 'afc.device'

    # 构建一个model层列表
    data_model = []

    if user_id and repair_apply_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])

        res_model = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'afc.repair.apply', 'read', [int(repair_apply_id)],
                                             {'fields': ['deviceId']})

        if user_ids and res_model:
            is_save_redis_success = False
            r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
            task_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'afc.repair.task', 'search',
                                                [[['RepairApplyId', '=', int(repair_apply_id)]]])
            if task_ids != []:
                task_id = task_ids[0]

                task_id_str = str(task_id)
                # 处理数据格式问题：去u
                task_id_handle = json.dumps(task_id_str)
                r.set('task_id', task_id_handle)
                if r.get('task_id') and r.get('task_id') is not None:
                    task_id_back = r.get('task_id')
                    if task_id_handle == str(task_id_back):
                        is_save_redis_success = True

            if is_save_redis_success:

                # 设备ID
                device_id = res_model[0]['deviceId'][0]
                # 对model数据查询
                dict_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                    model_name, 'fields_get',
                                                    [],
                                                    {'attributes': ['string', 'type', 'help']})

                value_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                     model_name, 'search_read',
                                                     [[['id', '=', device_id]]])
                if is_save_redis_success and value_res is not None and value_res != []:
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
                                            item_data = Config.models.execute_kw(Config.dbname, Config.uid,
                                                                                 Config.password,
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
                    # 报修处理
                    data_repair_apply = {
                        'field_name': 'repair_apply_handle',
                        'is_readonly': True,
                        'display_name': "报修处理",
                        'field_type': 'char',
                        'field_value': '',
                        "field_order": -1,
                        'field_params': {}
                    }

                    res_repair_apply = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                'afc.repair.apply', 'read', [int(repair_apply_id)]
                                                                )

                    if res_repair_apply:

                        # 构建一个model层下的字典,并赋值

                        type_apply = str(res_repair_apply[0]['applyType'])
                        if type_apply == 'type_1':
                            apply_type = u'整机报修'
                        elif type_apply == 'type_2':
                            apply_type = u'模块报修'
                        else:
                            apply_type = u'无类型'
                        create_date = res_repair_apply[0]['create_date'][0:10]
                        record_content = res_repair_apply[0]['recordContent']
                        context = create_date + "  " + record_content + "  " + apply_type
                        data_repair_apply['field_value'] = context
                    data_model.append(data_repair_apply)

    return jsonify({'data': data_model})


@repair_blueprint.route('/get_handle_confirm', methods=['GET'])
def get_handle_confirm():
    user_id = request.args.get('user_id', None)
    repair_apply_id = request.args.get('repair_apply_id', None)

    data = {'repair_apply_id': -1,
            'apply_type': 'type_0'
            }

    if user_id and repair_apply_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])

        res_model = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'afc.repair.apply', 'read', [int(repair_apply_id)],
                                             {'fields': ['deviceId', 'applyType']})

        if user_ids and res_model:
            apply_type = res_model[0]['applyType']
            # 整机报修，则现象描述处理 ,获得模块确认界面所需接口数据
            if apply_type == 'type_1':

                data = {'repair_apply_id': repair_apply_id,
                        'apply_type': apply_type
                        }

                # 改写维修任务表状态值：为已确认
                task_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                   'afc.repair.task', 'search',
                                                   [[['RepairApplyId', '=', int(repair_apply_id)]]])
                if task_id[0] is not None:
                    is_success = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                          'afc.repair.task', 'write',
                                                          [[int(task_id[0])], {'is_confirm': True}])
                    if is_success:
                        return jsonify({'data': data})

            # 模块报修，则获取，故障解决方案列表方案
            if apply_type == 'type_2':
                data = {'repair_apply_id': repair_apply_id,
                        'apply_type': apply_type
                        }
                # 改写维修任务表状态值：为已确认
                task_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                   'afc.repair.task', 'search',
                                                   [[['RepairApplyId', '=', int(repair_apply_id)]]])
                if task_id[0] is not None:
                    is_success = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                          'afc.repair.task', 'write',
                                                          [[int(task_id[0])], {'is_confirm': True}])
                    if is_success:
                        return jsonify({'data': data})

    return jsonify({'data': data})


@repair_blueprint.route('/get_handle_error', methods=['GET'])
def get_handle_error():
    user_id = request.args.get('user_id', None)
    repair_apply_id = request.args.get('repair_apply_id', None)

    data = {'device_code': '',
            'user_id': user_id,
            }
    if user_id and repair_apply_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])

        res_repair_apply = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                    'afc.repair.apply', 'read', [int(repair_apply_id)],
                                                    {'fields': ['deviceId']})
        if user_ids and res_repair_apply:
            # 设备ID
            device_id = res_repair_apply[0]['deviceId'][0]
            res_device = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                  'afc.device', 'read', [int(device_id)],
                                                  {'fields': ['deviceCode']})
            if res_device != [] and res_device[0].has_key('deviceCode') and res_device[0]['deviceCode']:
                device_code = res_device[0]['deviceCode']

            # 删除原有报修记录，和已分配任务，先删除分配任务
            task_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'afc.repair.task', 'search',
                                                [[['RepairApplyId', '=', int(repair_apply_id)]]])
            if task_ids[0] is not None:
                is_success_1 = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                        'afc.repair.task', 'unlink',
                                                        [[int(task_ids[0])]])
                is_success_2 = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                        'afc.repair.apply', 'unlink',
                                                        [[int(repair_apply_id)]])
                if is_success_1 and is_success_2:
                    data = {'device_code': device_code,
                            'user_id': int(user_id),
                            }
    return jsonify({'data': data})


@repair_blueprint.route('/get_module_list', methods=['GET'])
def get_handle_module_list():
    user_id = request.args.get('user_id', None)
    repair_apply_id = request.args.get('repair_apply_id', None)
    data = []
    if user_id and repair_apply_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])

        res_model = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                             'afc.repair.apply', 'read', [int(repair_apply_id)],
                                             {'fields': ['deviceId', 'applyType']})

        if user_ids and res_model:
            # 设备ID
            device_id = res_model[0]['deviceId'][0]
            apply_type = res_model[0]['applyType']
            # 整机报修，则现象描述处理
            if apply_type == 'type_1':
                # 查询设备下的模块
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
                            'selection_type': {}
                        }
                    }
                ]
                res_module = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                      'afc.module', 'search_read',
                                                      [[['deviceID', '=', device_id]]])
                for res in res_module:
                    module_id = res['id']
                    module_name = res['name']
                    selection_type = str(module_id)
                    data[0]['field_params']['selection_type'][selection_type] = module_name

    return jsonify({'data': data})


@repair_blueprint.route('/post_module_confirm', methods=['POST'])
def post_module_confirm():
    # 接收参数
    post_data = request.json
    data = {'apply_type': 'type_0',
            'repair_apply_id': -1,
            'user_id': -1
            }
    if post_data.has_key('user_id') and post_data.has_key('repair_apply_id') and post_data.has_key('module_id'):
        user_id = post_data['user_id']
        repair_apply_id = post_data['repair_apply_id']
        module_id = post_data['module_id']

        if user_id is not None and repair_apply_id and module_id:
            user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'res.users', 'search',
                                                [[['id', '=', user_id]]])
            repair_apply_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                        'afc.repair.apply', 'search',
                                                        [[['id', '=', int(repair_apply_id)]]])
            module_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                  'afc.module', 'search',
                                                  [[['id', '=', int(module_id)]]])
            if user_ids and repair_apply_ids and module_ids:
                # 模块确定检索整机报修单并修改为模块报修（待开发）
                data = {'apply_type': 'type_1'}

    return jsonify({'data': data})


@repair_blueprint.route('/get_fault_solution', methods=['GET'])
def get_handle_module_confirm():
    apply_type = request.args.get('apply_type', None)
    user_id = request.args.get('user_id', None)
    repair_apply_id = request.args.get('repair_apply_id', None)
    data = []
    if user_id and repair_apply_id:

        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', user_id]]])
        if user_ids:
            if apply_type == 'type_1':
                result = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                  'afc.repair.apply', 'read', [int(repair_apply_id)],
                                                  {'fields': ['fault_type_1']})

                if result != [] and result[0].has_key('fault_type_1') and result[0]['fault_type_1'] != []:
                    fault_id = result[0]['fault_type_1'][0]
            elif apply_type == 'type_2':
                result = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                  'afc.repair.apply', 'read', [int(repair_apply_id)],
                                                  {'fields': ['fault_type_2']})

                if result != [] and result[0].has_key('fault_type_2') and result[0]['fault_type_2'] != []:
                    fault_id = result[0]['fault_type_2'][0]
            else:
                fault_id = - 1

            res_solution = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                    'afc.solution', 'search_read',
                                                    [[['faultName', '=', int(fault_id)]]],
                                                    {'fields': ['solutionItemModels']})

            if res_solution != [] and res_solution[0].has_key('solutionItemModels'):

                solution_item_ids = res_solution[0]['solutionItemModels']

                res_solution_items = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                              'afc.solution.item', 'search_read',
                                                              [[['id', 'in', solution_item_ids]]],
                                                              {'fields': ['name', 'genre']})
                for item in res_solution_items:
                    item_id = item['id']
                    item_name = item['name']
                    item_genre = item['genre']

                    dict_model = {'field_name': 'name',
                                  'display_name': item_name,
                                  'field_type': 'checkbox',
                                  'is_readonly': False,
                                  'field_value': False,
                                  "field_order": '',
                                  'field_params': {
                                      'item_genre': item_genre,
                                      'field_id': item_id
                                  }}
                    data.append(dict_model)

    return jsonify({'data': data})


@repair_blueprint.route('/post_create_repair_form', methods=['POST'])
def post_create_repair_form():
    # 接收参数
    post_data = request.json
    model_name = 'afc.repair.form'

    data = {
        'create_state': False,
        'repair_form_id': -1
    }

    if post_data.has_key('user_id') and post_data.has_key('repair_apply_id') and post_data.has_key('solution_ids'):
        user_id = post_data['user_id']
        repair_apply_id = post_data['repair_apply_id']
        solution_ids = post_data['solution_ids']

        if user_id is not None and repair_apply_id and solution_ids:
            user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'res.users', 'search',
                                                [[['id', '=', user_id]]])
            repair_apply_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                        'afc.repair.apply', 'search',
                                                        [[['id', '=', int(repair_apply_id)]]])
            if user_ids and repair_apply_ids:
                res_repair_applys = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                             'afc.repair.apply', 'read',
                                                             [int(repair_apply_id)],
                                                             {'fields': ['deviceId',
                                                                         'applyType',
                                                                         'fault_type_1',
                                                                         'fault_type_2'
                                                                         ]})

                if res_repair_applys[0]:
                    res_repair_apply = res_repair_applys[0]
                    # 设备
                    if res_repair_apply.has_key('deviceId') and res_repair_apply['deviceId']:
                        device_id = res_repair_apply['deviceId'][0]
                    # 故障原因
                    if res_repair_apply.has_key('applyType'):
                        apply_type = res_repair_apply['applyType']
                        if apply_type == 'type_1' and res_repair_apply.has_key('fault_type_1') \
                                and res_repair_apply['fault_type_1']:
                            fault_id = res_repair_apply['fault_type_1'][0]
                        elif apply_type == 'type_2' and res_repair_apply.has_key('fault_type_2') \
                                and res_repair_apply['fault_type_2']:
                            fault_id = res_repair_apply['fault_type_2'][0]
                        else:
                            fault_id = False

                res_solution_items = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                              'afc.solution.item', 'search_read',
                                                              [[['id', 'in', solution_ids]]],
                                                              {'fields': ['name']})
                num = 1
                context = ''
                for item in res_solution_items:
                    item_name = item['name']
                    context_item = str(num) + '. ' + item_name + '。'
                    num = num + 1
                    context = context + context_item

                model_data = {
                    'deviceId': int(device_id),
                    'userId': int(user_id),
                    'faultReason': int(fault_id),
                    'solutions': str(context)
                }

                model_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                    model_name, 'create',
                                                    [model_data])
                if type(model_id) == int:
                    data = {
                        'create_state': True,
                        'repair_form_id': int(model_id)
                    }
                    return jsonify({'data': data})

    return jsonify({'data': data})


@repair_blueprint.route('/get_repair_form_info', methods=['GET'])
def get_repair_form_info():
    # 接收参数
    user_id = request.args.get('user_id', None)
    repair_form_id = request.args.get('repair_form_id', None)
    model_name = 'afc.repair.form'

    # 构建一个model层列表
    data_model = []

    if user_id and repair_form_id:
        user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['id', '=', int(user_id)]]])
        repair_form_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                   model_name, 'search',
                                                   [[['id', '=', int(repair_form_id)]]])
        if user_ids and repair_form_ids:
            # 对model数据查询
            dict_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                model_name, 'fields_get',
                                                [],
                                                {'attributes': ['string', 'type', 'help']})

            value_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                 model_name, 'search_read',
                                                 [[['id', '=', int(repair_form_id)]]])

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
                                              'is_readonly': False,
                                              'display_name': dict_res[i]['string'],
                                              'field_type': dict_res[i]['type'],
                                              'field_value': value_res[0][i],
                                              "field_order": dict_res[i]['help'],
                                              'field_params': {}}
                                # 设备参数
                                if str(dict_model['field_type']) == "many2one":
                                    dict_model['field_value'] = value_res[0][i][1]
                                    dict_model['field_params']['field_id'] = value_res[0][i][0]

                                data_model.append(dict_model)
                # 冒泡排序
                for i in range(len(data_model) - 1):
                    for j in range(len(data_model) - i - 1):
                        if data_model[j]['field_order'] > data_model[j + 1]['field_order']:
                            data_model[j], data_model[j + 1] = data_model[j + 1], data_model[j]

    return jsonify({'data': data_model})


@repair_blueprint.route('/post_update_repair_form', methods=['POST'])
def post_update_repair_form():
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    # 接收参数
    post_data = request.json

    model_name = 'afc.repair.form'

    if post_data.has_key('user_id') and post_data.has_key("data") and post_data.has_key("repair_form_id"):
        user_id = post_data['user_id']
        repair_form_id = post_data['repair_form_id']
        json_data = post_data['data']
        if user_id and repair_form_id:
            user_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                'res.users', 'search',
                                                [[['id', '=', int(user_id)]]])
            repair_form_ids = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                       model_name, 'search',
                                                       [[['id', '=', int(repair_form_id)]]])

            if user_ids and repair_form_ids and json_data != []:
                model_data = {}

                for res in json_data:
                    field_name = res['field_name']
                    field_type = res['field_type']
                    field_value = res['field_value']
                    if field_type == 'boolean':
                        if field_value == 'true':
                            field_value = True
                        else:
                            field_value = False

                    if field_type == 'many2one':
                        field_value = int(res['field_params']['field_id'])
                    print field_name
                    model_data[field_name] = field_value
                print model_data

                is_success_1 = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                        model_name, 'write',
                                                        [[int(repair_form_id)], model_data])
                if is_success_1:
                    # 从服务端redis中获取存入的当前维修单对应的任务id
                    if r.get('task_id') and r.get('task_id') is not None:
                        task_id_str = r.get('task_id')
                        task_id = json.loads(task_id_str)
                        if task_id:
                            is_success_2 = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                                    'afc.repair.task', 'write',
                                                                    [[int(task_id)],
                                                                     {'is_complete': True}])
                            if is_success_2:
                                return jsonify({'data': True})
    return jsonify({'data': False})


def post_repair_form_data_to_redis(data):
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    # 非空处理
    if data is not None and data.has_key('user_id') and data.has_key('device_id') and data.has_key('fault_id'):
        # 处理数据格式问题：去u
        json_data_for_redis = json.dumps(data)
        r.set('form_data_for_redis', json_data_for_redis)
        if r.get('form_data_for_redis') and r.get('form_data_for_redis') is not None:
            get_data_for_redis = r.get('form_data_for_redis')
            json_get_data_for_redis = json.dumps(get_data_for_redis)
            if json_get_data_for_redis['device_id'] == json_data_for_redis['device_id']:
                return jsonify({'data': True})

    return jsonify({'data': False})
