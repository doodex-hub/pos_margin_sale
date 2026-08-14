# -*- coding: utf-8 -*-
# BACKFILL (doc-dev-backfill) — test baru ditambahkan retroaktif, tidak mengubah kode bisnis.
# Ref: doc-dev/backfill/spec/sale_margin_threshold/01B_ACCEPTANCE_CRITERIA.md
import logging

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'sale_margin_threshold')
class TestActionConfirm(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'BACKFILL Sale Test Category',
            'margin_sale': 20.0,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'BACKFILL Test Partner'})

    def _make_product(self, name, standard_price=100.0):
        return self.env['product.product'].create({
            'name': name,
            'categ_id': self.category.id,
            'standard_price': standard_price,
            'type': 'consu',
        })

    def _make_order(self, product, price_unit):
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': price_unit,
            })],
        })

    def test_action_confirm_blocking_below_minimum(self):
        """AC-01-01: blocking_transaction_order=True, harga di bawah minimum -> ValidationError."""
        self.env['ir.config_parameter'].sudo().set_param(
            'post_margin_sale.blocking_transaction_order', True)
        product = self._make_product('BACKFILL Product AC-01-01', standard_price=100.0)
        self.assertEqual(product.minimum_sale_price, 120.0)
        order = self._make_order(product, price_unit=50.0)
        with self.assertRaises(ValidationError):
            order.action_confirm()
        self.assertEqual(order.state, 'draft')

    def test_action_confirm_wizard_path_when_not_blocking(self):
        """AC-01-02: blocking_transaction_order=False -> wizard konfirmasi, order belum confirm."""
        self.env['ir.config_parameter'].sudo().set_param(
            'post_margin_sale.blocking_transaction_order', False)
        product = self._make_product('BACKFILL Product AC-01-02', standard_price=100.0)
        order = self._make_order(product, price_unit=50.0)
        result = order.action_confirm()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('res_model'), 'sale.confirmation.wizard')
        self.assertEqual(order.state, 'draft', "order belum boleh confirm sebelum wizard di-confirm")

        wizard = self.env['sale.confirmation.wizard'].browse(result['res_id'])
        wizard.with_context(active_model='sale.order', active_ids=order.ids).action_confirm()
        self.assertEqual(order.state, 'sale', "setelah wizard confirm, order harus benar-benar confirmed")

    def test_action_confirm_normal_no_price_issue(self):
        """AC-01-03: harga di atas minimum -> confirm langsung tanpa popup/wizard."""
        self.env['ir.config_parameter'].sudo().set_param(
            'post_margin_sale.blocking_transaction_order', False)
        product = self._make_product('BACKFILL Product AC-01-03', standard_price=100.0)
        order = self._make_order(product, price_unit=150.0)
        order.action_confirm()
        self.assertEqual(order.state, 'sale')

    def test_action_confirm_BATCH_MULTI_ORDER_F05(self):
        """F-05 (PRIORITAS TINGGI) / AC-02-01: action_confirm dipanggil pada recordset berisi
        LEBIH DARI SATU sale.order (batch confirm dari list view, didukung Odoo core secara
        native) -- membaca `self.is_rental_order_installed_true` tanpa loop `for order in self`
        pada baris PERTAMA action_confirm. Test ini mengeksekusi hipotesis F-05 secara langsung
        untuk membuktikan/merefute -- JANGAN diedit untuk "membuat lolos", hasil aslinya (Pass
        atau Fail) WAJIB dilaporkan apa adanya ke FINDINGS.md."""
        product = self._make_product('BACKFILL Product F-05 A', standard_price=100.0)
        order_1 = self._make_order(product, price_unit=150.0)
        order_2 = self._make_order(product, price_unit=150.0)
        batch = order_1 + order_2
        self.assertEqual(len(batch), 2)

        try:
            batch.action_confirm()
            raised = False
        except ValueError as exc:
            raised = True
            _logger.info("BACKFILL F-05: ValueError ter-raise seperti diduga: %s", exc)
        _logger.info("BACKFILL F-05: batch action_confirm() untuk 2 sale.order -> "
                     "ValueError ter-raise = %s (state order_1=%s order_2=%s)",
                     raised, order_1.state, order_2.state)
        self.assertTrue(
            raised,
            "F-05: diduga ValueError 'Expected singleton' ter-raise saat action_confirm "
            "dipanggil pada >1 sale.order sekaligus. Kalau assertion INI GAGAL (tidak ada "
            "exception), berarti hipotesis F-05 TERBUKTI SALAH -- update FINDINGS.md jadi "
            "REFUTED, JANGAN ubah test ini supaya 'lolos'."
        )
