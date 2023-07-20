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
    default_val = fields.Many2one(
        comodel_name="product.attribute.value", string="Default Value"
    )

    sequence = fields.Integer(default=10)

    @api.onchange("value_ids", "attribute_id")
    def onchange_values(self):
        if self.default_val and self.default_val not in self.value_ids:
            self.default_val = None

    @api.constrains("value_ids", "default_val")
    def _check_default_values(self):
        """default value should not be outside of the
        values selected in attribute line"""
        for line in self.filtered(lambda l: l.default_val):
            if line.default_val not in line.value_ids:
                raise ValidationError(
                    _(
                        "Default values for each attribute line must exist in "
                        "the attribute values (%(attribute_name)s: %(default_name)s)"
                    )
                    % {
                        "attribute_name": line.attribute_id.name,
                        "default_name": line.default_val.name,
                    }
                )


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

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Use name_search as a domain restriction for the frontend to show
        only values set on the product template taking all the configuration
        restrictions into account.

        TODO: This only works when activating the selection not when typing
        """
        product_tmpl_id = self.env.context.get("_cfg_product_tmpl_id")
        if product_tmpl_id:
            # TODO: Avoiding browse here could be a good performance enhancer
            product_tmpl = self.env["product.template"].browse(product_tmpl_id)
            tmpl_vals = product_tmpl.attribute_line_ids.mapped("value_ids")
            attr_restrict_ids = []
            preset_val_ids = []
            new_args = []
            for arg in args:
                # Restrict values only to value_ids set on product_template
                if arg[0] == "id" and arg[1] == "not in":
                    preset_val_ids = arg[2]
                    # TODO: Check if all values are available for configuration
                else:
                    new_args.append(arg)
            val_ids = set(tmpl_vals.ids)
            if preset_val_ids:
                val_ids -= set(arg[2])
            val_ids = self.env["product.config.session"].values_available(
                val_ids, preset_val_ids, product_tmpl_id=product_tmpl_id
            )
            new_args.append(("id", "in", val_ids))
            mono_tmpl_lines = product_tmpl.attribute_line_ids.filtered(
                lambda l: not l.multi
            )
            for line in mono_tmpl_lines:
                line_val_ids = set(line.mapped("value_ids").ids)
                if line_val_ids & set(preset_val_ids):
                    attr_restrict_ids.append(line.attribute_id.id)
            if attr_restrict_ids:
                new_args.append(("attribute_id", "not in", attr_restrict_ids))
            args = new_args
        res = super(ProductAttributeValue, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        return res

    # TODO: Prevent unlinking custom options by overriding unlink


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
