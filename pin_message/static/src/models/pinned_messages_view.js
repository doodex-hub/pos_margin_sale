/** @odoo-module **/

import { registerModel } from '@mail/model/model_core';
import { attr, many, one } from '@mail/model/model_field';

registerModel({
    name: 'PinnedMessagesView',
    fields: {
        component: attr(),
        isPinnedMessageListVisible: attr({
            default: false,
        }),
        pinnedBoxViews: many('PinnedBoxView', {
            compute() {
                if (!this.thread || !this.thread.messages) {
                    console.log('PinnedMessagesView: Thread empty.');
                    return [];
                }
                const pinnedMessages = this.thread.messages.filter(message => message.isPinned);
                return pinnedMessages.map(message => ({ message }));
            },
        }),
        thread: one('Thread', {
            required: true,
        }),
        chatter: one('Chatter', {
            identifying: true,
            inverse: 'pinnedMessagesView',
        }),
    },
    recordMethods: {
        /**
         * @param {MouseEvent} ev
         */
        onClickPinnedMessagesTitle(ev) {
            ev.preventDefault();
            this.update({ isPinnedMessageListVisible: !this.isPinnedMessageListVisible });
        },
    },
});