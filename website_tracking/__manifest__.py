# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#    Copyright (C) Monoyer Fabian (info@olabs.be)                            #
#                                                                            #
# Part of Odoo. See LICENSE file for full copyright and licensing details.   #
##############################################################################
{
    'name': "Website Sale Tracker",
    'author': "O'Labs",
    'website': "http://www.olabs.be",
    'description': """


    """,
    'category': 'website',
    'version': '1.1',
    'depends': ['website','website_sale'],
   'data': [
         'security/ir.model.access.csv',
         'views/backend.xml'
       ],
    'images':['static/description/banner.jpg'],
    'installable': True,
    'licence':"LGPL",
}

