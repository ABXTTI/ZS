from odoo import models, fields, api, _
from odoo.exceptions import Warning

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