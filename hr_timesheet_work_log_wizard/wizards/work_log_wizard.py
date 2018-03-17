# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models


class TimesheetWorkLogger(models.TransientModel):
    _name = 'hr.timesheet.work.logger'

    time_spent = fields.Float('Time Spent', required=True)
    date = fields.Date('Date Started',
                               default=lambda self: fields.Date.today(),
                               required=True)
    description = fields.Text('Description', required=True)
    project_id = fields.Many2one('project.project', 'Project', required=True)
    task_id = fields.Many2one('project.task', 'Task')
    product_id = fields.Many2one('product.product', 'Product')

    display_task = fields.Boolean('Display Task', default=True)
    display_product = fields.Boolean('Display Product')

    @api.multi
    @api.constrains('time_spent')
    def check_time_spent(self):
        self.ensure_one()
        if self.time_spent == 0:
            raise exceptions.ValidationError('Time Spent cannot be zero')
        if self.time_spent < 0:
            raise exceptions.ValidationError('Time Spent cannot be negative')

    @api.multi
    @api.onchange('project_id')
    def remove_non_matching_task(self):
        # Remove the task if it is not matching with the project
        if self.task_id and self.project_id and self.task_id.project_id != \
                self.project_id:
            self.task_id = False

    @api.multi
    @api.onchange('project_id', 'task_id')
    def _onchange_display_task_product(self):
        self.ensure_one()

        domain = {'task_id': [], 'product_id': []}

        # Set project from task
        if self.task_id and not self.project_id:
            self.project_id = self.task_id.project_id.id

        # Only display selection of task/product if there is one
        if self.project_id:
            # Task
            task_ids = self.env['project.task'].search([
                ('project_id', '=', self.project_id.id)])
            self.display_task = task_ids and True or False
            domain['task_id'] = [
                ('project_id', '=', self.project_id.id)]

            # Product
            sale_order = self.env['sale.order'].search(
                [('project_id', '=', self.project_id.analytic_account_id.id),
                 ('state', 'not in', ['done', 'cancel'])], limit=1)
            product_ids = \
                [line.product_id.id for line in
                 sale_order.sudo().order_line.filtered(lambda
                    l: l.product_id.product_tmpl_id.track_service == 'timesheet')]
            self.display_product = product_ids and True or False
            domain['product_id'] = [('id', 'in', product_ids)]

        return {'domain': domain}

    @api.multi
    def submit_log_work(self):
        self.env['account.analytic.line'].create({
            'unit_amount': self.time_spent,
            'project_id': self.project_id.id,
            'name': self.description,
            'is_timesheet': True,
            'product_id': self.product_id.id,
            'date': self.date,
            'task_id': self.task_id.id,
            'user_id': self._uid
        })
        return {'type': 'ir.actions.act_window_close'}
