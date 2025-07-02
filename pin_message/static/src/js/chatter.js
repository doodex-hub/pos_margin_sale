/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { onMounted, onWillUpdateProps, toRaw } from "@odoo/owl";
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
        
        // Store pinned message IDs
        this.pinnedMessageIds = [];
        
        onMounted(() => {
            this.loadPinnedMessages();
        });
        
        onWillUpdateProps((nextProps) => {
            if (
                this.props.threadId !== nextProps.threadId ||
                this.props.threadModel !== nextProps.threadModel
            ) {
                this.loadPinnedMessages();
            }
        });
    },

    async loadPinnedMessages() {
        if (!this.state.thread) return;
        
        try {
            const pinnedMessages = await this.orm.searchRead(
                'mail.message',
                [['is_pinned', '=', true], ['model', '=', this.props.threadModel], ['res_id', '=', this.props.threadId]],
                ['id', 'body', 'author_id', 'date', 'is_pinned'],
                { order: 'date DESC' }
            );
            
            // Store pinned message IDs for reference
            this.pinnedMessageIds = pinnedMessages.map(msg => msg.id);
            
            // Update pinned status for current messages
            this._updatePinnedStatus();
        } catch (error) {
            console.error('Error loading pinned messages:', error);
        }
    },
    
    _updatePinnedStatus() {
        if (!this.state.thread || !this.pinnedMessageIds.length) return;
        
        // Update pinned status for all messages
        this.state.thread.messages.forEach(message => {
            if (this.pinnedMessageIds.includes(message.id)) {
                message.is_pinned = true;
            }
        });
    },

    get pinnedMessages() {
        return this.state.thread?.messages.filter(message => message.is_pinned) ?? [];
    },

    togglePinnedMessages() {
        this.state.showPinnedMessages = !this.state.showPinnedMessages;
    },
    
    // Override load to ensure pinned status is preserved
    load(thread, requestList) {
        if (!thread.id || !this.state.thread?.eq(thread)) {
            return;
        }
        
        // Call original method
        super.load(thread, requestList);
        
        // Update pinned status after loading with a delay to ensure messages are loaded
        setTimeout(() => this._updatePinnedStatus(), 200);
    },
    
    // Override Thread's fetchData method to update pinned status after fetching
    async fetchData(requestList) {
        if (super.fetchData) {
            await super.fetchData(requestList);
        }
        
        // Update pinned status after fetching with a delay
        setTimeout(() => this._updatePinnedStatus(), 200);
    },
    
    // Clean up when component is destroyed
    __destroy() {
        if (super.__destroy) {
            super.__destroy();
        }
    }
});
Chatter.components = { ...Chatter.components, MessageCardList };
