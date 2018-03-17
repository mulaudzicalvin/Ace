# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Issue Sequence',
    'version': '10.0.0.1',
    'author': 'BrowseInfo',
    'category':'Project',
    'website': 'www.browseinfo.in',
    'summary': 'This module allow to create automatic sequence of project issue',
    'description':""" This module allow to create automatic sequence of project issue.""", 
    'depends':['project','rating_project_issue'],
    'data':[
        'data/ir_sequence_data.xml',
        'views/project_issue.xml',
        ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
