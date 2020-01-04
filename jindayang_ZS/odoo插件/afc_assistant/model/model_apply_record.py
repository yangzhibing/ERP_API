# -*- coding: utf-8 -*-
from odoo import models, fields


class ApplyRecordModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 14:28
    Version : 1.0
    """
    _name = 'afc.apply.record'

    recordContent = fields.Char(string="报修记录内容")
    # _log_access = False
