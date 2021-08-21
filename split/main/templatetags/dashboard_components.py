from django import template
from main import utils
from main import models

register = template.Library()



@register.inclusion_tag('dashboard_components/debts_small_card.html')
def debts_small_card(debts, user):
    user_debts = []
    for debt in debts:
        user_debts.append(utils.UserDebt(debt, user))
    return {
        'debts': user_debts,
        'user': user,
    }

@register.inclusion_tag('dashboard_components/group_row.html')
def group_row(group):
    memberships = models.Membership.objects.filter(group=group)
    expenses = models.Expense.objects.filter(group=group)
    return {
        'group': group,
        'members': memberships,
        'expenses_amount': expenses.total_amount(),
        'expenses_count': expenses.count(),
    }

@register.inclusion_tag('dashboard_components/expenses_small.html')
def expenses_card_small(expenses):
    return {
        'expenses': expenses,
    }

@register.inclusion_tag('dashboard_components/transaction_small.html')
def transactions_card_small(transactions, user):
    return {
        'transactions': transactions,
        'user': user,
    }
