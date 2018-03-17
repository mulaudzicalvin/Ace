# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_ids = fields.Many2many(
        'project.version', 'project_version_rel', 'project_id', 'version_id',
        'Versions')


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    done = fields.Boolean('Done')


class ProjectVersion(models.Model):
    _name = 'project.version'
    _order = 'major DESC'

    @api.model
    def _default_state(self):
        return self.env.ref('project_version.draft')

    name = fields.Char('Name', compute='_compute_name', store=True,
                       readonly=True)
    major = fields.Char('Major', required=True)
    project_ids = fields.Many2many(
        'project.project', 'project_version_rel', 'version_id', 'project_id',
        'Projects', required=True)
    task_ids = fields.One2many('project.task', 'version_id', 'Tasks')
    state_id = fields.Many2one('project.version.state', 'State',
                               default=_default_state)

    @api.multi
    @api.depends('major', 'state_id')
    def _compute_name(self):
        for version in self:
            version.name = '%s [%s]' % (version.major or '',
                                        version.state_id.name)

    @api.multi
    def check_not_in_progress(self):
        self.ensure_one()
        done_stages = self.env['project.task.type'].search(
            [('done', '=', True)])
        not_started_tasks = self.env['project.task']

        for task in self.task_ids:
            if task.stage_id.id not in done_stages.ids:
                not_started_tasks |= task

        if not_started_tasks:
            warning = 'The following tasks are not ready for %s:\n' % \
                      self.state_id.name
            for name in not_started_tasks.name_get():
                warning = '%s- %s\n' % (warning, name[1])
            raise exceptions.ValidationError(warning)

    @api.multi
    @api.constrains('state_id', 'task_ids')
    def check_state(self):

        production = self.env.ref('project_version.production')
        past = self.env.ref('project_version.past')

        done_states = self.env['project.version.state'].search(
            [('done', '=', True)])
        ProjectVersion = self.env['project.version']

        for version in self:
            if version.state_id.id in done_states.ids:
                version.check_not_in_progress()
                if version.state_id.id == production.id:
                    old_production = ProjectVersion.search([
                        ('state_id', '=', production.id),
                        ('project_ids', 'in', version.project_ids.ids),
                        ('id', '!=', version.id)
                    ])
                    if old_production:
                        old_production.state_id = past

    @api.multi
    def write(self, vals):
        if 'task_ids' in vals:
            # Many2many widget on One2many field deletes the record
            # We just remove the link between the version and the task
            ProjectTask = self.env['project.task']

            for task in vals['task_ids']:
                if task[0] == 2:
                    vals['task_ids'].remove(task)
                    task_object = ProjectTask.browse(int(task[1]))
                    task_object.version_id = None

        return super(ProjectVersion, self).write(vals)


class ProjectVersionState(models.Model):
    _name = 'project.version.state'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence')
    done = fields.Boolean('Done State')

    _sql_constraints = [
        ('version_state_name_unique',
         'unique (name)',
         'The same state already exists.'),
    ]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    version_id = fields.Many2one('project.version', 'Version',
                                 track_visibility='onchange', copy=False)

    @api.multi
    @api.constrains('version_id')
    def _check_version(self):
        done_stages = self.env['project.task.type'].search(
            [('done', '=', True)])
        done_states = self.env['project.version.state'].search(
            [('done', '=', True)])
        for task in self:
            if task.stage_id.id not in done_stages.ids \
                    and task.version_id.state_id.id in done_states.ids:
                raise exceptions.ValidationError(
                    'You cannot add an unfinished task to a finished version')

    @api.multi
    def go_to_version_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'name': self.version_id.name,
            'domain': [('version_id', '=', self.version_id.id)],
        }
