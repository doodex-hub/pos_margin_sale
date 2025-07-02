/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';

registerPatch({
    name: 'Message',
    fields: {
        isPinned: attr({
            default: false,
        }),
        hasTogglePinAction: attr({
            compute() {
                return !this.isTemporary && !this.isTransient;
            }
        }),
    },
    recordMethods: {
        /**
         * Toggle the pin status of this message.
         */
        async togglePin() {
            await this.messaging.rpc({
                model: 'mail.message',
                method: 'toggle_pin',
                args: [[this.id]],
            });
            this.update({ isPinned: !this.isPinned });
        },
    },
    modelMethods: {
        /**
         * @override
         */
        convertData(data) {
            const data2 = this._super(data);
            if ('is_pinned' in data) {
                data2.isPinned = data.is_pinned;
            }
            return data2;
        },
    },
});