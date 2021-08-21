from django import template
from main import utils
from main import models
import json

register = template.Library()


@register.inclusion_tag('group_components/card.html')
def card():
    return{}


@register.inclusion_tag('components/base_chart.html')
def spent_chart(transactions, id, title, subtitle, icon, spent=False):
    ctx = utils.get_spent_chart(transactions)
    ctx['id'] = id
    ctx['spent'] = spent
    ctx['json'] = json.dumps(ctx)
    ctx['title'] = title
    ctx['subtitle'] = subtitle
    ctx['icon'] = icon

    return ctx


@register.inclusion_tag('group_components/expense_row.html')
def expense_row(expense, user):
    can_delete = models.Membership.objects.filter(group=expense.group).get(
        user=user).is_admin or expense.created_by.id == user.id

    return{
        'e': expense,
        'can_delete': can_delete,
        'user': user,
    }


@register.inclusion_tag('group_components/member_row.html')
def member_row(membership, user):
    debt = models.Debt.objects.get_by_users(membership.user, user)
    group_admin = models.Membership.objects.filter(
        group=membership.group).get(user=user).is_admin
    return {
        'd': utils.UserDebt(debt, user),
        'expenses_num': models.Expense.objects.filter(group=membership.group).filter(created_by=membership.user).count(),
        'is_admin': membership.is_admin,
        'joined': membership.joined_at,
        'group_admin': group_admin,
    }
