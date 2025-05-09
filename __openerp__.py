{
    'name': 'Logo.dev',
    'version': '1.0',
    'category': 'Administration',
    'author': 'App4indus',
    'license': 'LGPL',
    'summary': 'Récupération des logos d\'entreprises depuis logo.dev',
    'website': 'https://app4indus.com',
    'module_type': 'base',
    'complexity': 'easy',
    'description': "Récupération des logos d'entreprises depuis logo.dev",
    'depends': ['base'],
    'data': [
        'views/config.xml',
        'views/menu.xml',
        'crons/cron_get_logo.xml'
             ],
    'installable': True
}
