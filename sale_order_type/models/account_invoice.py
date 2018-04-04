# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    sale_type_id = fields.Many2one(
        comodel_name='sale.order.type',
        string='Sale Type', default=_get_order_type)
    sale_sub_type_id = fields.Many2one("sale.order.sub.type", string="Sale Sub Type")

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            # _logger.info("The value in partner_id = "+str(self.partner_id.sale_sub_type.id))
            if self.partner_id.sale_type:
                self.sale_type_id = self.partner_id.sale_type.id
            if self.partner_id.sale_sub_type:
                self.sale_sub_type_id = self.partner_id.sale_sub_type.id


    @api.onchange('sale_type_id')
    def onchange_sale_type_id(self):
        if self.sale_type_id.payment_term_id:
            self.payment_term = self.sale_type_id.payment_term_id.id
        if self.sale_type_id.journal_id:
            self.journal_id = self.sale_type_id.journal_id.id

class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    sale_sub_type_id = fields.Many2one('sale.order.sub.type', string="Sale Sub Type", required=True)

    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        formstate, forminter, inter, state = False, False, False, False
        tax_lines = []
        taxes, fp_taxes = [], []
        if self.sale_sub_type_id.tax_type == 'gst':
            state = True
            formstate, forminter, inter = False, False, False
        elif self.sale_sub_type_id.tax_type == 'igst':
            inter = True
            formstate, forminter, state = False, False, False
        elif self.sale_sub_type_id.tax_type == 'formstate':
            formstate = True
            forminter, state, inter = False, False, False
        elif self.sale_sub_type_id.tax_type == 'forminter':
            forminter = True
            formstate, state, inter = False, False, False

        if state or inter:
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids
            company_id = self.company_id or self.env.user.company_id
            taxes = taxes.filtered(lambda r: r.company_id == company_id)
            if taxes:
                for tax in taxes:
                    if state:
                        if tax.tax_type == "cgst" or tax.tax_type == "sgst":
                            tax_lines.append(tax.id)
                    elif inter:
                        if tax.tax_type == "igst":
                            tax_lines.append(tax.id)
        elif forminter or formstate:
            taxes = self.partner_id.taxes_id or self.account_id.tax_ids
            company_id = self.company_id or self.env.user.company_id
            taxes = taxes.filtered(lambda r: r.company_id == company_id)
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
            self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_id)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
        else:
            self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a partner!'),
                }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            # Use the purchase uom by default
            self.uom_id = self.product_id.uom_po_id

            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            sale_sub_type = self.env['sale.order.sub.type'].browse(self._context.get('sub_type_id'))
            self.sale_sub_type_id = sale_sub_type.id
            self._set_taxes()
            if type in ('in_invoice', 'in_refund'):
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
            else:
                if product.description_sale:
                    self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:
                if company.currency_id != currency:
                    self.price_unit = self.price_unit * currency.with_context(dict(self._context or {}, date=self.invoice_id.date_invoice)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
        return {'domain': domain}


class AccountTaxes(models.Model):

    _inherit = 'account.tax'

    @api.multi
    def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
        """Subtract tax amount from price when corresponding "price included" taxes do not apply"""
        # FIXME get currency in param?
        if prod_taxes:
            incl_tax = prod_taxes.filtered(lambda tax: tax not in line_taxes and tax.price_include)
            if incl_tax:
                return incl_tax.compute_all(price)['total_excluded']
        return price
