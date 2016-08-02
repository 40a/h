# -*- coding: utf-8 -*-

from functools import partial

from jinja2 import Markup
from pyramid.request import Request

from h import __version__
from h import emails
from h import mailer
from h.api import storage
from h.notification import reply

def render_view(request, name):
    """
    Helper for rendering a view within another view.

    This can be used to render a reusable widget across multiple pages or share
    a widget

    The rendered sub-view will use the same cookies, host and other properties
    as the parent request.

    :param name: The name of the route to render
    """

    # Copy the original request to inherit the authenticated user, host and
    # other attributes.
    #
    # Adapted from http://stackoverflow.com/a/24199503/434243
    req = request.copy_get()
    req.path_info = request.route_path(name)
    response = request.invoke_subrequest(req, use_tweens=True)
    return Markup(response.ubody)


def add_renderer_globals(event):
    request = event['request']

    event['h_version'] = __version__
    event['base_url'] = request.route_url('index')
    event['feature'] = request.feature

    # Add Google Analytics
    ga_tracking_id = request.registry.settings.get('ga_tracking_id')
    if ga_tracking_id is not None:
        event['ga_tracking_id'] = ga_tracking_id
        if 'localhost' in request.host:
            event['ga_cookie_domain'] = "none"
        else:
            event['ga_cookie_domain'] = "auto"

    # Add a helper which can be used to render reusable views in the middle of
    # another response
    event['render_view'] = partial(render_view, request)


def publish_annotation_event(event):
    """Publish an annotation event to the message queue."""
    data = {
        'action': event.action,
        'annotation_id': event.annotation_id,
        'src_client_id': event.request.headers.get('X-Client-Id'),
    }
    if event.annotation_dict:
        data['annotation_dict'] = event.annotation_dict

    event.request.realtime.publish_annotation(data)


def send_reply_notifications(event,
                             get_notification=reply.get_notification,
                             generate_mail=emails.reply_notification.generate,
                             send=mailer.send.delay):
    """Queue any reply notification emails triggered by an annotation event."""
    request = event.request
    annotation = storage.fetch_annotation(event.request.db, event.annotation_id)
    action = event.action
    try:
        notification = get_notification(request, annotation, action)
        if notification is None:
            return
        send_params = generate_mail(request, notification)
        send(*send_params)
    # We don't want any exceptions thrown by this code to cause the annotation
    # CRUD action to fail, but we do want to collect the error in Sentry, so we
    # explicitly wrap this here.
    #
    # FIXME: Fix the underlying bugs and remove this try/except.
    except Exception:
        event.request.sentry.captureException()
        if event.request.debug:
            raise
