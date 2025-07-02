/* @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

messageActionsRegistry.add("pins", {
    condition: (component) => {
        console.log(component.message.type)
        if (!component.canAddReaction) {
            return false;
        }

        const isNote = !component.message.is_discussion && 
                       component.message.type !== "user_notification" &&
                       component.message.type !== "auto_comment" &&
                       component.message.type !== "notification";

        const isNotChangeLog = !component.message.subtype_description || 
                              component.message.subtype_description === "";
        
        return isNote && isNotChangeLog;
    },
    icon: "fa-thumb-tack",
    title: _t("Pin"),
    onClick: (component) => component.onClickPin(),
    sequence: 15,
});