from odoo import _, api, fields, models


# NOTE (migrasi 18.0): `pos.session._loader_params_product_product` — hook yang di-override
# file ini di 17.0 — sudah TIDAK ADA sama sekali di Odoo 18.0 (mekanisme loading data POS
# diganti total jadi `_load_pos_data_fields()` per-model, lihat `models/product.py`). Override
# lama SUDAH DIHAPUS dari sini (bukan cuma dibiarkan mati) karena kalau hook itu dipanggil lagi
# di versi Odoo mendatang, `super()._loader_params_product_product()` akan crash AttributeError.
# Field `minimum_sale_price`/`minimum_sale_price_with_tax` sekarang ditambahkan lewat
# `ProductProduct._load_pos_data_fields()` di `models/product.py`, bukan di sini lagi.
