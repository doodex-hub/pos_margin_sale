/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { onMounted, onWillUpdateProps } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { MessageCardList } from "@mail/core/common/message_card_list";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        Object.assign(this.state, {
            showPinnedMessages: false,
        });
        onMounted(() => {
            this.initialLoad();
        });
        onWillUpdateProps((nextProps) => {
            if (
                this.props.threadId !== nextProps.threadId ||
                this.props.threadModel !== nextProps.threadModel
            ) {
                this.initialLoad();
            }
        });
    },

    async initialLoad() {
        if (!this.state.thread) return;
        await this.load(this.state.thread, ["messages"]);
        try {
            const pinnedMessages = await this.orm.searchRead(
        'mail.message',
        [['is_pinned', '=', true], ['model', '=', this.props.threadModel], ['res_id', '=', this.props.threadId]],
        ['id', 'body', 'author_id', 'date', 'is_pinned'],
        { order: 'date DESC' }
    );

    pinnedMessages.forEach(pinnedMsg => {
        const message = this.state.thread.messages.find(msg => msg.id === pinnedMsg.id);
        if (message) {
            message.is_pinned = true;
        }
    });
        } catch (error) {
            console.error('Error loading pinned messages:', error);
        }
    },

    get pinnedMessages() {
        return this.state.thread?.messages.filter(message => message.is_pinned) ?? [];
    },

    togglePinnedMessages() {
        this.state.showPinnedMessages = !this.state.showPinnedMessages;
    },
    // 18.0: `load()` core (`chatter/web_portal/chatter.js`) sudah tidak menerima parameter
    // custom field ("messageFields") -- `fetchData(requestList)` cuma minta kategori data
    // ("messages", "activities", dst), bukan field spesifik. `is_pinned` sekarang datang
    // otomatis lewat `mail.message._to_store()` (Python, lihat models/mail_message.py) --
    // method ini EXTEND super() apa adanya, tidak lagi full-override.
});
Chatter.components = { ...Chatter.components, MessageCardList };
