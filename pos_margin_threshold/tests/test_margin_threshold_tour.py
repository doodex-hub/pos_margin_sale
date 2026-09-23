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
        # MF-40: set_param() removed in native 20.0, replaced by typed set_bool()/set_str()/etc.
        cls.env['ir.config_parameter'].sudo().set_bool(
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
        # MF-43/MF-44 re-investigation: force stored compute fields (margin_sale ->
        # minimum_sale_price -> minimum_sale_price_with_tax) to flush to the DB row now,
        # instead of staying pending in this transaction's cache. HttpCase's browser makes
        # requests from a SEPARATE thread/cursor that only sees committed DB state -- if these
        # computes haven't been flushed by the time the browser's first read of this product
        # happens, it can read the field's un-computed default (0.0) instead of the correct
        # value, even though every same-transaction/in-process check (session.load_data()
        # called directly, this test's own ORM reads) always sees the correct in-memory value.
        cls.env.flush_all()
        cls.main_pos_config.write({
            'payment_method_ids': [(4, cls.bank_payment_method.id)],
            # MF-42 (native bug, NOT our module): 20.0's numpad Price button reads
            # `!(config.restrict_price_control or cashier.role != "manager")` for its disabled
            # state (access_right_plugin.js, get disablePriceButton). Despite the field's own
            # help text ("Only users with Manager access rights... can modify prices"), the
            # actual boolean logic is inverted: with restrict_price_control=False (the default)
            # a manager-role cashier gets the Price button DISABLED, not enabled. Confirmed by
            # diffing against 19.0 (product_screen.js), which used a completely different,
            # non-inverted condition (cashierHasPriceControlRights()/role check). This is a
            # native logic bug unrelated to any of this project's modules -- never patch native
            # files for this, work around it here so pos_admin (manager role) can use the
            # numpad Price step our tour depends on (ProductScreen.addOrderline()).
            'restrict_price_control': True,
        })

    def test_pos_margin_threshold_below_minimum_confirm_tour(self):
        self.main_pos_config.open_ui()
        self.start_pos_tour("pos_margin_threshold_below_minimum_confirm_tour", login="pos_admin")

    def test_pos_margin_threshold_below_minimum_blocked_tour(self):
        # Step 9 addendum: closes the AC-02-01 gap flagged in Step 8 Code Review -- the confirm
        # path (above) had Tour coverage, the blocking path did not.
        self.env['ir.config_parameter'].sudo().set_bool(
            'post_margin_sale.blocking_transaction_pos', True
        )
        self.main_pos_config.open_ui()
        self.start_pos_tour("pos_margin_threshold_below_minimum_blocked_tour", login="pos_admin")
