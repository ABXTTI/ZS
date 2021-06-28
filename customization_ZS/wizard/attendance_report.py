from odoo import models, fields, api
import pytz


class AttendanceReportWizard(models.TransientModel):
    _name = "attendance.report.wizard"

    person_id = fields.Many2one('hr.employee', string="Employee")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

    def print_report(self):
        print("kkkkk----->", self.read()[0])
        user_tz = pytz.timezone(self.env.context.get('tz')) or self.env.user.tz
        data = {
            'model': 'attendance.report.wizard',
            'form': self.read()[0]
        }
        print("DATA", data)
        selected_person = data['form']['person_id'][0]
        print("selected_person--->", selected_person)
        attendances = self.env['hr.attendance'].search([('employee_id', '=', selected_person),
                                                        ('check_in', '>=', self.date_from),
                                                        ('check_in', '<=', self.date_to)])
        print("Attendances", attendances)
        attendances_list = []
        for att in attendances:
            vals = {
                'employee_code': att.x_employee_code,
                'person_id': att.employee_id.name,
                'check_in': pytz.utc.localize(att.check_in).astimezone(user_tz),
                'check_out': pytz.utc.localize(att.check_out).astimezone(user_tz),
                'shift_name': att.employee_id.resource_calendar_id.name,
                'worked_hours': int(att.worked_hours),
            }
            attendances_list.append(vals)
        data['attendances'] = attendances_list
        print("list item =====", data)

        form_detail = []
        flag = 0
        for fd in attendances:
            if flag < 1:
                vals = {
                    'employee_code': fd.x_employee_code,
                    'person_name': fd.employee_id.name
                }
                form_detail.append(vals)
                flag += 1

        data['forms'] = form_detail

        print(data)

        return self.env.ref('customization_ZS.attendance_report_pdf').report_action(self, data=data)

    # # @api.onchange('employee_id')
    # def print_attendance(self):
    #     print("Sucessfully VVVVVVVVVVV.GOOD")
    #     data = {
    #         'model': 'attendance.report.wizard',
    #         'form': self.read()[0],
    #     }
    #     print(data)
    #     selected_data = data['form']['employee_id'][0]
    #     dict = self.env['hr.attendance'].search([('employee_id', '=', selected_data)])
    #     dict_list = []
    #     for l in dict:
    #         values = {
    #             'employee_id': l.employee_id,
    #         }
    #         dict_list.append(values)
    #     data['dict'] = dict_list
    #     print(data)
    #     print(dict)
    #     print(dict_list)
    #
    #     return self.env.ref('customization_ZS.attendance_report_pdf').report_action(self, data=data)
