{
    'name': 'D3 Chart',
    'version': '0.0.1',
    'sequence': 150,
    'category': 'Anybox',
    'description': """
        Use Koloria icon: http://www.graphicrating.com/2012/06/14/koloria-free-icons-set
    """,
    'author': 'Anybox',
    'website': 'http://anybox.fr',
    'depends': [
        'base',
        'web',
        'web_graph',
        'purchase'
    ],
    'data': ["view/web_d3_chart.xml"],

    'qweb': [
        'static/src/xml/view_d3.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
