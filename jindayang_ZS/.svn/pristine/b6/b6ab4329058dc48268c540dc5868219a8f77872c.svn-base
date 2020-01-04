# -*- coding: utf-8 -*-
from odoo import models, fields


class UserModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 15:45
    Version : 1.0
    """
    _name = 'afc.module'

    name = fields.Char(string="模块名称", help='1')
    has_parent = fields.Boolean(string="是否有父模块", help='2')
    deviceID = fields.Many2one('afc.device', string="所属设备", help='3')
    # 此字段应该做过滤
    parentId = fields.Many2one('afc.module', string="父模块", help='4')
    # _log_access = False
