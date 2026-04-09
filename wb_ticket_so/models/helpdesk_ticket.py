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
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_order_ids = fields.One2many(
        'sale.order',
        'helpdesk_ticket_id',
        string='Sales Orders'
    )
    so_count = fields.Integer(compute='_compute_so_count', string="Sales Orders")

    @api.depends('sale_order_ids')
    def _compute_so_count(self):
        for ticket in self:
            ticket.so_count = len(ticket.sale_order_ids)

    def action_create_sale_order(self):
        """Action to trigger creation of a new SO linked to this ticket."""
        self.ensure_one()
        return {
            'name': _('Create Sales Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'context': {
                'default_helpdesk_ticket_id': self.id,
                'default_origin': self.name,
                'default_partner_id': self.partner_id.id,
            },
        }

    def action_view_sale_orders(self):
        """Action to view the list of linked Sales Orders."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        if self.so_count > 1:
            action['domain'] = [('id', 'in', self.sale_order_ids.ids)]
            action['view_mode'] = 'list,form'
        else:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.sale_order_ids.id
            action['view_mode'] = 'form'
            
        action['context'] = {'default_helpdesk_ticket_id': self.id}
        return action

    def action_link_existing_so(self):
        self.ensure_one()
        return {
            'name': _('Link Existing Sales Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'wb.link.so.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_ticket_id': self.id},
        }

    def _move_to_so_generated_stage(self):
        """Finds a stage named 'SO Generated' and moves the ticket there."""
        stage = self.env['helpdesk.stage'].search([('name', '=', 'SO Generated')], limit=1)
        
        if stage:
            # Check if stage is linked to team. If not, link and resort.
            if self.team_id:
                # If the team has specific stages, we must ensure ours is one of them
                if self.team_id.stage_ids:
                    if stage.id not in self.team_id.stage_ids.ids:
                         self.team_id.write({'stage_ids': [(4, stage.id)]})
                else:
                    # If team has no specific stages (using default/global), 
                    # we usually don't need to do anything unless the stage itself is restricted to other teams.
                    # But to be safe, if the stage has team_ids set and ours isn't in it, we might need to add it.
                    if stage.team_ids and self.team_id.id not in stage.team_ids.ids:
                         stage.write({'team_ids': [(4, self.team_id.id)]})

            # Move the ticket to the stage
            if self.stage_id != stage:
                self.write({'stage_id': stage.id})
