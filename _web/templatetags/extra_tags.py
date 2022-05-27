from django import template
from _web.models import main_site
from _web.models import footer

register = template.Library()


@register.filter(name='keyvalue')
def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        return ''


@register.filter(name='organisation_name')
def organisation_name(dummy):
    _site = main_site.objects.order_by('-site_id')[0]
    return _site.site_name_en


@register.filter(name='organisation_logo')
def organisation_logo(dummy):
    _site = main_site.objects.order_by('-site_id')[0]
    return _site.site_logo.url


@register.filter(name='site_version')
def site_version(dummy):
    _footer = footer.objects.order_by('-footer_id')[0]
    return _footer.footer_version


@register.filter(name='site_year')
def site_year(dummy):
    _footer = footer.objects.order_by('-footer_id')[0]
    return _footer.footer_year

