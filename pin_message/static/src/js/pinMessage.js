/* @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

messageActionsRegistry.add("pins", {
    condition: (component) => {
        console.log(component.message.message_type);
        if (!component.props.message.canAddReaction) {
            return false;
        }

        const isNote = !component.message.is_discussion &&
                       component.message.message_type !== "user_notification" &&
                       component.message.message_type !== "auto_comment" &&
                       component.message.message_type !== "notification";

        const isNotChangeLog = !component.message.subtype_description ||
                              component.message.subtype_description === "";

        return isNote && isNotChangeLog;
    },
    icon: "fa fa-thumb-tack",
    title: _t("Pin"),
    onClick: (component) => component.onClickPin(),
    sequence: 25,
});