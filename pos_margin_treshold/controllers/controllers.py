# -*- coding: utf-8 -*-
# from odoo import http


# class PosMarginSale(http.Controller):
#     @http.route('/pos_margin_treshold/pos_margin_treshold', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_margin_treshold/pos_margin_treshold/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_margin_treshold.listing', {
#             'root': '/pos_margin_treshold/pos_margin_treshold',
#             'objects': http.request.env['pos_margin_treshold.pos_margin_treshold'].search([]),
#         })

#     @http.route('/pos_margin_treshold/pos_margin_treshold/objects/<model("pos_margin_treshold.pos_margin_treshold"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_margin_treshold.object', {
#             'object': obj
#         })

