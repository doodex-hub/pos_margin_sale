# -*- coding: utf-8 -*-
# BACKFILL (doc-dev-backfill) — test baru ditambahkan retroaktif, tidak mengubah kode bisnis.
# Ref: doc-dev/backfill/spec/pin_message/01B_ACCEPTANCE_CRITERIA.md
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'pin_message')
class TestPinMessage(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'BACKFILL Pin Test Partner'})

    def _make_log_note(self, body='BACKFILL test note'):
        return self.partner.message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_note')

    def test_toggle_pin_sets_true(self):
        """AC-01-01."""
        message = self._make_log_note()
        self.assertFalse(message.is_pinned)
        message.toggle_pin()
        self.assertTrue(message.is_pinned)

    def test_toggle_pin_sets_false_when_already_pinned(self):
        """AC-01-02."""
        message = self._make_log_note()
        message.is_pinned = True
        message.toggle_pin()
        self.assertFalse(message.is_pinned)

    def test_toggle_pin_multi_record_safe(self):
        """toggle_pin di-loop `for message in self` -- harus aman untuk multi-record,
        beda dengan bug F-05 di sale_margin_threshold."""
        msg_1 = self._make_log_note('note 1')
        msg_2 = self._make_log_note('note 2')
        batch = msg_1 + msg_2
        batch.toggle_pin()
        self.assertTrue(msg_1.is_pinned)
        self.assertTrue(msg_2.is_pinned)
