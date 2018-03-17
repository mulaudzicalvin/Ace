# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    'name': 'Update Sale Order with Time & Material',
    'category': 'Generic Modules/Others',
    'summary': 'Improve the sales workflow around Time & Material projects',
    'website': 'https://www.niboo.be/',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'description': """.
- Update the sale order when confirming it with the lines from Time & Material projects
- Force selection of project on sale order for time and material products
- Improves the sale order view by adding buttons to see linked and unlinked
timesheets logs
        """,
    'author': 'Niboo',
    'depends': [
        'sale_timesheet',
    ],
    'data': [
        'views/sale_timesheet_view.xml',
    ],
    'images': [
        'static/description/cover.png',
    ],
    'installable': True,
    'application': False,
}
