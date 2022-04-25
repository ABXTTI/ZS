# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta
from collections import defaultdict

import odoo.exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.exceptions import UserError

from odoo import models, fields, api, _
from datetime import datetime

class BundlePackage(models.Model):
    _name = "bundle.package"
    _description = "Create Bundles Package"

    name = fields.Char(string="Name")

    @api.onchange('ref')
    def onchange_ref(self):
        self.product_id = self.ref.product_id.id
        self.product_quantity = self.ref.product_qty

    product_id = fields.Many2one("product.product", string="Product")
    product_quantity = fields.Float(string="Product Quantity")
    required_bundle_size = fields.Float(string="Bundle Size")
    date = fields.Datetime(string="Date", default=datetime.now())
    product_color = fields.Char(string="Color")
    product_sizes = fields.Char(string="Product Sizes")
    ref = fields.Many2one("mrp.production", string="ref")
    bundle_package_line_ids = fields.One2many("bundle.package.line", "parent_id", string="Bundle Package Lines")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('cancel', 'Cancelled')],
        'State', default="draft", ondelete='restrict')


    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_reset(self):
        for rec in self:
            rec.state = 'draft'

    def fetch_values_sale_order(self):
        so_id = self.env['sale.order'].search([('name', '=', self.ref.origin)])
        if so_id:
            if len(so_id.order_line) > 1:
                raise UserError("Sale Order Line Contains More Than 1 Line")
            else:
                # fields = so_id.order_line._fields
                # fields_list = []
                # for rec in fields:
                #     fields_list.append(rec)
                # start_num = 42
                # end_num = 86
                # relevent_fields_list = fields_list[start_num:end_num]
                relevent_fields_list = [
                                        'x_1_2', 'x_2_3', 'x_3_4', 'x_4_5', 'x_5_6', 'x_6_7', 'x_7_8', 'x_8_9', 'x_9_10', 'x_10_11', 'x_11_12', 'x_12_13', 'x_13_14', 'x_14_15', 'x_16_17', 'x_18_19', 'x_20_21', 'x_0', 'x_2', 'x_4',
                                        'x_6', 'x_8', 'x_10', 'x_12', 'x_14', 'x_16', 'x_18', 'x_20', 'x_22', 'x_24', 'x_26', 'x_28', 'x_30', 'x_xxs', 'xs_small', 'x_small', 'x_medium', 'x_large', 'x_xl', 'x_xxl', 'x_3xl', 'x_4xl',
                                        'x_5xl', 'x_6xl'
                                        ]
                self.product_color = so_id.order_line.x_color
                sum_qty = 0.0
                true_fields = []
                for rec in relevent_fields_list:
                    val = so_id.order_line[rec]
                    if val:
                        sum_qty += val
                        true_fields.append(rec)
                self.product_sizes = str(true_fields)
                if sum_qty != self.product_quantity:
                    raise UserError("Total Quantity Does Not Match with total lines Quantity !!!!!!")
                else:
                    pass
                factor = 0.0
                if self.required_bundle_size:
                    factor = sum_qty / self.required_bundle_size
                    int_factor = int(factor)
                    modulus = sum_qty % self.required_bundle_size
                    print(modulus)
                    vals = []
                    for rec in range(0, int_factor):
                        vals.append((0,0, {
                            'description': self.product_id.name,
                            'product_qty': self.required_bundle_size,
                            'bundle_contains_qty': self.required_bundle_size,
                            'bundle_count': 1,
                        }))
                    if modulus:
                        vals.append((0,0, {
                            'description': self.product_id.name,
                            'product_qty': modulus,
                            'bundle_contains_qty': modulus,
                            'bundle_count': 1,
                        }))
                    self.bundle_package_line_ids = [(5, 0, 0)]
                    self.bundle_package_line_ids = vals
                    print(factor)
                else:
                    raise UserError("Bundle Size is not Greater than '0'...!!!!!!")

    def unlink(self):
        if self.state != 'draft':
            raise odoo.exceptions.ValidationError("You Cannot Delete This Doc.!!!!!")

        rtn = super(BundlePackage, self).unlink()
        return rtn


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.bundle.package') or 'New'

        result = super(BundlePackage, self).create(vals)
        return result


class BundlesPackageLine(models.Model):
    _name = "bundle.package.line"
    _description = "Create your Bundle line"

    name = fields.Char(string="Sequence")
    description = fields.Char(string="Description")
    product_size = fields.Char(string="Product Size")
    date = fields.Datetime(string="Date", default=datetime.now())
    product_qty = fields.Float(string="Product Qty.")
    bundle_contains_qty = fields.Float(string="Product Qty./Bundle Size")
    bundle_count = fields.Float(string="Bundles Qty.")
    product_id = fields.Many2one("product.product", string="Product", related="parent_id.product_id", store=True)
    parent_id = fields.Many2one("bundle.package", string="Bundle Package ID", readonly=True)
    parent_date = fields.Datetime(string='Parent Date', related="parent_id.date", readonly=True, store=True)
    parent_state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('cancel', 'Cancelled')],
        'State', related="parent_id.state", readonly=True, store=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sequence.bundle.package.line') or 'New'

        result = super(BundlesPackageLine, self).create(vals)
        return result