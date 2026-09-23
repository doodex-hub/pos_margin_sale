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
        # BSL-018 (Step 10 addendum): a SECOND, distinct product used as the above-minimum
        # control line. Deliberately not the same product at a different price: POS merges
        # lines per product, and addOrderline() asserts the new line has quantity "1", so a
        # merge would fail the tour for the wrong reason instead of testing the decoration.
        # NOT PRESENT IN 18.0/19.0 -- added for the first time in this 20.0 project.
        cls.margin_control_product = cls.env['product.template'].create({
            'name': 'Margin Threshold Control Product',
            'type': 'consu',
            'available_in_pos': True,
            'standard_price': 10.0,
            'margin_sale': 50.0,  # same minimum as the product above; only the sale price differs
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

    # --- Step 10 addendum (2026-09-23): BSL-018, finally closed -------------------------------
    # BSL-018 (01b_BASELINE_SPEC.md) had been carried forward WITHOUT a decision through three
    # consecutive migration projects (17.0 -> 18.0, 18.0 -> 19.0, 19.0 -> 20.0). The dev decided
    # on 2026-09-23 to close it here rather than carry it a fourth time.
    #
    # NOT PRESENT IN ANY EARLIER VERSION: the two tests below and their tours are written for the
    # first time in this 20.0 project. Branches migration/18.0 and migration/19.0 do NOT have
    # them, so 18.0 and 19.0 remain without automated coverage for these two behaviours. Treat
    # them as new coverage added in 20.0, not as something regressed elsewhere.

    def test_pos_margin_threshold_no_dialog_above_minimum_tour(self):
        # AC-03-05: an order whose lines are ALL at or above the minimum must raise no dialog at
        # all when paying -- the AC explicitly includes "not even a brief flash", so the tour
        # watches the DOM with a MutationObserver instead of only checking the end state.
        # blocking_transaction_pos stays False (set in setUpClass) so that a regression would
        # surface as the confirm dialog, the branch a user is most likely to hit.
        self.main_pos_config.open_ui()
        self.start_pos_tour(
            "pos_margin_threshold_no_dialog_above_minimum_tour", login="pos_admin"
        )

    def test_pos_margin_threshold_orderline_warning_tour(self):
        # BSL-018's second half: assert the orderline warning's text AND colour on their own.
        # The existing dialog tours only ever showed that rendering an below-minimum line does
        # not crash; they never asserted what it actually says or that it is red. The tour also
        # adds an above-minimum control line, so a regression that flagged every line would fail.
        #
        # The tour deliberately asserts NO hard-coded amount. The exact figure depends on which
        # taxes the accounting test fixture puts on a freshly created product, and that turned
        # out to be neither stable nor easy to pin down from here: `'taxes_id': []` does not
        # clear the fixture's default 15% sale tax, and writing taxes_id afterwards left the
        # stored minimum_sale_price_with_tax inconsistent with its own inputs (stored 19.5 while
        # the fields it depends on give 17.25, with a single 15% tax attached). The module's
        # compute is sound in a plain ORM transaction -- clearing taxes recomputes 17.25 -> 15.00
        # correctly, verified directly -- so this is confined to this fixture path and is
        # recorded separately in FINDINGS.md rather than worked around silently here.
        #
        # What the tour asserts instead is the invariant that actually matters for BSL-018: the
        # warning row shows a real, positive, currency-formatted amount that is strictly greater
        # than the price the line is being sold at (5). That catches the regressions worth
        # catching -- wrong field rendered, 0.00, the unit price echoed back, formatting broken --
        # without coupling the test to fixture tax behaviour. Guard the precondition here.
        for product in (self.margin_test_product, self.margin_control_product):
            self.assertGreater(
                product.minimum_sale_price_with_tax, 5.0,
                "BSL-018 fixture precondition: %s must have a minimum sale price incl. tax above "
                "the 5.00 the tour sells the flagged line at, got %s" % (
                    product.name, product.minimum_sale_price_with_tax,
                ),
            )
            self.assertLess(
                product.minimum_sale_price_with_tax, 50.0,
                "BSL-018 fixture precondition: %s must have a minimum sale price incl. tax below "
                "the 50.00 the tour sells the control line at, got %s" % (
                    product.name, product.minimum_sale_price_with_tax,
                ),
            )
        self.main_pos_config.open_ui()
        self.start_pos_tour("pos_margin_threshold_orderline_warning_tour", login="pos_admin")
