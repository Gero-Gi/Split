from django import template
import json
from main import utils
from main import models

register = template.Library()


@register.inclusion_tag('components/chart.html')
def chart_card(dict, id, icon, spent=False):
    dict['id'] = str(id)
    dict['spent'] = spent

    return {
        'value': dict['value'],
        'title': dict['title'],
        'subtitle': dict['subtitle'],
        'json': json.dumps(dict),
        'id': id,
        'spent': spent,
        'icon': icon,
    }


@register.simple_tag()
def you_or_name(user, other):
    if user.id == other.id:
        return 'You'
    return other


@register.simple_tag()
def get_memberships(group, count=False):
    m = models.Membership.objects.filter(group=group)
    if count:
        return m.count()
    return m


@register.inclusion_tag('components/value_card.html')
def value_card(title, icon, value, footer, footer_value, clickable=False):
    return {
        'title': title,
        'icon': icon,
        'value': value,
        'footer': footer,
        'footer_value': footer_value,
        'clickable': 'clickable' if clickable else ''

    }


@register.inclusion_tag('components/modal_form.html')
def modal_form(form_name, title, text, value=''):
    return {
        'form_name': form_name,
        'id': '{}{}'.format(form_name, value),
        'title': title,
        'text': text,
        'value': value,
    }
