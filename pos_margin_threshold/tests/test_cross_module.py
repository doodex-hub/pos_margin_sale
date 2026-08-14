# -*- coding: utf-8 -*-
# BACKFILL — test cross-module (F-03), hanya bermakna kalau sale_margin_threshold JUGA terinstall.
import logging

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'pos_margin_threshold')
class TestCrossModuleWizardMargin(TransactionCase):

    def test_wizard_margin_product_model_merged_when_both_installed(self):
        """F-03: kalau sale_margin_threshold JUGA terinstall, model wizard.margin.product
        yang didefinisikan independen di 2 modul harus tetap bisa dipakai tanpa error."""
        sale_margin_installed = self.env['ir.module.module'].search([
            ('name', '=', 'sale_margin_threshold'),
            ('state', '=', 'installed'),
        ], limit=1)
        if not sale_margin_installed:
            self.skipTest(
                "BACKFILL: sale_margin_threshold tidak terinstall di database test ini -- "
                "F-03 (koeksistensi model wizard.margin.product) tidak bisa diverifikasi. "
                "Lihat FINDINGS.md F-03 -- jalankan ulang dengan kedua modul terinstall bersamaan."
            )
        model = self.env['ir.model'].search([('model', '=', 'wizard.margin.product')])
        _logger.info("BACKFILL F-03: ir.model rows for wizard.margin.product = %s (module: %s)",
                     model.mapped('id'), model.mapped('modules'))
        wizard = self.env['wizard.margin.product'].create({'margin': 10.0})
        self.assertTrue(wizard.exists(), "model gabungan harus tetap bisa create() tanpa error")

        full_mro = ["%s.%s" % (c.__module__, c.__name__)
                    for c in type(self.env['wizard.margin.product']).__mro__]
        _logger.info("BACKFILL F-03: FULL __mro__ (unfiltered) of wizard.margin.product = %s", full_mro)

        classes = [c.__module__ for c in type(self.env['wizard.margin.product']).__mro__
                   if (getattr(c, '_name', None) or '').find('margin') >= 0
                   or 'WizardMarginProduct' in c.__name__]
        _logger.info("BACKFILL F-03: __mro__ classes contributing to wizard.margin.product = %s", classes)
