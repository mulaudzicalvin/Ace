# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    identifier = fields.Char('Identifier', compute='compute_identifier',
                             store=True)
    is_created = fields.Boolean('Is Created', default=False,
                                compute='_compute_is_created')

    @api.depends('project_id.partner_id')
    def compute_identifier(self):
        for task in self:
            if not task.id:
                continue

            if task.project_id.partner_id:
                partner = task.project_id.partner_id.commercial_partner_id

                if not partner.project_key or (
                            task.identifier and not self._context.get(
                            'force_update')):
                    continue

                code = 'project.task.order.' + partner.project_key
                sequence = self.env['ir.sequence'].search(
                    [('code', '=', code)])
                if not sequence:
                    sequence = partner.create_sequence()
                id = sequence.next_by_code(code)
                task.identifier = id

    @api.multi
    def _compute_is_created(self):
        for task in self:
            if task.id:
                task.is_created = True

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('identifier', operator, name)]

        res = self.search(domain + args, limit=limit)
        return res.name_get()

    @api.multi
    @api.depends('name', 'identifier')
    def name_get(self):
        result = []
        for task in self:
            name = '%s - %s' % (task.identifier or '', task.name)
            result.append((task.id, name))
        return result
