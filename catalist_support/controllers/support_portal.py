# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        support_center = request.env['support.center']
        if 'ticket_count' in counters:
            values['ticket_count'] = support_center.search_count([
                ('customer_contact_id', '=', partner.id)
            ]) if support_center.check_access_rights(
                'read', raise_exception=False) else 0
        if 'current_ticket_count' in counters:
            values['current_ticket_count'] = support_center.search_count([
                ('customer_contact_id', '=', partner.id),
                ('state', 'not in', ['delivered', 'completed'])
            ]) if support_center.check_access_rights(
                'read', raise_exception=False) else 0
        return values

    @http.route(['/my/tickets/open'], type='http', auth="user", website=True)
    def portal_my_open_tickets(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        support_center = request.env['support.center']

        domain = [('customer_contact_id', '=', partner.id),
                  ('state', 'not in', ['delivered', 'completed'])]

        # count for pager
        current_ticket_count = support_center.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/tickets/open",
            total=current_ticket_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        ticket_ids = support_center.search(
            domain, order='date_received desc, name asc',
            limit=self._items_per_page, offset=pager['offset'])
        new_ticket_available = 0
        if partner.parent_id.id:
            new_ticket_available = 1

        values.update({
            'ticket_ids': ticket_ids,
            'new_ticket_available': new_ticket_available,
            'page_name': 'open ticket',
            'pager': pager,
            'default_url': '/my/tickets/open',
        })
        return request.render("catalist_support.portal_my_open_tickets", values)

    @http.route(['/my/tickets'], type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        support_center = request.env['support.center']

        domain = [('customer_contact_id', '=', partner.id)]

        # count for pager
        ticket_count = support_center.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/tickets",
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        ticket_ids = support_center.search(
            domain, order='date_received desc, name asc',
            limit=self._items_per_page, offset=pager['offset'])
        new_ticket_available = 0
        if partner.parent_id.id:
            new_ticket_available = 1

        values.update({
            'ticket_ids': ticket_ids,
            'new_ticket_available': new_ticket_available,
            'page_name': 'ticket',
            'pager': pager,
            'default_url': '/my/tickets',
        })
        return request.render("catalist_support.portal_my_tickets", values)

    @http.route(['/my/tickets/<int:ticket_id>'], type='http', auth="user", website=True)
    def ticket_detail_page(self, ticket_id, **kwargs):
        ticket_id = request.env['support.center'].search(
            [('id', '=', ticket_id)])
        return request.render("catalist_support.portal_ticket_details", {
            'ticket_id': ticket_id
        })

    @http.route(['/ticket/new'], type='http', auth="user", website=True)
    def new_ticket_form(self, **kwargs):
        return request.render("catalist_support.portal_template")

    @http.route(['/ticket/new/submit'], type='http', auth="user", website=True)
    def new_ticket_form_submit(self, **kwargs):
        print(kwargs, kwargs.get('name'))
        request.env['support.center'].create({
            'name': kwargs.get('name'),
            'issue_description': kwargs.get('issue_description'),
            'date_received': datetime.now(),
            'customer_id': request.env.user.partner_id.parent_id.id,
            'customer_contact_id': request.env.user.partner_id.id,
        })
        return request.redirect('/my/tickets/open')
