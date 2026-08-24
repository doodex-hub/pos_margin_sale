/** @odoo-module **/
// Step 6/9 Mode D — Tour test headless (real Chrome, via HttpCase.start_tour()).
// Verifies AC-02-02 (05a_MIGRATION_ACCEPTANCE_CRITERIA.md): selling a product below its
// minimum sale price, with blocking_transaction_pos=False, shows the confirmation dialog and
// lets the cashier proceed. This exercises the migrated PosStore.pay() patch end-to-end
// (dialog service, ask()/AlertDialog — see 06c_IMPLEMENTATION_LOG.md Fase E).

import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("pos_margin_threshold_below_minimum_confirm_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            // main_pos_config already computes cash_control=True (a default cash payment method
            // exists on the config before we add Bank on top) -- opening control dialog appears.
            // No text match (env renders this in whatever --load-language ends up active, not
            // necessarily the test user's own .lang) -- Dialog.confirm() with no argument just
            // clicks the modal's primary button, which is unambiguous here (only one exists).
            Dialog.confirm(),
            ProductScreen.isShown(),
            // Test Product is set up with standard_price=10, margin_sale=50 -> minimum_sale_price=15.
            // Selling at unit price 5 is below that minimum.
            ProductScreen.addOrderline("Margin Threshold Test Product", "1", "5"),
            // shouldCheck=false: clickPayButton()'s own built-in "wait for payment screen"
            // check assumes an instant transition — it doesn't know our confirmation dialog
            // (PosStore.pay() patch) sits in between. We wait for the payment screen ourselves,
            // after confirming the dialog.
            ProductScreen.clickPayButton(false),
            Dialog.is({ title: "Price unit less than minimum price" }),
            Dialog.bodyIs("Some products are below the minimum price. Proceed to payment?"),
            Dialog.confirm(),
            {
                content: "now in payment screen (after confirming below-minimum dialog)",
                trigger: ".pos-content .payment-screen",
            },
            PaymentScreen.clickPaymentMethod("Bank"),
            PaymentScreen.clickValidate(),
            {
                content: "receipt screen is shown (payment went through)",
                trigger: ".pos .receipt-screen",
            },
            Chrome.endTour(),
        ].flat(),
});
