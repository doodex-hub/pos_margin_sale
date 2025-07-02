/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { one } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'MessageActionList',
    fields: {
        actionTogglePin: one('MessageAction', {
            compute() {
                if (this.message && this.message.hasTogglePinAction) {
                    return {};
                }
                return clear();
            },
            inverse: 'messageActionListOwnerAsTogglePin',
        }),
    },
});