import logging
from io import StringIO

from mako.runtime import Context
from mako.template import Template

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_conversions_dict(self):
        conversions = {"float": float, "integer": int}
        return conversions

    @api.constrains("product_template_attribute_value_ids")
    def _check_duplicate_product(self):
        """Check for prducts with same attribute values/custom values"""
        config_session_obj = self.env["product.config.session"]
        for product in self.filtered(lambda p: p.config_ok):
            ptav_ids = product.product_template_attribute_value_ids.mapped(
                "product_attribute_value_id"
            )
            duplicates = config_session_obj.search_variant(
                product_tmpl_id=product.product_tmpl_id,
                value_ids=ptav_ids.ids,
            ).filtered(lambda p: p.id != product.id)
            if duplicates:
                raise ValidationError(
                    _(
                        "Configurable Products cannot have duplicates "
                        "(identical attribute values)"
                    )
                )

    def _get_mako_context(self, buf):
        """Return context needed for computing product name based
        on mako-tamplate define on it's product template"""
        self.ensure_one()
        ptav_ids = self.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        )
        return Context(
            buf,
            product=self,
            attribute_values=ptav_ids,
            steps=self.product_tmpl_id.config_step_line_ids,
            template=self.product_tmpl_id,
        )

    def _get_mako_tmpl_name(self):
        """Compute and return product name based on mako-tamplate
        define on it's product template"""
        self.ensure_one()
        if self.mako_tmpl_name:
            mytemplate = Template(self.mako_tmpl_name or "")
            buf = StringIO()
            ctx = self._get_mako_context(buf)
            mytemplate.render_context(ctx)
            return buf.getvalue()
        return self.display_name

    def _get_mako_tmpl_default_code(self):
        """
        Compute and return product default_code based on mako-tamplate
        define on it's product template
        """
        self.ensure_one()
        if self.mako_tmpl_default_code:
            mytemplate = Template(self.mako_tmpl_default_code or "")
            buf = StringIO()
            ctx = self._get_mako_context(buf)
            mytemplate.render_context(ctx)
            return buf.getvalue()
        return self.config_ref

    @api.depends("product_template_attribute_value_ids.weight_extra")
    def _compute_product_weight_extra(self):
        for product in self:
            product.weight_extra = sum(
                product.mapped("product_template_attribute_value_ids.weight_extra")
            )

    @api.depends("weight_dummy", "weight_extra", "product_tmpl_id.weight")
    def _compute_product_weight(self):
        for product in self:
            if product.config_ok:
                tmpl_weight = product.product_tmpl_id.weight
                product.weight = tmpl_weight + product.weight_extra
            else:
                product.weight = product.weight_dummy

    def _inverse_product_weight(self):
        """Store weight in dummy field"""
        self.weight_dummy = self.weight

    weight_extra = fields.Float(compute="_compute_product_weight_extra", store=True)
    weight_dummy = fields.Float(string="Manual Weight", digits="Stock Weight")
    weight = fields.Float(
        compute="_compute_product_weight",
        inverse="_inverse_product_weight",
        store=True,
    )

    # product preset
    config_preset_ok = fields.Boolean(string="Is Preset")

    def reconfigure_product(self):
        """launches a product configurator wizard with a linked
        template and variant in order to re-configure an existing product.
        It is essentially a shortcut to pre-fill configuration
        data of a variant"""
        self.ensure_one()

        extra_vals = {"product_id": self.id}
        return self.product_tmpl_id.create_config_wizard(extra_vals=extra_vals)

    @api.model
    def check_config_user_access(self, mode):
        """Check user have access to perform action(create/write/delete)
        on configurable products"""
        if not self.env["product.template"]._check_config_group_rights():
            return True
        config_manager = self.env.user.has_group(
            "product_configurator.group_product_configurator_manager"
        )
        config_user = self.env.user.has_group(
            "product_configurator.group_product_configurator"
        )
        user_root = self.env.ref("base.user_root")
        user_admin = self.env.ref("base.user_admin")
        if (
            config_manager
            or (config_user and mode not in ["delete"])
            or self.env.user.id in [user_root.id, user_admin.id]
        ):
            return True
        raise ValidationError(
            _(
                "Sorry, you are not allowed to create/change this kind of "
                "document. For more information please contact your manager."
            )
        )

    def unlink(self):
        """
        Check access rights of user(configurable products)
        Signal unlink from product variant through context so
        removal can be stopped for configurable templates
        """
        configurable_products = self.filtered(lambda p: p.config_ok)
        if configurable_products:
            self.env["product.product"].check_config_user_access(mode="delete")
        return super(
            ProductProduct, self.with_context(unlink_from_variant=True)
        ).unlink()

    @api.model
    def create(self, vals):
        """Patch for check access rights of user(configurable products)"""
        config_ok = vals.get("config_ok", False)
        if config_ok:
            self.check_config_user_access(mode="create")
        return super(ProductProduct, self).create(vals)

    def write(self, vals):
        """Patch for check access rights of user(configurable products)"""
        change_config_ok = "config_ok" in vals
        configurable_products = self.filtered(lambda product: product.config_ok)
        if change_config_ok or configurable_products:
            self[:1].check_config_user_access(mode="write")

        return super(ProductProduct, self).write(vals)

    # pylint:disable=missing-return
    def _compute_product_price_extra(self):
        standard_products = self.filtered(lambda product: not product.config_ok)
        config_products = self - standard_products
        if standard_products:
            super(ProductProduct, standard_products)._compute_product_price_extra()
        for product in config_products:
            attribute_value_obj = self.env["product.attribute.value"]
            value_ids = (
                product.product_template_attribute_value_ids.product_attribute_value_id
            )
            extra_prices = attribute_value_obj.get_attribute_value_extra_prices(
                product_tmpl_id=product.product_tmpl_id.id, pt_attr_value_ids=value_ids
            )
            product.price_extra = sum(extra_prices.values())
