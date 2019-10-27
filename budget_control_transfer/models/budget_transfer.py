# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class BudgetTransfer(models.Model):
    _name = 'budget.transfer'
    _description = 'Budget Transfer by Item'

    name = fields.Char(
        required=True,
    )
    budget_management_id = fields.Many2one(
        comodel_name='budget.management',
        string='Budget Year',
        required=True,
    )
    mis_budget_id = fields.Many2one(
        comodel_name='mis.budget',
        related='budget_management_id.mis_budget_id',
        readonly=True,
    )
    transfer_item_ids = fields.One2many(
        comodel_name='budget.transfer.item',
        inverse_name='transfer_id',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('transfer', 'Transferred'),
         ('reverse', 'Reversed'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
    )

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_transfer(self):
        self.mapped('transfer_item_ids').transfer()
        self._check_budget_control()
        self.write({'state': 'transfer'})

    @api.multi
    def action_reverse(self):
        self.mapped('transfer_item_ids').reverse()
        self._check_budget_control()
        self.write({'state': 'reverse'})

    @api.multi
    def _check_budget_control(self):
        """Ensure no budget control will result in negative amount."""
        transfers = self.mapped('transfer_item_ids')
        budget_controls = transfers.mapped('source_budget_control_id') | \
            transfers.mapped('target_budget_control_id')
        # TODO:
        # Test that, after the transfer,
        # no one analytic will be negative amount


class BudgetTransferItem(models.Model):
    _name = 'budget.transfer.item'
    _description = 'Budget Transfer by Item'

    transfer_id = fields.Many2one(
        comodel_name='budget.transfer',
        ondelete='cascade',
        index=True,
    )
    mis_budget_id = fields.Many2one(
        comodel_name='mis.budget',
        related='transfer_id.mis_budget_id',
    )
    source_budget_control_id = fields.Many2one(
        comodel_name='budget.control',
        string='Source',
        domain="[('budget_id', '=', mis_budget_id)]",
        required=True,
    )
    target_budget_control_id = fields.Many2one(
        comodel_name='budget.control',
        string='Target',
        domain="[('budget_id', '=', mis_budget_id)]",
        required=True,
    )
    source_item_id = fields.Many2one(
        comodel_name='mis.budget.item',
        domain="[('budget_control_id', '=', source_budget_control_id)]",
        ondelete='restrict',
        required=True,
    )
    target_item_id = fields.Many2one(
        comodel_name='mis.budget.item',
        domain="[('budget_control_id', '=', target_budget_control_id)]",
        ondelete='restrict',
        required=True,
    )
    source_amount = fields.Float(
        related='source_item_id.amount',
        readonly=True,
    )
    target_amount = fields.Float(
        related='target_item_id.amount',
        readonly=True,
    )
    amount = fields.Float(
        string='Transfer Amount',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('transfer', 'Transferred'),
         ('reverse', 'Reversed')],
        string='Status',
        default='draft',
    )

    @api.onchange('source_budget_control_id')
    def _onchange_source_budget_control_id(self):
        self.source_item_id = False

    @api.onchange('target_budget_control_id')
    def _onchange_target_budget_control_id(self):
        self.target_item_id = False

    @api.multi
    def transfer(self):
        for transfer in self:
            if transfer.state != 'draft':
                raise ValidationError(_('Invalid state!'))
            if transfer.source_budget_control_id == \
                    transfer.target_budget_control_id:
                raise UserError(_(
                    'You can transfer from the same budget control sheet!'))
            if transfer.amount > transfer.source_amount:
                raise UserError(_('Transfer amount exceed source amount!'))
            transfer.source_item_id.amount -= transfer.amount
            transfer.target_item_id.amount += transfer.amount
            transfer.state = 'transfer'

    @api.multi
    def reverse(self):
        for transfer in self:
            if transfer.state != 'transfer':
                raise ValidationError(_('Invalid state!'))
            if transfer.amount > transfer.source_amount:
                raise UserError(_('Transfer amount exceed source amount!'))
            transfer.source_item_id.amount += transfer.amount
            transfer.target_item_id.amount -= transfer.amount
            transfer.state = 'reverse'
