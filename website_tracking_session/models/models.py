from openerp import api, models, fields
from odoo.http import root


class tracker(models.Model):
    _inherit= "website.sale.tracker"

    session=fields.Char(string="session")

    @api.model
    def create(self,data):
        data.update({'session':root.session_store})
        return super(tracker,self).create(data)
