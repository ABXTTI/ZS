# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date
import pytz

class HrContract(models.Model):
    _inherit = "hr.contract"
    mobile_allowance = fields.Monetary(string="Mobile Allowance", store=True)
