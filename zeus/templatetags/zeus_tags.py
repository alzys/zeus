import json

from functools import partial

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import Template

register = template.Library()


def _confirm_action(context, label, url, confirm_msg="", icon="",
                    method="POST", cls="", extra_cls="", disabled=False,
                    inline=False):

    form_cls = ""

    if not confirm_msg:
        confirm_msg = _("Are you sure ?")

    if icon == "remove" and cls == "":
        cls += " alert"

    if inline:
        form_cls += " inline"

    confirm_msg = unicode(confirm_msg)
    confirm_msg = Template(confirm_msg).render(context)
    confirm_msg = confirm_msg.replace('\n', ' ');

    confirm_code = """onsubmit="return confirm('%s');" """ % confirm_msg
    if "noconfirm" in cls:
        confirm_code = ""

    onclick = ""
    if not disabled:
        onclick = ("""onclick="$(this).closest('form').submit(); """
                   """return false" """)
    else:
        cls += " disabled"


    csrf_token = ""
    if 'csrf_token' in context:
        csrf_token = """<input type="hidden" """ + \
                     """value="%s" """ % context['csrf_token'] + \
                     """name="csrfmiddlewaretoken" />"""
    if "nocsrf" in cls:
        csrf_token = ""

    html = """
    <form action="%(url)s" method="%(method)s" class="action-form %(form_cls)s"
     %(confirm_code)s>
     %(csrf_token)s
    <a href="#" %(onclick)s
    class="button foundicon-%(icon)s %(cls)s %(extra_cls)s"> &nbsp;%(label)s</a>
    </form>
    """ % {
        'label': label,
        'url': url,
        'cls': cls,
        'extra_cls': extra_cls,
        'icon': icon,
        'method': method,
        'form_cls': form_cls,
        'confirm_code': confirm_code,
        'confirm_msg': confirm_msg,
        'csrf_token': csrf_token,
        'onclick': onclick
    }
    return html


def _action(context, label, url, icon="", cls="", extra_cls="",
            tag_content="", disabled=False):

    if disabled:
        cls += " disabled"
        if "onclick" in tag_content:
            tag_content = ""

    if not url:
        url = "#"

    if not "nobutton" in cls:
        cls += " button"

    html = """
    <a class="%(extra_cls)s %(cls)s foundicon-%(icon)s"
       href="%(url)s" %(tag_content)s> &nbsp;%(label)s</a>
    """ % {
        'label': label,
        'url': url,
        'icon': icon,
        'cls': cls,
        'extra_cls': extra_cls,
        'tag_content': tag_content
    }
    return html


@register.simple_tag(takes_context=True)
def action(context, *args, **kwargs):
    return _action(context, *args, **kwargs)


@register.simple_tag(takes_context=True)
def small_action(context, *args, **kwargs):
    kwargs['extra_cls'] = 'small'
    return _action(context, *args, **kwargs)


@register.simple_tag(takes_context=True)
def medium_action(context, *args, **kwargs):
    kwargs['extra_cls'] = 'medium'
    return _action(context, *args, **kwargs)


@register.simple_tag(takes_context=True)
def confirm_action(context, *args, **kwargs):
    return _confirm_action(context, *args, **kwargs)


@register.simple_tag(takes_context=True)
def small_confirm_action(context, *args, **kwargs):
    kwargs['extra_cls'] = 'small'
    return _confirm_action(context, *args, **kwargs)


@register.simple_tag(takes_context=True)
def medium_confirm_action(context, *args, **kwargs):
    kwargs['cls'] = 'medium'
    return _confirm_action(context, *args, **kwargs)


@register.simple_tag(takes_context=True)
def menu_action(context, label, url, icon="", cls=""):
    html = """
    <li>
    <a class="foundicon-%(icon)s"
       href="%(url)s"> &nbsp;%(label)s
    </a>
    </li>
    """ % {
        'label': label,
        'url': url,
        'icon': icon
    }
    return html


@register.simple_tag(takes_context=True)
def menu_confirm_action(context, label, url, confirm_msg="", icon="",
                        method="POST", cls=""):
    if not confirm_msg:
        confirm_msg = _("Are you sure ?")

    if icon == "remove" and cls == "":
        cls += " alert"

    confirm_msg = unicode(confirm_msg)
    confirm_msg = Template(confirm_msg).render(context)
    confirm_msg = confirm_msg.replace('\n', ' ')

    icon_cls = ""
    if icon:
        icon_cls = "foundicon-%s" % icon

    confirm_code = """onsubmit="return confirm('%s');" """ % confirm_msg
    if "noconfirm" in cls:
        confirm_code = ""

    csrf_token = ""
    if 'csrf_token' in context:
        csrf_token = """<input type="hidden" """ + \
                     """value="%s" """ % context['csrf_token'] + \
                     """name="csrfmiddlewaretoken" />"""
    if "nocsrf" in cls:
        csrf_token = ""

    html = """
    <li>
    <form action="%(url)s" method="%(method)s" class="action-form"
    %(confirm_code)s>
    %(csrf_token)s
    <a href="#" onclick="$(this).closest('form').submit(); return false"
    class="%(icon)s %(cls)s"> &nbsp;%(label)s</a>
    </form>
    </li>
    """ % {
        'label': label,
        'url': url,
        'cls': cls,
        'icon': icon_cls,
        'method': method,
        'confirm_code': confirm_code,
        'confirm_msg': confirm_msg,
        'csrf_token': csrf_token
    }
    return html


@register.simple_tag(takes_context=True)
def reveal_action(context, label, selector, icon="", cls="", disabled=False):
    params = {
        'animationSpeed': 100
    }
    jsparams = json.dumps(params).replace("\"", "&quot;")
    js_content = """$('%(selector)s').reveal(%(jsparams)s);""" % {
        'selector': selector,
        'jsparams': jsparams
    }
    tag_content = """onclick="%(js_content)s return false;" """ % {
        'js_content': js_content
    }
    action_html = _action(context, label, "", icon, cls, disabled=disabled,
                          tag_content=tag_content)
    return action_html


@register.filter
def negate(value):
    return not value


@register.simple_tag(takes_context=True)
def set_election_issues(context, election):
    context['election_issues_list'] = \
        election.election_issues_before_freeze
    context['polls_issues_list'] = \
        election.polls_issues_before_freeze
    return ''


@register.simple_tag
def complete_voter_get_parameters(GET, new_order):
    page_param = ''
    page = GET.get('page', None)
    if page:
        page_param += "&page=%s"%page
    order_by = GET.get('order', 'voter_login_id')
    order_type = GET.get('order_type', 'asc')
    order_param = ''
    if order_by == new_order:
        if order_type == 'asc':
            new_order_type = 'desc'
        else:
            new_order_type = 'asc'
    else:
        new_order_type = 'asc'
    order_param = '&order_type=%s' % new_order_type
    params = '%s%s' % (page_param, order_param)
    return params
