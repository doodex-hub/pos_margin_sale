# -*- coding: utf-8 -*-
# BACKFILL (doc-dev-backfill) — test baru ditambahkan retroaktif, tidak mengubah kode bisnis.
# Ref: doc-dev/backfill/spec/pos_margin_threshold/01B_ACCEPTANCE_CRITERIA.md
import logging

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'pos_margin_threshold')
class TestMarginSale(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'BACKFILL Test Category',
            'margin_sale': 20.0,
        })

    def test_margin_sale_from_category(self):
        """AC-01-01: margin_sale template baru = margin_sale kategori (compute)."""
        product = self.env['product.template'].create({
            'name': 'BACKFILL Product AC-01-01',
            'categ_id': self.category.id,
            'standard_price': 100.0,
        })
        self.assertEqual(product.margin_sale, 20.0)

    def test_margin_sale_manual_override_persists(self):
        """AC-01-02: override manual tidak balik ke nilai kategori tanpa trigger dependency."""
        product = self.env['product.template'].create({
            'name': 'BACKFILL Product AC-01-02',
            'categ_id': self.category.id,
            'standard_price': 100.0,
        })
        self.assertEqual(product.margin_sale, 20.0)
        product.margin_sale = 35.0
        product.flush_recordset()
        product.invalidate_recordset()
        self.assertEqual(product.margin_sale, 35.0, "override manual harus tetap 35, bukan balik ke 20")

    def test_minimum_sale_price_computation(self):
        """AC-01-03: minimum_sale_price = standard_price * (1 + margin/100)."""
        product = self.env['product.template'].create({
            'name': 'BACKFILL Product AC-01-03',
            'categ_id': self.category.id,
            'standard_price': 100.0,
        })
        self.assertEqual(product.minimum_sale_price, 120.0)

    def test_minimum_sale_price_inverse(self):
        """AC-01-04: set minimum_sale_price manual -> margin_sale ter-inverse."""
        product = self.env['product.template'].create({
            'name': 'BACKFILL Product AC-01-04',
            'categ_id': self.category.id,
            'standard_price': 100.0,
        })
        product.minimum_sale_price = 150.0
        self.assertAlmostEqual(product.margin_sale, 50.0)

    def test_minimum_sale_price_zero_standard_price_guard(self):
        """AC-01-05: standard_price=0, set minimum_sale_price manual -> margin_sale=0 (guard)."""
        product = self.env['product.template'].create({
            'name': 'BACKFILL Product AC-01-05',
            'categ_id': self.category.id,
            'standard_price': 0.0,
        })
        product.minimum_sale_price = 999.0
        self.assertEqual(product.margin_sale, 0.0)

    def test_margin_sale_inverse_writes_to_shared_template_not_per_variant(self):
        """F-01 (REVISI setelah eksekusi nyata, lihat FINDINGS.md): hipotesis awal F-01
        ("minimum_sale_price_with_tax tidak konsisten untuk variant dengan margin berbeda")
        TERNYATA TIDAK BISA TERJADI -- karena `margin_sale` inverse di ProductProduct menulis
        ke `product_tmpl_id.margin_sale` (TEMPLATE, shared), bukan ke variant itu sendiri. Ini
        otomatis membuat SEMUA variant satu template ikut berubah (karena mereka semua compute
        dari `product_tmpl_id.margin_sale` yang sama). Ditemukan TIDAK SENGAJA saat menulis test
        untuk hipotesis F-01 asli -- test awal (assert variant_a != variant_b) GAGAL karena
        kedua variant selalu berakhir dengan nilai yang SAMA (nilai TERAKHIR yang ditulis)."""
        attr = self.env['product.attribute'].create({'name': 'BACKFILL Size'})
        val_a = self.env['product.attribute.value'].create({'name': 'A', 'attribute_id': attr.id})
        val_b = self.env['product.attribute.value'].create({'name': 'B', 'attribute_id': attr.id})
        template = self.env['product.template'].create({
            'name': 'BACKFILL Multivariant F-01',
            'categ_id': self.category.id,
            'attribute_line_ids': [(0, 0, {
                'attribute_id': attr.id,
                'value_ids': [(6, 0, [val_a.id, val_b.id])],
            })],
        })
        variants = template.product_variant_ids
        self.assertEqual(len(variants), 2, "harus ada 2 variant dari 2 attribute value")
        variant_a, variant_b = variants[0], variants[1]

        variant_a.margin_sale = 20.0
        self.assertEqual(
            template.margin_sale, 20.0,
            "F-01: inverse margin_sale variant HARUS menulis ke template.margin_sale (shared)"
        )
        self.assertEqual(
            variant_b.margin_sale, 20.0,
            "F-01 TERKONFIRMASI: variant_b ikut berubah jadi 20 walau yang di-set cuma variant_a "
            "-- membuktikan margin_sale TIDAK BISA berbeda antar variant satu template"
        )

        variant_b.margin_sale = 50.0
        self.assertEqual(
            variant_a.margin_sale, 50.0,
            "F-01 TERKONFIRMASI (arah sebaliknya): variant_a ikut berubah jadi 50 walau yang "
            "di-set cuma variant_b -- 'last write wins' untuk SEMUA variant template ini"
        )
        _logger.info(
            "BACKFILL F-01 (revisi): variant_a.margin_sale=%s variant_b.margin_sale=%s "
            "template.margin_sale=%s -- konfirmasi ketiganya SELALU sama (tidak bisa divergen)",
            variant_a.margin_sale, variant_b.margin_sale, template.margin_sale,
        )

    def test_wizard_assign_margin_from_template_list(self):
        """AC-03-01."""
        product = self.env['product.template'].create({
            'name': 'BACKFILL Product AC-03-01',
            'categ_id': self.category.id,
            'standard_price': 100.0,
        })
        wizard = self.env['wizard.margin.product'].with_context(
            active_model='product.template'
        ).create({'product_template_ids': [(6, 0, [product.id])], 'margin': 15.0})
        self.assertTrue(wizard.is_product)
        wizard.action_assing_margin()
        self.assertEqual(product.margin_sale, 15.0)

    def test_blocking_transaction_order_field_has_no_view_in_this_module(self):
        """AC-04-01 / F-02: field ada di model, tapi tidak direferensikan di view settings
        modul ini sendiri."""
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'res.config.settings'),
            ('name', '=', 'blocking_transaction_order'),
        ], limit=1)
        self.assertTrue(field, "field blocking_transaction_order harus ada di registry")
        own_view = self.env.ref('pos_margin_threshold.res_config_settings_view_form_pos_margin_threshold')
        self.assertNotIn(
            'blocking_transaction_order', own_view.arch_db,
            "F-02: field ini TIDAK boleh muncul di view settings milik pos_margin_threshold sendiri"
        )
