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
