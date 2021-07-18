from . import models
from django.db.models import Sum
from django.db.models.functions import TruncDay
from datetime import datetime

def get_expenses_by_user(user):
    memberships = models.Membership.objects.filter(user=user)
    querysets = []
    # retrieve all expenses in each group
    for m in memberships:
        querysets.append(models.Expense.objects.filter(group=m.group))
    expenses = querysets.pop()
    # merge all expenses in one queryset object
    for queryset in querysets:
        expenses.union(queryset)
    return expenses
   
def get_expenses_chart(expenses):
    labels = []
    data = []

    queryset = expenses.order_by('created_at')
    queryset = queryset.values('created_at__date').annotate(total=Sum('amount')).order_by()
    for expense in queryset:
        labels.append(expense['created_at__date'].__str__())
        data.append(expense['total'])

    sum = expenses.aggregate(sum=Sum('amount')).get('sum')

    return {
        'labels': labels,
        'data': data,
        'value': sum,
        'title': 'Expenses'
    }

def get_private_transactions_chart(transactions):
    labels = []
    data = []

    queryset = transactions.order_by('transactioninfo__created_at')
    queryset = queryset.values('transactioninfo__created_at__date').annotate(total=Sum('amount')).order_by()
    for expense in queryset:
        labels.append(expense['transactioninfo__created_at__date'].__str__())
        data.append(expense['total'])

    sum = transactions.aggregate(sum=Sum('amount')).get('sum')

    return {
        'labels': labels,
        'data': data,
        'value': sum,
        'title': 'Transactions'
    }

def get_total_amount(queryset):
    return queryset.aggregate(total=Sum('amount'))['total']

def get_balance(user):
    debts = models.Debt.objects.filter_by_user(user)
    total = 0
    for debt in debts:
        total += debt.get_amount(user)
    return round(total, 2)

def shared_group_transactions(user, other_user):
    return models.Transaction.objects.filter_by_users(user, other_user).filter(expense__isnull=False)




class QueryForm():
    def __init__(self, request, *args, **kwargs):
        self._request = request
        self._user = request.user
        self._init_query_param()

    class QueryParam():
        def __init__(self, start_date, end_date, tag, *args, **kwargs):
            self.start_date = start_date.strftime('%Y-%m-%d') if start_date is not None else ''
            self.end_date = end_date.strftime('%Y-%m-%d') if end_date is not None else ''
            self.tag = tag if tag is not None else ''

    def get_params(self):
        return self.QueryParam(self._start_date, self._end_date, self._tag)

    def _init_query_param(self):
        start_date = self._request.GET.get('start_date')
        end_date = self._request.GET.get('end_date')
        tag = self._request.GET.get('tag')

        self._start_date = datetime.strptime(start_date, '%Y-%m-%d') if self.is_param_valid(start_date) else None 
        self._end_date = datetime.strptime(end_date, '%Y-%m-%d') if self.is_param_valid(end_date) else None 
        self._tag = tag if self.is_param_valid(tag) else None 

    def get_expenses(self):
        queryset = get_expenses_by_user(self._user)
        try:
            if self._start_date is not None:
                queryset = queryset.filter(created_at__date__gte=self._start_date)
            if self._end_date is not None:
                queryset = queryset.filter(created_at__date__lte=self._end_date)
            if self._tag is not None:
                queryset = queryset.filter(tag__name=self._tag)
        except:
            return []
        
        return queryset

    def get_private_transactions(self):
        queryset = models.Transaction.objects.filter_by_user(self._user)
        queryset = queryset.filter(expense=None)
        try:
            if self._start_date is not None:
                queryset = queryset.filter(transactioninfo__created_at__gte=self._start_date)
            if self._end_date is not None:
                queryset = queryset.filter(transactioninfo__created_at__lte=self._end_date)
        except:
            return []
        return queryset

    @staticmethod
    def is_param_valid(param):
        return param != '' and param is not None


class UserDebt():
    def __init__(self, debt, user, *args, **kwargs):
        self.user = user
        self.other_user = debt.get_other_user(user)
        self.amount = debt.get_amount(user)
        self.color = 'danger' if self.amount < 0 else 'success'
        self.private_transactions = models.Transaction.objects.filter_by_users_flag(user, self.other_user)
        self.group_transactions = models.Transaction.objects.filter_by_users_flag(user, self.other_user, False)




