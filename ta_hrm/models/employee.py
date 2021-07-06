# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date
import pytz


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    x_joining_date = fields.Date(string="Joining Date", store=True)
    is_piece_rate = fields.Boolean(string="Is Piece Rate", store=True)
    is_Overtime = fields.Boolean(string="Is Piece Rate", store=True)
    is_pessi = fields.Boolean(string="Is Piece Rate", store=True)
    is_eobi = fields.Boolean(string="Is Piece Rate", store=True)
    is_late_deduction = fields.Boolean(string="Is Piece Rate", store=True)
    is_earlyout_deduction = fields.Boolean(string="Is Piece Rate", store=True)
    is_attendance_allowance = fields.Boolean(string="Is Piece Rate", store=True)
    father_name = fields.Char(string="Father Name", store=True)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.depends('employee_id')
    def get_employee_detail(self):
        for rec in self:
            rec.x_employee_code = rec.employee_id.device_id
            rec.x_shift_attendance = rec.employee_id.resource_calendar_id.id
            rec.x_department_id = rec.employee_id.department_id
            rec.x_job_id = rec.employee_id.job_id

    x_employee_code = fields.Char(string="Employee Code", compute="get_employee_detail", store=True)
    x_shift_attendance = fields.Many2one('resource.calendar', string="Shift", compute='get_employee_detail', store=True)
    x_department_id = fields.Many2one('hr.department', string="Department", compute='get_employee_detail', store=True)
    x_job_id = fields.Many2one('hr.job', string="Job Position", compute='get_employee_detail', store=True)
    eval_field = fields.Integer(string="Evaluation Field")

    @api.depends('check_in')
    def get_day(self):
        for rec in self:
            user_tz = pytz.timezone(self.env.context.get('tz')) or self.env.user.tz
            check_in_tz = pytz.utc.localize(rec.check_in).astimezone(user_tz)
            rec.x_day = check_in_tz.date()
            rec.day_name = check_in_tz.date().strftime("%A")
    x_day = fields.Char("Date", compute="get_day", store=True)
    day_name = fields.Char("Day Name", compute="get_day", store=True)

    @api.depends('employee_id', 'x_shift_attendance')
    def get_shift_time(self):
        for rec in self:
            shift = self.env['resource.calendar.attendance'].search([('calendar_id', '=', rec.x_shift_attendance.id),
                                                         ('dayofweek', '=', rec.check_in.weekday())])
            if shift:
                rec.start_time = shift.hour_from
                rec.end_time = shift.hour_to_night_shift
                rec.shift_hours = shift.shift_hours

    start_time = fields.Float(string="Start Time", compute="get_shift_time", store=True)
    end_time = fields.Float(string="End Time", compute="get_shift_time", store=True)
    shift_hours = fields.Float(string="Shift Hours", compute="get_shift_time", store=True)

    @api.depends('worked_hours', 'eval_field')
    def get_overtime(self):
        for rec in self:
            print("@@@@@@@@@@@@@ ITS WORKING @@@@@@@@")
            check_in_local = rec.check_in + datetime.timedelta(hours=5) #converting to local time
            day = check_in_local.date()
            print("type:", type(day), "day:", day)
            standard_check_in = datetime.datetime.combine(day, datetime.time()) + datetime.timedelta(hours=rec.start_time)
            standard_check_out = standard_check_in + datetime.timedelta(hours=rec.shift_hours)
            if rec.check_out:
                actual_check_out = rec.check_out + datetime.timedelta(hours=5)
                if check_in_local > standard_check_out:
                    difference = actual_check_out - check_in_local
                    rec.t_overtime = difference.total_seconds()*1/60*1/60
                    if rec.t_overtime >= 0.5:
                        rec.rule_overtime = rec.t_overtime
                    else:
                        rec.rule_overtime = 0
                else:
                    print("day start time !!!!!!!", standard_check_in)
                    day_end_time_actual = actual_check_out
                    print("day end time !!!!!", day_end_time_actual)
                    difference = day_end_time_actual - standard_check_in
                    print("!!!!!!!!!!!!!!!!", difference.total_seconds())
                    rec.t_overtime = difference.total_seconds()*1/60*1/60 - rec.shift_hours

                    print("$$$$$$", rec.t_overtime)
                    if rec.t_overtime >= 0.5:
                        rec.rule_overtime = rec.t_overtime
                    elif rec.t_overtime < 0:
                        rec.t_overtime = 0
                    else:
                        rec.rule_overtime = 0

    t_overtime = fields.Float(string="Total Overtime", compute="get_overtime", store=True)
    rule_overtime = fields.Float(string="Overtime Calc", compute="get_overtime", store=True)

    @api.depends('x_shift_attendance', 'check_in')
    def get_day_type(self):
        print("helo dkfjkfjkfjfkjfkjfkfjk")
        for rec in self:
            public_holiday = rec.env['resource.calendar.leaves'].search([('x_date', '=', rec.x_day), ('resource_id', '=', False)])
            # print("!!!!@@@@ PUBLIC HOLIDAY", public_holiday, public_holiday.name)
            if public_holiday or rec.day_name == "Sunday":
                rec.day_type = "0"
            else:
                rec.day_type = "1"

    day_type = fields.Selection([
        ('0', 'Holiday'),
        ('1', 'Working Day'),
    ], compute="get_day_type", readonly=True)

    leave_type = fields.Many2one('hr.leave.type', string="Leave Type", store=True)
    days_count_before_leave = fields.Float(string="C.Days.before.Leave", default=0, store=True)
    days_count = fields.Float(string="C.Days", default=0, store=True)
    state = fields.Selection([
        ('0', 'Absent'),
        ('1', 'Present'),
        ('2', 'Late In'),
        ('3', 'Early Out'),
        ('4', 'Half Day'),
        ('5', 'Half Day Leave'),
        ('6', 'Leave'),
        ('13', 'Off-Day'),
    ], 'Status', default='0', readonly=True,)

    late_in = fields.Float(string="Late In", store=True)
    early_out = fields.Float(string="Early Out", store=True)


