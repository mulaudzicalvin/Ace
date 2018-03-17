# -*- coding: utf-8 -*-
# © 2017 ThinkOpen Solutions <https://tkobr.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class project_project(models.Model):
    _inherit = "project.project"

    default_assign_to_id = fields.Many2one(comodel_name='res.users',
                                           string='Default Assign To')
    default_reviewer_id = fields.Many2one(comodel_name='res.users',
                                          string='Default Reviewer To')
