# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.exceptions import ValidationError
import urllib2
import math
import urllib, json
import logging
import yaml

_logger = logging.getLogger(__name__)

DEFAULT_PARAMS = '''#Insert a python dictionnay with all the needed parameters
# you can use 'o' which is the mrp.production object. If you want to print its
# ID, you could add the following to the dictionnary:'production_id': o.id
# Example:
# params = {
#     'product': 'product_name',
#     'price': 125,
#     'barcode': 123456789,
# }
'''


class PrintOperation(models.Model):

    _name = 'print.operation'

    name = fields.Char(string='Name')
    params = fields.Text(string='Parameters',
                         default=DEFAULT_PARAMS)

    print_qty = fields.Integer(string='Quantity to print', default=1)
    print_on = fields.Selection([('mark_as_done', 'Mark as Done'),
                                 ('input_quantity', 'Quantity Input'),
                                 ('workorder_done', 'Work Order is Done'),
                                 ('stock_pack_operation_manual',
                                  'Stock Pack Operation (manual click)')],
                                required=True, string='Print on')
    print_template_name = fields.Char(string='Name of the bartender template',
                                      required=True)

    object = fields.Selection([('mrp_production', 'MRP Production'),
                               ('products', 'MRP Production Product'),
                               ('mrp_workorder', 'MRP Work Order'),
                               ('stock_pack_operation', 'Stock Pack Operation')],
                              string='Object', required=True)

    operation_ids = fields.Many2many('mrp.routing.workcenter',
                                     string='On operations')

    picking_type_ids = fields.Many2many('stock.picking.type',
                                           string='Picking Type')

    @api.constrains('params')
    def _check_params(self):
        for action in self.filtered('params'):
            msg = test_python_expr(expr=action.params.strip(), mode='eval')
            if msg:
                raise ValidationError(msg)

    @api.multi
    def test_print(self):
        self.ensure_one()

        irconfig = self.env['ir.config_parameter']
        host = irconfig.get_param('bartender_host', default='')
        port = irconfig.get_param('bartender_port', default='')

        if not host or not port:
            raise ValidationError('Please Configure a Bartender Host/port')

        url = 'http://%s:%s/Integration/%s/Execute' \
              % (host, port, self.print_template_name)
        urllib2.urlopen(url).read()

    @api.multi
    def run_code(self, object_id=False, quantity=1, final_lot_id=False, pack_lot_id=False):
        self.ensure_one()

        irconfig = self.env['ir.config_parameter']
        host = irconfig.get_param('bartender_host', default='')
        port = irconfig.get_param('bartender_port', default='')

        if not host or not port:
            raise ValidationError('Please Configure a Bartender Host/port')


        elif self.object == 'products':
            object = object_id.move_finished_ids
        else:
            object = object_id

        params = {
        }
        safe_eval(self.params.strip(),
                           {'o': object,
                            'params': params,
                            'final_lot_id': final_lot_id},
                           mode='eval', nocopy=True)
        # adding the total quantity to print to the parameter
        params['total_quantity'] = quantity

        # doing a for loop instead of passing nb_copy in the params,
        # so we can for example print 3 stickers
        # for each product if they configure the print operation as so.
        qty = int(math.ceil(quantity))
        for index in range(qty):

            # adding the current sticker index to the parameters
            params['index'] = index
            self.print_product(host, port, params, object_id)

    @api.multi
    def print_product(self,  host, port, params, object_id):
        url = 'http://%s:%s/Integration/%s/Execute' \
              % (host, port, self.print_template_name)

        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')

        self.env['printed.sticker'].create({
            'template_name': self.print_template_name,
            'json_params': params,
            'date_printed': fields.Datetime.now(),
            'mrp_production_id': object_id.id if
                object_id._name == 'mrp.production' else False,
            'stock_picking_id': object_id.operation_id.picking_id.id if
                object_id._name == 'stock.pack.operation.lot' else False,
        })
        _logger.info("Printed with url %s and parameterss %s" % (
            url, json.dumps(params)))

        try:
            response = urllib2.urlopen(req, json.dumps(params))
            _logger.info(response)
        except urllib2.URLError, ex:
            _logger.info('Exception occured during print: %s' % ex)

    @api.multi
    def manual_print(self):
        self.ensure_one()
        params = self.params.strip().split("params.update(", 1)[1][:-1]
        param_dict = yaml.load(params)
        manual_print_lines = []

        for key, value in param_dict.iteritems():
            manual_print_lines.append((0, 0, {
                'parameter_name': key,
                'parameter_value': value,
            }))

        return {
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref(
                'sticker_management.manual_print_form').id,
            'name': 'Manual Print',
            'target': 'new',
            'res_model': 'manual.print.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'default_print_operation_id': self.id,
                        'default_parameter_line_ids': manual_print_lines},
        }
