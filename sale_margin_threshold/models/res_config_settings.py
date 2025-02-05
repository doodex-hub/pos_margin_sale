from odoo import _, api, fields, models



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_epson_printer_ip = fields.Char("POS Epson Printer IP", config_parameter="pos_margin_threshold.pos_epson_printer_ip")
    blocking_transaction_order = fields.Boolean("Blocking Transaction Order", config_parameter="post_margin_sale.blocking_transaction_order")
