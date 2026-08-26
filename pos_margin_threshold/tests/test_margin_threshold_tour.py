# -*- coding: utf-8 -*-
# Step 6/9 Mode D — Tour test headless (real Chrome). Companion of
# static/tests/tours/margin_threshold_tour.js. Verifies the migrated PosStore.pay()
# blocking/confirm dialog end-to-end (AC-02-02, 05a_MIGRATION_ACCEPTANCE_CRITERIA.md).
from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestMarginThresholdTour(TestPointOfSaleHttpCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `--load-language=fr_FR` (dipasang di docker-compose.yml untuk MF-21) membuat UI
        # ter-render Prancis kalau tidak dipaksa eksplisit -- tour ini mencocokkan teks Inggris.
        cls.pos_admin.write({'lang': 'en_US'})
        cls.env['ir.config_parameter'].sudo().set_param(
            'post_margin_sale.blocking_transaction_pos', False
        )
        cls.margin_test_product = cls.env['product.template'].create({
            'name': 'Margin Threshold Test Product',
            'type': 'consu',
            'available_in_pos': True,
            'standard_price': 10.0,
            'margin_sale': 50.0,  # minimum_sale_price = 10 * 1.5 = 15
            'taxes_id': [],
        })
        cls.main_pos_config.write({
            'payment_method_ids': [(4, cls.bank_payment_method.id)],
        })

    def test_pos_margin_threshold_below_minimum_confirm_tour(self):
        self.main_pos_config.open_ui()
        self.start_pos_tour("pos_margin_threshold_below_minimum_confirm_tour", login="pos_admin")

    def test_pos_margin_threshold_below_minimum_blocked_tour(self):
        # Step 9 addendum: closes the AC-02-01 gap flagged in Step 8 Code Review -- the confirm
        # path (above) had Tour coverage, the blocking path did not.
        self.env['ir.config_parameter'].sudo().set_param(
            'post_margin_sale.blocking_transaction_pos', True
        )
        self.main_pos_config.open_ui()
        self.start_pos_tour("pos_margin_threshold_below_minimum_blocked_tour", login="pos_admin")
