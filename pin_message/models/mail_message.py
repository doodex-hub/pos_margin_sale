from odoo import models, fields, api
from odoo.addons.mail.tools.discuss import Store


class Message(models.Model):
    _inherit = 'mail.message'

    is_pinned = fields.Boolean(string='Pinned', default=False, index=True)

    def toggle_pin(self):
        for message in self:
            message.is_pinned = not message.is_pinned
            self.env['bus.bus']._sendone(
                f'{self._name},{message.id}',
                'mail.message/pin_changed',
                {
                    'id': message.id,
                    'is_pinned': message.is_pinned,
                }
            )
        return True

    def _store_message_fields(self, res: Store.FieldList, **kwargs):
        # 20.0: `_to_store(self, store, fields, **kwargs)` dihapus total dari core -- diganti pola
        # serializer field-list `_store_message_fields(self, res: Store.FieldList, **kwargs)`
        # (odoo20/addons/mail/models/mail_message.py:1177, tipe Store.FieldList didefinisikan di
        # odoo20/addons/mail/tools/discuss.py:830-963). Pola rewrite ini sama persis dengan dua
        # override native yang sudah jalan untuk kasus identik (tambah satu field ke store pesan
        # tanpa syarat): odoo20/addons/rating/models/mail_message.py dan
        # odoo20/addons/im_livechat/models/mail_message.py.
        super()._store_message_fields(res, **kwargs)
        res.attr("is_pinned")
