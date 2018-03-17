# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project - Version Management',
    'category': 'Project',
    'summary': 'Manage the versions of your projects',
    'website': 'https://www.niboo.be/',
    'version': '10.0.1.0.0',
    'description': '''
Allows you to manage versions in your projects.
    ''',
    'author': 'Niboo',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'data/project_version_state.xml',

        'views/project.xml',
        'views/project_version_state.xml',

        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/versioning_cover.png',
    ],
    'installable': True,
    'application': False,
}
