/** @odoo-module **/
// Step 6/9 Mode D — Tour test headless (real Chrome, via HttpCase.start_tour()).
// Verifies AC-01/AC-02/AC-04 (05a_MIGRATION_ACCEPTANCE_CRITERIA.md): pin a log note from the
// chatter action menu, confirm the "Pinned Messages" section (this module's own patch of
// mail.Chatter) appears with the pinned note, then unpin it. Exercises DIFF-01..05 end-to-end
// (t-inherit xpaths on mail.Chatter/mail.Message + the action registry entry).

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("pin_message_toggle_pin_tour", {
    steps: () =>
        [
            {
                content: "open Log note composer",
                trigger: ".o-mail-Chatter-logNote",
                run: "click",
            },
            {
                content: "type the note text",
                trigger: ".o-mail-Composer-input",
                run: "edit Pin message migration test note",
            },
            {
                content: "submit the log note",
                trigger: ".o-mail-Composer-send",
                run: "click",
            },
            {
                content: "note appears in the chatter",
                trigger: ".o-mail-Message:contains('Pin message migration test note')",
            },
            {
                content: "click the inline pin button (pinnedMessages.xml patch, next to author name)",
                trigger:
                    ".o-mail-Message:contains('Pin message migration test note') button:has(.fa-thumb-tack.text-muted)",
                run: "click",
            },
            {
                content: "Pinned Messages section appears with badge 1",
                trigger: ".o-mail-PinnedMessages .badge:contains('1')",
            },
            {
                content: "expand the Pinned Messages section (click the header specifically, not the whole container)",
                trigger: ".o-mail-PinnedMessages .cursor-pointer",
                run: "click",
            },
            {
                content: "a message card is listed inside the expanded section",
                trigger: ".o-mail-PinnedMessages .o-mail-MessageCardList .card",
                timeout: 15000,
            },
            {
                content: "unpin via the same inline button (now showing the pinned icon)",
                trigger:
                    ".o-mail-Message:contains('Pin message migration test note') button:has(.fa-thumb-tack.text-primary)",
                run: "click",
            },
            {
                content: "Pinned Messages section disappears once nothing is pinned",
                trigger: "body:not(:has(.o-mail-PinnedMessages))",
            },
        ].flat(),
});

// Step 9 Dev Testing addendum (2026-08-24) — closes the AC-02-02 gap flagged in Step 8 Code Review
// (08_review/pin_message/08_CODE_REVIEW.md, MF-24): the tour above only proves the inline pin
// button (pinnedMessages.xml) works; MF-24's fix was to the action-menu "Pin" entry
// (messageActionsRegistry, pinMessage.js), which the tour above never exercises. This tour proves
// that entry actually renders in the UI now, end-to-end -- not just that the test suite doesn't error.
registry.category("web_tour.tours").add("pin_message_action_menu_pin_visible_tour", {
    steps: () =>
        [
            {
                content: "open Log note composer",
                trigger: ".o-mail-Chatter-logNote",
                run: "click",
            },
            {
                content: "type the note text",
                trigger: ".o-mail-Composer-input",
                run: "edit Action menu visibility test note",
            },
            {
                content: "submit the log note",
                trigger: ".o-mail-Composer-send",
                run: "click",
            },
            {
                content: "note appears in the chatter",
                trigger: ".o-mail-Message:contains('Action menu visibility test note')",
            },
            {
                content: "hover the message to reveal its (otherwise hidden) actions bar",
                trigger: ".o-mail-Message:contains('Action menu visibility test note')",
                run: "hover",
            },
            {
                content: "the 'Pin' action-menu entry is present (as a quick action or inside the '...' overflow menu)",
                trigger:
                    ".o-mail-Message:contains('Action menu visibility test note') .o-mail-Message-actions button[name='pins'], " +
                    ".o-mail-Message:contains('Action menu visibility test note') .o-mail-Message-actions button:has(.fa-ellipsis-v)",
                run: "click",
            },
            {
                content: "either the 'Pin' button was clicked directly, or the overflow menu is now open with a 'Pin' entry inside it",
                trigger:
                    ".o-mail-Message-moreMenu .dropdown-item:contains('Pin'), " +
                    ".o-mail-PinnedMessages .badge:contains('1')",
            },
        ].flat(),
});
