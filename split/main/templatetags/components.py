from django import template
import json
from main import utils

register = template.Library()


@register.inclusion_tag('chart.html')
def chart_card(dict, id, icon):
    dict['id'] = str(id)
 
    
    return {
        'value': dict['value'],
        'title': dict['title'],
        'json': json.dumps(dict),
        'id': id, 
        'icon': icon,

    }

@register.inclusion_tag('value_card.html')
def value_card(title, icon, value, footer, footer_value, clickable=False):
    return {
        'title': title,
        'icon': icon,
        'value': value,
        'footer': footer,
        'footer_value': footer_value,
        'clickable': 'clickable' if clickable else ''

    }

@register.inclusion_tag('debts_small_card.html')
def debts_small_card(debts, user):
    user_debts = []
    for debt in debts:
        user_debts.append(utils.UserDebt(debt, user))
    return {
        'debts': user_debts,
        'user': user,
    }

@register.inclusion_tag('expenses_small.html')
def expenses_card_small(expenses):
    return {
        'expenses': expenses,
    }

@register.inclusion_tag('transaction_small.html')
def transactions_card_small(transactions, user):
    return {
        'transactions': transactions,
        'user': user,
    }

@register.simple_tag()
def you_or_name(user, other):
    if user.id == other.id:
        return 'You'
    return other

