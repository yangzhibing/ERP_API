# -*- coding: utf-8 -*-
from odoo import models, fields


class RepairFormModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 14:28
    Version : 1.0
    """
    _name = 'afc.repair.form'
    PART_TYPE = [
        ('type_1', '是'),
        ('type_2', '否')
    ]
    DELAY_TYPE = [
        ('type_1', '是'),
        ('type_2', '否')
    ]

    deviceId = fields.Many2one('afc.device', string="设备", help='1')
    userId = fields.Many2one("res.users", string="维修人", help='2')
    faultReason = fields.Many2one('afc.fault', string="故障原因", help='3')
    solutions = fields.Text(string="解决方案", help='4')
    repairParts = fields.Boolean(string="是否更换备件", help='5')
    delayReason = fields.Boolean(string="是否延迟", help='6')
    remarks = fields.Text(string="备注信息", help='7')
    # _log_access = False
