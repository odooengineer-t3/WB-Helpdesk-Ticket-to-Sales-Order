# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import UserError

class LinkSOWizard(models.TransientModel):
    _name = 'wb.link.so.wizard'
    _description = 'Wizard to Link Existing Sales Orders'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True, readonly=True)
    sale_order_ids = fields.Many2many(
        'sale.order', 
        string='Sales Orders', 
        required=True,
        domain="[('helpdesk_ticket_id', '=', False), ('state', '!=', 'cancel')]"
    )

    def action_link_so(self):
        """
        Links the selected sales orders to the ticket.
        Also explicitly checks for prior linking to be safe.
        """
        self.ensure_one()
        
        if not self.sale_order_ids:
             raise UserError(_("Please select at least one Sales Order to link."))

        for so in self.sale_order_ids:
            if so.helpdesk_ticket_id:
                 raise UserError(_("Sales Order %s is already linked to ticket %s.") % (so.name, so.helpdesk_ticket_id.name))
        
        # Link the SOs
        self.sale_order_ids.write({'helpdesk_ticket_id': self.ticket_id.id})
        
        # Trigger stage move if needed
        self.ticket_id._move_to_so_generated_stage()
        
        return {'type': 'ir.actions.act_window_close'}
