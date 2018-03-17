# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, exceptions, models, fields


class SaleOrders(models.Model):
    _inherit = 'sale.order'

    timesheet_unlinked_ids = fields.Many2many(
        'account.analytic.line', compute='_compute_unlinked_timesheet_ids',
        string='Timesheet activities associated bot not to this sale')
    timesheet_unlinked_count = fields.Float(string='Unlinked Timesheet',
                                   compute='_compute_unlinked_timesheet_ids')

    timesheet_linked_ids = fields.Many2many(
        'account.analytic.line', compute='_compute_linked_timesheet_ids',
        string='Timesheet activities associated to this sale')
    timesheet_linked_count = fields.Float(string='Linked Timesheet',
                                      compute='_compute_linked_timesheet_ids')

    @api.multi
    def action_confirm(self):
        res = super(SaleOrders, self).action_confirm()
        AccountAnalyticLine = self.env['account.analytic.line']

        domain = [('account_id', '=', self.project_id.id),
                  ('so_line', '=', False),
                  '|',
                  ('sheet_id', '=', False),
                  ('sheet_id.state', 'not in', ('done', 'confirm'))]
        acc_analytic_lines = AccountAnalyticLine.search(domain)
        acc_analytic_lines.write({})
        for order in self:
            order.order_line._compute_analytic()
        return res

    @api.multi
    @api.constrains('order_line')
    def check_invoice_policy(self):
        for order in self:
            for line in order.order_line:
                if line.product_id.invoice_policy == 'cost' and \
                        not order.project_id:
                    raise exceptions.ValidationError(
                        'You must set a project for Time and Material'
                        ' products')

    @api.multi
    def action_view_timesheet_unlinked(self):
        result = self.action_view_timesheet()
        if self.timesheet_unlinked_count > 0:
            result['domain'] = "[('id','in',%s)]" % \
                               self.timesheet_unlinked_ids.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    @api.depends('project_id.line_ids')
    def _compute_unlinked_timesheet_ids(self):
        for order in self:
            timesheets = []
            if order.project_id:
                timesheets = self.env['account.analytic.line'].search(
                    [('is_timesheet', '=', True),
                     ('so_line', '=', False),
                     ('account_id', '=', order.project_id.id)])
            order.timesheet_unlinked_ids = timesheets
            order.timesheet_unlinked_count = round(
                sum([line.unit_amount
                     for line in order.timesheet_unlinked_ids]), 2)

    @api.multi
    def action_view_timesheet_linked(self):
        result = self.action_view_timesheet()
        if self.timesheet_linked_count > 0:
            result['domain'] = "[('id','in',%s)]" % \
                               self.timesheet_linked_ids.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    @api.depends('project_id.line_ids')
    def _compute_linked_timesheet_ids(self):
        for order in self:
            timesheets = []
            if order.project_id:
                timesheets = self.env['account.analytic.line'].search(
                    [('is_timesheet', '=', True),
                     ('so_line', 'in', order.order_line.ids),
                     ('account_id', '=', order.project_id.id)])
            order.timesheet_linked_ids = timesheets
            order.timesheet_linked_count = round(
                sum([line.unit_amount
                     for line in order.timesheet_linked_ids]), 2)

    @api.model
    def _check_multi_timesheet(self):
        return {}

