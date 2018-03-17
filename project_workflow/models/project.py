# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models


class ProjectTaskStep(models.Model):
    _name = 'project.task.step'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    next_step_ids = fields.Many2many(
        'project.task.step', 'project_task_step_rel', 'previous_step_id',
        'next_step_id', 'Next steps')
    previous_step_ids = fields.Many2many(
        'project.task.step', 'project_task_step_rel', 'next_step_id',
        'previous_step_id', 'Previous steps')
    sequence = fields.Integer('Sequence')
    stage_id = fields.Many2one('project.task.type', 'Stage')
    start = fields.Boolean('Start', default=False)
    end = fields.Boolean('End', default=False)

    workflow_ids = fields.Many2many('project.task.workflow',
                                    'project_steps_workflows_rel', 'step_id',
                                    'workflow_id',
                                    string='Workflows',
                                    required=True)

    hidden = fields.Boolean('Hide In Status Bar', default=False,
                            help='Select to hide this step in the status bar')

    @api.constrains('start', 'workflow_ids')
    @api.multi
    def check_start(self):
        for step in self:
            if step.start:
                start_step = self.env['project.task.step'].search([
                    ('start', '=', True),
                    ('workflow_ids', 'in', step.workflow_ids.ids),
                    ('id', '!=', step.id)
                ])
                if start_step:
                    raise exceptions.Warning(
                        'You can only have one start step per workflow')


class ProjectTaskWorkflow(models.Model):
    _name = 'project.task.workflow'

    name = fields.Char('Name', required=True)
    step_ids = fields.Many2many('project.task.step',
                                'project_steps_workflows_rel',
                                'workflow_id', 'step_id',
                                string='Steps')


class ProjectTaskCategory(models.Model):
    _name = 'project.task.category'

    name = fields.Char('Name', required=True)
    workflow_id = fields.Many2one('project.task.workflow', 'Workflow',
                                  required=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    step_id = fields.Many2one('project.task.step', 'Step',
                              track_visibility='onchange')

    stage_id = fields.Many2one('project.task.type', track_visibility=False)

    category_id = fields.Many2one(
        'project.task.category', 'Type', required=True,
        default=lambda self: self.default_category())

    is_created = fields.Boolean('Is Created', default=False,
                                compute='_compute_is_created')
    workflow_id = fields.Many2one(
        'project.task.workflow', 'Workflow', related='category_id.workflow_id',
        readonly=True)

    @api.constrains('step_id')
    @api.multi
    def check_step(self):
        for task in self:
            task.stage_id = task.step_id.stage_id

    @api.multi
    def next_step(self):
        for task in self:
            if not task.category_id:
                task.category_id = task.default_category()
                task.onchange_category()
            if task.step_id and task.step_id.next_step_ids:
                task.step_id = task.get_next_step()

    @api.multi
    def get_next_step(self):
        self.ensure_one()
        return max(self.step_id.next_step_ids, key=lambda step: step.sequence)

    @api.onchange('category_id')
    @api.multi
    def onchange_category(self):
        for task in self:
            domain = [('start', '=', True),
                      ('workflow_ids', 'in', task.category_id.workflow_id.id)]
            step = self.env['project.task.step'].search(domain, limit=1)
            task.step_id = step

    def default_category(self):
        return self.env['project.task.category'].search([], limit=1)

    @api.multi
    def _compute_is_created(self):
        for task in self:
            if task.id:
                task.is_created = True
