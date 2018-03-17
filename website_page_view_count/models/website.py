# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2017 darkknightapps@gmail.com
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import api, fields, models, _
from odoo.http import request

class Website(models.Model):
    _inherit = "website"
    
    @api.multi
    def get_page_view_count(self):
        page_view_count = request.session.get('page_visit_counter', 0)
        self.env.user.company_id.sudo().write({'website_page_visit_count': page_view_count})
        return page_view_count