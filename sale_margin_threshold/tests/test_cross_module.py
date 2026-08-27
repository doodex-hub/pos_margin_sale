# -*- coding: utf-8 -*-
# BACKFILL — test cross-module (F-04), hanya bermakna kalau pos_margin_threshold JUGA terinstall.
import logging

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'sale_margin_threshold')
class TestCrossModuleGroupDedup(TransactionCase):

    def test_group_sale_margin_action_emptied_when_pos_margin_installed(self):
        """F-04 / AC-04-01: kalau pos_margin_threshold terinstall, _register_hook harus sudah
        mengosongkan group_sale_margin_action (dedup action 'Update margin sale')."""
        pos_margin_installed = self.env['ir.module.module'].search([
            ('name', '=', 'pos_margin_threshold'),
            ('state', '=', 'installed'),
        ], limit=1)
        group = self.env.ref('sale_margin_threshold.group_sale_margin_action', raise_if_not_found=False)
        self.assertTrue(group, "group_sale_margin_action harus ada")

        if not pos_margin_installed:
            self.skipTest(
                "BACKFILL: pos_margin_threshold tidak terinstall di database test ini -- "
                "F-04 (dedup group membership) tidak bisa diverifikasi arah 'kedua modul "
                "terinstall'. Lihat FINDINGS.md F-04."
            )

        _logger.info("BACKFILL F-04: pos_margin_threshold installed=True, "
                     "group_sale_margin_action.user_ids=%s", group.user_ids.ids)
        self.assertFalse(
            group.user_ids.ids,
            "F-04: group_sale_margin_action harus KOSONG saat pos_margin_threshold terinstall "
            "(_register_hook menghapus semua user) -- kalau assertion ini gagal, hipotesis F-04 "
            "arah ini TERBUKTI SALAH, update FINDINGS.md."
        )

    def test_wizard_margin_product_model_merged_when_both_installed(self):
        # Step 9 addendum (2026-08-24): closes the AC-04-02 gap flagged in Step 8 Code Review --
        # the equivalent MRO-inspection test only existed in pos_margin_threshold/tests, giving no
        # evidence from this module's side. Mirrors that test exactly, so whichever install order
        # (-i pos_margin_threshold,sale_margin_threshold OR the reverse) is used to build the test
        # database, BOTH modules' test suites independently confirm wizard.margin.product still
        # works and log the actual MRO for inspection -- not just one module's perspective.
        pos_margin_installed = self.env['ir.module.module'].search([
            ('name', '=', 'pos_margin_threshold'),
            ('state', '=', 'installed'),
        ], limit=1)
        if not pos_margin_installed:
            self.skipTest(
                "Step 9: pos_margin_threshold tidak terinstall di database test ini -- "
                "AC-04-02 (MRO wizard.margin.product tergantung urutan install) tidak bisa "
                "diverifikasi dari sisi modul ini. Jalankan ulang dengan kedua modul terinstall."
            )
        wizard = self.env['wizard.margin.product'].create({'margin': 10.0})
        self.assertTrue(wizard.exists(), "model gabungan harus tetap bisa create() tanpa error")

        full_mro = ["%s.%s" % (c.__module__, c.__name__)
                    for c in type(self.env['wizard.margin.product']).__mro__]
        _logger.info("Step 9 AC-04-02: FULL __mro__ (unfiltered) of wizard.margin.product "
                     "(from sale_margin_threshold's test suite) = %s", full_mro)
