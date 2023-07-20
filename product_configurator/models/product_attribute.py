from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    _order = "sequence"

    active = fields.Boolean(
        default=True,
    )
    description = fields.Text(translate=True)
    required = fields.Boolean(
        default=True,
    )
    multi = fields.Boolean(help="Allow selection of multiple values")

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)


class ProductAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"
    _order = "product_tmpl_id, sequence, id"

    required = fields.Boolean(related="attribute_id.required", store=True)
    multi = fields.Boolean(related="attribute_id.multi", store=True)
    sequence = fields.Integer(default=10)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    active = fields.Boolean(
        default=True,
        help="By unchecking the active field you can "
        "disable a attribute value without deleting it",
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Related Product"
    )
    is_custom_type = fields.Selection(
        [
            ("integer", "Integer"),
            ("float", "Float"),
            ("char", "Text"),
        ],
        string="Custom value type",
    )

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)

    @api.model
    def get_attribute_value_extra_prices(
        self, product_tmpl_id, pt_attr_value_ids, pricelist=None
    ):
        extra_prices = {}
        if not pricelist:
            pricelist = self.env.user.partner_id.property_product_pricelist

        related_product_av_ids = self.env["product.attribute.value"].search(
            [("id", "in", pt_attr_value_ids.ids), ("product_id", "!=", False)]
        )
        extra_prices = {
            av.id: av.product_id.with_context(pricelist=pricelist.id).price
            for av in related_product_av_ids
        }
        remaining_av_ids = pt_attr_value_ids - related_product_av_ids
        pe_lines = self.env["product.template.attribute.value"].search(
            [
                ("product_attribute_value_id", "in", remaining_av_ids.ids),
                ("product_tmpl_id", "=", product_tmpl_id),
            ]
        )
        for line in pe_lines:
            attr_val_id = line.product_attribute_value_id
            if attr_val_id.id not in extra_prices:
                extra_prices[attr_val_id.id] = 0
            extra_prices[attr_val_id.id] += line.price_extra
        return extra_prices

    def name_get(self):
        res = super(ProductAttributeValue, self).name_get()
        if not self._context.get("show_price_extra"):
            return res
        product_template_id = self.env.context.get("active_id", False)

        price_precision = self.env["decimal.precision"].precision_get("Product Price")
        extra_prices = self.get_attribute_value_extra_prices(
            product_tmpl_id=product_template_id, pt_attr_value_ids=self
        )

        res_prices = []
        for val in res:
            price_extra = extra_prices.get(val[0])
            if price_extra:
                val = (
                    val[0],
                    "%s ( +%s )"
                    % (
                        val[1],
                        ("{0:,.%sf}" % (price_precision)).format(price_extra),
                    ),
                )
            res_prices.append(val)
        return res_prices


class ProductAttributePrice(models.Model):
    _inherit = "product.template.attribute.value"
    # Leverage product.template.attribute.value to compute the extra weight
    # each attribute adds

    weight_extra = fields.Float(string="Attribute Weight Extra", digits="Stock Weight")


class ProductAttributeValueLine(models.Model):
    _name = "product.attribute.value.line"
    _description = "Product Attribute Value Line"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        ondelete="cascade",
        required=True,
    )
    value_id = fields.Many2one(
        comodel_name="product.attribute.value",
        required="True",
        string="Attribute Value",
    )
    attribute_id = fields.Many2one(
        comodel_name="product.attribute", related="value_id.attribute_id"
    )
    value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="product_attribute_value_product_attribute_value_line_rel",
        column1="product_attribute_value_line_id",
        column2="product_attribute_value_id",
        string="Values Configuration",
    )
    product_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="product_attr_values_attr_values_rel",
        column1="product_val_id",
        column2="attr_val_id",
        compute="_compute_get_value_id",
        store=True,
    )

    @api.depends(
        "product_tmpl_id",
        "product_tmpl_id.attribute_line_ids",
        "product_tmpl_id.attribute_line_ids.value_ids",
    )
    def _compute_get_value_id(self):
        for attr_val_line in self:
            template = attr_val_line.product_tmpl_id
            value_list = template.attribute_line_ids.mapped("value_ids")
            attr_val_line.product_value_ids = [(6, 0, value_list.ids)]

    @api.constrains("value_ids")
    def _validate_configuration(self):
        """Ensure that the passed configuration in value_ids is a valid"""
        cfg_session_obj = self.env["product.config.session"]
        for attr_val_line in self:
            value_ids = attr_val_line.value_ids.ids
            value_ids.append(attr_val_line.value_id.id)
            valid = cfg_session_obj.validate_configuration(
                value_ids=value_ids,
                product_tmpl_id=attr_val_line.product_tmpl_id.id,
                final=False,
            )
            if not valid:
                raise ValidationError(
                    _(
                        "Values provided to the attribute value line are "
                        "incompatible with the current rules"
                    )
                )
