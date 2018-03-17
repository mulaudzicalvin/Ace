# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def log_work_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref(
                'hr_timesheet_work_log_wizard.work_log_wizard').id,
            'name': 'Log Work',
            'target': 'new',
            'res_model': 'hr.timesheet.work.logger',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'default_task_id': self.id},
        }
