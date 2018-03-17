# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):

    _inherit = "res.partner"

    tax_id_number = fields.Char('Tax Id Number')
    c_pin = fields.Integer('PIN')
    c_owner = fields.Char('Owner/President')
    c_ssn = fields.Char('SSN.')
    c_dob = fields.Char('D.O.B.')
    c_driver_lic = fields.Char('Driver Lic.#')
    c_bussines_start = fields.Date('Bussines Start')
    c_fns = fields.Integer('FNS#')
    c_routing = fields.Char('Routing')










