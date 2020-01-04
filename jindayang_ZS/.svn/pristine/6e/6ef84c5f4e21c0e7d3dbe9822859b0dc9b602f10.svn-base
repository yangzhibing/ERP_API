# -*- coding: utf-8 -*-
from odoo import models, fields


class RepairTaskModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 15:45
    Version : 1.0
    """
    _name = 'afc.repair.task'

    RepairApplyId = fields.Many2one('afc.repair.apply', string="报修单号", help='1')
    repair_user_id = fields.Many2one("res.users", string="分配维修人", help='2')
    is_confirm = fields.Boolean(string="是否已确认", help='3')
    is_complete = fields.Boolean(string="是否已完成", help='4')
