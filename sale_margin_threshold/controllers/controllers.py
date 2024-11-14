# -*- coding: utf-8 -*-
# from odoo import http


# class PosMarginSale(http.Controller):
#     @http.route('/sale_margin_treshold/sale_margin_treshold', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_margin_treshold/sale_margin_treshold/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_margin_treshold.listing', {
#             'root': '/sale_margin_treshold/sale_margin_treshold',
#             'objects': http.request.env['sale_margin_treshold.sale_margin_treshold'].search([]),
#         })

#     @http.route('/sale_margin_treshold/sale_margin_treshold/objects/<model("sale_margin_treshold.sale_margin_treshold"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_margin_treshold.object', {
#             'object': obj
#         })

