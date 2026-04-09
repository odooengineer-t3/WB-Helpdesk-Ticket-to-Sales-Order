# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import models, fields, api, _
from markupsafe import Markup

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Originating Ticket',
        readonly=True,
        help="Support Ticket that generated this Sales Order.",
        copy=False
    )

    def message_post(self, **kwargs):
        """
        Override to sync chatter messages from Sale Order to the linked Helpdesk Ticket.
        Wraps content in Markup to prevent HTML escaping.
        """
        message = super().message_post(**kwargs)
        for order in self:
            if order.helpdesk_ticket_id:
                body = kwargs.get('body')
                subtype_xmlid = kwargs.get('subtype_xmlid')
                subtype_id = kwargs.get('subtype_id')
                tracking_value_ids = kwargs.get('tracking_value_ids')
                
                # If no body and no specific subtype/tracking, skip (likely internal noise)
                if not body and not subtype_xmlid and not subtype_id and not tracking_value_ids:
                    continue
                
                # Ensure body is treated as safe HTML if it's not already Markup
                if body and not isinstance(body, Markup):
                    body = Markup(body)
                elif not body:
                    body = Markup("")

                # Prepare safe HTML prefix
                prefix = Markup(_("<strong>Log from %s:</strong><br/>")) % order._get_html_link()
                
                # Combine prefix with body
                new_body = prefix + body
                
                order.helpdesk_ticket_id.message_post(
                    body=new_body,
                    subject=kwargs.get('subject'),
                    message_type=kwargs.get('message_type', 'notification'),
                    subtype_xmlid=subtype_xmlid,
                    subtype_id=subtype_id,
                    attachment_ids=kwargs.get('attachment_ids'),
                )
        return message

    @api.model_create_multi
    def create(self, vals_list):
        """Override to log creation on linked ticket and move stage."""
        orders = super().create(vals_list)
        for order in orders:
            if order.helpdesk_ticket_id:
                order.helpdesk_ticket_id._move_to_so_generated_stage()
                msg = Markup(_("Sales Order created: %s")) % order._get_html_link()
                order.helpdesk_ticket_id.message_post(body=msg, subtype_xmlid='mail.mt_note')
        return orders

    def write(self, vals):
        """Override to log linking actions on linked ticket."""
        res = super().write(vals)
        if 'helpdesk_ticket_id' in vals and vals['helpdesk_ticket_id']:
            for order in self:
                if order.helpdesk_ticket_id:
                    order.helpdesk_ticket_id._move_to_so_generated_stage()
                    msg = Markup(_("Sales Order linked: %s")) % order._get_html_link()
                    order.helpdesk_ticket_id.message_post(body=msg, subtype_xmlid='mail.mt_note')
        return res

    def action_cancel(self):
        """Override to log cancellation on linked ticket."""
        res = super().action_cancel()
        for order in self:
            if order.helpdesk_ticket_id:
                msg = Markup(_("Sales Order cancelled: %s")) % order._get_html_link()
                order.helpdesk_ticket_id.message_post(body=msg, subtype_xmlid='mail.mt_note')
        return res

    def unlink(self):
        """Override to log deletion on linked ticket."""
        for order in self:
            if order.helpdesk_ticket_id:
                msg = Markup(_("Sales Order deleted: %s")) % order.name
                order.helpdesk_ticket_id.message_post(body=msg, subtype_xmlid='mail.mt_note')
        return super().unlink()
