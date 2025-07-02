/** @odoo-module **/

import { registerModel } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';

registerModel({
    name: 'PinnedBoxView',
    fields: {
        component: attr(),
        formattedDate: attr({
            compute() {
                if (!this.message || !this.message.date) {
                    return '';
                }
                return this.message.date.format('hh:mm a');
            },
        }),
        message: one('Message', {
            identifying: true,
        }),
        avatarUrl: attr({
            compute() {
                if (this.message.author && (!this.message.originThread || this.message.originThread.model !== 'mail.channel')) {
                    return this.message.author.avatarUrl;
                } else if (this.message.author && this.message.originThread && this.message.originThread.model === 'mail.channel') {
                    return `/mail/channel/${this.message.originThread.id}/partner/${this.message.author.id}/avatar_128`;
                } else if (this.message.guestAuthor && (!this.message.originThread || this.message.originThread.model !== 'mail.channel')) {
                    return this.message.guestAuthor.avatarUrl;
                } else if (this.message.guestAuthor && this.message.originThread && this.message.originThread.model === 'mail.channel') {
                    return `/mail/channel/${this.message.originThread.id}/guest/${this.message.guestAuthor.id}/avatar_128?unique=${this.message.guestAuthor.name}`;
                } else if (this.message.message_type === 'email') {
                    return '/mail/static/src/img/email_icon.png';
                }
                return '/mail/static/src/img/smiley/avatar.jpg';
            },
        }),
    },
    recordMethods: {
        async onClickUnpin(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            await this.message.togglePin();
        },
    },
});
