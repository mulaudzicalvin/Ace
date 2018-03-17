# -*-coding:utf-8-*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class res_partner(models.Model):
    _inherit = "res.partner"

    default_support_project_id = fields.Many2one(
        comodel_name='project.project', string='Default Project')
