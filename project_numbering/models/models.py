# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class PNProjectTask(models.Model):
    _inherit = ['project.task']

    number = fields.Char('Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('project_numbering.task_seq') or _('New')

        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
        task = super(PNProjectTask, self.with_context(context)).create(vals)
        return task


class PNProjectIssue(models.Model):
    _inherit = ['project.issue']

    number = fields.Char('Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('project_numbering.issue_seq') or _('New')

        context = dict(self.env.context)
        if vals.get('project_id') and not self.env.context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        if vals.get('user_id') and not vals.get('date_open'):
            vals['date_open'] = fields.Datetime.now()
        if 'stage_id' in vals:
            vals.update(self.update_date_closed(vals['stage_id']))

        # context: no_log, because subtype already handle this
        context['mail_create_nolog'] = True
        return super(PNProjectIssue, self.with_context(context)).create(vals)
