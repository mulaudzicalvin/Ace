# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import urllib2
import json
import logging
_logger = logging.getLogger(__name__)


class PrintedStickers(models.Model):

    _name = 'printed.sticker'

    date_printed = fields.Datetime(String='Printed On')
    template_name = fields.Text(string='URL called')
    json_params = fields.Text(string='Parameters')
    mrp_production_id = fields.Many2one('mrp.production',
                                        string='Origin Production')
    stock_picking_id = fields.Many2one('stock.picking',
                                        string='Origin Picking')

    @api.multi
    def reprint_sticker(self):
        irconfig = self.env['ir.config_parameter']
        host = irconfig.get_param('bartender_host', default='')
        port = irconfig.get_param('bartender_port', default='')

        for sticker in self:
            url = 'http://%s:%s/Integration/%s/Execute' \
              % (host, port, sticker.template_name)
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/json')
            params = json.dumps(sticker.json_params)
            _logger.info("Printed with url %s and parameterss %s" % (url,
                                                                     params))

            response = urllib2.urlopen(req, params)
            _logger.info(response)
