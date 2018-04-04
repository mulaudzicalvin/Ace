# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class ResPartner(models.Model):
	_inherit = 'res.partner'


	sale_type = fields.Many2one(
		comodel_name='sale.order.type', string='Sale Order Type',
		company_dependent=True)
	sale_sub_type = fields.Many2one("sale.order.sub.type", string="Sub Type")

	taxes_id = fields.Many2many('account.tax', "form_wise_tax_in_partner", "partner_id", "taxes_id", string="Form Tax")
	tax_desc = fields.Text(string="Form Description")

	@api.multi
	@api.onchange('customer','supplier', 'company_id')
	def onchange_supplier_customer(self):
		res = {}
		if self.customer:
			res['domain'] = {'taxes_id':[('type_tax_use', '=', 'sale'),('company_id', '=', self.company_id.id)]}
		elif self.supplier:
			res['domain'] = {'taxes_id':[('type_tax_use', '=', 'purchase'),('company_id', '=', self.company_id.id)]}
		return res
