# -*- coding: utf-8 -*-
from odoo import models, fields


class RepairApplyModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 15:45
    Version : 1.0
    """
    _name = 'afc.repair.apply'

    APPLY_TYPE = [
        ('type_1', '整机报修'),
        ('type_2', '模块报修')
    ]

    WORKFLOW_STATE_SELECTION = [
        ('draft', '草稿'),
        ('sel_type', "报修类型选择"),
        ('sel_module', '模块选择'),
        ('sel_fault', '故障填写'),
        ('commit', '提交报修单')
    ]

    name = fields.Char(string="报修单号", help='0')
    deviceId = fields.Many2one('afc.device', string='设备', help='1')
    applyType = fields.Selection(APPLY_TYPE, string="报修类型", help='2')
    userId = fields.Many2one("res.users", string="报修人", help='3')
    module = fields.Many2one('afc.module', string="报修模块", help='4')
    fault_type_1 = fields.Many2one('afc.fault', string="报修故障(整机)", help='5')
    fault_type_2 = fields.Many2one('afc.fault', string="报修故障(模块)", help='6')
    recordContent = fields.Text(string="报修记录内容", help='7')
    is_allocation = fields.Boolean(string="已分配任务", help='8')

    state = fields.Selection(WORKFLOW_STATE_SELECTION, default='draft', string="状态", readonly=True)

    # _log_access = False
