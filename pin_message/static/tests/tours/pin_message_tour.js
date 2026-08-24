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
                    ".o-mail-Message:contains('Pin message migration test note') button:has(.fa-thumb-tack-o)",
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
