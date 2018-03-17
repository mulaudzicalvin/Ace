# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR - Contractor',
    'category': 'HR',
    'summary': 'Add a limited access group to projects and timesheets.',
    'website': 'https://www.niboo.be/',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'description': '''
Add a group that has no access to customer, projects and analytic accounts.
Access will be given only with "Followers".
        ''',
    'author': 'Niboo',
    'depends': [
        'project',
        'hr',
    ],
    'data': [
        'security/ir_rule.xml',
    ],
    'images': [
        'static/description/hr_contractor_cover.png',
    ],
    'installable': True,
    'application': False,
}
