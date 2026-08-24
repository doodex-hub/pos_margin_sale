# -*- coding: utf-8 -*-
# Step 6/9 Mode D — Tour test headless (real Chrome). Companion of
# static/tests/tours/pin_message_tour.js. Verifies pin/unpin from the chatter action menu and
# the "Pinned Messages" section end-to-end (AC-01/AC-02/AC-04).
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestPinMessageTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_partner = cls.env['res.partner'].create({'name': 'Pin Message Tour Partner'})

    def test_pin_message_toggle_pin_tour(self):
        self.start_tour(
            f"/odoo/res.partner/{self.test_partner.id}",
            "pin_message_toggle_pin_tour",
            login="admin",
        )
