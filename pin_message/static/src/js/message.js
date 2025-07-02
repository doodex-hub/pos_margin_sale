/** @odoo-module */
import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(Message.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
    },
    async onClickPin() {
        if (this.message.is_discussion) {
            const isPinned = Boolean(this.messagePinService.getPinnedAt(this.message.id));
            if (isPinned) {
                this.messagePinService.unpin(this.message);
            } else {
                this.messagePinService.pin(this.message);
            }
        } else {
            try {
                await this.orm.call("mail.message", "toggle_pin", [[this.props.message.id]]);
                this.props.message.is_pinned = !this.props.message.is_pinned;
            } catch (error) {
                console.error("Error toggling pin status:", error);
            }
        }
    },
    async onMessagePin(){
        await this.orm.call("mail.message", "toggle_pin", [[this.props.message.id]]);
        this.props.message.is_pinned = !this.props.message.is_pinned;
    }
});
