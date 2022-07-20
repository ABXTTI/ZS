# -*- coding: utf-8 -*-
import datetime

from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    advance_loan_account = fields.Many2one("account.account", string="Advance/Loan Account", required=True)

    def action_view_sale_order(self):
        return

class CounterParty(models.Model):
    _name = "counter.party"

    name = fields.Char(string="Name")
    date = fields.Date(string="Date", required=True)
    detail = fields.Char(string="Detail", required=True)
    payment_type = fields.Selection([
        ('receive', 'Receive'),
        ('pay', 'Pay'),
        ], string="Payment Type", help="Payment Type", required=True, default="", readonly=True)
    transaction_with = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ], string="Transaction With", help="Payment Type", required=True, readonly=True)
    counter_adj_type = fields.Selection([
        # ('through_loan', 'Through Loan/Advance'),
        ('advance_cash_or_bank', 'Loan/Advance in Cash/Bank'),
        ], string="Counter Party Adj. Type", help="Counter Adjustment Type", required=True, default="", readonly=True)

    account_debit = fields.Many2one("account.account", string="Debit Account")
    account_credit = fields.Many2one("account.account", string="Credit Account")
    debit_partner = fields.Many2one("res.partner", string="Debit Partner")
    credit_partner = fields.Many2one("res.partner", string="Credit Partner")

    amount = fields.Float(string="Amount")

    state = fields.Selection([
            ('draft', 'Draft'),
            ('post', 'Posted'),
            ('cancel', 'Cancelled'),
            ], string="State", help="State", required=True, default="draft")

    move_id = fields.Many2one("account.move")
    journal_id = fields.Many2one("account.journal")
    cash_bank_journals_ids = fields.Many2one("account.journal")


    @api.onchange('counter_party')
    def onchange_counterparty(self):
        journals = self.env['account.journal']
        for rec in self:
            if rec.counter_party and not rec.counter_party.advance_loan_account:
                raise ValidationError("There is no Loan/Advance Account on Selected Customer/Vendors Form !!!!")
            if rec.payment_type == "receive":
                if rec.counter_adj_type == "through_loan":
                    counter_journal = journals.search([('name', '=', 'Counter Misc. Operations')])
                    rec.debit_partner = rec.counter_party.id
                    rec.account_debit = rec.counter_party.advance_loan_account.id
                    rec.journal_id = counter_journal

            elif rec.payment_type == "pay":
                if rec.counter_adj_type == "through_loan":
                    counter_journal = journals.search([('name', '=', 'Counter Misc. Operations')])
                    rec.credit_partner = rec.counter_party.id
                    rec.account_credit = rec.counter_party.advance_loan_account.id
                    rec.journal_id = counter_journal

    counter_party = fields.Many2one("res.partner", string="Counter Party")

    @api.onchange('cash_bank_journals_ids')
    def onchangejournalid(self):
        for rec in self:
            if rec.partner_id:
                rec.journal_id = rec.cash_bank_journals_ids.id
                if rec.transaction_with == "customer":
                    rec.account_debit = rec.cash_bank_journals_ids.default_debit_account_id.id
                elif rec.transaction_with == "vendor":
                    rec.account_credit = rec.cash_bank_journals_ids.default_credit_account_id.id

    @api.onchange('payment_type')
    def onchangepaymenttype(self):
        for rec in self:
            if rec.partner_id:
                rec.onchangepartnerid()
            if rec.counter_party:
                rec.onchange_counterparty()

    @api.onchange('counter_adj_type')
    def onchangecounteradjtype(self):
        for rec in self:
            rec.partner_id = False
            rec.counter_party = False
            rec.cash_bank_journals_ids = False

    @api.onchange('partner_id')
    def onchangepartnerid(self):
        for rec in self:
            if rec.partner_id and not rec.partner_id.advance_loan_account:
                raise ValidationError("There is no Loan/Advance Account on Selected Customer/Vendors Form !!!!")
            if rec.payment_type == "receive":
                if rec.counter_adj_type == "through_loan":
                    rec.credit_partner = rec.partner_id.id
                    if rec.transaction_with == 'customer':
                        rec.account_credit = rec.partner_id.property_account_receivable_id.id
                    elif rec.transaction_with == 'vendor':
                        rec.account_credit = rec.partner_id.property_account_payable_id.id
                elif rec.counter_adj_type == "advance_cash_or_bank":
                    if rec. transaction_with == 'customer':
                        rec.credit_partner = rec.partner_id.id
                        rec.debit_partner = rec.partner_id.id
                        rec.account_credit = rec.partner_id.advance_loan_account.id

            elif rec.payment_type == "pay":
                if rec.counter_adj_type == "through_loan":
                    rec.debit_partner = rec.partner_id.id
                    if rec.transaction_with == 'customer':
                        rec.account_debit = rec.partner_id.property_account_receivable_id.id
                    elif rec.transaction_with == 'vendor':
                        rec.account_debit = rec.partner_id.property_account_payable_id.id

                elif rec.counter_adj_type == "advance_cash_or_bank":
                    rec.debit_partner = rec.partner_id.id
                    rec.account_debit = rec.partner_id.advance_loan_account.id

    partner_id = fields.Many2one("res.partner", string="Customer/Vendor")

    def action_draft(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.button_draft()
            rec.state = "draft"

    def action_cancel(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.button_cancel()
            rec.state = "cancel"

    def action_post(self):
        move = {
            'name': self.name,
            'date': self.date or datetime.datetime.today(),
            'journal_id': self.journal_id.id,
            # 'company_id': uid.company_id,
            # 'type': 'entry',
            'state': 'draft',
            'ref': (self.detail) + '- ' +" " + '- ' + 'Transferred',
            'line_ids': [(0, 0, {
                'name': self.name or self.detail,
                'partner_id': self.debit_partner.id,
                'account_id': self.account_debit.id,
                'debit': self.amount}),
                         (0, 0, {
                             # 'name': self.name or self.detail,
                             'partner_id': self.credit_partner.id,
                             'account_id': self.account_credit.id,
                             'credit': self.amount,
                         })]
        }
        if not self.move_id:
            move_id = self.env['account.move'].create(move)
            move_id.post()
        elif self.move_id:
            move_id = self.move_id
            move_id.line_ids = [(5, 0, 0)]
            move_id.write(move)
            move_id.post()

        self.state = "post"
        return self.write({'move_id': move_id.id})