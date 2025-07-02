/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { one } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'MessageAction',
    fields: {
        messageActionListOwner: {
            compute() {
                if (this.messageActionListOwnerAsTogglePin) {
                    return this.messageActionListOwnerAsTogglePin;
                }
                return this._super();
            },
        },
        messageActionListOwnerAsTogglePin: one('MessageActionList', {
            identifying: true,
            inverse: 'actionTogglePin',
        }),
        sequence: {
            compute() {
                switch (this.messageActionListOwner) {
                    case this.messageActionListOwnerAsTogglePin:
                        return 1.5;
                    default:
                        return this._super();
                }
            },
        },
    },
});