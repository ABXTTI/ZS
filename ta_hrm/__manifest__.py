# -*- coding: utf-8 -*-
# Copyright 2016, 2020 The Adepts
# License LGPL-3.0 or later (https://www.theadepts.net).

{
    "name": "TA HRM",
    "summary": "TA HRM",
    "version": "13.0.0.3",
    "category": "",
    "website": "https://www.theadepts.net",
	"description": """
		TA HRM
    """,
	'images':[

	],
    "author": "The Adepts",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'report_xlsx',
        'hr',
        'hr_attendance',
        'hr_payroll_community',
    ],
    "data": [
        "views/employee_contract.xml",
        "views/employee.xml",
        "views/attendance.xml",
        "views/resource_calendar_form_inherit.xml",
        "data/process_leaves_cron.xml",
        "views/resource_calendar_leaves.xml",
        "views/inherit_hr_payslip.xml",
        "report/payroll_report_wizard.xml",
        "report/payroll_report_xlsx_call.xml",
        "security/ir.model.access.csv",
    ],

}
