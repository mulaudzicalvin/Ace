# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models, _
import logging
from odoo.osv import  osv
from odoo import SUPERUSER_ID


class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"
    
    @api.multi
    def issue_count(self):
        task_obj = self.env['project.issue']
        self.issue_number = task_obj.search_count([('lead_id', 'in', [a.id for a in self])])

    issue_number = fields.Integer(compute='issue_count', string='Tasks')

class crm_issue_wizard(models.TransientModel):
    _name = 'crm.issue.wizard'
    
    
    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        name = crm_brw.name
        return name
    
    
    project_id = fields.Many2one('project.project','Project')
    name = fields.Char('Task Name',default = get_name)
    user_id = fields.Many2one('res.users','Assigned To',default=lambda self: self.env.uid,
        index=True, track_visibility='always')
    
    @api.one
    def create_issue(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        vals = {'name': self.name,
                'project_id':self.project_id.id or False,
                'user_id': self.user_id.id or False,
                'partner_id': crm_brw.partner_id.id or False,
                'lead_id':crm_brw.id or False
                }
        self.env['project.issue'].create(vals)
        
        
class project_issue(models.Model):
    _inherit='project.issue'
    
    lead_id =  fields.Many2one('crm.lead', 'Opportunity')