/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


patch(PosStore.prototype, {
    async pay() {
        const currentOrder = this.get_order();
        const orderLines = currentOrder.get_orderlines();
        const lines = orderLines.filter(
            (line) => line.get_unit_display_price() < line.get_product().get_minimum_sale_price_with_tax()
        );
        const blocked = this.config.is_blocked_warning;
        if (lines.length > 0) {
            // Display the confirmation popup with the constructed message
            if (!blocked) {
                const confirmed = await ask(this.env.services.dialog, {
                    title: _t("Price unit less than minimum price"),
                    body: _t("Some products are below the minimum price. Proceed to payment?")
                });
                if (!confirmed) {
                    return;
                }
            } else {
                this.env.services.dialog.add(AlertDialog, {
                    title: _t("Price unit less than minimum price"),
                    body: _t("Some products are below the minimum price. Please check !")
                });
                return;
            }
        }

        return super.pay(...arguments);
    }
});
