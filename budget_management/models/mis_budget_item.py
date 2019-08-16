# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class MisBudgetItem(models.Model):
    _inherit = 'mis.budget.item'

    budget_control_id = fields.Many2one(
        comodel_name='budget.control',
        ondelete='cascade',
        index=True,
    )
    active = fields.Boolean(
        compute='_compute_active',
        readonly=True,
    )

    @api.multi
    def _compute_active(self):
        for rec in self:
            if rec.budget_control_id:
                rec.active = rec.budget_control_id.active
            else:
                rec.active = True
