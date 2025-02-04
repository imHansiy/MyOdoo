# -*- coding: utf-8 -*-
{
    'name': 'Estate_account',
    'version': '17.0.1.0.0',
    'summary': """ Estate_account Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'estate','account'],
    'data': [
        
    ],'assets': {
              'web.assets_backend': [
                  'estate_account/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
