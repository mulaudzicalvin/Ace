# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields, _
from odoo import api
from odoo.exceptions import Warning
import odoo.exceptions
import odoo.addons.decimal_precision as dp

class crmproductline(models.Model):
    _name = 'crm.product.line'
    _description = 'CRM Lead Product Line'

    name = fields.Many2one('product.product', string='Product')
    customer_id = fields.Many2one("res.partner", string="Customer")
    opportunity = fields.Char(string="Opportunity")
    product_uom_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal')   
 
#     @api.model
#     def create(self,vals):
#         res_id = super(LeadOrderLine, self).create(vals)
#         res_id.price_subtotal= res_id.price_unit * res_id.product_uom_qty 
#         return res_id  
