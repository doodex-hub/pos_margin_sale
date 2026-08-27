/** @odoo-module **/

import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";

// 19.0: Orderline no longer validates `props.line` against a strict shape, and
// PosOrderline.getDisplayData() (the old vehicle for custom display fields) was removed
// entirely — the component now reads getters straight off the live PosOrderline record
// (`line.<getter>`, see orderline.xml). The two getters below replace what getDisplayData()
// used to inject.

patch(ProductProduct.prototype, {
    get_minimum_sale_price() {
        return this.minimum_sale_price;
    },

    get_minimum_sale_price_with_tax() {
        return this.minimum_sale_price_with_tax;
    }
})


patch(PosOrderline.prototype, {
    setUnitPrice(price) {
        super.setUnitPrice(price);
    },

    get minimumSalePriceWithTax() {
        const product = this.getProduct();
        return formatCurrency(product.get_minimum_sale_price_with_tax(), this.currency);
    },

    get isLessMinimumSalePrice() {
        const product = this.getProduct();
        return this.displayPriceUnit < product.get_minimum_sale_price_with_tax();
    },

});
