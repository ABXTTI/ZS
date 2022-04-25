from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date

class ProcessLeavesCrone(models.Model):
    _name = "process.leaves.cron"


    def process_leaves_cron(self):
        employees = self.env['hr.employee'].search([('device_id', '!=', "")])
        leaves = self.env['hr.leave']
        att_obj = self.env['hr.attendance']
        if employees:
            for employee in employees:
                att_search_att = att_obj.search([('employee_id', '=', employee.id)])
                if att_search_att:
                    for rec in att_search_att:
                        if rec.check_out:
                            if rec.day_type == "0":
                                rec.state = "13"
                            elif rec.day_type == "1":
                                day_checkout = rec.check_out.date()
                                standard_checkout = datetime.datetime.combine(day_checkout, datetime.time()) + \
                                                    datetime.timedelta(hours=rec.end_time) - \
                                                    datetime.timedelta(hours=5)  # for utc adjustment
                                if standard_checkout < rec.check_out:
                                    difference_time = standard_checkout - rec.check_in
                                else:
                                    difference_time = rec.check_out - rec.check_in

                                difference_hours = difference_time.total_seconds() * 1 / 60 * 1 / 60
                                if difference_hours < 4:
                                    rec.state = "0"
                                    rec.days_count = 0
                                elif difference_hours == 4:
                                    rec.state = "4"
                                    rec.days_count_before_leave = 0.5
                                elif difference_hours > 4:
                                    rec.state = "1"
                                    rec.days_count = 1

                                if not rec.leave_type and rec.state != "0":
                                    check_in_actual_localtz = rec.check_in + datetime.timedelta(hours=5)
                                    standard_check_in = datetime.datetime.combine(check_in_actual_localtz.date(), datetime.time()) + \
                                                        datetime.timedelta(hours=rec.start_time)
                                    check_out_actual_localtz = rec.check_out + datetime.timedelta(hours=5)
                                    standard_check_out = datetime.datetime.combine(check_out_actual_localtz.date(), datetime.time()) + \
                                                         datetime.timedelta(hours=(rec.end_time))
                                    flour_late_in = standard_check_in + datetime.timedelta(hours=0, minutes=15, seconds=59)
                                    cap_late_in = standard_check_in + datetime.timedelta(hours=4)
                                    if check_in_actual_localtz > flour_late_in and check_in_actual_localtz < cap_late_in:
                                        diff = check_in_actual_localtz - standard_check_in
                                        rec.late_in = diff.total_seconds()*1/60*1/60
                                    else:
                                        rec.late_in = 0
                                    if check_out_actual_localtz > cap_late_in and check_out_actual_localtz < standard_check_out:
                                        diff = standard_check_out - check_out_actual_localtz
                                        rec.early_out = diff.total_seconds()*1/60*1/60
                                    else:
                                        rec.early_out = 0
                                else:
                                    rec.late_in = 0
                                    rec.early_out = 0

                # for leaves calculation
                leaves_greater_than_1 = leaves.search([('employee_id', '=', employee.id),
                                                       ('number_of_days', '>', 1),
                                                       ('state', '=', 'validate')])
                leaves_equal_to_1 = leaves.search([('employee_id', '=', employee.id),
                                                   ('number_of_days', '=', 1),
                                                   ('state', '=', 'validate')])
                leaves_less_than_1 = leaves.search([('employee_id', '=', employee.id),
                                                    ('number_of_days', '<', 1),
                                                    ('state', '=', 'validate')])
                # print(leaves_less_than_1, "<1")
                # print(leaves_equal_to_1, "=1")
                # print(leaves_greater_than_1, ">1")
                if leaves_greater_than_1:
                    for rec in leaves_greater_than_1:
                        for d in range(0, int(rec.number_of_days)):
                            x_date = rec.request_date_from + datetime.timedelta(days=d)
                            print(d)

                            att_var = att_obj.search([('employee_id', '=', employee.id),
                                                      ('x_day', '=', x_date)])
                            if att_var:
                                att_var.write({
                                    'leave_type': rec.holiday_status_id,
                                    'days_count': 1,
                                    'state': "6",
                                    'late_in': 0.0,
                                    'early_out': 0.0,
                                })
                if leaves_equal_to_1:
                    for rec in leaves_equal_to_1:
                        att_var = att_obj.search([('employee_id', '=', employee.id),
                                                  ('x_day', '=', rec.request_date_from)])
                        if att_var:
                            att_var.write({
                                'leave_type': rec.holiday_status_id,
                                'days_count': 1,
                                'state': "6",
                                'late_in': 0.0,
                                'early_out': 0.0,
                            })
                if leaves_less_than_1:
                    print("ITS WORKING $$$$$$$$$$$$$$$$$$")
                    for rec in leaves_less_than_1:
                        att_var = att_obj.search([('employee_id', '=', employee.id),
                                                  ('x_day', '=', rec.request_date_from)])
                        print(att_var)
                        if att_var:
                            for r in att_var:
                                att_var.write({
                                    'leave_type': rec.holiday_status_id,
                                    'days_count': 0.5 if r.days_count < 0.5 else 1,
                                    'state': "5.1" if rec.holiday_status_id.name == "Short Leave" else "5",
                                    'late_in': 0.0,
                                    'early_out': 0.0,
                                    })