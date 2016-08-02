# -*- coding: utf-8 -*-


def includeme(config):
    config.include('h.views.exceptions')
    config.include('h.views.help')
    config.include('h.views.home')
    config.include('h.views.main')
    config.include('h.views.client')
    config.include('h.views.widgets')

    # homepage
    config.add_route('index', '/')
    config.add_route('via_redirect', '/via')

    # client
    config.add_route('token', '/api/token')
    config.add_route('embed', '/embed.js')
    config.add_route('widget', '/app.html')

    # help
    config.add_route('help', '/docs/help')
    config.add_route('onboarding', '/welcome/')
    config.add_route('custom_onboarding', '/welcome/{slug}')

    # shared widgets
    config.add_route('widgets.navbar', '/widgets/navbar')

    # main
    config.add_route('annotation',
                     '/a/{id}',
                     factory='h.api.resources:AnnotationFactory',
                     traverse='/{id}')
    config.add_route('robots', '/robots.txt')
    config.add_route('session', '/app')
    config.add_route('stream', '/stream')
    config.add_route('stream.user_query', '/u/{user}')
    config.add_route('stream.tag_query', '/t/{tag}')
