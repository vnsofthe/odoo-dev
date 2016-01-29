{
    'name': 'Add button and menu in action',
    'category': 'Hidden',
    'description': ''' ''',
    'version': '0.1',
    'depends': [
        'web',
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'base.xml',
    ],
    'js': [
        'static/src/js/*.js',
    ],
    'css': [
        'static/src/css/*.css',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': True,
    'web_preload': True,
}
