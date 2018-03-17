# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BartenderConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    bartender_host = fields.Char(string='Bartender Host')
    bartender_port = fields.Char(string='Bartender Port')

    @api.multi
    def set_bartender(self):
        params = self.env['ir.config_parameter']
        params.set_param('bartender_host', self.bartender_host)
        params.set_param('bartender_port', self.bartender_port)

    @api.model
    def get_default_bartender(self, fields):
        params = self.env['ir.config_parameter']
        bartender_host = params.get_param('bartender_host', default='')
        bartender_port = params.get_param('bartender_port', default='')
        return dict(bartender_port=bartender_port,
                    bartender_host=bartender_host)
