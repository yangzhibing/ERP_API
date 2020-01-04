# -*- coding: utf-8 -*-
from odoo import models, fields


class AttributeElementModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 15:45
    Version : 1.0
    """
    _name = 'afc.attribute.element'

    name = fields.Char(string="数据名称")
    value = fields.Char(string="数据值")
    type = fields.Char(string="数据类型")
    positionNumber = fields.Char(string="显示位置")
    # _log_access = False
