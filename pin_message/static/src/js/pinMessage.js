/* @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

messageActionsRegistry.add("pins", {
    condition: ({ message, thread }) => {
        if (!message.canAddReaction(thread)) {
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
    // Odoo 18.0+ message actions carry the full icon class, family prefix included
    // ("fa fa-reply" in core); 17.0 supplied the "fa" base class from the template.
    icon: "fa fa-thumb-tack",
    name: _t("Pin"),
    onSelected: ({ owner }) => owner.onClickPin(),
    sequence: 15,
});