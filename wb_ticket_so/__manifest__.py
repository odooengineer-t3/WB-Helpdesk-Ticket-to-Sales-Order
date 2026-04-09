# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

{
    "name": "Helpdesk Ticket to Sales Order",
    "version": "18.0.1.0.0",
    "summary": "Link Support Tickets to Sales Orders",
    "description": """Helpdesk Ticket to Sales Order module bridges the gap between customer support and sales 
            operations by seamlessly linking support tickets to sales orders. This module allows support teams to create 
            new sales orders directly from helpdesk tickets or link existing orders, ensuring complete traceability and 
            improved customer service. It automatically syncs chatter messages between tickets and orders, moves tickets 
            to a dedicated 'SO Generated' stage, and provides smart buttons for quick navigation. Designed for 
            businesses that want to convert support interactions into sales opportunities and maintain a unified view 
            of customer engagement across support and sales departments.
            """,
    "category": "Helpdesk",
    "author": "Wan Buffer Services",
    "depends": ["helpdesk", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/helpdesk_data.xml",
        "views/helpdesk_ticket_views.xml",
        "views/sale_order_views.xml",
        "wizard/link_so_wizard_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "images": ["static/description/background.png", ],
    "installable": True,
    "application": True,
    "website": "https://wanbuffer.com",
    "maintainer": "Wan Buffer Services",
    "support": "info@wanbuffer.com",
    "license": "OPL-1"
}
