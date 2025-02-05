/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

Orderline.props = {
    class: { type: Object, optional: true },
    line: {
        type: Object,
        shape: {
            isSelected: { type: Boolean, optional: true },
            productName: String,
            price: String,
            qty: String,
            unit: { type: String, optional: true },
            unitPrice: String,
            discount: { type: String, optional: true },
            comboParent: { type: String, optional: true },
            oldUnitPrice: { type: String, optional: true },
            customerNote: { type: String, optional: true },
            internalNote: { type: String, optional: true },
            imageSrc: { type: String, optional: true },
            packLotLines: { type: Array, optional: true },
            price_without_discount: { type: String, optional: true },
            taxGroupLabels: { type: String, optional: true },
            minimumSalePriceWithTax: { type: String, optional: true },
            isLessMinimumSalePrice: { type: Boolean, optional: true },
        },
    },
    showTaxGroupLabels: { type: Boolean, optional: true },
    slots: { type: Object, optional: true },
    basic_receipt: { type: Boolean, optional: true },
}

patch(PosOrderline.prototype, {
    getDisplayData() {
        const priceStr = this.get_unit_display_price(); // Removes any non-numeric characters except the decimal point
        const priceNum = parseFloat(priceStr); // Converts cleaned string to a float
        const isLessMinimumSalePrice = !isNaN(priceNum) && priceNum < this.product_id.minimal_price_tax; // Ensures it's a valid number before comparison
        return {
            productName: this.get_full_product_name(),
            price: this.getPriceString(),
            qty: this.get_quantity_str(),
            unit: this.product_id.uom_id ? this.product_id.uom_id.name : "",
            unitPrice: formatCurrency(this.get_unit_display_price(), this.currency),
            oldUnitPrice: this.get_old_unit_display_price()
                ? formatCurrency(this.get_old_unit_display_price(), this.currency)
                : "",
            discount: this.get_discount_str(),
            customerNote: this.get_customer_note() || "",
            internalNote: this.getNote(),
            comboParent: this.combo_parent_id?.get_full_product_name?.() || "",
            packLotLines: this.pack_lot_ids.map(
                (l) =>
                    `${l.pos_order_line_id.product_id.tracking == "lot" ? "Lot Number" : "SN"} ${
                        l.lot_name
                    }`
            ),
            price_without_discount: formatCurrency(
                this.getUnitDisplayPriceBeforeDiscount(),
                this.currency
            ),
            taxGroupLabels: [
                ...new Set(
                    this.product_id.taxes_id
                        ?.map((tax) => tax.tax_group_id.pos_receipt_label)
                        .filter((label) => label)
                ),
            ].join(" "),
            minimumSalePriceWithTax: formatCurrency(this.product_id.minimal_price_tax, this.currency),
            isLessMinimumSalePrice: isLessMinimumSalePrice,
        };
    }
});

patch(PosStore.prototype, {
    async pay() {
        this.dialogService = this.env.services.dialog; 
        const currentOrder = this.get_order().lines;
        const lines = currentOrder.filter(line => line.get_unit_display_price() < line.product_id.minimal_price_tax);
        const blocked = await this.orm.call('pos.config', 'get_block_config', []);
        if (lines.length > 0) {
            if (!blocked) {
                this.dialogService.add(ConfirmationDialog, {
                    title: _t("Price unit less than minimum price"),
                    body: _t("Some products are below the minimum price. Proceed to payment?"),
                    confirmClass: "btn-primary",
                    confirmLabel: _t("Confirm"),
                    confirm: () => {
                        return super.pay(...arguments);
                    },
                    cancelLabel: _t("Cancel"),
                    cancel: () => { },
                });
            } else {
                this.dialog.add(AlertDialog, {
                    title: _t("Price unit less than minimum price"),
                    body: _t("Some products are below the minimum price. Please check !")
                });
            }
        }
        else{
            return super.pay(...arguments);
        }
    }
});