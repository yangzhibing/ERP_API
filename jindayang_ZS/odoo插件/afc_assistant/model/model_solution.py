# -*- coding: utf-8 -*-
from odoo import models, fields


class SolutionModel(models.Model):
    """
    Author  : ZNB
    Date    : 2017/9/04 16:28
    Version : 1.0
    """
    _name = 'afc.solution'

    name = fields.Char(string="方案分类", help='2')
    faultName = fields.Many2one('afc.fault', string="故障名称", help='1')
    solutionItemModels = fields.One2many('afc.solution.item', 'solution_id', string="解决方案列表", help='2')

    # _log_access = False


class SolutionItemModel(models.Model):

    _name = 'afc.solution.item'

    solution_id = fields.Many2one('afc.solution', string='故障解决方案', help='1')
    name = fields.Char(string="解决方案", help='2')
    genre = fields.Char(string="方案分类", help='3')

    # _log_access = False
