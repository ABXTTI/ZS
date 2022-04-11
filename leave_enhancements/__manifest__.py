{
    'name': 'leave_enhancements',
    'version': '13.0.0',
    'summary': """Enhancements in Leave Module.""",
    'author': 'Ehtesham Ansare',
    'category': 'Payroll',
    'depends': ['base','hr_holidays'],
    'data':[
        'security/ir.model.access.csv',
        'views/model.xml',
        'data/ir_cron_data.xml',
        'views/leave_allocation_view.xml',
    ],
    'installable' : True,
    'application' : False,
}