/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { one } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'Chatter',
    fields: {
        pinnedMessagesView: one('PinnedMessagesView', {
            compute() {
                if (!this.thread || !this.thread.id) {
                    return clear();
                }
                return {
                    thread: this.thread,
                };
            },
            inverse: 'chatter',
        }),
    },
});