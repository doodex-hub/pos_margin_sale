from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class Message(models.Model):
    _inherit = 'mail.message'

    is_pinned = fields.Boolean(string='Pinned', default=False)

    def toggle_pin(self):
        """Toggle the pin status of the given messages."""
        for message in self:
            message.is_pinned = not message.is_pinned
            _logger.info(f"Message {message.id} pin toggled to: {message.is_pinned}")
        return True
        
    def _message_format(self, fnames=None, format_reply=True, legacy=False):
        """Override to add is_pinned to the message format."""
        vals_list = super()._message_format(fnames=fnames, format_reply=format_reply, legacy=legacy)
        
        messages_dict = {message.id: message for message in self}
        for vals in vals_list:
            message_id = vals['id']
            message = messages_dict.get(message_id)
            if message:
                vals['is_pinned'] = message.is_pinned
                
        return vals_list