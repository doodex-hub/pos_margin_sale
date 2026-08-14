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
                     "group_sale_margin_action.users=%s", group.users.ids)
        self.assertFalse(
            group.users.ids,
            "F-04: group_sale_margin_action harus KOSONG saat pos_margin_threshold terinstall "
            "(_register_hook menghapus semua user) -- kalau assertion ini gagal, hipotesis F-04 "
            "arah ini TERBUKTI SALAH, update FINDINGS.md."
        )
