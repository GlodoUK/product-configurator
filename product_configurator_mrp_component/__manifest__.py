# Copyright (C) 2022-Today Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Configurator Manufacturing Components",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "summary": "BOM Support for configurable products",
    "author": "Pledra, Odoo Community Association (OCA), Glo Networks",
    "license": "AGPL-3",
    "website": "https://github.com/GlodoUK/product-configurator",
    "depends": ["product_configurator_mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom.xml",
    ],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
}
