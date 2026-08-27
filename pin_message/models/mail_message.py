from odoo import models, fields, api


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

    def _to_store(self, store, fields, **kwargs):
        # 18.0: field ke frontend TIDAK LAGI diambil lewat Chatter.load() dengan
        # messageFields custom (mekanisme itu sudah dihapus, lihat MF-xx) -- pindah ke
        # override _to_store() ini, dipanggil server-side setiap message diserialisasi ke
        # frontend (chatter, discuss, dst).
        # 19.0: `fields` jadi parameter positional wajib di core (dulu keyword-only
        # opsional) -- diteruskan apa adanya ke super(), tidak pernah dipakai langsung
        # di sini karena is_pinned selalu ditambahkan tanpa syarat.
        super()._to_store(store, fields, **kwargs)
        # 19.0: store.add(message, {...}) sekarang selalu re-entry ke _to_store() (tidak ada
        # lagi jalur pintas "raw values dict" seperti 18.0) -- akan infinite-recurse kalau
        # dipanggil dari sini. store.add_records_fields() adalah API 19.0 yang eksplisit
        # dibuat untuk menambah field dari dalam _to_store() tanpa re-trigger (dipakai core
        # sendiri, mis. mail_message.py/discuss_channel.py).
        store.add_records_fields(self, ['is_pinned'])
