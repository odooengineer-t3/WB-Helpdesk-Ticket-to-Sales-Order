# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    """
    Forcefully add the 'SO Generated' stage to all existing Helpdesk Teams
    to ensure consistent sorting and visibility.
    """
    # Retrieve the stage by its XML ID
    stage = env.ref('wb_ticket_so.stage_so_generated', raise_if_not_found=False)
    if not stage:
        return

    stage.write({
        'name': 'SO Generated',
        'fold': False
    })
    
    # Target stages to place 'SO Generated' BEFORE
    targets = ['Solved', 'Cancelled']

    # Find all Helpdesk Teams
    teams = env['helpdesk.team'].search([])
    
    for team in teams:
        # Get current stages as a list of IDs to preserve/manipulate order
        # We fetch the recordset, but we need to work with the list of records to reorder them
        current_stages = list(team.stage_ids)
        
        # If SO Generated is not in the list, add it
        if stage not in current_stages:
            current_stages.append(stage)
        
        # Now find the insertion point
        insert_index = len(current_stages) - 1 # Default to end
        
        for i, s in enumerate(current_stages):
            if s.name in targets:
                insert_index = i
                break
        
        # Remove stage from current position and insert at target
        if stage in current_stages:
            current_stages.remove(stage)
            current_stages.insert(insert_index, stage)
            
        # Re-assign the sequence numbers based on this new explicit order
        # This ensures persistence even if Odoo re-sorts by sequence later
        for idx, s in enumerate(current_stages):
            s.write({'sequence': idx + 1})

        # Write the explicitly ordered list back to the team
        # Using (6, 0, ids) forces this exact order
        team.write({'stage_ids': [(6, 0, [s.id for s in current_stages])]})
