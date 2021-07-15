# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date
import pytz
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    piece_rate_ids = fields.One2many('piece.rate', 'production_id', string="Piece Rate Ids")

class PieceRate(models.Model):
    _name = "piece.rate"
    _description = 'Piece Rate Lines'
    _order = 'production_id, sequence'

    name = fields.Char(string='Description', required=True)
    production_id = fields.Many2one('mrp.production', string='Production Order', required=False, ondelete='cascade', index=True,
                                 help="Production Order")
    sequence = fields.Integer(required=True, index=True, default=10, help="Sequence")
    operation_id = fields.Many2one('piece.rate.operation', string="Operation", required=True)
    operation_code = fields.Char(string="Operation Code", related="operation_id.code")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    qty = fields.Float(string="Qty", default=1)

    @api.onchange('operation_id')
    def onchange_operation_id(self):
        self.rate = self.operation_id.rate

    rate = fields.Float(string="Rate")

    @api.depends('qty', 'rate')
    def cal_total_amount(self):
        self.total_amount = self.qty * self.rate

    total_amount = fields.Float(string="Total", compute="cal_total_amount", store=True)
    is_completed = fields.Boolean(string="Is Completed", default=False)
    complete_date = fields.Date(string="Date Completed")


class PieceRateOperation(models.Model):
    _name = "piece.rate.operation"
    _description = "Piece Rate Operation"

    name = fields.Char(string="Operation Name", required=True)
    code = fields.Char(string="Operation Code", Required=True)
    rate = fields.Float(string="Rate /pcs")