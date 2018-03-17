# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project - Light Workflow',
    'category': 'Project',
    'summary': 'Add a workflow to project tasks',
    'website': 'https://www.niboo.be/',
    'version': '10.0.1.0.0',
    'description': '''
Define a workflow enabling you to better manage the state of your tasks.
Create workflows personalized to the different types of tasks you have.
Advance your task in its different steps and states seamlessly and coherently.
    ''',
    'license': 'AGPL-3',
    'author': 'Niboo',
    'depends': [
        'project',
    ],
    'data': [
        'views/project.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/project_workflow.png',
    ],
    'installable': True,
    'application': False,
}
