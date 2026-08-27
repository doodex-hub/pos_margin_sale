/* @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

messageActionsRegistry.add("pins", {
    condition: ({ message, thread }) => {
        console.log(message.type)
        if (!message.canAddReaction(thread)) {
            return false;
        }

        const isNote = !message.is_discussion &&
                       message.type !== "user_notification" &&
                       message.type !== "auto_comment" &&
                       message.type !== "notification";

        const isNotChangeLog = !message.subtype_description ||
                              message.subtype_description === "";

        return isNote && isNotChangeLog;
    },
    icon: "fa-thumb-tack",
    name: _t("Pin"),
    onSelected: ({ owner }) => owner.onClickPin(),
    sequence: 15,
});