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

// ---------------------------------------------------------------------------------------------
// Step 10 addendum (2026-09-23) — closes BSL-018 (01b_BASELINE_SPEC.md), i.e. AC-03-05 plus the
// orderline-warning half of the same finding (05a_MIGRATION_ACCEPTANCE_CRITERIA.md).
//
// NOT PRESENT IN ANY EARLIER VERSION. This gap was carried forward, undecided, through THREE
// consecutive migration projects: 17.0 -> 18.0, 18.0 -> 19.0 and (until now) 19.0 -> 20.0. The
// two tours below are written here for the first time, so branches migration/18.0 and
// migration/19.0 do NOT have them, and those versions remain without automated coverage for
// these two behaviours. Anyone back-porting must add these tours there explicitly rather than
// assume the older branches are covered.
// ---------------------------------------------------------------------------------------------

// BSL-018 part 1 (AC-03-05): with EVERY line at or above its minimum, clicking Pay must produce
// NO dialog whatsoever -- and the AC is explicit that this includes no brief flash/render. A
// plain "is the payment screen shown" assertion cannot prove that: a dialog that appeared and
// closed within the same frame would still pass it. So we install a MutationObserver before
// clicking Pay and fail if ANY .modal node was ever inserted, however briefly.
registry.category("web_tour.tours").add("pos_margin_threshold_no_dialog_above_minimum_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            ProductScreen.isShown(),
            // standard_price=10, margin_sale=50 -> the minimum sits well below 50 (the Python side
            // guards that precondition), so PosStore.pay()'s `lines.length > 0` guard must be
            // false and neither branch (ask() nor AlertDialog) may run.
            ProductScreen.addOrderline("Margin Threshold Test Product", "1", "50"),
            {
                content: "start recording any modal insertion (BSL-018: not even a flash allowed)",
                trigger: ".product-screen",
                run: () => {
                    window.__bsl018ModalsSeen = [];
                    const observer = new MutationObserver((records) => {
                        for (const record of records) {
                            for (const node of record.addedNodes) {
                                if (node.nodeType !== Node.ELEMENT_NODE) {
                                    continue;
                                }
                                if (node.matches?.(".modal")) {
                                    window.__bsl018ModalsSeen.push(node.className);
                                } else if (node.querySelector?.(".modal")) {
                                    window.__bsl018ModalsSeen.push(
                                        "nested: " + node.querySelector(".modal").className
                                    );
                                }
                            }
                        }
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                    window.__bsl018Observer = observer;
                },
            },
            // shouldCheck=false for symmetry with the tours above: we assert the transition
            // ourselves below, together with the no-modal assertion.
            ProductScreen.clickPayButton(false),
            {
                content: "went straight to the payment screen, no dialog in between",
                trigger: ".pos-content .payment-screen",
            },
            {
                content: "no modal is present right now",
                trigger: "body:not(:has(.modal))",
            },
            {
                content: "and no modal was EVER inserted while paying (catches a transient flash)",
                trigger: ".pos-content .payment-screen",
                run: () => {
                    window.__bsl018Observer?.disconnect();
                    const seen = window.__bsl018ModalsSeen || [];
                    if (seen.length) {
                        throw new Error(
                            "BSL-018/AC-03-05 violated: " +
                                seen.length +
                                " modal(s) rendered while paying an order whose lines are all " +
                                "above the minimum sale price: " +
                                JSON.stringify(seen)
                        );
                    }
                },
            },
            Chrome.endTour(),
        ].flat(),
});

// BSL-018 part 2: assert the orderline warning's TEXT and COLOUR in their own right, instead of
// only inferring "it didn't crash" from the dialog tours above. A second line that is ABOVE the
// minimum acts as an in-tour control, so a bug that painted every line red would still fail.
registry.category("web_tour.tours").add("pos_margin_threshold_orderline_warning_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            ProductScreen.isShown(),
            // Both products share the same minimum sale price. The first is sold below
            // it (5) and must be flagged; the second is sold above it (50) and must not be.
            // Two DISTINCT products on purpose: POS merges lines per product, and addOrderline()
            // asserts the new line has quantity "1", so reusing one product at two prices would
            // risk failing the tour for a merge reason rather than for the decoration itself.
            ProductScreen.addOrderline("Margin Threshold Test Product", "1", "5"),
            ProductScreen.addOrderline("Margin Threshold Control Product", "1", "50"),
            {
                content: "below-minimum line carries the warning text",
                trigger:
                    "li.orderline.text-danger strong:contains('The price of this product is less than minimum sale price')",
            },
            {
                // No hard-coded amount on purpose. minimumSalePriceWithTax goes through
                // formatCurrency(), so the rendering (symbol side, separators, non-breaking
                // spaces) follows the database's currency and locale, and the figure itself
                // follows whichever taxes the accounting fixture attaches -- neither is stable
                // enough to pin from a tour. What IS invariant, and is what BSL-018 asks for, is
                // that the row shows a real positive amount which is strictly above the price
                // this line is sold at: the warning only ever renders when price < minimum. That
                // still catches a wrong field, a 0.00, the unit price echoed back, or broken
                // formatting. The Python side guards the 5 < minimum < 50 precondition.
                content: "the warning shows a real amount above the price this line is sold at",
                trigger: "li.orderline.text-danger strong",
                run: () => {
                    const text = document.querySelector("li.orderline.text-danger strong").innerText;
                    const numbers = (text.match(/\d+(?:[.,]\d+)?/g) || []).map((n) =>
                        parseFloat(n.replace(",", "."))
                    );
                    if (!numbers.length) {
                        throw new Error(
                            "BSL-018: the warning row shows no amount at all. Rendered text was: " +
                                JSON.stringify(text)
                        );
                    }
                    if (!numbers.some((value) => value > 5)) {
                        throw new Error(
                            "BSL-018: the warning row does not show a minimum sale price above " +
                                "the 5.00 this line is sold at -- it is showing the wrong value " +
                                "(the unit price, or 0). Rendered text was: " +
                                JSON.stringify(text)
                        );
                    }
                },
            },
            {
                content: "the above-minimum line is NOT flagged and carries no warning row",
                trigger:
                    "li.orderline:not(.text-danger):not(:has(strong:contains('less than minimum sale price')))",
            },
            // Select the flagged line before comparing colours. POS styles `.orderline.selected`
            // (background plus, in this theme, a text colour that computes to the very same red
            // as .text-danger), and the last line added is the selected one -- comparing against
            // a selected control line reports "both are red" and proves nothing. Selecting the
            // flagged line puts the control back in its neutral state.
            ProductScreen.clickLine("Margin Threshold Test Product"),
            {
                content: "the flagged line is genuinely rendered red, not merely class-tagged",
                trigger: "li.orderline.text-danger",
                run: () => {
                    // Both lines are located by PRODUCT NAME rather than by
                    // `li.orderline:not(.text-danger)`: POS renders order lines in more than one
                    // place, so a bare querySelector can return a line from a different render
                    // root and make the comparison meaningless (it did, first time round).
                    const lineFor = (name) =>
                        [...document.querySelectorAll("li.orderline")].find((li) =>
                            li.innerText.includes(name)
                        );
                    const flagged = lineFor("Margin Threshold Test Product");
                    const control = lineFor("Margin Threshold Control Product");
                    if (!flagged || !control) {
                        throw new Error(
                            "BSL-018: expected both the flagged and the control orderline to be " +
                                "present, found flagged=" +
                                Boolean(flagged) +
                                " control=" +
                                Boolean(control)
                        );
                    }
                    if (!flagged.classList.contains("text-danger")) {
                        throw new Error("BSL-018: the below-minimum line is not class-tagged red");
                    }
                    if (control.classList.contains("text-danger")) {
                        throw new Error(
                            "BSL-018: the above-minimum control line is flagged red, so the " +
                                "decoration is not conditional"
                        );
                    }
                    const channels = (el) =>
                        getComputedStyle(el)
                            .color.match(/\d+/g)
                            .slice(0, 3)
                            .map(Number);
                    const [r, g, b] = channels(flagged);
                    // Assert the rendered colour rather than a hard-coded rgb() string, which
                    // would break on any theme change: "red" means red clearly dominant over the
                    // other channels, and visibly different from the untouched control line.
                    if (!(r > g + 40 && r > b + 40)) {
                        throw new Error(
                            "BSL-018: below-minimum orderline is not rendered red, got rgb(" +
                                [r, g, b].join(", ") +
                                ")"
                        );
                    }
                    if (channels(control).join() === [r, g, b].join()) {
                        throw new Error(
                            "BSL-018: flagged and unflagged orderlines render the same colour (" +
                                getComputedStyle(control).color +
                                "), so the decoration is not actually conditional"
                        );
                    }
                },
            },
            Chrome.endTour(),
        ].flat(),
});
