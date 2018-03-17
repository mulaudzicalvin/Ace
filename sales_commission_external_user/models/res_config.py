# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'
    
    commission_based_on = fields.Selection([
        ('sales_team', 'Sales Team'),
        ('product_category', 'Product Category'),
        ('product_template', 'Product')], 
        string="Calculation Based On",
    )
    when_to_pay = fields.Selection([
        ('sales_confirm', 'Sales Confirmation'),
        ('invoice_validate', 'Invoice Validate'),
        ('invoice_payment', 'Customer Payment')], 
        string="When To Pay",
    )
    
    @api.multi
    def set_commission_based_on_defaults(self):
        if self.when_to_pay == 'invoice_payment':
            if self.commission_based_on == 'product_category' or self.commission_based_on == 'product_template':
                raise Warning(_("Sales Commission: You can not have commision based on product or category if you have selected when to pay is payment."))
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'commission_based_on', self.commission_based_on)

    @api.multi
    def set_when_to_pay_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'when_to_pay', self.when_to_pay)
