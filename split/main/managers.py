from django.db import models
from django.db.models import Q, Sum

def get_total_amount(queryset):
    try:
        value = round(queryset.aggregate(total=Sum('amount'))['total'], 2)
        return value
    except:
        return 0
        
class DebtQuerySet(models.QuerySet):
    # debt associated with user_a and user_b    
    def get_by_users(self, user_a, user_b):
        return self.get(
            (Q(debtor=user_a) & Q(creditor=user_b)) |
            (Q(debtor=user_b) & Q(creditor=user_a))
        )

    def filter_by_user(self, user):
        return self.filter(Q(debtor=user)|Q(creditor=user))

    def balance(self, user):
        debts = self.filter_by_user(user)
        total = 0
        for debt in debts:
            total += debt.get_balance(user)
        return round(total, 2)

class TransactionQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        return self.filter(Q(sender=user)|Q(receiver=user))

    def filter_by_user_flag(self, user, private=True):
        if private:
            return self.filter_by_user(user).filter(expense__isnull=True)
        return self.filter_by_user(user).filter(expense__isnull=False)
    
    def filter_by_users(self, user, other_user):
        return self.filter((Q(sender=user) & Q(receiver=other_user))|
        (Q(sender=other_user) & Q(receiver=user)))
    
    # private flag refers to transactions not linked to expenses
    def filter_by_users_flag(self, user, other_user, private=True):
        if private:
            return self.filter_by_users(user, other_user).filter(expense__isnull=True)
        return self.filter_by_users(user, other_user).filter(expense__isnull=False)

    # return daily amount (total)
    # queryset['total']
    def daily_total(self, is_private=False):
        if is_private:
            transactions = self.self.order_by('transactioninfo__created_at')
            transactions = transactions.values('transactioninfo__created_at__date').annotate(total=Sum('amount')).order_by()
        else:
            transactions = self.order_by('expense__created_at')
            transactions = transactions.values('expense__created_at__date').annotate(total=Sum('amount')).order_by()
        return transactions

    def total_amount(self):
        return get_total_amount(self)

class ExpenseQuerySet(models.QuerySet):

    def filter_by_user(self, user):
        return self.filter(group__membership__user=user)

    def total_amount(self):
        return get_total_amount(self)

    # return daily amount (total)
    # queryset['total']
    def daily_total(self):
        expenses = self.order_by('created_at')
        expenses = expenses.values('created_at__date').annotate(total=Sum('amount')).order_by()
        return expenses







