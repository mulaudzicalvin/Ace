# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	def _get_order_type(self):
		return self.env['sale.order.type'].search([], limit=1)


	type_id = fields.Many2one(
		comodel_name='sale.order.type', string='Type', default=_get_order_type)

	sub_type_id = fields.Many2one("sale.order.sub.type", string="Sub Type", required=True)

	@api.multi
	@api.onchange('partner_id')
	def onchange_partner_id(self):
		super(SaleOrder, self).onchange_partner_id()
		if self.partner_id.sale_type:
			self.type_id = self.partner_id.sale_type

	@api.multi
	@api.onchange('type_id')
	def onchange_type_id(self):
		for order in self:
			if order.type_id.warehouse_id:
				order.warehouse_id = order.type_id.warehouse_id
			if order.type_id.picking_policy:
				order.picking_policy = order.type_id.picking_policy
			if order.type_id.payment_term_id:
				order.payment_term_id = order.type_id.payment_term_id.id
			if order.type_id.pricelist_id:
				order.pricelist_id = order.type_id.pricelist_id.id
			if order.type_id.incoterm_id:
				order.incoterm = order.type_id.incoterm_id.id

	@api.model
	def create(self, vals):
		if vals.get('name', '/') == '/'and vals.get('type_id'):
			sale_type = self.env['sale.order.type'].browse(vals['type_id'])
			if sale_type.sequence_id:
				vals['name'] = sale_type.sequence_id.next_by_id()
		return super(SaleOrder, self).create(vals)

	@api.multi
	def _prepare_invoice(self):
		res = super(SaleOrder, self)._prepare_invoice()
		if self.type_id.journal_id:
			res['journal_id'] = self.type_id.journal_id.id
		if self.type_id:
			res['sale_type_id'] = self.type_id.id
		if self.sub_type_id:
			res['sale_sub_type_id'] = self.sub_type_id.id
		#_logger.info("the Value in res = "+str(res))
		return res

class SaleOrderLine(models.Model):

	_inherit = "sale.order.line"

	@api.multi
	def _compute_tax_id(self):
		for line in self:
			fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
			# If company_id is set, always filter taxes by the company
			formstate, forminter, inter, state = False, False, False, False
			tax_lines = []
			if line.sale_sub_type.tax_type == 'gst':
				state = True
				formstate, forminter, inter = False, False, False
			elif line.sale_sub_type.tax_type == 'igst':
				inter = True
				formstate, forminter, state = False, False, False
			elif line.sale_sub_type.tax_type == 'formstate':
				formstate = True
				forminter, state, inter = False, False, False
			elif line.sale_sub_type.tax_type == 'forminter':
				forminter = True
				formstate, state, inter = False, False, False
			if state or inter:
				taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
				if taxes:
					for tax in taxes:
						if state:
							if tax.tax_type == "cgst" or tax.tax_type == "sgst":
								tax_lines.append(tax.id)
						elif inter:
							if tax.tax_type == "igst":
								tax_lines.append(tax.id)
			elif forminter or formstate:
				taxes = line.order_partner_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
				if taxes:
					for tax in taxes:
						if formstate:
							if tax.tax_type == "cgst" or tax.tax_type == "sgst":
								tax_lines.append(tax.id)
						elif forminter:
							if tax.tax_type == "igst":
								tax_lines.append(tax.id)
			if tax_lines:
				taxes = self.env['account.tax'].browse(tax_lines)
				line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
			
			
	sale_sub_type = fields.Many2one("sale.order.sub.type", string="Sale Sub Type", store=True)


	@api.multi
	def _prepare_invoice_line(self, qty):
		res = super(SaleOrderLine, self)._prepare_invoice_line(qty=qty)
		res['sale_sub_type_id'] = self.sale_sub_type.id
		return res

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		if not self.product_id:
			return {'domain': {'product_uom': []}}

		vals = {}
		domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
			vals['product_uom'] = self.product_id.uom_id
			vals['product_uom_qty'] = 1.0

		product = self.product_id.with_context(
			lang=self.order_id.partner_id.lang,
			partner=self.order_id.partner_id.id,
			quantity=vals.get('product_uom_qty') or self.product_uom_qty,
			date=self.order_id.date_order,
			pricelist=self.order_id.pricelist_id.id,
			uom=self.product_uom.id
		)

		result = {'domain': domain}
		sale_sub_type = self.env['sale.order.sub.type'].browse(self._context.get('sale_sub_type'))
		if sale_sub_type:
			self.sale_sub_type = sale_sub_type
			vals['sale_sub_type'] = sale_sub_type

		_logger.info("The Values are = "+str(vals))
		title = False
		message = False
		warning = {}
		if product.sale_line_warn != 'no-message':
			title = _("Warning for %s") % product.name
			message = product.sale_line_warn_msg
			warning['title'] = title
			warning['message'] = message
			result = {'warning': warning}
			if product.sale_line_warn == 'block':
				self.product_id = False
				return result

		name = product.name_get()[0][1]
		if product.description_sale:
			name += '\n' + product.description_sale
		vals['name'] = name

		self._compute_tax_id()

		if self.order_id.pricelist_id and self.order_id.partner_id:
			vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
		self.update(vals)

		return result
