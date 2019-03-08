{
    'name': 'Product Configurator',
    'version': '11.0.1.0.15',
    'category': 'Generic Modules/Base',
    'summary': 'Base for product configuration interface modules',
    'author': 'Pledra',
    'license': 'AGPL-3',
    'website': 'http://www.pledra.com/',
    'depends': ['account', 'stock'],
    "data": [
        'data/menu_configurable_product.xml',
        'data/product_attribute.xml',
        'data/ir_sequence_data.xml',
        'security/configurator_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_view.xml',
        'views/product_attribute_view.xml',
        'views/product_config_view.xml',
        'wizard/product_configurator_view.xml',
    ],
    'demo': [
        'demo/product_template.xml',
        'demo/product_attribute.xml',
        'demo/product_config_domain.xml',
        'demo/product_config_lines.xml',
        'demo/product_config_step.xml',
        'demo/config_image_ids.xml',
    ],
    'images': [
        'static/description/cover.png'
    ],
    'qweb': ['static/xml/create_button.xml'],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
