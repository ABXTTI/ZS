from odoo import tools
from odoo import models, fields, api, _
import datetime
from datetime import date
import calendar
import pytz



class ZkMachine(models.Model):
    _inherit = 'zk.machine'

    def button_process_attendance(self):
        # _________________________________19-03-2021__________________________________________________

        existing_attendance_data = self.env['hr.attendance'].search([('check_in', '>', '2003-12-31')])
        if existing_attendance_data:
            start_date = date.today() - datetime.timedelta(days=26)
            end_date = date.today() + datetime.timedelta(days=1)
        else:
            start_date = date(2021, 2, 1)
            end_date = date.today() + datetime.timedelta(days=1)

        diff_delta = end_date - start_date
        range_days = diff_delta.days
        # Processing Attendance
        data = self.env['attendance.logs']
        attendance_obj = self.env['hr.attendance']
        employees = self.env['hr.employee'].search([('device_id', '!=', "")])
        # user_tz = pytz.timezone(self.env.context.get('tz')) or self.env.user.tz
        if employees:
            for employee in employees:
                for d in range(0, range_days):
                    days = start_date + datetime.timedelta(days=d)
                    print(range_days)
                    # print(date.anc)
                    # print(days.strftime("%A"), days, employee)
                    if date.today() < days:
                        break
                    else:
                        # for night shift in which days changes to next day and day shift both
                        shift = self.env['resource.calendar.attendance'].search([('calendar_id', '=', employee.resource_calendar_id.id),
                                                                                 ('dayofweek', '=', days.weekday())])

                        days_in_daystime = datetime.datetime.combine(days, datetime.time())
                        shift_in_with_margin =  days_in_daystime + \
                                                datetime.timedelta(hours=shift.hour_from) - \
                                                datetime.timedelta(hours=shift.margin_work_from) - \
                                                datetime.timedelta(hours=5)# adjustment to convert to utc
                        shift_out_with_margin = days_in_daystime + \
                                                datetime.timedelta(hours=shift.hour_from) + \
                                                datetime.timedelta(hours=shift.shift_hours) + \
                                                datetime.timedelta(hours=shift.margin_work_to) - \
                                                datetime.timedelta(hours=5) # adjustment to convert to utc

                        print("$$$$$$$$$$$$ In", days_in_daystime, shift_in_with_margin, shift_in_with_margin.astimezone(pytz.utc))
                        print("$$$$$$$$$$$$ out", days_in_daystime, shift_out_with_margin, shift_out_with_margin.astimezone(pytz.utc))
                        # print(days.abc)


                        att_search = data.search([('name', '=', employee.id),
                                                  ('punching_time', '>=', shift_in_with_margin ),
                                                  ('punching_time', '<=', shift_out_with_margin)])
                        if att_search:
                            # Getting TIme List and seperating max and min from it
                            list_time = []
                            for rec in att_search:
                                list_time.append(rec.punching_time)
                            print("list_time =========", list_time, employee.name)
                            max_att = max(list_time)
                            min_att = min(list_time)
                            print("For Night Shift", max_att)
                            # _________________________________________________________
                            # check if check in already existed
                            att_duplicates = attendance_obj.search([('employee_id', '=', employee.id),
                                                                    ('check_in', '>=', shift_in_with_margin),
                                                                    ('check_in', '<=', shift_out_with_margin)])
                            print("Attendance _ Duplicates 22222", att_duplicates)
                            if not att_duplicates:
                                # Process attendance
                                if days.strftime("%A") != "Sunday":
                                    print("###############Working Day###################")
                                    attendance_obj.create({
                                        'employee_id': employee.id,
                                        'check_in': min_att,
                                    })

                                elif days.strftime("%A") == "Sunday":
                                    print("###########Sunday Overtime worked ##########")
                                    attendance_obj.create({
                                        'employee_id': employee.id,
                                        'check_in': min_att,
                                    })
                            # check if check out missing for previous and existing days
                            att_var = attendance_obj.search([('employee_id', '=', employee.id),
                                                             ('check_out', '=', False),
                                                             ('check_in', '>=', shift_in_with_margin),
                                                             ('check_in', '<=', shift_out_with_margin)])
                            if att_var and datetime.datetime.now() > shift_out_with_margin:
                                att_var.write({
                                    'check_out': max_att
                                })

                        att_s = self.env['attendance.logs'].search([('name', '=', employee.id),
                                                                               ('punching_time', '>=', shift_in_with_margin),
                                                                               ('punching_time', '<=', shift_out_with_margin)
                                                                               ])
                        if not att_s and datetime.datetime.now() > shift_out_with_margin:
                            att_dups = attendance_obj.search([('employee_id', '=', employee.id),
                                                                    ('check_in', '>=', shift_in_with_margin),
                                                                    ('check_in', '<=', shift_out_with_margin)])
                            if not att_dups:
                                attendance_obj.create({
                                    'employee_id': employee.id,
                                    'check_in': shift_in_with_margin,
                                    'check_out': shift_in_with_margin,
                                })

                        # elif not att_search and datetime.datetime.now() > shift_out_with_margin:
                        #     att_duplicates = attendance_obj.search([('employee_id', '=', employee.id),
                        #                                             ('check_in', '>=', shift_in_with_margin),
                        #                                             ('check_in', '<=', shift_out_with_margin)])
                        #     if not att_duplicates:
                        #         if days.strftime("%A") != "Sunday":
                        #             print("#nnnnnnnn##############Working Day###################")
                        #             attendance_obj.create({
                        #                 'employee_id': employee.id,
                        #                 'check_in': days_in_daystime,
                        #                 'check_out': days_in_daystime,
                        #             })
                        #
                        #         elif days.strftime("%A") == "Sunday":
                        #             print("###########Sunday Overtime worked ##########")
                        #             attendance_obj.create({
                        #                 'employee_id': employee.id,
                        #                 'check_in': days_in_daystime,
                        #                 'check_out': days_in_daystime,
                        #             })
                        #         att_var = attendance_obj.search([('employee_id', '=', employee.id),
                        #                                          ('check_out', '=', False),
                        #                                          ('check_in', '>=', shift_in_with_margin),
                        #                                          ('check_in', '<=', shift_out_with_margin)])
                        #         if att_var and datetime.datetime.now() > shift_out_with_margin:
                        #             att_var.write({
                        #                 'check_out': days_in_daystime
                        #             })



        #
        # print(calendar.abc)
        #
        # attendance_obj = self.env['hr.attendance']
        # data = self.env['zk.report.daily.attendance']
        # test = self.env['zk.report.daily.attendance'].search([('id', '>', 0)])
        #
        # # getting unique date
        # list_unique_date = []
        # for rec in test:
        #     vals = ({
        #         'punching_time': rec.punching_time.date()
        #     })
        #     for v in vals.values():
        #         if v not in list_unique_date:
        #             list_unique_date.append(v)
        #
        # list_unique_employees = []
        # for rec in test:
        #     values = ({
        #         'employee_id': rec.name
        #     })
        #     for value in values.values():
        #         if value not in list_unique_employees:
        #             list_unique_employees.append(value)
        #
        # for employee in list_unique_employees:
        #     for d in list_unique_date:
        #         attendance = data.search([('name', '=', employee.id),
        #                                   ('punching_time', '>=', d),
        #                                   ('punching_time', '<', d + datetime.timedelta(days=1))])
        #         list_att = []
        #         if attendance:
        #             for rec in attendance:
        #                 list_att.append(rec.punching_time)
        #
        #             print(list_att)
        #             max_att = max(list_att)
        #             min_att = min(list_att)
        #             print(list_att)
        #             print(max_att)
        #             print(min_att)
        #
        #             for rec in attendance:
        #                 check_dups = attendance_obj.search([('employee_id', '=', employee.id),
        #                                                     ('check_in', '>=', d),
        #
        #                                                     ('check_in', '<', d + datetime.timedelta(days=1))])
        #                 if not check_dups:
        #                     if rec.punching_time == min_att and rec.punching_time == max_att and d < date.today():
        #                         attendance_obj.create({
        #                             'employee_id': employee.id,
        #                             'check_in': rec.punching_time,
        #                         })
        #
        #                     if rec.punching_time == min_att and rec.punching_time != max_att:
        #                         attendance_obj.create({
        #                             'employee_id': employee.id,
        #                             'check_in': rec.punching_time,
        #                         })
        #
        #                     att_var = attendance_obj.search([('employee_id', '=', employee.id),
        #                                                      ('check_out', '=', False)])
        #
        #                     for r in attendance:
        #                         if r.punching_time == max_att and att_var:
        #                             att_var.write({
        #                                 'check_out': r.punching_time,
        #                             })
