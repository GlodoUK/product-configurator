from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMrpApplyonVariants(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_alu_leg = cls.env["product.product"].create(
            {
                "name": "Steel Leg, Aluminium",
                "type": "product",
            }
        )

        cls.product_steel_leg_black = cls.env["product.product"].create(
            {
                "name": "Steel Leg, Black",
                "type": "product",
            }
        )

        cls.product_steel_leg_white = cls.env["product.product"].create(
            {
                "name": "Steel Leg, White",
                "type": "product",
            }
        )

        cls.product_bolt = cls.env["product.product"].create(
            {
                "name": "Bolt",
                "type": "product",
            }
        )

        cls.product_top = cls.env["product.product"].create(
            {
                "name": "Table Top",
                "type": "product",
            }
        )

        cls.product_attr_colour = cls.env["product.attribute"].create(
            {
                "name": "Leg Colour",
                "value_ids": [
                    (0, 0, {"name": "White"}),
                    (0, 0, {"name": "Black"}),
                ],
            }
        )

        cls.product_attr_material = cls.env["product.attribute"].create(
            {
                "name": "Leg Type",
                "value_ids": [
                    (0, 0, {"name": "Steel"}),
                    (0, 0, {"name": "Aluminium"}),
                ],
            }
        )

        cls.tmpl_configurable = cls.env["product.template"].create(
            {
                "name": "Configurable Table",
                "config_ok": True,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.product_attr_colour.id,
                            "value_ids": [
                                (6, 0, cls.product_attr_colour.value_ids.ids)
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.product_attr_material.id,
                            "value_ids": [
                                (6, 0, cls.product_attr_material.value_ids.ids)
                            ],
                        },
                    ),
                ],
            }
        )

        cls.bom_configurable = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.tmpl_configurable.id,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_bolt.id,
                            "product_qty": 12.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_top.id,
                            "product_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_steel_leg_black.id,
                            "product_qty": 2.0,
                            "bom_product_template_attribute_value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env["product.template.attribute.value"]
                                        .search(
                                            [
                                                (
                                                    "product_tmpl_id",
                                                    "=",
                                                    cls.tmpl_configurable.id,
                                                ),
                                                (
                                                    "attribute_id",
                                                    "=",
                                                    cls.product_attr_colour.id,
                                                ),
                                                ("name", "=", "Black"),
                                            ]
                                        )
                                        .id,
                                        cls.env["product.template.attribute.value"]
                                        .search(
                                            [
                                                (
                                                    "product_tmpl_id",
                                                    "=",
                                                    cls.tmpl_configurable.id,
                                                ),
                                                (
                                                    "attribute_id",
                                                    "=",
                                                    cls.product_attr_material.id,
                                                ),
                                                ("name", "=", "Steel"),
                                            ]
                                        )
                                        .id,
                                    ],
                                )
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_steel_leg_white.id,
                            "product_qty": 2.0,
                            "bom_product_template_attribute_value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env["product.template.attribute.value"]
                                        .search(
                                            [
                                                (
                                                    "product_tmpl_id",
                                                    "=",
                                                    cls.tmpl_configurable.id,
                                                ),
                                                (
                                                    "attribute_id",
                                                    "=",
                                                    cls.product_attr_colour.id,
                                                ),
                                                ("name", "=", "White"),
                                            ]
                                        )
                                        .id,
                                        cls.env["product.template.attribute.value"]
                                        .search(
                                            [
                                                (
                                                    "product_tmpl_id",
                                                    "=",
                                                    cls.tmpl_configurable.id,
                                                ),
                                                (
                                                    "attribute_id",
                                                    "=",
                                                    cls.product_attr_material.id,
                                                ),
                                                ("name", "=", "Steel"),
                                            ]
                                        )
                                        .id,
                                    ],
                                )
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_alu_leg.id,
                            "product_qty": 2.0,
                            "bom_product_template_attribute_value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env["product.template.attribute.value"]
                                        .search(
                                            [
                                                (
                                                    "product_tmpl_id",
                                                    "=",
                                                    cls.tmpl_configurable.id,
                                                ),
                                                (
                                                    "attribute_id",
                                                    "=",
                                                    cls.product_attr_material.id,
                                                ),
                                                ("name", "=", "Aluminium"),
                                            ]
                                        )
                                        .id,
                                    ],
                                )
                            ],
                        },
                    ),
                ],
            }
        )

    def test_mrp_config_ok(self):
        self.assertTrue(self.bom_configurable.config_ok)

    def test_mrp_config_white_steel(self):
        config = self.env["product.config.session"].create(
            {
                "product_tmpl_id": self.tmpl_configurable.id,
                "user_id": self.env.user.id,
            }
        )

        value_ids = self.env["product.attribute.value"].search(
            [("attribute_id", "=", self.product_attr_colour.id), ("name", "=", "White")]
        )

        value_ids |= self.env["product.attribute.value"].search(
            [
                ("attribute_id", "=", self.product_attr_material.id),
                ("name", "=", "Steel"),
            ]
        )

        product_id = config.create_get_variant(
            value_ids=value_ids.ids,
        )

        bom_id = product_id.bom_ids.filtered(lambda b: b.product_id == product_id)

        self.assertEqual(len(bom_id.bom_line_ids), 3)

        for line_id in bom_id.bom_line_ids:
            self.assertTrue(
                line_id.product_id
                in (self.product_steel_leg_white | self.product_top | self.product_bolt)
            )

            if line_id.product_id == self.product_steel_leg_white:
                self.assertTrue(line_id.product_qty == 2.0)

            elif line_id.product_id == self.product_top:
                self.assertTrue(line_id.product_qty == 1.0)

            elif line_id.product_id == self.product_bolt:
                self.assertTrue(line_id.product_qty == 12.0)

            else:
                self.assertTrue(False, "Unknown product!")
