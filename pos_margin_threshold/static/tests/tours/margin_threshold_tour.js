/** @odoo-module **/
// Step 6/9 Mode D — Tour test headless (real Chrome, via HttpCase.start_tour()).
// Verifies AC-02-02 (05a_MIGRATION_ACCEPTANCE_CRITERIA.md): selling a product below its
// minimum sale price, with blocking_transaction_pos=False, shows the confirmation dialog and
// lets the cashier proceed. This exercises the migrated PosStore.pay() patch end-to-end
// (dialog service, ask()/AlertDialog — see 06c_IMPLEMENTATION_LOG.md Fase E).

// 19.0: test-tour util files moved -- chrome_util/product_screen_util/payment_screen_util
// dari "tests/tours/utils/" ke "tests/pos/tours/utils/"; dialog_util pindah keluar dari
// "tours/" sepenuhnya ke "tests/generic_helpers/" (dipakai bersama modul lain, bukan spesifik
// POS lagi). Nama export (startPoS, confirm, isShown, dst) tidak berubah.
import * as Chrome from "@point_of_sale/../tests/pos/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/generic_helpers/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/pos/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/pos/tours/utils/payment_screen_util";
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
                // MF-44: native 20.0 renamed ReceiptScreen -> FeedbackScreen (CSS class
                // ".receipt-screen" no longer exists anywhere in native point_of_sale, confirmed by
                // full grep). Native's own tour utils (feedback_screen_util.js isShown()) trigger on
                // ".pos .feedback-screen" instead. Using the old 19.0 class name here made this step
                // ALWAYS time out (100% reproducible, not flaky) even though payment had already
                // synced correctly to the backend -- confirmed via a native control test
                // (point_of_sale.TestUi.test_payment_screen_tour, unrelated to this module) passing
                // cleanly in the same environment, which is what proved this wasn't environment
                // flakiness. See FINDINGS.md MF-44.
                content: "receipt screen is shown (payment went through)",
                trigger: ".pos .feedback-screen",
            },
            Chrome.endTour(),
        ].flat(),
});

// Step 9 Dev Testing addendum (2026-08-24) — closes the AC-02-01 gap flagged in Step 8 Code Review
// (08_review/pos_margin_threshold/08_CODE_REVIEW.md): the confirm/proceed path (AC-02-02, above)
// was the only one with Tour coverage; the blocking path (blocking_transaction_pos=True, AlertDialog,
// payment fully stopped) had none. Verifies PosStore.pay()'s other branch end-to-end.
registry.category("web_tour.tours").add("pos_margin_threshold_below_minimum_blocked_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            ProductScreen.isShown(),
            ProductScreen.addOrderline("Margin Threshold Test Product", "1", "5"),
            // shouldCheck=false: clicking Pay does NOT transition to the payment screen at all in
            // the blocked path -- it opens the AlertDialog and returns, staying on ProductScreen.
            ProductScreen.clickPayButton(false),
            Dialog.is({ title: "Price unit less than minimum price" }),
            Dialog.bodyIs("Some products are below the minimum price. Please check !"),
            // AlertDialog has a single "Ok" button (core default confirmLabel) -- dismissing it
            // must NOT advance to payment; the sale is genuinely blocked, not just delayed.
            Dialog.confirm(),
            ProductScreen.isShown(),
            Chrome.endTour(),
        ].flat(),
});
