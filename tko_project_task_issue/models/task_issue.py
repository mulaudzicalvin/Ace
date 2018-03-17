# -*- coding: utf-8 -*-
# © 2017 ThinkOpen Solutions <https://tkobr.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class TasktoIssue(models.Model):
    _inherit = 'project.task'
    is_issue = fields.Selection(string="Is Issue",
                                selection=[('i', 'Issue'), ('t', 'Task')],
                                required=True,
                                default='t',
                                track_visibility='onchange')

    email_from = fields.Char(string='E-mail', required=False, size=128,
                             help='These people will receive email.', )
    author_id = fields.Many2one(comodel_name='res.partner', string='Author',
                                required=False)
    email_body = fields.Text(u'E-mail Body')

    def message_new(self, msg, custom_values=None):
        """ Override to updates the document according to the email. """
        if custom_values is None:
            custom_values = {}
        email_from = msg.get('email_from')
        if '<' in email_from and '>' in email_from:
            email_from = msg.get('email_from').split('<')[1].split('>')[0]
        partner_id = msg.get('author_id', False)
        if partner_id:
            author_obj = self.env['res.partner'].browse(msg.get(
                'author_id', False))
            partner_id = author_obj.parent_id and author_obj.parent_id.id
        defaults = {
            'email_from': email_from,
            'author_id': msg.get('author_id', False),
            'email_body': msg.get('body', False),
            'partner_id': partner_id,
        }
        defaults.update(custom_values)
        return super(TasktoIssue, self).message_new(msg,
                                                    custom_values=defaults)

    @api.one
    def convert_to_task(self):
        if self.is_issue == 'i':
            self.is_issue = 't'

    @api.onchange('author_id')
    def onchange_author_id(self):
        self.email_from = self.author_id.email

    @api.onchange('project_id')
    def _onchange_project(self):
        super(TasktoIssue, self)._onchange_project()
        if self.project_id:
            self.user_id = self.project_id.default_assign_to_id
            self.reviewer_id = self.project_id.default_reviewer_id
