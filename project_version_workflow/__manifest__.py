# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project - Version and Workflow link',
    'category': 'Project',
    'summary': 'Allows to change task step on version state change',
    'website': 'https://www.niboo.be/',
    'version': '10.0.1.0.0',
    'description': '''
This module makes the link between the Project - Light Workflow module and the Project - Version Management module.
It automatically changes the step of your tasks when you put a version in production.
    ''',
    'author': 'Niboo',
    'license': 'AGPL-3',
    'depends': [
        'project_version',
        'project_workflow',
    ],
    'data': [
        'views/version_state_step_link.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/workflow_versioning_cover.png',
    ],
    'installable': True,
    'application': False,
}
