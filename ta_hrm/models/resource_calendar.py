from odoo import tools
from odoo import models, fields, api, _
import datetime
from datetime import date
import calendar

class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    is_night_shift = fields.Boolean(string="Is Night Shift", store=True)


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    hour_to_night_shift = fields.Float(string="Work To Night Shift", store=True)
    margin_work_from = fields.Float(string="Margin Work From", store=True, required=True)
    margin_work_to = fields.Float(string="Margin Work To", store=True, required=True)
    shift_hours = fields.Float(string="Shift Hours", default=9, required=True)

    api.depends('margin_work_from', 'margin_work_to', 'shift_hours')
    def compute_available_hours(self):
        for rec in self:
            rec.cin_cout_in_hours = rec.margin_work_to + rec.margin_work_from + rec.shift_hours

    cin_cout_in_hours = fields.Float(string="Available C.In/C.out Hours", compute='compute_available_hours', readonly=True)

class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    @api.depends('date_from')
    def get_date(self):
        for rec in self:
            x = rec.date_from + datetime.timedelta(hours=5)
            rec.x_date = x.date()
            print(rec.x_date, rec.date_from)

    x_date = fields.Char("Day", compute="get_date", store=True)