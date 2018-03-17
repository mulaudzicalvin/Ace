# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    @api.constrains('version_id', 'step_id')
    def check_version_id(self):
        for task in self.filtered(lambda t: t.step_id.requires_version):
            if not task.version_id:
                raise exceptions.ValidationError('Please add a version on this'
                                                 ' task')


class ProjectTaskStep(models.Model):
    _inherit = 'project.task.step'

    requires_version = fields.Boolean('Version Required')


class VersionStateStepLink(models.Model):
    _name = 'version.state.step.link'

    state_id = fields.Many2one('project.version.state', 'Version State',
                               required=True)
    step_id = fields.Many2one('project.task.step', 'Task Step',
                              required=True)
    category_id = fields.Many2one('project.task.category', 'Task Type',
                                  required=True)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        domain = {'step_id': []}

        # Remove the step if it is not matching with the workflow
        if self.step_id and self.category_id \
            and self.category_id.workflow_id.id \
                        not in self.step_id.workflow_ids.ids:
            self.step_id = False

        if self.category_id:
            domain['step_id'] = [(
                'workflow_ids', 'in', self.category_id.workflow_id.id)]
        return {'domain': domain}

    _sql_constraints = [(
        'state_category_unique',
        'unique (state_id,category_id)',
        'There is already an action on this state for this type of task'
    )]


class ProjectVersion(models.Model):
    _inherit = 'project.version'

    @api.multi
    @api.constrains('state_id', 'task_ids')
    def check_state(self):
        super(ProjectVersion, self).check_state()
        ProjectLink = self.env['version.state.step.link']
        for version in self:
            links = ProjectLink.search([
                ('state_id', '=', version.state_id.id),
            ])
            for link in links:
                tasks = version.task_ids.filtered(
                    lambda task: task.category_id.id == link.category_id.id)
                if tasks:
                    tasks.write({'step_id': link.step_id.id})
