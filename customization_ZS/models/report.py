# -*- coding: utf-8 -*-

from odoo import models, fields, api
import num2words


class AccountMove(models.Model):
    _inherit = "account.move"

    x_num2words =  fields.Char("Amount in Words", compute='amount_to_text')

    # def amount_to_text(self, amount):
    #     in_words = num2words.num2words(amount)
    #     return in_words.upper() + " ONLY"
    def amount_to_text(self):
        x = num2words.num2words(self.amount_total) + " Only"
        self.x_num2words = x.title()