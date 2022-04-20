from odoo import models, fields, api, _
from odoo.exceptions import Warning
import calendar

class hrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    date_of_joining = fields.Date(string="Date of Joining")
    annual_leaves_allocation_dt = fields.Date(string="AL Allocation Date")
    leave_encashment = fields.Boolean(string="Leave Encashment")
        
    @api.depends('name', 'barcode')
    def name_get(self):
        result = []
        for record in self:
            if record.barcode:
                name = str(record.name) + ' (' + str(record.barcode) + ')'
            else:
                name = record.name
            result.append((record.id, name))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        employees = self.search(['|',('name', operator, name),('barcode', operator, name)])
        return employees.name_get()
    
class inheritHrLeave(models.Model):
    _inherit = 'hr.leave'
    
    def action_confirm(self):
        
        casual = self.env['hr.leave.type'].search([('name','=ilike','%Casual%')])
        sick = self.env['hr.leave.type'].search([('name','=ilike','%Sick%')])
        
        if self.holiday_status_id == casual or self.holiday_status_id == sick:

            rec = self.env['automatic.leave.allocation'].search([('leave_type_id','=', self.holiday_status_id.id)])
            if self.number_of_days > rec.no_of_days:
                raise Warning(_("You cannot request more than allowed days"))
            
            Startdate = self.request_date_from
            Month_of_start = Startdate.replace(day = 1)
            Month_of_end = Startdate.replace(day = calendar.monthrange(Startdate.year, Startdate.month)[1])
            
            leave_request = self.search([('employee_id','=',self.employee_id.id),('state','=','validate'),
                         ('request_date_from','>=',Month_of_start),
                         ('request_date_to','<=',Month_of_end),('holiday_status_id','=',self.holiday_status_id.id)])
            
            if leave_request:
                raise Warning(_("You have already availed leave for this month"))
            
        res = super(inheritHrLeave, self).action_confirm()
        return res
    
    def action_approve(self):
        
        casual = self.env['hr.leave.type'].search([('name','=ilike','%Casual%')])
        sick = self.env['hr.leave.type'].search([('name','=ilike','%Sick%')])
        
        if self.holiday_status_id == casual or self.holiday_status_id == sick:

            rec = self.env['automatic.leave.allocation'].search([('leave_type_id','=', self.holiday_status_id.id)])
            if self.number_of_days > rec.no_of_days:
                raise Warning(_("You cannot request more than allowed days"))
            
            Startdate = self.request_date_from
            Month_of_start = Startdate.replace(day = 1)
            Month_of_end = Startdate.replace(day = calendar.monthrange(Startdate.year, Startdate.month)[1])
            
            leave_request = self.search([('employee_id','=',self.employee_id.id),('state','=','validate'),
                         ('request_date_from','>=',Month_of_start),
                         ('request_date_to','<=',Month_of_end),('holiday_status_id','=',self.holiday_status_id.id)])
            
            if leave_request:
                raise Warning(_("You have already availed leave for this month"))
            
        res = super(inheritHrLeave, self).action_approve()
        return res