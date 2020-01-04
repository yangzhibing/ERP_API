# -*- coding: utf-8 -*-
from odoo import models, fields


class FaultModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 14:28
    Version : 1.0
    """
    _name = 'afc.fault'

    FAULT_TYPE = [
        ('type_1', '整机故障'),
        ('type_2', '模块故障')
    ]
    name = fields.Char(string="故障名称", help='1')
    faultType = fields.Selection(FAULT_TYPE, string="故障类型", help='2')
    deviceID = fields.Many2one('afc.device', string="所属设备", help='3')
    moduleID = fields.Many2one('afc.module', string="所属模块", help='4')
    faultContent = fields.Char(string="故障内容", help='5')
    # _log_access = False
