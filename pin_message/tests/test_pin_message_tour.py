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

    def test_pin_message_action_menu_pin_visible_tour(self):
        # Step 9 addendum: closes the AC-02-02 gap flagged in Step 8 Code Review (MF-24) -- proves
        # the action-menu "Pin" entry (pinMessage.js) actually renders in the UI after the fix,
        # not just that the (unrelated) inline-button tour above still passes.
        self.start_tour(
            f"/odoo/res.partner/{self.test_partner.id}",
            "pin_message_action_menu_pin_visible_tour",
            login="admin",
        )
