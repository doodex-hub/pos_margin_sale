/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'MessageView',
    recordMethods: {
        onClickPin() {
            this.message.togglePin();
        },
        onClickUnpin() {
            this.message.togglePin();
        },
    },
});
