# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    display_task = fields.Boolean('Display Task', default=True)

    @api.multi
    @api.onchange('project_id')
    def remove_non_matching_task(self):
        # Remove the task if it is not matching with the project
        if self.task_id and self.project_id and self.task_id.project_id != \
                self.project_id:
            self.task_id = False

    @api.multi
    @api.onchange('project_id', 'task_id')
    def _onchange_display_task(self):
        self.ensure_one()

        domain = {'task_id': []}

        # Set project from task
        if self.task_id and not self.project_id:
            self.project_id = self.task_id.project_id

        # Only display selection of task/product if there is one
        if self.project_id:
            task_ids = self.env['project.task'].search([
                ('project_id', '=', self.project_id.id)])

            self.display_task = task_ids and True or False

            domain['task_id'] = [
                ('project_id', '=', self.project_id.id)]

        return {'domain': domain}

    # Remove existing onchange
    @api.onchange('project_id')
    def onchange_project_id(self):
        pass
