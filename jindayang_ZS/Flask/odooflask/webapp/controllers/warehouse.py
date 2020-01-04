# -*- encoding: utf-8 -*-
from flask import jsonify, request, json
from os import path
from flask import Blueprint
from ..config import Config

wh_blueprint = Blueprint(
    'wh',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'wh'),
    url_prefix="/wh"
)


@wh_blueprint.route('/get/erp', methods=['GET'])
def get_test12():
    user_id = request.args.get('user_id', None)

    return user_id


@wh_blueprint.route('/get/other/out', methods=['POST'])
def get_wh_move_other_out():
    data = []
    # json_pro = {}
    # json_pro.update(data)

    # 接收参数
    post_data = request.json
    if post_data.has_key('other_out_num'):
        other_out_num = post_data['other_out_num']

        lines = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                         'wh.move', 'search_read',
                                         [[['name', '=', other_out_num]]],
                                         {'fields': ['line_out_ids']})

        if lines != [] and lines[0].has_key('line_out_ids'):
            item_ids = lines[0]['line_out_ids']
            lines_items = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                                   'wh.move.line', 'search_read',
                                                   [[['id', 'in', item_ids]]],
                                                   {'fields': ['good_name',
                                                               'goods_id',
                                                               'lot',
                                                               'goods_qty',
                                                               'uom_id',
                                                               'goods_uos_qty',
                                                               'uos_id',
                                                               'valid_date',
                                                               ]})
            for item in lines_items:
                good_name = item['good_name']
                goods_num = item['goods_id'][1]
                lot = item['lot']
                goods_qty = item['goods_qty']
                uom_id = item['uom_id'][1]
                goods_uos_qty = item['goods_uos_qty']
                uos_id = item['uos_id'][1]
                valid_date = item['valid_date']

                data_json = Config.data_Json

                dict_model = {
                    'good_name': good_name,
                    'goods_num': goods_num,
                    'lot': lot,
                    'goods_qty': goods_qty,
                    'uom_id': uom_id,
                    'goods_uos_qty': goods_uos_qty,
                    'uos_id': uos_id,
                    'valid_date': valid_date
                }

                data.append(dict_model)

            data_json['success'] = True
            data_json['code'] = "200"
            data_json['message'] = "数据获取成功"
            data_json['data'] = data

            return jsonify(data_json)
    else:
        return jsonify(Config.data_Json)
