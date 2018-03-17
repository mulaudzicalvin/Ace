# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None,
                          subtype_ids=None, force=True):
        for project in self:
            partners = self.env['res.partner'].browse(partner_ids)

            partner_names = ', '.join(map(unicode, partners.mapped('name')))

            if project.analytic_account_id.partner_id:
                project.analytic_account_id.partner_id.message_subscribe(
                    partner_ids, channel_ids, subtype_ids, force)
                project.message_post(
                    body='Partner(s) %s now have access to this project'
                         % partner_names)
            else:
                project.message_post(
                    body='''
Partner(s) %s were added as follower but do not have access to this project.
Please select a customer they follow to give access to this project
''' % partner_names)

            super(ProjectProject, project).message_subscribe(
                partner_ids, channel_ids, subtype_ids, force)

    @api.multi
    def message_unsubscribe(self, partner_ids=None, channel_ids=None):
        partners = self.env['res.partner'].browse(partner_ids)
        partner_names =', '.join(map(unicode, partners.mapped('name')))

        for project in self:
            project.analytic_account_id.partner_id.message_unsubscribe(
                partner_ids, channel_ids)

            super(ProjectProject, project).message_unsubscribe(
                partner_ids, channel_ids)
            project.message_post(
                body='Partner(s) %s removed from followers' % partner_names
            )
