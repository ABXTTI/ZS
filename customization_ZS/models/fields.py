# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_voucherdate = fields.Date(string="Voucher Date", required=False)

    @api.depends('invoice_origin')
    def _find_ordertype(self):
        for rec in self:
            if len(rec) > 0:
                x_order_id = self.env['purchase.order'].search([('name', '=', rec.invoice_origin)])
                rec.x_purchaseorderref = x_order_id
                rec.x_typeref = rec.x_purchaseorderref.x_type
                # if self.env['purchase.order'].search([('x_type', 'contain', "Import")]):
                if str(rec.x_typeref).find("Import"):
                    rec.x_gdnumber = x_order_id.x_gdnumber
                    rec.x_containernumber = x_order_id.x_containernumber

    x_typeref = fields.Many2one('x.type', string="Order Type", compute='_find_ordertype', readonly=False)
    x_gdnumber = fields.Char(string="GD #", compute='_find_ordertype', store=True, readonly=False)
    x_containernumber = fields.Char(string="Container #", compute='_find_ordertype', store=True, readonly=False)
    x_purchaseorderref = fields.Many2one('purchase.order', string="Purchase Order Ref", compute='_find_ordertype')

class Partner(models.Model):
    _inherit = 'res.partner'

    x_strn = fields.Char(string="STRN #", required=True)
    x_cheq_to = fields.Char(string="Cheque To", required=True)

class StockMove(models.Model):
    _inherit = 'stock.move'

    x_hscoderef = fields.Char(string="HS Code", related='product_id.x_hscode')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('origin')
    def _find_ordertype(self):
        for rec in self:
            if len(rec) > 0:
                x_order_id = self.env['purchase.order'].search([('name', '=', rec.origin)])
                rec.x_purchaseorderref = x_order_id
                rec.x_type = rec.x_purchaseorderref.x_type
                # if self.env['purchase.order'].search([('x_type', 'contain', "Import")]):
                if str(rec.x_type).find("Import"):
                    rec.x_gdnumber = x_order_id.x_gdnumber
                    rec.x_containernumber = x_order_id.x_containernumber


    x_type = fields.Many2one('x.type', string="Order Type", compute='_find_ordertype', store=True, readonly=False)
    x_gdnumber = fields.Char(string="GD #", compute='_find_ordertype', store=True, readonly=False)
    x_containernumber = fields.Char(string="Container #", compute='_find_ordertype', store=True, readonly=False)
    x_purchaseorderref = fields.Many2one('purchase.order', string="Purchase Order Ref", compute='_find_ordertype')
    x_netweight = fields.Char(string="Net Weight (kg)", required=False)




class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_type = fields.Many2one('x.type', string="Order Type", required=False)
    x_gdnumber = fields.Char(string="GD #")
    x_containernumber = fields.Char(string="Container #")
    x_saleorderref = fields.Many2one('sale.order', string="Sale Order Ref")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_hscoderef = fields.Char(string="HS Code", related='product_id.x_hscode', readonly=True)


# adding HS code field in Product form
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_hscode = fields.Char(string="HS Code")


# creating new table for category
class XType(models.Model):
    _name = 'x.type'

    _rec_name = 'x_type'

    x_type = fields.Char(string="Category")


class XCategory(models.Model):
    _name = 'x.category'

    _rec_name = 'x_category'

    x_category = fields.Char(string="Category")


# adding new fild in sale order to add many 2 one field from the above new table i-e category
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_category = fields.Many2one('x.category', string="Category")


# creating new fields in sale order lines
class SaleOrderLines(models.Model):
    _inherit = 'sale.order.line'

    x_hscoderef = fields.Char(string="HS Code", related='product_id.x_hscode', readonly=True)

    x_1_2 = fields.Float(string="1-2")
    x_2_3 = fields.Float(string="2-3")
    x_3_4 = fields.Float(string="3-4")
    x_4_5 = fields.Float(string="4-5")
    x_5_6 = fields.Float(string="5-6")
    x_6_7 = fields.Float(string="6-7")
    x_7_8 = fields.Float(string="7-8")
    x_8_9 = fields.Float(string="8-9")
    x_9_10 = fields.Float(string="9-10")
    x_10_11 = fields.Float(string="10-11")
    x_11_12 = fields.Float(string="11-12")
    x_12_13 = fields.Float(string="12-13")
    x_13_14 = fields.Float(string="13-14")
    x_14_15 = fields.Float(string="14-15")
    x_16_17 = fields.Float(string="16-17")
    x_18_19 = fields.Float(string="18-19")
    x_20_21 = fields.Float(string="20-21")
    x_0 = fields.Float(string="0")
    x_2 = fields.Float(string="2")
    x_4 = fields.Float(string="4")
    x_6 = fields.Float(string="6")
    x_8= fields.Float(string="8")
    x_10 = fields.Float(string="10")
    x_12 = fields.Float(string="12")
    x_14 = fields.Float(string="14")
    x_16 = fields.Float(string="16")
    x_18 = fields.Float(string="18")
    x_20 = fields.Float(string="20")
    x_22 = fields.Float(string="22")
    x_24 = fields.Float(string="24")
    x_26 = fields.Float(string="26")
    x_28 = fields.Float(string="28")
    x_30 = fields.Float(string="30")
    x_xxs = fields.Float(string="XXS")
    xs_small = fields.Float(string="XS")
    x_small = fields.Float(string="S")
    x_medium = fields.Float(string="M")
    x_large = fields.Float(string="L")
    x_xl = fields.Float(string="XL")
    x_xxl = fields.Float(string="2XL")
    x_3xl = fields.Float(string="3XL")
    x_4xl = fields.Float(string="4XL")
    x_5xl = fields.Float(string="5XL")
    x_6xl = fields.Float(string="6XL")
    product_uom_qty = fields.Float(string="T.Quantity", compute='compute_quantity')

    @api.depends('x_small', 'x_medium', 'x_large', 'x_xl')
    def compute_quantity(self):
        for rec in self:
            rec.product_uom_qty = rec.x_small + rec.x_medium + rec.x_large + rec.x_xl
            return rec.product_uom_qty
