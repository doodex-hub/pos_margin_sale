from odoo import _, api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'


    margin_sale = fields.Float('Margin')
    

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    margin_sale = fields.Float(string="Margin", tracking=True, compute="_compute_margin_sale", store=True, readonly=False)
    minimum_sale_price = fields.Float(string="Minimum sale price", compute='_compute_minimum_sale_price', 
                                      inverse='_inverse_minimum_sale_price', store=True, readonly=False)
    minimum_sale_price_with_tax = fields.Float(string="Minimum sale price (Tax include)", compute='_compute_minimum_sale_price_with_tax', store=True)
    module_pos_margin_threshold = fields.Boolean(
    compute='_compute_module_pos_margin_threshold',
        store=False,
    )

    @api.depends_context('uid')
    def _compute_module_pos_margin_threshold(self):
        pos_margin_installed = self.env['ir.module.module'].search([
            ('name', '=', 'pos_margin_threshold'),
            ('state', '=', 'installed')
        ], limit=1)
        
        for record in self:
            record.module_pos_margin_threshold = bool(pos_margin_installed) 
            
    @api.depends('categ_id.margin_sale')
    def _compute_margin_sale(self):
        for rec in self:
            rec.margin_sale = rec.categ_id.margin_sale

    @api.depends('margin_sale', 'minimum_sale_price', 'taxes_id')
    def _compute_minimum_sale_price_with_tax(self):
        for rec in self:
            tax_amount = sum(tax.amount for tax in rec.taxes_id)
            rec.minimum_sale_price_with_tax = rec.minimum_sale_price * (1 + tax_amount / 100)

    @api.depends('margin_sale', 'standard_price')
    def _compute_minimum_sale_price(self):
        for rec in self:
            rec.minimum_sale_price = rec.standard_price * (1 + rec.margin_sale/100)
          
    def _inverse_minimum_sale_price(self):
        for rec in self:
            if rec.standard_price:
                rec.margin_sale = ((rec.minimum_sale_price / rec.standard_price) - 1) * 100
            else:
                rec.margin_sale = 0.0

    def action_assign_margin(self):
        wizard = self.env['wizard.margin.product'].create({
            'product_template_ids': [(6, 0, self.ids)]
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update margin sale'),
            'view_mode': 'form',
            'res_model': 'wizard.margin.product',
            'target': 'new',
            'res_id': wizard.id,
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    margin_sale = fields.Float(string="Margin", tracking=True, compute="_compute_margin_sale", inverse="_set_product_margin_sale", store=True, readonly=False)
    minimum_sale_price = fields.Float(string="Minimum sale price", compute="_compute_minimum_sale_price", inverse='_inverse_minimum_sale_price', store=True, readonly=False)
    is_less_minimum_sale = fields.Boolean(string="Less minimum price", compute="_compute_warning")

    @api.onchange('margin_sale')
    def _set_product_margin_sale(self):
        for rec in self:
            rec.product_tmpl_id.write({'margin_sale': rec.margin_sale})

    def _compute_warning(self):
        for rec in self:
            rec.is_less_minimum_sale = rec.lst_price < rec.minimum_sale_price

    @api.depends('categ_id.margin_sale', 'product_tmpl_id.margin_sale')
    def _compute_margin_sale(self):
        for record in self:
            record.margin_sale = record.product_tmpl_id.margin_sale
    
    @api.depends('margin_sale', 'standard_price')
    def _compute_minimum_sale_price(self):
        for rec in self:
            rec.minimum_sale_price = rec.standard_price * (1 + rec.margin_sale/100)

    def _inverse_minimum_sale_price(self):
        for rec in self:
            if rec.standard_price:
                rec.margin_sale = ((rec.minimum_sale_price / rec.standard_price) - 1) * 100
            else:
                rec.margin_sale = 0.0

    def action_assign_margin(self):
        wizard = self.env['wizard.margin.product'].create({
            'product_ids': [(6, 0, self.ids)]
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update margin sale'),
            'view_mode': 'form',
            'res_model': 'wizard.margin.product',
            'target': 'new',
            'res_id': wizard.id,
        }

    def _get_view(self, view_id=None, view_type='list', **options):
        # MF-37/MF-29: Product Variants list gets margin_sale/minimum_sale_price columns from
        # this module AND from pos_margin_threshold (both inherit the same native
        # product.product_product_tree_view, same field names since it is the same field on
        # product.product). column_invisible cannot reference plain record fields (Odoo
        # evaluates it without record context, confirmed empirically: "Name
        # 'module_pos_margin_threshold' is not defined") and invisible only blanks list cells,
        # not the column header, so the dedup decided at MF-29 needs to happen here in Python
        # instead of in the view arch: strip this module's own columns from the FINAL MERGED
        # arch when pos_margin_threshold is installed, leaving that module's columns as the
        # only ones rendered. `view` here is the base/requested view record (e.g. the native
        # product.product_product_tree_view itself), NOT either inheriting delta view, so the
        # dedup cannot be gated on view.id — it must run whenever this model's list arch is
        # built, and select the nodes to strip via the class="o_smt_dedup_*" marker (both
        # modules add a field literally named margin_sale/minimum_sale_price, so field name
        # alone cannot tell the two modules' nodes apart in the merged arch).
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'list' and self._name == 'product.product':
            pos_margin_installed = self.env['ir.module.module'].sudo().search([
                ('name', '=', 'pos_margin_threshold'),
                ('state', '=', 'installed'),
            ], limit=1)
            if pos_margin_installed:
                for node in arch.xpath(
                    "//field[@name='margin_sale'][contains(@class, 'o_smt_dedup_margin')]"
                    " | //field[@name='minimum_sale_price'][contains(@class, 'o_smt_dedup_min_price')]"
                ):
                    node.getparent().remove(node)
        return arch, view

    @api.model
    def _register_hook(self):
        super()._register_hook()
        
        
        group = self.env.ref('sale_margin_threshold.group_sale_margin_action', raise_if_not_found=False)
        if group:
            pos_margin_installed = self.env['ir.module.module'].search([
                ('name', '=', 'pos_margin_threshold'),
                ('state', '=', 'installed')
            ], limit=1)
            
            if pos_margin_installed:
                group.user_ids = [(5, 0, 0)]  # Remove all users
            else:
                internal_users = self.env.ref('base.group_user').user_ids
                group.user_ids = [(6, 0, internal_users.ids)]
    