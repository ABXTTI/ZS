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


class hrContract(models.Model):
    _inherit = 'hr.contract'


    def check_leave_encashment_sick(self,date_from,date_end,employee_id):
        
        if self.employee_id.leave_encashment:
            leave_type = self.env['hr.leave.type'].search([('name','=ilike','%Sick%')])
            
            availed_leaves = self.env['hr.leave'].search([('request_date_from','>=',date_from),('request_date_from','<=',date_end),
                                                          ('employee_id','=',employee_id.id),('holiday_status_id','=',leave_type.id),
                                                          ('state','=','validate')])
            
            if availed_leaves:
                return 0
            
            else:
                rec = self.env['automatic.leave.allocation'].search([('leave_type_id','=', leave_type.id)])
                
                if rec:
                
                    vals = {
                        'name': 'Auto-Leave Register for Leave Encashment',
                        'holiday_status_id': leave_type.id,
                        'holiday_type': 'employee',
                        'employee_id': employee_id.id,
                        'request_date_from':date_from,
                        'request_date_to':date_end,
                        'number_of_days':rec[0].no_of_days}
                
                    Leave = self.env['hr.leave'].create(vals)
                    Leave.action_approve()
                

                    return 1
        
        else:
            return 0
            
    @api.model
    def check_leave_encashment_casual(self,date_from,date_end,employee_id):
        
        if employee_id.leave_encashment:
    
            leave_type = self.env['hr.leave.type'].search([('name','=ilike','%Casual%')])
            
            availed_leaves = self.env['hr.leave'].search([('request_date_from','>=',date_from),('request_date_from','<=',date_end),
                                                              ('employee_id','=',employee_id.id),('holiday_status_id','=',leave_type.id),
                                                              ('state','=','validate')])
                
            if availed_leaves:
            
                return 0
            
            else:
                
                rec = self.env['automatic.leave.allocation'].search([('leave_type_id','=', leave_type.id)])
                
                if rec:
            
                    vals = {
                    'name': 'Auto-Leave Register for Leave Encashment',
                    'holiday_status_id': leave_type.id,
                    'holiday_type': 'employee',
                    'employee_id': employee_id.id,
                    'request_date_from':date_from,
                    'request_date_to':date_end,
                    'number_of_days':rec.no_of_days}
        
                    Leave = self.env['hr.leave'].create(vals)
                    Leave.action_approve()
            
                    return 1
            
    
        else:
            return 0   

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