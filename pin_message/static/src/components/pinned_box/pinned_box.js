/** @odoo-module **/

import { useComponentToModel } from '@mail/component_hooks/use_component_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { LegacyComponent } from "@web/legacy/legacy_component";

export class PinnedBox extends LegacyComponent {

    /**
     * @override
     */
    setup() {
        super.setup();
        useComponentToModel({ fieldName: 'component' });
    }

    /**
     * @returns {PinnedBoxView}
     */
    get pinnedBoxView() {
        return this.props.record;
    }

}

Object.assign(PinnedBox, {
    props: { record: Object, className: { type: String, optional: true } },
    template: 'pin_message.PinnedBox',
});

registerMessagingComponent(PinnedBox);
