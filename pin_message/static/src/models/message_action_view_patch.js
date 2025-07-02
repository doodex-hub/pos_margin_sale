/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'MessageActionView',
    recordMethods: {
        onClick(ev) {
            if (this.messageAction.messageActionListOwnerAsTogglePin) {
                this.messageAction.messageActionListOwnerAsTogglePin.message.togglePin();
                return;
            }
            this._super(ev);
        },
    },
    fields: {
        classNames: {
            compute() {
                const classNames = this._super();
                if (this.messageAction.messageActionListOwnerAsTogglePin) {
                    const isPinned = this.messageAction.messageActionListOwnerAsTogglePin.message.isPinned;
                    return classNames + ' fa fa-lg fa-thumb-tack o_MessageActionView_actionTogglePin' +
                           (isPinned ? ' o_MessageActionView_actionTogglePin_active' : '');
                }
                return classNames;
            },
        },
        title: {
            compute() {
                if (this.messageAction.messageActionListOwnerAsTogglePin) {
                    if (this.messageAction.messageActionListOwnerAsTogglePin.message.isPinned) {
                        return this.env._t("Unpin");
                    }
                    return this.env._t("Pin");
                }
                return this._super();
            },
        },
    },
});