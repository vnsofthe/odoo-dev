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
    ],
    'data': [
    ],
    'js': [
        'static/lib/canvg/rgbcolor.js',
        'static/lib/canvg/StackBlur.js',
        'static/lib/canvg/canvg.js',
        'static/lib/d3.min.js',
        'static/lib/d3_chart.js',
        'static/src/js/view_d3.js',
    ],
    'qweb': [
        'static/src/xml/view_d3.xml',
    ],
    'css': [
        'static/lib/d3_chart.css',
        'static/src/css/view_d3.css',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
