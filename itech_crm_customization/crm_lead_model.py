# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields, _
from odoo import api
from odoo.exceptions import Warning
import odoo.exceptions
import odoo.addons.decimal_precision as dp

class crmleadinherit(models.Model):
    _inherit = "crm.lead"
    
    planned_revenue = fields.Float(compute='_compute_total',string='Expected Revenue', track_visibility='always',store=True)
    order_line = fields.One2many('lead.order.line', 'lead_id', string='Order Lines')
    amount_total = fields.Float(compute='_compute_total',string='Amount Total',readonly=True,store=True)

 
    @api.model
    def create(self,vals):
        
        res_id = super(crmleadinherit, self).create(vals)
        if res_id.order_line:
            for rec in res_id.order_line:
                product_record={
                        'customer_id':res_id.partner_id.id,
                        'opportunity':res_id.name,
                        'name':rec.name.id,
                        'product_uom_qty':rec.product_uom_qty,
                        'price_unit':rec.price_unit,
                        'price_subtotal':rec.price_subtotal,
                        }
                self.env['crm.product.line'].create(product_record)  
        return res_id 

    @api.multi
    def write(self, vals):
        print vals
        res = super(crmleadinherit, self).write(vals)
        if 'order_line' in vals:
            print self.order_line
            for list in self.order_line:
                print list
                record_id = self.env['lead.order.line'].search([('id', '=', list.id)])
                print record_id.name
                con_id = self.env['crm.product.line'].search([('name', '=', record_id.name.id),('opportunity','=',self.name)])
                if con_id:
                    con_id.unlink()
            for list_item in self.order_line:
                record_id = self.env['lead.order.line'].search([('id', '=', list_item.id)])
                product_record={
                            'customer_id':self.partner_id.id,
                            'opportunity':self.name,
                            'name':record_id.name.id,
                            'product_uom_qty':record_id.product_uom_qty,
                            'price_unit':record_id.price_unit,
                            'price_subtotal':record_id.price_subtotal,
                            }
                self.env['crm.product.line'].create(product_record)  
        return res
     

           
    @api.one
    @api.depends('order_line')
    def _compute_total(self):
        if self.order_line:
            for lists in self.order_line:
                self.amount_total += lists.price_subtotal
        self.planned_revenue =self.amount_total

class LeadOrderLine(models.Model):
    _name = 'lead.order.line'
    _description = 'CRM Lead Order Line'
    _order = 'lead_id'

    lead_id = fields.Many2one('crm.lead', string='Order Reference', required=True, ondelete='cascade')
    name = fields.Many2one('product.template', string='Product', domain=[('sale_ok', '=', True)], required=True)
    product_uom_qty = fields.Float(string='Quantity',required=True, default=1.0)
    price_unit = fields.Float(related="name.list_price",string='Unit Price', required=True)
    price_subtotal = fields.Float(compute='_compute_amount',string='Subtotal',readonly=True,store=True)   
 
#     @api.model
#     def create(self,vals):
#         res_id = super(LeadOrderLine, self).create(vals)
#         res_id.price_subtotal= res_id.price_unit * res_id.product_uom_qty 
#         return res_id  
    @api.one  
    @api.depends('product_uom_qty','price_unit')
    def _compute_amount(self):
        self.price_subtotal= self.price_unit * self.product_uom_qty

    @api.multi        
    def unlink(self):
        print "a"
        con_id = self.env['crm.product.line'].search([('name', '=', self.name.id),('opportunity','=',self.lead_id.name)])
        print con_id.unlink()
        return super(LeadOrderLine, self).unlink()