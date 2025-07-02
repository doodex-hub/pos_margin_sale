/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class PinnedMessages extends Component {

    /**
     * @returns {PinnedMessagesView}
     */
    get pinnedMessagesView() {
        return this.props.record;
    }

}

Object.assign(PinnedMessages, {
    props: {
        record: Object,
        className: { type: String, optional: true },
    },
    template: 'pin_message.PinnedMessages',
});

registerMessagingComponent(PinnedMessages);
