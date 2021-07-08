from odoo import models, fields, api
class PayrollReportWizard(models.TransientModel):
    _name = "payroll.report.wizard"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")

    def print_xlsx(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref('ta_hrm.payroll_report').report_action(self, data=data)

class PayrollReportXlsx(models.AbstractModel):
    _name = 'report.ta_hrm.payroll_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        filtered_object = self.env['hr.payslip'].search([('date_from', '>=', data['date_from']),
                                                 ('date_to', '=', data['date_to'])
                                                 ])
        rule_list = self.env['hr.salary.rule'].search([('appears_on_payslip', '=', True)])
        H1 = workbook.add_format({'font_size': 28, 'align': 'center', 'bold': True})
        H3 = workbook.add_format({'font_size': 14, 'align': 'center', 'bold': True})
        H4 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True, 'text_wrap': True})
        H5 = workbook.add_format({'font_size': 10, 'align': 'center'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
        date_format2 = workbook.add_format({'font_size': 14, 'num_format': 'dd/mm/yy'})
        sheet = workbook.add_worksheet('Payroll_Report')
        # Headings only----------------------------------------------
        sheet.write(6, 0, "Employee", H4)
        sheet.write(6, 1, "Badge ID", H4)
        sheet.write(6, 2, "CNIC#", H4)
        sheet.write(6, 3, "DOJ", H4)
        sheet.write(6, 4, "Father Name", H4)
        sheet.write(6, 5, "Department", H4)
        sheet.write(6, 6, "Designation", H4)
        sheet.write(6, 7, "Salary Structure", H4)
        sheet.write(6, 8, "Reference", H4)
        sheet.write(6, 9, "From", H4)
        sheet.write(6, 10, "To", H4)
        count = 10
        max_len = len(rule_list)
        heads_location = []
        if count != max_len:
            for rule in rule_list:
                var = {
                    'col': count,
                    'rule': rule.name,
                }
                heads_location.append(var)
                count += 1
                sheet.write(6, count, rule.name, H4)

        # Headings Only ------------------------------------------------------
        # for first 4 columns data
        row = 7
        for rec in filtered_object:
            sheet.write(row, 0, rec.employee_id.name)
            sheet.write(row, 1, rec.employee_id.device_id)
            sheet.write(row, 2, rec.employee_id.identification_id)
            sheet.write(row, 3, rec.employee_id.x_joining_date, date_format)
            sheet.write(row, 4, rec.employee_id.father_name)
            sheet.write(row, 5, rec.employee_id.department_id.name)
            sheet.write(row, 6, rec.employee_id.job_id.name)
            sheet.write(row, 7, rec.struct_id.name)
            sheet.write(row, 8, rec.number)
            sheet.write(row, 9, rec.date_from, date_format)
            sheet.write(row, 10, rec.date_to, date_format)
        # _______________________________________________________________________
        # for payslip line_ids ___________________________________________________
            for h in heads_location:
                for line in rec.line_ids:
                    if line.name == h['rule']:
                        col = h['col']
                        sheet.write(row, col+1, line.amount)
            row += 1
        # for payslip line_ids___________________________________________________

        ##########Adjusting column width######################
        sheet.set_column(6, 0, 20)
        sheet.set_column(6, 1, 12)

        sheet.insert_image('A1', r'/opt/odoo13/custom_addons/ta_hrm/static/images/logo.png', {'x_scale': 0.5, 'y_scale': 0.5})
        sheet.write(1, 7, "Payroll Report", H1)
        sheet.write(3, 5, "From:", H3)
        sheet.write(3, 8, "To:", H3)
        sheet.write(3, 6, data['date_from'], date_format2)
        sheet.write(3, 9, data['date_to'], date_format2)
        # ________________________________________________________________________________
