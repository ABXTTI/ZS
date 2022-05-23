from odoo import fields, models, api

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def draft_mo(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'draft'
                for line in rec.move_raw_ids:
                    line.state = 'draft'