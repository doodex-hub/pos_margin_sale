# -*- coding: utf-8 -*-
{
    'name': "POS Margin Threshold",

    'summary': "Ensure products are sold above their minimum price with margin checks in POS orders.",

    'description': """
        The POS Margin Threshold module ensures that each product is sold at a price that covers its cost and desired profit margin. 
        If a product is sold below its minimum price in a POS order, 
        the system triggers a warning, helping businesses maintain profitability and prevent underpricing.
    """,

    'author': "Doodex",
    'website': "https://www.doodex.net",
    'license': "AGPL-3",
    'category': 'POSs',
    'version': '17.0.1.0',

    'depends': [
        'base', 
        'product', 
        'sale', 
        'point_of_sale',
        'stock_account'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/products.xml',
        'views/sale_order.xml',
        'wizard/wizard_margin_product.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'images': ["static/description/banner.png"],
} 