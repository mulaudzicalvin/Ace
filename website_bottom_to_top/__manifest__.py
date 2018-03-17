# -*- coding: utf-8 -*-

###################################################################################
#
#    Odoo Websit Bottom to Top
#
#    Copyright (C) 2017 Aminia Technology
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name' : 'Odoo Websit Bottom to Top',
    'version': '10.0.1.1.1', 
    'summary': 'Module is useful for adding functionality to website up down',
    'sequence': 30,
    'category': 'Website',   
    'license': 'AGPL-3',    
    'author': "Aminia Technology",
    'depends': [
        'website'
    ],
    'data': [
          'views/website_bottom_to_top.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
