from odoo import fields, api, models, tools, _
from odoo.exceptions import ValidationError, except_orm

import logging

_logger = logging.getLogger(__name__)
ITEM_TYPE = [("machine", "Machine"),
			("subcomponents", "Components"),
                        ("consumables", "Consumables"),
			("accessories", "Accessories"),
			("spares", "Spares"),
			("others", "Others")]

SERVICE_TYPE = [("installation", "Installation Charge"),
		("assembly", "Assembling Charge"),
		("servicech", "Service/Repair Charge"),
		("amcspare", "Annual Maintanance Contract"),
		("amcnospare", "Annual Service Contract")
		]
class ProductTemplates(models.Model):

	_inherit = 'product.template'

#        @api.model
#       def _get_default_type_service(self):
#		_logger.info("The default service is")
#                context = self._context
#		_logger.info("The default service context is = "+str(context))
#                if context.has_key('product_type'):
#                        type = context.get('product_type')
#                        if type == 'service':
#                                return 'installation'


#        @api.model
#        def _get_default_type_item(self):
#                context = self._context
#                if context.has_key('product_type'):
#                        type = context.get('product_type')
#                        if type == 'product':
#                                return 'machine'


	rental_ok = fields.Boolean(string="Can Be Rented")
	item_type = fields.Selection(ITEM_TYPE, string="Item Types", store=True)
	comparing_visible = fields.Boolean(string="Visible For Compairing")
	min_sale_price = fields.Float(string="Minimum Sale Price")
	spare_parts = fields.Many2many('product.template', 'spare_parts_prod_id', 'spare_id', string="Spare Parts")
	service_type = fields.Selection(SERVICE_TYPE, string="Service Type", store=True)
	machine_type = fields.Many2many("product.template", 'machine_prod_id', 'machine_id', string="Machines")	
	default_code = fields.Char(string="Model/Ref No")
	supplier_ref = fields.Char(string="Sup Model/Ref No")
	mini_buy_back = fields.Char(string="Minimum Buy Back(%)")
	consumables_ref = fields.Many2many("product.template", "consumables_prod_id", "consumable_id", string="Consumable")
	installation_ref = fields.Many2many("product.template", "instalation_prod_id", "installation_id", string="Installation")
	assembling_ref = fields.Many2many("product.template", "assembling_prod_id", "assembling_id", string="Assembling")
	service_ref = fields.Many2many("product.template", "service_prod_id", "service_id", string="Service")
	amc_with_ref = fields.Many2many("product.template", "amc_with_prod_id", "amc_with_id", string="Annual Maintananace Contract")
        amc_without_ref = fields.Many2many("product.template", "amc_without_prod_id", "amc_without_id", string="Annual Service Contract")
	prod_desc = fields.Text("Product Description")

	@api.onchange('type')
	def onchange_product_type(self):
		if self.type == 'service':
			self.service_type = 'installation'
		elif self.type == 'product':
			self.item_type = 'machine'
		else:
			self.service_type = None
			self.item_type = None

	@api.one
	@api.constrains("service_type", "is_contract")
	def onchange_service_type(self):
		if self.service_type != "amc" and self.is_contract:
			raise ValidationError("Contract Can Only Be Used For AMC")
		elif self.service_type == "amc" and not self.is_contract:
			raise ValidationError("Need Contract For AMC")

class ProductProduct(models.Model):

	_inherit = "product.product"

	rental_ok = fields.Boolean(string="Can Be Rented")
	item_type = fields.Selection(ITEM_TYPE, string="Item Types")
	comparing_visible = fields.Boolean(string="Visible For Compairing")
	sale_price_2 = fields.Float(string="Sale Price 2")
        prod_desc = fields.Text("Product Description", compute="_compute_prod_desc")
	price = fields.Float("Sale Price" , store=True)

	@api.depends('list_price', 'price_extra')
    	def _compute_product_lst_price(self):
		to_uom = None
        	if 'uom' in self._context:
            		to_uom = self.env['product.uom'].browse([self._context['uom']])

        	for product in self:
            		product.lst_price = product.price

	@api.one
	@api.depends('product_tmpl_id.prod_desc')
	def _compute_prod_desc(self):
		if not self.prod_desc:
			if self.product_tmpl_id.prod_desc:
				self.prod_desc = self.product_tmpl_id.prod_desc

