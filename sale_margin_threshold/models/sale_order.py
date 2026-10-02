from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



class SaleOrder(models.Model):
    _inherit = 'sale.order'


    is_rental_order_installed_true = fields.Boolean(default=False, compute='_compute_is_rental_order_installed', store=False)

    def _compute_is_rental_order_installed(self):
        # MF-26 (fixed 20.0 only, per dev decision -- kept as-is in 19.0 and earlier):
        # `self.is_rental_order` inside this loop read the WHOLE recordset instead of the
        # current `record`, so it raised "Expected singleton" whenever called on more than
        # one order at once (e.g. any batch action touching sale.order). Changed to `record`.
        for record in self:
            if hasattr(record, 'is_rental_order') and record.is_rental_order:
                record.is_rental_order_installed_true = True
            else:
                record.is_rental_order_installed_true = False

    def action_confirm(self):
        # `self` can hold several orders (list view > Action > Confirm), so the computed flag
        # is read per record. Rental orders skip the price check; it runs once over the rest.
        orders_to_check = self.filtered(lambda order: not order.is_rental_order_installed_true)
        if not orders_to_check:
            return super(SaleOrder, self).action_confirm()

        skip_check_price = self.env.context.get('skip_check_price')
        check_product = orders_to_check.check_product_price()
        # MF-40: ir.config_parameter.get_param()/set_param() removed entirely in native 20.0,
        # replaced by typed get_bool()/get_str()/etc (this field is Boolean,
        # config_parameter=...). Confirmed install-succeeds-but-crashes-at-runtime.
        blocking_warning = self.env['ir.config_parameter'].sudo().get_bool('post_margin_sale.blocking_transaction_order')
        if len(check_product) > 0 and not skip_check_price:
            product_str = ('\n').join(f" {i + 1}. {product.display_name} minimum price is {product.currency_id.symbol}. {product.minimum_sale_price:.2f}" for i,product in enumerate(check_product))
            product_str_fr = ('\n').join(f" {i + 1}. {product.display_name} le prix minimum est {product.currency_id.symbol}. {product.minimum_sale_price:.2f}" for i,product in enumerate(check_product))
            message = (_(f"Price of this product is less than minimum sale price \n\n{product_str}"))
            message_Fr = f"Le prix de ce produit est inférieur au prix de vente minimum \n\n{product_str_fr}"
            user_language = self.detect_user_language()
            if blocking_warning:
                    if user_language == 'French':
                        raise ValidationError(_(f"{message_Fr} \n\nTransaction bloquée car prix inférieur au prix minimum de vente."))
                    else:
                        raise ValidationError(_(f"{message} \n\nTransaction blocked due to price being lower than the minimum sale price."))
            else:
                message += "\n\nDo you want to continue with the quotation for making sale order?"
                message_Fr += "\n\nVoulez-vous continuer avec le devis pour passer commande ?"
                wizard_message = message_Fr if user_language == 'French' else message
                wizard = self.env['sale.confirmation.wizard'].create({'message': wizard_message})
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Confirm minimum sale price'),
                    'view_mode': 'form',
                    'res_model': 'sale.confirmation.wizard',
                    'target': 'new',
                    'res_id': wizard.id,
                }
        return super(SaleOrder, self).action_confirm()

    def detect_user_language(self):
        # Get the user's language from the context
        user_lang = self.env.context.get('lang', 'en_US')  # Default to English if not set

        # Check if the user language is French
        if user_lang.startswith('fr'):
            return 'French'
        else:
            return 'Other'

    def check_product_price(self):
        products = []
        for line in self.order_line:
            if line.price_unit < line.minimum_sale_price:
                products.append(line.product_id)
        return products

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    minimum_sale_price = fields.Float(string="Minimum sale price", related='product_id.minimum_sale_price')