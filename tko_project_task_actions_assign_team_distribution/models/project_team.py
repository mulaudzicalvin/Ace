# -*- encoding: utf-8 -*-
from odoo import fields, api, models, _






class ProjectTeam(models.Model):
    _inherit = 'project.task.action'

    team_type = fields.Selection([('t',u'Single Team'),('d',u'Team Distribution')], default='t', string=u'Team Type')
    distribution_id = fields.Many2one('teams.distribution',u'Distribução')


class ProjectTaskActionLine(models.Model):
    _inherit = 'project.task.action.line'


    def get_team_id(self):
        team_id = super(ProjectTaskActionLine, self).get_team_id()
        if self.action_id.team_type == 'd':
            field_name = self.action_id.distribution_id.field_id.name
            # match team with grupo_id of task
            if getattr(self.task_id,field_name, False):
                for line in self.action_id.distribution_id.team_distribution_ids:
                    if line.grupo_id == getattr(self.task_id,field_name, False):
                        team_id = line.team_id.id or False
        return team_id



class TeamClientDistribution(models.Model):
    _name = 'teams.distribution'

    name = fields.Char(u'Name')
    team_id = fields.Many2one('project.team', 'Team')
    grupo_id = fields.Many2one('res.partner',u'Grupo')
    field_id = fields.Many2one('ir.model.fields',u'Validation Field')
    distribution_id = fields.Many2one('teams.distribution', u'Distribução')
    team_distribution_ids = fields.One2many('teams.distribution', 'distribution_id', 'Team')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
        ('name_uniq', 'unique (team_id,grupo_id,distribution_id)', _('Teams and Groupo must be unique')),
    ]



