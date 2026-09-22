/* @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registerMessageAction } from "@mail/core/common/message_actions";

registerMessageAction("pins", {
    condition: ({ message }) => {
        if (!message.canAddReaction) {
            return false;
        }

        const isNote = !message.is_discussion &&
                       message.message_type !== "user_notification" &&
                       message.message_type !== "auto_comment" &&
                       message.message_type !== "notification";

        const isNotChangeLog = !message.subtype_description ||
                              message.subtype_description === "";

        return isNote && isNotChangeLog;
    },
    // 20.0: registerMessageAction() (bukan messageActionsRegistry.add() langsung) -- tanpa helper
    // ini, entry lolos registrasi tanpa error tapi difilter keluar diam-diam sebelum dirender
    // (action.js filter berbasis Symbol privat yang cuma dipasang helper ini). canAddReaction juga
    // sudah jadi getter di native (bukan method), sehingga parameter thread di destructure dibuang.
    // FontAwesome dihapus total dari template mail -- ikon sekarang nama Odoo Icon polos,
    // "push_pin" dikonfirmasi nama resmi (dipakai native sendiri, message_model.js
    // get notificationIcon() case "pin").
    icon: "push_pin",
    name: _t("Pin"),
    onSelected: ({ owner }) => owner.onClickPin(),
    sequence: 15,
});
