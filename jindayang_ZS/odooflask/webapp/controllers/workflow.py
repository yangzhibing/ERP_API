# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, request, json
# 导入xmlrpc库，这个库是python的标准库。
import xmlrpclib
import datetime
from os import path
from flask import Blueprint
from ..config import Config

workflow_blueprint = Blueprint(
    'workflow',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'workflow'),
    url_prefix="/workflow"
)


# 获取请假单模板列表
@workflow_blueprint.route('/template/show', methods=['GET'])
def workflow_template_show():
    res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                   'workflow', 'search_read',
                                   [],
                                   {'fields': ['name', 'osv']})
    return jsonify({'data': {'workflow_template': res}})


# 发起工作流程
@workflow_blueprint.route('/template/init', methods=['POST'])
def workflow_template_init():
    # 接收参数
    json_data = request.json
    print json_data
    # 非空处理
    if json_data is None or json_data["osv"] is None:
        return jsonify({'data': ""})
    else:

        model_name = json_data["osv"]

        # 对model数据查询
        dict_res = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            model_name, 'fields_get',
                                            [],
                                            {'attributes': ['string', 'help', 'type']})
        print dict_res
        # 检查数据类型
        print "返回值的类型：", type(dict_res)

        # 构建返回数据外层框架
        data = {'osv': model_name,
                'workflow': {},
                'action': {},
                'model': []}

        # 构建一个model层列表
        data_model = []

        # 遍历赋值过程
        for i in dict_res:
            if i in Config.ignore_fields:
                continue
            else:
                if i == "state":
                    dict_workflow = {
                        "state_show": {},
                        "current_state": i
                    }
                    # 并入列表
                    data['workflow'] = dict_workflow
                else:
                    # 构建一个model层下的字典,并赋值
                    dict_model = {'field_name': i,
                                  'display_name': dict_res[i]['string'],
                                  'field_type': dict_res[i]['type'],
                                  'field_value': '',
                                  "field_order": dict_res[i]['help'],
                                  'field_params': {}}
                    # 参数属性处理过程
                    # 并入列表
                    data_model.append(dict_model)
        # 冒泡排序
        for i in range(len(data_model) - 1):
            for j in range(len(data_model) - i - 1):
                if data_model[j]['field_order'] > data_model[j + 1]['field_order']:
                    data_model[j], data_model[j + 1] = data_model[j + 1], data_model[j]
        # 并入列表
        data['model'] = data_model
        return jsonify({'data': data})


# 发起工作流程
@workflow_blueprint.route('/instance/handle', methods=['POST'])
def workflow_template_handle():
    # 接收参数
    json_data = request.json
    # 关联模型
    mode_name = json_data["osv"]

    # 构建model-Create-JSON
    model_json = json_data["model"]
    print "参数数据类型：", type(model_json)
    print "model层数据：", model_json

    # 定义model字段字典
    model_data = {}
    # 当前状态
    state = json_data['workflow']['current_state']
    print "当前状态：", state

    # model_data["state"] = state

    # 定义ID初始值为：-1，标识不存在该记录
    # current_id = -1

    # 遍历赋值
    for i in model_json:
        real_value = None
        field_name = i['field_name']
        field_value = i['field_value']
        field_type = i['field_type']
        if field_type in ['char', 'text']:
            real_value = field_value
        if field_type in ['date', 'datetime']:
            real_value = field_value
        if field_type in ['integer']:
            real_value = int(field_value)
        if field_type in ['boolean']:
            if field_value == 1:
                real_value = True
            else:
                real_value = False

        # if field_name == 'id':
        #     current_id = field_value
        #     continue
        model_data[field_name] = real_value
    print model_data

    model_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                        mode_name, 'create',
                                        [model_data])

    # # 根据ID,查询实例存在个数
    # instance_num = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
    #                                         mode_name, 'search_count',
    #                                         [[['id', '=', current_id]]])
    # # 判断实例是否存在，存在就更新，不存在就创建
    # print"已存在实例个数：", instance_num
    # if instance_num == 0:
    #     model_id = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
    #                                         mode_name, 'create',
    #                                         [model_data])
    #     print "新创建ID：", model_id
    # else:
    #     is_success = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
    #                                           mode_name, 'write',
    #                                           [[current_id], [model_data]])
    #     print"更新操作：", is_success
    data = True
    return jsonify({'data': data})
