/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { useService } from "@web/core/utils/hooks";

patch(PosStore.prototype, {
    async processProductAttributes() {
        this.orm = this.env.services.orm; 
        const productIds = new Set();
        const productTmplIds = new Set();
        const productByTmplId = {};

        for (const product of this.models["product.product"].getAll()) {
            product.minimal_price_tax = await this.orm.call('product.product', 'get_minimal_price_tax', [product.id]);
            if (product.product_template_variant_value_ids.length > 0) {
                productTmplIds.add(product.raw.product_tmpl_id);
                productIds.add(product.id);

                if (!productByTmplId[product.raw.product_tmpl_id]) {
                    productByTmplId[product.raw.product_tmpl_id] = [];
                }

                productByTmplId[product.raw.product_tmpl_id].push(product);
            }
        }

        if (productIds.size > 0) {
            await this.data.searchRead("product.product", [
                "&",
                ["id", "not in", [...productIds]],
                ["product_tmpl_id", "in", [...productTmplIds]],
            ]);
        }

        for (const product of this.models["product.product"].filter(
            (p) => !productIds.has(p.id) && p.product_template_variant_value_ids.length > 0
        )) {
            productByTmplId[product.raw.product_tmpl_id].push(product);
        }

        for (const products of Object.values(productByTmplId)) {
            const nbrProduct = products.length;

            for (let i = 0; i < nbrProduct - 1; i++) {
                products[i].available_in_pos = false;
                this.mainProductVariant[products[i].id] = products[nbrProduct - 1];
            }
        }
    }
});