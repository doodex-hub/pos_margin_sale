/** @odoo-module **/

import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";

// The Orderline OWL component validates `line` against a strict props shape (Odoo 18.0) —
// extra keys returned by getDisplayData() below must be declared here or Owl raises
// "Invalid props for component 'Orderline'".
patch(Orderline.props.line.shape, {
    minimumSalePrice: { type: String, optional: true },
    minimumSalePriceWithTax: { type: String, optional: true },
    isLessMinimumSalePrice: { type: Boolean, optional: true },
});


patch(ProductProduct.prototype, {
    get_minimum_sale_price() {
        return this.minimum_sale_price;
    },

    get_minimum_sale_price_with_tax() {
        return this.minimum_sale_price_with_tax;
    }
})


patch(PosOrderline.prototype, {
    set_unit_price(price) {
        super.set_unit_price(price);
    },

    getDisplayData() {
        const product = this.get_product();
        return {
            ...super.getDisplayData(),
            minimumSalePrice: formatCurrency(product.get_minimum_sale_price(), this.currency), // Added minimum_sale_price
            minimumSalePriceWithTax: formatCurrency(product.get_minimum_sale_price_with_tax(), this.currency),
            isLessMinimumSalePrice: this.get_unit_display_price() < product.get_minimum_sale_price_with_tax()
        };
    }

});
