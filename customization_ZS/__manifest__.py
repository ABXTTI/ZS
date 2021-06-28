# -*- coding: utf-8 -*-
# Copyright 2016, 2020 The Adepts
# License LGPL-3.0 or later (https://www.theadepts.net).

{
    "name": "Customization for ZS V13",
    "summary": "Customization for ZS V13",
    "version": "13.0.0.3",
    "category": "",
    "website": "https://www.theadepts.net",
	"description": """
		Customization for ZS
    """,
	'images':[

	],
    "author": "The Adepts",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'base',
        'report_py3o',
        'stock',
        'sale_management',
        'purchase',
        'base_accounting_kit',
        'hr_attendance',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_picking_view_inherit.xml',
        'views/po_view_inherit.xml',
        'views/inherit_view_product.xml',
        'views/view_for_new_model.xml',
        'views/so_view.xml',
        'views/menu_sale_order_line.xml',
        'views/res_partner_form_inherit.xml',
        'views/account_move_form_inherit.xml',
        'reports/vendor_bill.xml',
        'reports/cash_invoice_voucher.xml',
        'reports/reports_call.xml',
        'wizard/attendance_report_py3o.xml',
        'wizard/attendance_report.xml',

    ],

    #'live_test_url': 'https://youtu.be/JX-ntw2ORl8'

}
