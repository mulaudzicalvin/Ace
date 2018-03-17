# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Timesheet - Work Logger',
    'category': 'HR',
    'summary': 'Makes logging time easy and efficient',
    'license': 'AGPL-3',
    'website': 'https://www.niboo.be',
    'version': '10.0.1.0.0',
    'description': '''
Add a wizard to simply log your work:
- Direct access from tasks form and kanban view: click on the Log Work button
- Choose a task, and the corresponding project is automatically set
        ''',
    'author': 'Niboo',
    'depends': [
        'timesheet_grid',
        'project',
    ],
    'data': [
        'views/timesheet_views.xml',
        'views/project_task.xml',
        'wizards/work_log_wizard.xml',
    ],
    'images': [
        'static/description/hr_timesheet_work_log_wizard_cover.png',
    ],
    'installable': True,
    'application': False,
}
