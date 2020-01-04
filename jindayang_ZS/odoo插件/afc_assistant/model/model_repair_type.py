# -*- coding: utf-8 -*-
from odoo import models, fields


class RepairTypeModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 16:15
    Version : 1.0

    """
    _name = 'afc.repair.type'

    name = fields.Char(string="报修类型")
    faultId = fields.Char(string="故障Id")
    moduleId = fields.Char(string="模块id")
    moduleName = fields.Char(string="模块名称")
    # _log_access = False
