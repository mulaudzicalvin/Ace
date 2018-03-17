# -*- coding: utf-8 -*-
# © 2016 Michael Viriyananda
# © 2017 Stella Fredö, adapt it to v10
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Issue Code",
    "version": "10.0.2.0.0",
    'author': 'Michael Viriyananda, Stella Fredö',
    "category": "Project Management",
    'summary': 'Adding Field Code For Project Issue',
    'website': 'https://github.com/stellaf/project-issue-code',
    "license": "AGPL-3",
    "depends": [
        "project_issue",
    ],
    "data": [
        "data/project_issue_sequence.xml",
        "views/project_issue_view.xml",
    ],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'auto_install': False,
    "installable": True,
}

