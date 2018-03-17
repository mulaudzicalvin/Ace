# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#    Copyright (C) Monoyer Fabian (info@olabs.be)                            #
#                                                                            #
# Part of Odoo. See LICENSE file for full copyright and licensing details.   #
##############################################################################
{
    'name': "Website Sale Tracker Sessions",
    'author': "O'Labs",
    'website': "http://www.olabs.be",
    'description': """

        Add field sessions in tracker product for website sale

    """,
    'category': 'website',
    'version': '1.1',
    'depends': ['website_tracking'],
   'data': [
         'views/backend.xml'
       ],
    'images':['static/description/banner.jpg'],
    'installable': True,
}

