# -*- coding: utf-8 -*-
{
    'name': "Numbering tasks and issues",
    'version': '1.0',
    'sequence': 2,
    'category': 'Project',
    'summary': 'Numbering tasks and issues',
    'description': """
        Numbering tasks and issues
    """,
    'depends': ['project', 'project_issue'],
    'author': "BusinessApps",
    'website': "http://business-apps.ru",
    "price": 0.00,
    "currency": "EUR",

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
