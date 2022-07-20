# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_category = fields.Many2one("product.category", string="Product Category", related="product_id.categ_id", store=True)