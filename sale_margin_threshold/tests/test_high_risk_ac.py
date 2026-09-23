# -*- coding: utf-8 -*-
# Step 9 (Dev Testing) gate closure -- added 2026-09-23 per escalation in
# doc-dev/migration_19.0_20.0/doc/09_devtest/sale_margin_threshold/09_DEV_TESTING.md.
# Covers the 5 HIGH-RISK acceptance criteria that were flagged as having no automated test:
# AC-01-05, AC-02-08, AC-04-01, AC-04-02, AC-04-03 (see
# doc-dev/migration_19.0_20.0/doc/05_acceptance/sale_margin_threshold/05a_MIGRATION_ACCEPTANCE_CRITERIA.md).
# All 5 are backend-only (arch-inspection / pure compute) -- no Tour/HttpCase needed.
import logging

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'sale_margin_threshold')
class TestHighRiskAcceptanceCriteria(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'BACKFILL HighRisk AC Category',
            'margin_sale': 20.0,
        })
        cls.tax_10pct = cls.env['account.tax'].create({
            'name': 'BACKFILL AC-01-05 Tax 10%',
            'amount': 10.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
        })

    @staticmethod
    def _pos_margin_installed(env):
        return bool(env['ir.module.module'].search([
            ('name', '=', 'pos_margin_threshold'),
            ('state', '=', 'installed'),
        ], limit=1))

    # ------------------------------------------------------------------
    # AC-01-05 -- minimum_sale_price_with_tax formula (product.template + product.product)
    # ------------------------------------------------------------------

    def test_ac_01_05_minimum_sale_price_with_tax_template(self):
        """AC-01-05: minimum_sale_price_with_tax = minimum_sale_price * (1 + sum(tax.amount)/100)
        on product.template."""
        template = self.env['product.template'].create({
            'name': 'BACKFILL AC-01-05 Template',
            'categ_id': self.category.id,
            'standard_price': 100.0,
            'type': 'consu',
            'taxes_id': [(6, 0, self.tax_10pct.ids)],
        })
        self.assertEqual(
            template.margin_sale, 20.0,
            "AC-01-05 prerequisite: margin_sale harus terwarisi dari kategori (20.0)")
        self.assertEqual(
            template.minimum_sale_price, 120.0,
            "AC-01-05 prerequisite: minimum_sale_price = standard_price*(1+margin_sale/100)")
        self.assertAlmostEqual(
            template.minimum_sale_price_with_tax, 132.0, places=4,
            msg="AC-01-05: minimum_sale_price_with_tax harus 120.0*(1+10/100)=132.0 "
                "(product.template)")

    def test_ac_01_05_minimum_sale_price_with_tax_product(self):
        """AC-01-05: identik formula di atas, tapi di level product.product (variant),
        tax dibaca dari product_tmpl_id.taxes_id (lihat MF-38/MF-45)."""
        template = self.env['product.template'].create({
            'name': 'BACKFILL AC-01-05 Variant Template',
            'categ_id': self.category.id,
            'standard_price': 100.0,
            'type': 'consu',
            'taxes_id': [(6, 0, self.tax_10pct.ids)],
        })
        variant = template.product_variant_ids[:1]
        self.assertTrue(variant, "AC-01-05 prerequisite: template harus punya variant default")
        self.assertEqual(
            variant.minimum_sale_price, 120.0,
            "AC-01-05 prerequisite: minimum_sale_price variant harus 120.0")
        self.assertAlmostEqual(
            variant.minimum_sale_price_with_tax, 132.0, places=4,
            msg="AC-01-05: minimum_sale_price_with_tax harus 132.0 (product.product, MF-45 "
                "@api.depends fix)")

        # MF-45 regression guard: editing only the tax PERCENTAGE (not adding/removing a tax)
        # must still recompute minimum_sale_price_with_tax, since taxes_id.amount is a declared
        # dependency (not just taxes_id).
        self.tax_10pct.amount = 25.0
        self.assertAlmostEqual(
            variant.minimum_sale_price_with_tax, 150.0, places=4,
            msg="AC-01-05/MF-45: mengubah persentase pajak yang SUDAH terpasang harus memicu "
                "recompute (120.0*1.25=150.0), bukan tetap basi di nilai lama")

    # ------------------------------------------------------------------
    # AC-02-08 -- decoration-danger on sale.order order_line list (MF-35 xpath fix)
    # ------------------------------------------------------------------

    def test_ac_02_08_order_line_decoration_danger_arch(self):
        """AC-02-08: price_unit di list order_line harus punya decoration-danger yang
        membandingkan ke minimum_sale_price DAN mengecualikan rental order, dan xpath (MF-35)
        harus genuinely resolve (bukan install-blocking lagi)."""
        result = self.env['sale.order'].get_view(view_type='form')
        arch = etree.fromstring(result['arch'])

        # Scoped through list[@name='sol_list'] specifically (not just //field[@name='order_line']
        # descendants): order_line also embeds a separate o_kanban_mobile card with its own
        # price_unit node (native sale/views/sale_order_views.xml) which this module has NEVER
        # decorated, not even in 19.0 (confirmed via `git show migration/19.0:.../sale_order.xml`
        # -- only the desktop list was ever touched). Matching //field[@name='price_unit'] without
        # this scope double-counts that unrelated kanban node.
        price_unit_nodes = arch.xpath(
            "//page[@name='order_lines']/field[@name='order_line']"
            "/list[@name='sol_list']//field[@name='price_unit']"
        )
        self.assertEqual(
            len(price_unit_nodes), 1,
            "AC-02-08/MF-35: field price_unit harus resolve TEPAT SATU kali di dalam list "
            "(desktop) order_line (xpath lewat <column name='price_unit'> baru native 20.0)")
        self.assertEqual(
            price_unit_nodes[0].get('decoration-danger'),
            'minimum_sale_price > price_unit and not parent.is_rental_order_installed_true',
            "AC-02-08: ekspresi decoration-danger harus persis membandingkan minimum_sale_price "
            "vs price_unit DAN mengecualikan rental order (BSL-012)")

        min_price_nodes = arch.xpath(
            "//page[@name='order_lines']/field[@name='order_line']"
            "/list[@name='sol_list']//field[@name='minimum_sale_price']"
        )
        self.assertEqual(
            len(min_price_nodes), 1,
            "AC-02-08: minimum_sale_price harus tersedia di list (dipakai ekspresi decoration)")
        self.assertEqual(
            min_price_nodes[0].get('column_invisible'), '1',
            "AC-02-08: minimum_sale_price sendiri TIDAK boleh tampil sebagai kolom terpisah")

    # ------------------------------------------------------------------
    # AC-04-01/02/03 -- Product Variants list columns (MF-29/MF-37/MF-38)
    # ------------------------------------------------------------------

    def test_ac_04_01_product_variants_columns_visible_and_editable(self):
        """AC-04-01: kolom margin/minimum-price di list Product Variants harus tampil
        (optional='show', tanpa toggle manual) dan list tetap editable/multi_edit -- setara
        fungsional dengan popup 19.0 yang dihapus (MF-29). Berlaku independen dari kombinasi
        install (exactly ONE set of columns must survive, whichever module owns it)."""
        result = self.env['product.product'].get_view(view_type='list')
        arch = etree.fromstring(result['arch'])

        self.assertEqual(
            arch.get('editable'), 'bottom',
            "AC-04-01: list Product Variants harus tetap editable='bottom' (native 20.0)")
        self.assertEqual(
            arch.get('multi_edit'), '1',
            "AC-04-01: multi_edit harus aktif, setara edit-banyak-sekaligus popup lama")

        margin_nodes = arch.xpath("//field[@name='margin_sale']")
        min_price_nodes = arch.xpath("//field[@name='minimum_sale_price']")
        self.assertEqual(
            len(margin_nodes), 1,
            "AC-04-01/AC-04-02: harus ada TEPAT SATU kolom margin_sale yang tampil di arch "
            "final (0 = fitur hilang, >1 = dedup MF-37 gagal)")
        self.assertEqual(
            len(min_price_nodes), 1,
            "AC-04-01/AC-04-02: harus ada TEPAT SATU kolom minimum_sale_price yang tampil")
        self.assertEqual(
            margin_nodes[0].get('optional'), 'show',
            "AC-04-01: kolom margin_sale harus optional='show' (tampil tanpa toggle manual)")
        self.assertEqual(
            min_price_nodes[0].get('optional'), 'show',
            "AC-04-01: kolom minimum_sale_price harus optional='show'")

    def test_ac_04_02_product_variants_columns_dedup_contract(self):
        """AC-04-02/MF-37: kalau pos_margin_threshold JUGA terinstall, node milik
        sale_margin_threshold sendiri (marker o_smt_dedup_*) harus sudah di-strip dari arch final
        oleh ProductProduct._get_view(), menyisakan HANYA kolom pos_margin_threshold."""
        if not self._pos_margin_installed(self.env):
            self.skipTest(
                "AC-04-02: perlu pos_margin_threshold JUGA terinstall di DB ini untuk menguji "
                "dedup contract MF-37 (DB ini hanya sale_margin_threshold sendirian). Jalankan "
                "ulang dengan kedua modul terinstall bersamaan untuk mengeksekusi test ini.")

        result = self.env['product.product'].get_view(view_type='list')
        arch = etree.fromstring(result['arch'])

        dedup_marked_nodes = arch.xpath(
            "//field[@name='margin_sale'][contains(@class, 'o_smt_dedup_margin')]"
            " | //field[@name='minimum_sale_price'][contains(@class, 'o_smt_dedup_min_price')]"
            " | //field[@name='minimum_sale_price_with_tax']"
            "[contains(@class, 'o_smt_dedup_min_price_tax')]"
        )
        self.assertFalse(
            dedup_marked_nodes,
            "AC-04-02/MF-37: node bermarker o_smt_dedup_* milik sale_margin_threshold sendiri "
            "harus SUDAH DIHAPUS dari arch final saat pos_margin_threshold juga terinstall -- "
            "kalau node ini masih muncul, dedup gagal dan kolom akan tampil dobel")
        self.assertEqual(
            len(arch.xpath("//field[@name='margin_sale']")), 1,
            "AC-04-02: setelah dedup, harus tersisa TEPAT SATU kolom margin_sale (milik "
            "pos_margin_threshold)")
        self.assertEqual(
            len(arch.xpath("//field[@name='minimum_sale_price']")), 1,
            "AC-04-02: setelah dedup, harus tersisa TEPAT SATU kolom minimum_sale_price")
        self.assertEqual(
            len(arch.xpath("//field[@name='minimum_sale_price_with_tax']")), 1,
            "AC-04-02: setelah dedup, harus tersisa TEPAT SATU kolom minimum_sale_price_with_tax "
            "(Incl. Tax)")

    def test_ac_04_03_visual_parity_decoration_and_incl_tax_column(self):
        """AC-04-03/MF-38: paritas visual popup 19.0 -> kolom list 20.0: margin negatif harus
        decoration-danger, dan kolom "Incl. Tax" (minimum_sale_price_with_tax) harus ada TEPAT
        SATU kali (tidak dobel walau kedua modul terinstall, sama seperti AC-04-02)."""
        result = self.env['product.product'].get_view(view_type='list')
        arch = etree.fromstring(result['arch'])

        margin_nodes = arch.xpath("//field[@name='margin_sale']")
        self.assertEqual(len(margin_nodes), 1)
        self.assertEqual(
            margin_nodes[0].get('decoration-danger'), 'margin_sale < 0.0',
            "AC-04-03/MF-38: margin_sale negatif harus tampil merah (decoration-danger), "
            "paritas visual dengan popup 19.0")

        tax_nodes = arch.xpath("//field[@name='minimum_sale_price_with_tax']")
        self.assertEqual(
            len(tax_nodes), 1,
            "AC-04-03/MF-38: kolom Incl. Tax harus ada TEPAT SATU (baru ditambahkan MF-38, "
            "wajib tetap dedup-aware seperti AC-04-02)")
        self.assertEqual(
            tax_nodes[0].get('string'), 'Incl. Tax',
            "AC-04-03/MF-38: label kolom harus 'Incl. Tax', sama seperti popup 19.0")

        lst_price_nodes = arch.xpath("//field[@name='lst_price']")
        self.assertEqual(len(lst_price_nodes), 1)
        self.assertEqual(
            lst_price_nodes[0].get('decoration-danger'), 'is_less_minimum_sale',
            "AC-04-04 (regression guard, sekalian dicek di sini): lst_price harus tetap "
            "decoration-danger via is_less_minimum_sale, tidak boleh ikut ter-strip dedup")
