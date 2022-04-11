from odoo import api, fields, models
import datetime

class inheritHrLeave(models.Model):
    _inherit = 'hr.leave'
        
    def validate_cron(self):
        current_dtime = datetime.datetime.now()+datetime.timedelta(hours = 5)
        current_dt = current_dtime.date()
        
        for rec in self.search([('state','=','confirm')]):
            if rec.request_date_from >= current_dt:
                rec.action_approve()

class AutomaticLeaveAllocation(models.Model):
    _name = "automatic.leave.allocation"
    _description = "Automatic Leave Allocation"
    _inherit = ['mail.thread']

    name = fields.Char('Description')
    active = fields.Boolean('Active', default=True)
    leave_type_id = fields.Many2one("hr.leave.type",
                                    string="Leave Type", copy=False,
                                    track_visibility='onchange')
    type_request_unit = fields.Selection(
        related='leave_type_id.request_unit', readonly=True)
    no_of_days = fields.Float('No of Days', track_visibility='onchange')
    alloc_by = fields.Selection([('by_emp', 'By Employee')],
                                default='by_emp',
                                string='Allocation By',
                                track_visibility='onchange')
    
    emp_ids = fields.Many2many('hr.employee',
                               string='Employees',
                               track_visibility='onchange')
    
    def leaves_allocation(self,type,st = None):
    
        alloc_obj = self.env['hr.leave.allocation']
        
        if type != 'annual':
            for al in self:
                if al.alloc_by == 'by_emp':
                    for emp in al.emp_ids:
                        vals = {
                            'name': 'Auto-Leave Allocation for ' + emp.name,
                            'holiday_status_id': al.leave_type_id.id,
                            'holiday_type': 'employee',
                            'employee_id': emp.id,
                        }
                        
                        vals.update({'number_of_days': al.no_of_days})
                        
                        alloc = alloc_obj.create(vals)
                        alloc.action_approve()

        elif type == 'annual':
            for al in self:
                if al.alloc_by == 'by_emp':
                    for emp in al.emp_ids:

                        allocated_leaves = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),('holiday_status_id','=',st.id),('state','=','validate')])
                        
                        if not allocated_leaves:
                            
                            if emp.date_of_joining:
                                current_dtime = datetime.datetime.now()+datetime.timedelta(hours = 5)
                                delta = current_dtime.date() - emp.date_of_joining
                                
                                print (delta)
                                if delta.days >= 365:

                                    vals = {
                                        'name': 'Auto-Leave Allocation for ' + emp.name,
                                        'holiday_status_id': al.leave_type_id.id,
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,}
                                
                                    vals.update({'number_of_days': al.no_of_days})
                                
                                    alloc = alloc_obj.create(vals)
                                    alloc.action_approve()
                                    emp.write({'annual_leaves_allocation_dt':current_dtime.date()})
                        
                        else:
                            
                            current_dtime = datetime.datetime.now()+datetime.timedelta(hours = 5)
                            delta = current_dtime.date() - emp.annual_leaves_allocation_dt
                                
                            if delta.days >= 365:

                                availed_leaves = 0.0
                                allocated_count = 0.0
                                availed_count = 0.0 
                                
                                
                                allocated_leaves = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),('holiday_status_id','=',st.id),('state','=','validate')])
                                availed_leaves = self.env['hr.leave'].search([('employee_id','=',emp.id),('holiday_status_id','=',st.id),('state','=','validate')])
                            
                                for r in allocated_leaves:
                                    allocated_count += r.number_of_days
                            
                                for a in availed_leaves:
                                    availed_count += a.number_of_days
                            
                                remaining = (allocated_count - availed_count) + al.no_of_days
                            
                            
                                if remaining <= 28:
                            
                                    vals = {
                                        'name': 'Auto-Leave Allocation for ' + emp.name,
                                        'holiday_status_id': al.leave_type_id.id,
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,}
                            
                                    vals.update({'number_of_days': al.no_of_days})
                            
                                    alloc = alloc_obj.create(vals)
                                    alloc.action_approve()
                                    emp.write({'annual_leaves_allocation_dt':current_dtime.date()})
                            
                                else:   
                                    vals = {
                                        'name': 'Auto-Leave Allocation for ' + emp.name,
                                        'holiday_status_id': al.leave_type_id.id,
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,}
                            
                                    rm = 28 - (allocated_count - availed_count)
                            
                                    if rm > 0:
                            
                                        vals.update({'number_of_days': 28 - (allocated_count - availed_count)})
                            
                                        alloc = alloc_obj.create(vals)
                                        alloc.action_approve()
                                        emp.write({'annual_leaves_allocation_dt':current_dtime.date()})


    def leaves_refusal(self):
        exempted_leave_type = self.env['hr.leave.type'].search([('name','=ilike','%Annual%')])
        
        hr_leaves = self.env['hr.leave.allocation'].search([('holiday_status_id','!=',exempted_leave_type.id)])
        
        for rec in hr_leaves.filtered(lambda x:x.state == 'validate'):
            rec.action_refuse()
        

    @api.model
    def _auto_leaves_allocation_sc(self):
        self.leaves_refusal()
        
        exempted_leave_type = self.env['hr.leave.type'].search([('name','=ilike','%Annual%')])
        
        leaves_config = self.env['automatic.leave.allocation'].search([('leave_type_id','!=', exempted_leave_type.id)])
        
        for rec in leaves_config:
            rec.leaves_allocation('sc',exempted_leave_type)
        
    @api.model
    def _auto_leaves_allocation_an(self):
        
        exempted_leave_type = self.env['hr.leave.type'].search([('name','=ilike','%Annual%')])
        
        leaves_config = self.env['automatic.leave.allocation'].search([('leave_type_id','=', exempted_leave_type.id)])
        
        if leaves_config:
            leaves_config[0].leaves_allocation('annual',exempted_leave_type)