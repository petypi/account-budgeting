# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ExpenseBudgetMove(models.Model):
    _name = 'expense.budget.move'
    _description = 'Expense Budget Moves'

    sheet_id = fields.Many2one(
        comodel_name='hr.expense.sheet',
        related='expense_id.sheet_id',
        readonly=True,
        store=True,
        index=True,
    )
    expense_id = fields.Many2one(
        comodel_name='hr.expense',
        readonly=True,
        index=True,
        help="Commit budget for this expense_id",
    )
    date = fields.Date(
        required=True,
        index=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        auto_join=True,
        index=True,
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        auto_join=True,
        index=True,
        readonly=True,
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name='account.analytic.tag',
        string='Analytic Tags',
    )
    amount_currency = fields.Float(
        required=True,
        help="Amount in multi currency",
    )
    credit = fields.Float(
        readonly=True,
    )
    debit = fields.Float(
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id.id,
        index=True,
    )
