# -*- coding: utf-8 -*-
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        if commission_based_on == 'sales_team':
            return True

    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_id = fields.Many2one(
        'sales.commission',
        string='Sales Commission',
        states={'draft': [('readonly', False)]}
    )
#     commission_manager_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Manager'
#     )
#     commission_person_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Member'
#     )
    sale_commission_user_ids = fields.One2many(
        'sale.commission.level.users',
        'account_id',
        string="Sale Commission User"
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'account_id',
        string="Sale Commission Level Percentage"
    )

    @api.multi
    @api.depends()
    def _compute_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        for rec in self:
            if commission_based_on == 'sales_team':
                rec.is_apply = True

    @api.multi
    @api.onchange('partner_id')
    def partner_id_change(self):
        for rec in self:
            sale_commission = []
            for level in rec.partner_id.sale_commission_user_ids:
                sale_commission.append((0,0,{'level_id': level.level_id.id,
                                        'user_id': level.user_id.id,
                                        'order_id':rec.id}))
            rec.sale_commission_user_ids = sale_commission

    @api.multi
    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            sale_commission_percentage = []
            for level in rec.team_id.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage,
                                        'sale_order_id':rec.id}))
            rec.sale_commission_percentage_ids = sale_commission_percentage

    @api.model
    def get_categorywise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.invoice_line_ids:
                for commission_id in line.sale_commission_percentage_ids:
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.price_subtotal * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission

    @api.multi
    def get_productwise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.invoice_line_ids:
                for commission_id in line.sale_commission_percentage_ids:
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.price_subtotal * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission
    
    @api.multi
    def get_teamwise_commission(self):
        for rec in self:
            commission = {}
            for commission_id in rec.sale_commission_percentage_ids:
                for partner in rec.sale_commission_user_ids:
                    if partner.level_id == commission_id.level_id:
                        amount = (rec.amount_untaxed * commission_id.percentage)/100
                        if partner.user_id not in commission:
                            commission[partner.user_id] = 0.0
                        commission[partner.user_id] += amount
        return commission

    @api.multi
    def create_commission(self, user_commission,commission):
        commission_obj = self.env['sales.commission.line']
        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
        for user in user_commission:
            for invoice in self:
                date_invoice = invoice.date_invoice
                if not date_invoice:
                    date_invoice = fields.Date.context_today(self)
                origin = ''
                if invoice.number:
                    origin = invoice.number    
                if invoice.name:
                    origin = origin + '-' +  invoice.name
                if invoice.origin:
                    origin = origin + '-' +  invoice.origin
                if user_commission:
                    for sale_commission in commission.commission_user_id:
                        if user.id == sale_commission.id:
                            commission_value = {
                                'sales_membar_user_id': user.id,
                                'amount': user_commission[user],
                                'origin': origin,
                                'user_id': user.id,
                                'product_id': product.id,
                                'date' : date_invoice,
                                'src_invoice_id': invoice.id,
                                'sales_commission_id':commission.id,
                                'sales_team_id': invoice.team_id and invoice.team_id.id or False,
                            }
                            commission_id = commission_obj.sudo().create(commission_value)
                            invoice.commission_person_id = commission_id.id
        return True
    
    @api.multi
    def create_base_commission(self, user):
        commission_obj = self.env['sales.commission']
        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
        if user:
            for order in self:
                today = date.today()
                first_day = today.replace(day=1)
                last_day = datetime.datetime(today.year,today.month,1)+relativedelta(months=1,days=-1)
                commission_value = {
                        'start_date' : first_day,
                        'end_date': last_day,
                        'product_id':product.id,
                        'commission_user_id': user.id,
                    }
                commission_id = commission_obj.sudo().create(commission_value)
            return commission_id
    
    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
        if  when_to_pay == 'invoice_validate':
            commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
            
            if commission_based_on == 'sales_team':
                user_commission = self.get_teamwise_commission()
            elif commission_based_on == 'product_category':
                user_commission = self.get_categorywise_commission()
            elif commission_based_on == 'product_template':
                user_commission = self.get_productwise_commission()
            for invoice in self:
                date_invoice = invoice.date_invoice
                if not date_invoice:
                    date_invoice = fields.Date.context_today(self)
                for user in user_commission:
                    commission = self.env['sales.commission'].search([
                        ('commission_user_id', '=', user.id),
                        ('start_date', '<', date_invoice),
                        ('end_date', '>', date_invoice),
                        ('state','=','draft'),],limit=1)
                    if not commission:
                        commission = invoice.create_base_commission(user)
                    if  commission:
                        invoice.create_commission(user_commission, commission)
        return res
    
    @api.multi
    def action_invoice_cancel(self):
        res = super(AccountInvoice, self).action_invoice_cancel()
        commission_obj = self.env['sales.commission.line']
        for rec in self:
            lines = commission_obj.sudo().search([('src_invoice_id', '=', rec.id)])
            for line in lines:
                if line.state == 'draft' or line.state == 'cancel':
                    line.state = 'exception'
                elif line.state in ('paid', 'invoice'):
                    raise UserError(_('You can not cancel this invoice because sales commission is invoiced/paid. Please cancel related commission lines and try again.'))
            #if rec.commission_manager_id:
            #    rec.commission_manager_id.state = 'exception'
            #if rec.commission_person_id:
            #    rec.commission_person_id.state = 'exception'
        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _get_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
        if commission_based_on != 'sales_team' and when_to_pay == 'invoice_validate':
            return True

    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'account_invoice_line_id',
        string="Sale Commission Level Percentage"
    )

    @api.multi
    @api.depends()
    def _compute_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
        for rec in self:
            if commission_based_on != 'sales_team' and when_to_pay == 'invoice_validate':
                rec.is_apply = True

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        for rec in self:
            if commission_based_on:
                sale_commission_percentage = []
                if commission_based_on == 'product_category':
                    for level in rec.product_id.categ_id.sale_commission_percentage_ids:
                        sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                                'percentage': level.percentage,
                                                'account_invoice_line_id':rec.id}))
                elif commission_based_on == 'product_template':
                    for level in rec.product_id.sale_commission_percentage_ids:
                        sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                                'percentage': level.percentage,
                                                'account_invoice_line_id':rec.id}))
                rec.sale_commission_percentage_ids = sale_commission_percentage
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
