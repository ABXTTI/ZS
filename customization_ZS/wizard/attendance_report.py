from odoo import models, fields, api
import pytz
import datetime
import random
from odoo import api, models

class AttListCust(models.TransientModel):
    _name = "att.list.cust"

    x_date = fields.Char(string="Date")
    x_dayname = fields.Char(string="Day Name")
    x_employee_id = fields.Many2one('hr.employee', string="Employee_id")
    x_shift = fields.Char(string="Shift")
    x_starttime = fields.Char(string="start Time")
    x_endtime = fields.Char(string="End Time")
    x_shifhours = fields.Char(string="Shift Hours")
    x_checkin = fields.Char(string="Check In")
    x_checkout = fields.Char(string="Check Out")
    x_overtime = fields.Char(string="Overtime")
    x_daytype = fields.Char(string="Day Type")
    x_status = fields.Char(string="Status")
    x_leavetype = fields.Char(string="Leave Type")
    x_latein = fields.Char(string="Late In")
    x_earlyout = fields.Char(string="Early Out")
    x_workedhours = fields.Char(string="Worked Hours")
    wizard_id = fields.Many2one("attendance.report.wizard", string="Wiz Id")

class AttendanceReportWizardPre(models.Model):
    _name = "attendance.report.wizard"

    select_all_employees = fields.Boolean(string="Select All Employees")
    person_ids = fields.Many2many('hr.employee', string="Employees")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    employee_id = fields.Many2one('hr.employee')
    data = fields.Binary(compute="generate_report")
    attendance_list = fields.One2many('att.list.cust', 'wizard_id', copy=True,
                                             string='Attendance List', readonly=False)


    @api.onchange('select_all_employees')
    def select_employees(self):
        if self.select_all_employees:
            # print(type(self.person_ids))
            var = self.env['hr.employee'].search([('id', '>', 0)])
            # print(type(var))
            list = []
            for rec in var:
                list.append(rec.id)
            self.person_ids = list
        else:
            self.person_ids = [(6, 0, [])] # for clearing the selected employees

    def generate_report(self):
        user_tz = pytz.timezone(self.env.context.get('tz')) or self.env.user.tz
        for employee in self.person_ids:
            if self.env["attendance.report.wizard"].search([('employee_id', '=', employee.id)]):
                break
            else:
                data = {
                    'model': 'attendance.report.wizard',
                    'form': self.read()[0]
                }
                selected_person = employee
                attendances = self.env['hr.attendance'].search([('employee_id', '=', selected_person.id),
                                                                ('check_in', '>=', self.date_from),
                                                                ('check_in', '<=', self.date_to)])
                self.attendance_list = [(5, 0, 0)]
                attendances_list = []
                for att in attendances:
                    attendances_list.append((0, 0, {
                        'x_date': att.x_day,
                        'x_dayname': att.day_name,
                        'x_employee_id': employee.id,
                        'x_shift': att.x_shift_attendance.name,
                        'x_starttime': att.start_time,
                        'x_endtime': att.end_time,
                        'x_shifhours': att.shift_hours,
                        'x_checkin': att.check_in,
                        'x_checkout': att.check_out,
                        'x_overtime': round(att.rule_overtime, 2),
                        'x_daytype': att.day_type,
                        'x_status': att.state,
                        'x_leavetype': att.leave_type.name,
                        'x_latein': att.late_in,
                        'x_earlyout': att.early_out,
                        'x_workedhours': round(att.worked_hours, 2)
                    }))

                var_obj = self.env['attendance.report.wizard']
                var_obj.create({
                    'employee_id': employee.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'attendance_list': attendances_list,
                })
                print(data)
                print(self.data)