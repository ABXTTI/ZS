# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date
import pytz
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name + " " + "[" + str(rec.device_id) + "]"
            result.append((rec.id, name))
        return result

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    piece_rate_operations_ids = fields.One2many('piece.rate.operations', 'production_id', string="Piece Rate Operations")
    piece_rate_ids = fields.One2many('piece.rate', 'production_id', string="Piece Rate Ids")
    so_id = fields.Many2one("sale.order", string="Sale Order ID")
    so_line_id = fields.Many2one("sale.order.line", string="Sale Order Line ID")

    @api.constrains('piece_rate_operations_ids')
    def create_line_in_piece_rate(self):
        piece_rate_ids = self.piece_rate_ids
        var = []
        for rec in self.piece_rate_operations_ids:
            flag = False
            for record in piece_rate_ids:
                if record.operation_id:
                    if record.operation_id == rec.operation_id:
                        record.rate = rec.rate
                        flag = True
            if flag == False:
                var.append((0, 0, {
                    'operation_id': rec.operation_id.id,
                    'rate': rec.rate,

                }))
        self.piece_rate_ids = var



    @api.constrains('piece_rate_ids', 'piece_rate_operations_ids')
    def check_qty_each_operation(self):
        operations_unique = []
        piece_rate_actual = self.piece_rate_ids
        operations_piece_rate = self.piece_rate_operations_ids
        for rec in operations_piece_rate:
            operations_unique.append(rec.operation_id.id)
            piece_rate_related = piece_rate_actual.search([('operation_id', '=', rec.operation_id.id),
                                                           ('production_id', '=', self.name)])
            print("Piece Rate Actual : ", piece_rate_related)
            total_qty_piece_rate_actual = 0
            for operation in piece_rate_related:
                print("operation_id: ", operation.operation_id.name, " qty: ", operation.qty)
                total_qty_piece_rate_actual += operation.qty
            print("Total Quantity piece rate: ", total_qty_piece_rate_actual)
            if total_qty_piece_rate_actual > rec.total_qty:
                raise ValidationError("Per Operation Total Quantity Cannot Be More than Mentioned in 'Piece Rate Operation' Tab for operation"
                                      + " " + "'" + rec.operation_id.name + "'")

        for rec in piece_rate_actual:
            if rec.operation_id.id not in operations_unique:
                raise ValidationError("'" + rec.operation_id.name + "'" + "is not in 'Piece Rate Operation' Form")
        # # print(rec.abc)
        #
        #

class PieceRateOperations(models.Model):
    _name = "piece.rate.operations"
    _description = 'Piece Rate Operations Lines'
    _order = 'production_id, sequence'

    name = fields.Char(string='Description', required=False)
    production_id = fields.Many2one('mrp.production', string='Production Order', required=False, ondelete='cascade',
                                    index=True,
                                    help="Production Order")
    sequence = fields.Integer(required=True, index=True, default=10, help="Sequence")
    operation_id = fields.Many2one('piece.rate.operation', string="Operation", required=True)
    operation_code = fields.Char(string="Operation Code", related="operation_id.code")
    operation_qty = fields.Float(string="Operation Qty.", default=0)

    @api.onchange('operation_id')
    def onchange_operation_id(self):
        self.rate = self.operation_id.rate
        operations = self.search([('operation_id', '=', self.operation_id.id), ('production_id', '=', self.production_id.name)])
        if operations:
            raise ValidationError("You are repeating the same operation !!!!!!!!!")

    rate = fields.Float(string="Rate")

    @api.depends('operation_qty')
    def cal_total_qty(self):
        for rec in self:
            rec.total_qty = rec.production_id.product_qty * rec.operation_qty

    total_qty = fields.Float(string="Operation Total Qty", default=1, compute="cal_total_qty")


    @api.depends('operation_qty', 'total_qty', 'rate')
    def cal_total_amount(self):
        for rec in self:
            rec.total_amount = rec.total_qty * rec.rate

    total_amount = fields.Float(string="Estimated Total", compute="cal_total_amount")

class PieceRate(models.Model):
    _name = "piece.rate"
    _description = 'Piece Rate Lines'
    _order = 'production_id, sequence'

    name = fields.Char(string='Description', required=False)
    production_id = fields.Many2one('mrp.production', string='Production Order', required=False, ondelete='cascade', index=True,
                                 help="Production Order")
    sequence = fields.Integer(required=True, index=True, default=10, help="Sequence")
    operation_id = fields.Many2one('piece.rate.operation', string="Operation", required=True)
    operation_code = fields.Char(string="Operation Code", related="operation_id.code")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    qty = fields.Float(string="Qty", default=0)
    bundle_id = fields.Many2one('bundle.package.line', string="Bundle" )

    @api.onchange('operation_id')
    def onchange_operation_id(self):
        operation_line = self.env['piece.rate.operations'].search([('operation_id', '=', self.operation_id.id),
                                                                  ('production_id', '=', self.production_id.name)])
        self.rate = operation_line.rate

    rate = fields.Float(string="Rate", readonly=True)

    @api.depends('qty', 'rate')
    def cal_total_amount(self):
        for rec in self:
            rec.total_amount = rec.qty * rec.rate

    total_amount = fields.Float(string="Total", compute="cal_total_amount", store=True)
    is_completed = fields.Boolean(string="Is Completed", default=False)
    complete_date = fields.Date(string="Date Completed")

class PieceRateOperation(models.Model):
    _name = "piece.rate.operation"
    _description = "Piece Rate Operation"

    name = fields.Char(string="Operation Name", required=True)
    code = fields.Char(string="Operation Code", Required=True)
    rate = fields.Float(string="Rate /pcs")