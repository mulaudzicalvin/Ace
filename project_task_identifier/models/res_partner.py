# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    project_key = fields.Char('Project Identifier Key')
    project_partner_sequence = fields.Many2one('ir.sequence',
                                               'Identifier Sequence')

    @api.multi
    @api.constrains('project_key')
    def check_project_key(self):
        for partner in self:
            if not partner.project_partner_sequence and partner.project_key:
                partner.create_sequence()
                # update existing tasks
                tasks = self.env['project.task'].search([
                    ('project_id.analytic_account_id.partner_id', '=',
                     partner.id)
                ])
                tasks.with_context(force_update=True).compute_identifier()

    @api.multi
    def create_sequence(self):
        self.ensure_one()
        code = 'project.task.order.%s' % self.project_key
        sequence = self.env['ir.sequence'].search([('code', '=', code)])
        if not sequence:
            name = 'project task order - %s' % self.name
            sequence = self.env['ir.sequence'].sudo().create({
                'code': code,
                'name': name,
                'prefix': '%s-' % self.project_key
            })
            self.sudo().project_sequence = sequence

    _sql_constraints = [
        ('unique_project_key',
         'UNIQUE (project_key)',
         'Project key should be unique')
    ]
