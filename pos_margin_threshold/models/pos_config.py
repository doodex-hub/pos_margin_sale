from odoo import _, api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_blocked_warning = fields.Boolean(string="Blocked warning", compute='_compute_blocked_warning')


    def _compute_blocked_warning(self):
        for record in self:
            # MF-40: ir.config_parameter.get_param()/set_param() removed entirely in native
            # 20.0, replaced by typed get_bool()/get_str()/etc (this field is Boolean,
            # config_parameter=...). Confirmed install-succeeds-but-crashes-at-runtime: no
            # prior step caught this because it only surfaces when this compute actually runs
            # (e.g. clicking Pay in POS), not at module install.
            block_warning = self.env['ir.config_parameter'].sudo().get_bool('post_margin_sale.blocking_transaction_pos')
            if block_warning:
                record.is_blocked_warning = True
            else:
                record.is_blocked_warning = False