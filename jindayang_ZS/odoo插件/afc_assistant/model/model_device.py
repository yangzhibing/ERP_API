# -*- coding: utf-8 -*-
from odoo import models, fields


class DeviceModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 14:28
    Version : 1.0
    """
    _name = 'afc.device'

    name = fields.Char(string="设备名称", help='1')
    deviceType = fields.Char(string="设备类型", help='2')
    deviceCode = fields.Char(string="设备编码", help='3')
    country = fields.Char(string="国家", help='4')
    city = fields.Char(string="城市", help='5')
    line = fields.Char(string="线路", help='6')
    station = fields.Char(string="车站", help='7')
    itemModels = fields.One2many('afc.device.item', 'device_id', string="设备参数列表", help='8')
    # _log_access = False


class DeviceItemModel(models.Model):
    _name = 'afc.device.item'

    device_id = fields.Many2one('afc.device', string='设备')
    name = fields.Char(string="参数名", help='1')
    value = fields.Char(string="参数值", help='2')
    # _log_access = False
