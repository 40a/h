# -*- coding: utf-8 -*-

"""Shared widgets used across multiple pages on the site."""

from __future__ import unicode_literals

from pyramid.view import view_config

@view_config(route_name='widgets.navbar',
             request_method='GET',
             renderer='h:templates/widgets/navbar.html.jinja2')
def navbar(context, request):
    """
    The navigation bar displayed at the top of the page.
    """

    groups_menu_items = []
    stream_url = None
    username = None

    if request.authenticated_user:
        for group in request.authenticated_user.groups:
            groups_menu_items.append({
                'title': group.name,
                'link': request.route_url('group_read', pubid=group.pubid, slug=group.slug)
                })
        stream_url = (request.route_url('activity.search') +
            "?q=user:{}".format(request.authenticated_user.username))
        username = request.authenticated_user.username

    return {
        'settings_menu_items': [
            {'title': 'Account details', 'link': request.route_url('account')},
            {'title': 'Notifications', 'link': request.route_url('account_notifications')},
            {'title': 'Developer', 'link': request.route_url('account_developer')},
        ],
        'signout_item': {'title': 'Sign out', 'link': request.route_url('logout')},
        'groups_menu_items': groups_menu_items,
        'username': username,
        'username_link': stream_url,
    }


def includeme(config):
    config.scan(__name__)
