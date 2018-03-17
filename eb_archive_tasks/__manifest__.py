# -*- coding: utf-8 -*-
#AUTHOR {"RISTE KABRANOV"}
{
    'name': "Archive Tasks",

    'summary': """
        Archive tasks using list view in odoo""",

    'description': """
        Archive tasks using list view in odoo
    """,

    'author': "odoo@simplify-erp.com",
    'website': "http://www.simplify-erp.com",
    'images': ['static/description/banner.jpg'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
