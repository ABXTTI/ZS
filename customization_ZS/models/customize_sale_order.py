# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_image = fields.Binary(string="IMG")
    # client_order_ref = fields.Char(related='x_order_ref', store=True)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_order_ref = fields.Char(string="Order Ref.", store=True)
    x_product_code = fields.Char(string="Product Code", related='product_id.default_code')
    x_product_id = fields.Char(string="Product", related='product_id.name')
    # x_order_ref = fields.Char(string="Order Ref.", related='order_id.x_order_ref')
    x_mzz = fields.Char(string="MZZ", store=True)
    x_color = fields.Char(string="Color", store=True)
    x_actual_color = fields.Char(string="Actual Color", store=True)
    x_commitment_date = fields.Datetime(string="Delivery Date", related='order_id.expected_date')
    x_image = fields.Binary(string="IMG")
    x_itemcode = fields.Char(string="Item Code")
    x_weight = fields.Char(string="Weight")
    x_gadje = fields.Char(string="Gadje")
    x_productionprocessdate = fields.Date(string="Production Process Date")
    x_comments = fields.Char(string="Comments")
    x_shippedby = fields.Selection([('air', "Air"), ('sea', 'Sea')], string="Shipped By")


