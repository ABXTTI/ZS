# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 13 Advance Payment',
    'version': '13.0.4.0.0',
    'category': 'Invoicing Management',
    'summary': 'Advance Payment For Odoo 13',
    'sequence': '10',
    'author': 'The Adepts, Odoo PK',
    'license': 'LGPL-3',
    'company': 'The Adepts',
    'maintainer': 'The Adepts',
    'support': 'info@thadepts.net',
    'website': 'https://theadepts.net',
    'depends': ['base', 'account','base_accounting_kit'],
    'live_test_url': 'https://www.youtube.com/watch?v=Qu6R3yNKR60',
    'demo': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/automated_action_counter_party.xml',
        'data/counter_party_sequence.xml',
        'views/counter_party.xml',
        'views/cpp.xml',
        'views/account_move_line_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}