# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date
import pytz

class HrPayslipWorkedDaysActual(models.Model):
    _name = 'hr.payslip.worked_days_actual'
    _description = 'Payslip Worked Days'
    _order = 'payslip_id, sequence'

    name = fields.Char(string='Description', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True, help="Payslip")
    sequence = fields.Integer(required=True, index=True, default=10, help="Sequence")
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    number_of_days = fields.Float(string='Number of Days', help="Number of days worked")
    number_of_hours = fields.Float(string='Number of Hours', help="Number of hours worked")
    amount = fields.Float(sring="Amount", help="Amount")
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True,
                                  help="The contract for which applied this input")


class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    actual_worked_days_ids = fields.One2many('hr.payslip.worked_days_actual', 'payslip_id',
                                             string='Payslip Worked Days Actual/Customized', copy=True, readonly=True,
                                             states={'draft': [('readonly', False)]})
    @api.model
    @api.onchange('employee_id', 'date_from', 'date_to')
    def get_absents_etc(self):
        print("WWWWWWWOOOOOORRRRRRKINGGGGGG")
        if self.employee_id:
            piece_rate = self.env['piece.rate'].search([('employee_id', '=', self.employee_id.id),
                                                        ('is_completed', '=', True),
                                                        ('complete_date', '>=', self.date_from),
                                                        ('complete_date', '<=', self.date_to)])
            # print(piece_rate, "########################################################")
            days = self.env['hr.attendance']
            total_days = days.search([('employee_id', '=', self.employee_id.id),
                                      ('x_day', '>=', self.date_from),
                                      ('x_day', '<=', self.date_to)])
            holidays = days.search([('employee_id', '=', self.employee_id.id),
                                                        ('x_day', '>=', self.date_from),
                                                        ('x_day', '<=', self.date_to),
                                                        ('state', '=', 13)])
            absent_days = days.search([('employee_id', '=', self.employee_id.id),
                                                        ('x_day', '>=', self.date_from),
                                                        ('x_day', '<=', self.date_to),
                                                        ('state', '=', 0)])
            holidays_count = len(holidays)
            absent_days_count = len(absent_days)
            total_days_count = len(total_days)
            worked_days_count = total_days_count - holidays_count - absent_days_count
            sum_overtime = sum(rec.rule_overtime for rec in total_days)
            sum_latein = sum(rec.late_in for rec in total_days)
            sum_earlyout = sum(rec.early_out for rec in total_days)
            avg_shift_hrs = int(self.employee_id.resource_calendar_id.hours_per_day)
            sum_half_days = sum(rec.days_count for rec in total_days if rec.days_count < 1)
            sum_piece_rate = sum(rec.total_amount for rec in piece_rate)
            # print(sum_overtime, "$%%###########")

            self.actual_worked_days_ids = [(5, 0, 0)]
            var = []
            # for worked days
            var.append((0, 0, {
                'name': _("Worked Days"),
                'sequence': 0,
                'code': "workeddays100",
                'number_of_days': worked_days_count if worked_days_count else 0.0,
                'number_of_hours': worked_days_count if worked_days_count else 0.0,
                'contract_id': self.contract_id.id,
            }))
            # for absent days
            var.append((0, 0, {
                'name': _("Absent Days"),
                'sequence': 1,
                'code': "absentdays101",
                'number_of_days': absent_days_count if absent_days_count else 0.0,
                'number_of_hours': absent_days_count if absent_days_count else 0.0,
                'contract_id': self.contract_id.id,
            }))

            # for holidays
            var.append((0, 0, {
                'name': _("Holidays"),
                'sequence': 2,
                'code': "holidays102",
                'number_of_days': holidays_count if holidays_count else 0.0,
                'number_of_hours': holidays_count if holidays_count else 0.0,
                'contract_id': self.contract_id
            }))
            # for overtime
            var.append((0, 0, {
                'name': _("Overtime"),
                'sequence': 3,
                'code': "OT99",
                'number_of_days': 0,
                'number_of_hours': sum_overtime if sum_overtime else 0.0,
                'contract_id': self.contract_id.id,
            }))
            # for late in
            var.append((0, 0, {
                'name': _("Late In"),
                'sequence': 4,
                'code': "LT98",
                'number_of_days': 0,
                'number_of_hours': (sum_latein * -1) if sum_latein else 0.0,
                'contract_id': self.contract_id.id,
            }))
            # for early out
            var.append((0, 0, {
                'name': _("Early Out"),
                'sequence': 5,
                'code': "ET97",
                'number_of_days': 0,
                'number_of_hours': (sum_earlyout * -1) if sum_earlyout else 0.0,
                'contract_id': self.contract_id.id,
            }))
            var.append((0, 0, {
                'name': _("Average Shift Hours"),
                'sequence': 6,
                'code': "AVGHR96",
                'number_of_days': 0,
                'number_of_hours': avg_shift_hrs if avg_shift_hrs else 0.0,
                'contract_id': self.contract_id.id,
            }))
            var.append((0, 0, {
                'name': _("Half Days"),
                'sequence': 7,
                'code': "HDAYS95",
                'number_of_days': sum_half_days if sum_half_days else 0.0,
                'number_of_hours': 0,
                'contract_id': self.contract_id.id,
            }))
            var.append((0, 0, {
                'name': _("Piece Rate Calculation"),
                'sequence': 8,
                'code': "PR94",
                'number_of_days': 0,
                'number_of_hours': 0,
                'amount': sum_piece_rate if sum_piece_rate else 0.0,
                'contract_id': self.contract_id.id,
            }))
            self.actual_worked_days_ids = var

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
            }
            payslips += self.env['hr.payslip'].create(res)
        #//////////////////////////////////Added by AB///////////////////////////////////////////
            for p in payslips:
                if p.employee_id.id == employee.id:
                    piece_rate = self.env['piece.rate'].search([('employee_id', '=', p.employee_id.id),
                                                                ('is_completed', '=', True),
                                                                ('complete_date', '>=',  p.date_from),
                                                                ('complete_date', '<=', p.date_to)])
                    days = self.env['hr.attendance']
                    total_days = days.search([('employee_id', '=', p.employee_id.id),
                                              ('x_day', '>=', p.date_from),
                                              ('x_day', '<=', p.date_to)])
                    holidays = days.search([('employee_id', '=', p.employee_id.id),
                                            ('x_day', '>=', p.date_from),
                                            ('x_day', '<=', p.date_to),
                                            ('state', '=', 13)])
                    absent_days = days.search([('employee_id', '=', p.employee_id.id),
                                               ('x_day', '>=', p.date_from),
                                               ('x_day', '<=', p.date_to),
                                               ('state', '=', 0)])

                    holidays_count = len(holidays)
                    absent_days_count = len(absent_days)
                    total_days_count = len(total_days)
                    worked_days_count = total_days_count - holidays_count - absent_days_count
                    sum_overtime = sum(rec.rule_overtime for rec in total_days)
                    sum_latein = sum(rec.late_in for rec in total_days)
                    sum_earlyout = sum(rec.early_out for rec in total_days)
                    avg_shift_hrs = int(employee.resource_calendar_id.hours_per_day)
                    sum_half_days = sum(rec.days_count for rec in total_days if rec.days_count < 1)
                    sum_piece_rate = sum(rec.total_amount for rec in piece_rate)
                    # print(sum_overtime, "$%%###########"
                    p.actual_worked_days_ids = [(5, 0, 0)]
                    var = []
                    # for worked days
                    var.append((0, 0, {
                        'name': _("Worked Days"),
                        'sequence': 0,
                        'code': "workeddays100",
                        'number_of_days': worked_days_count if worked_days_count else 0.0,
                        'number_of_hours': worked_days_count if worked_days_count else 0.0,
                        'contract_id': p.contract_id.id,
                    }))
                    # for absent days
                    var.append((0, 0, {
                        'name': _("Absent Days"),
                        'sequence': 1,
                        'code': "absentdays101",
                        'number_of_days': absent_days_count if absent_days_count else 0.0,
                        'number_of_hours': absent_days_count if absent_days_count else 0.0,
                        'contract_id': p.contract_id.id,
                    }))

                    # for holidays
                    var.append((0, 0, {
                        'name': _("Holidays"),
                        'sequence': 2,
                        'code': "holidays102",
                        'number_of_days': holidays_count if holidays_count else 0.0,
                        'number_of_hours': holidays_count if holidays_count else 0.0,
                        'contract_id': p.contract_id.id
                    }))
                    # for overtime
                    var.append((0, 0, {
                        'name': _("Overtime"),
                        'sequence': 3,
                        'code': "OT99",
                        'number_of_days': 0,
                        'number_of_hours': sum_overtime if sum_overtime else 0.0,
                        'contract_id': p.contract_id.id,
                    }))
                    # for late in
                    var.append((0, 0, {
                        'name': _("Late In"),
                        'sequence': 4,
                        'code': "LT98",
                        'number_of_days': 0,
                        'number_of_hours': (sum_latein * -1) if sum_latein else 0.0,
                        'contract_id': p.contract_id.id,
                    }))
                    # for early out
                    var.append((0, 0, {
                        'name': _("Early Out"),
                        'sequence': 5,
                        'code': "ET97",
                        'number_of_days': 0,
                        'number_of_hours': (sum_earlyout * -1) if sum_earlyout else 0.0,
                        'contract_id': p.contract_id.id,
                    }))
                    var.append((0, 0, {
                        'name': _("Average Shift Hours"),
                        'sequence': 6,
                        'code': "AVGHR96",
                        'number_of_days': 0,
                        'number_of_hours': avg_shift_hrs if avg_shift_hrs else 0.0,
                        'contract_id': p.contract_id.id,
                    }))
                    var.append((0, 0, {
                        'name': _("Half Days"),
                        'sequence': 7,
                        'code': "HDAYS95",
                        'number_of_days': sum_half_days if sum_half_days else 0.0,
                        'number_of_hours': 0,
                        'contract_id': p.contract_id.id,
                    }))
                    var.append((0, 0, {
                        'name': _("Piece Rate Calculation"),
                        'sequence': 8,
                        'code': "PR94",
                        'number_of_days': 0,
                        'number_of_hours': 0,
                        'amount': sum_piece_rate if sum_piece_rate else 0.0,
                        'contract_id': p.contract_id.id,
                    }))
                    p.actual_worked_days_ids = var

        # /////////////////////////////////Added by AB/////////////////////////////////////////////
            payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}
