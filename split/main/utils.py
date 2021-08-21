from . import models
from django.db.models import Sum
from django.db.models.functions import TruncDay
from datetime import datetime

def get_spent_chart(transactions):
    labels = []
    data = []

    queryset = transactions.daily_total()
    for transaction in queryset:
        labels.append(transaction['expense__created_at__date'].__str__())
        data.append(transaction['total'])

    return {
        'labels': labels,
        'data': data,
        'value': transactions.total_amount(),
    }
   
def get_expenses_spent_chart(transactions):
    labels = []
    data = []

    queryset = transactions.daily_total()
    for transaction in queryset:
        labels.append(transaction['expense__created_at__date'].__str__())
        data.append(transaction['total'])

    return {
        'labels': labels,
        'data': data,
        'value': transactions.total_amount(),
        'title': 'Expenses',
        'subtitle': '/spent'
    }

def get_expenses_chart_double(expenses, transactions):
    labels = []
    dataset_a = []
    dataset_b = []
    value_a = expenses.total_amount()
    value_b = transactions.total_amount()

    expenses = expenses.daily_total()
    transactions = transactions.daily_total()
    for expense in expenses:
        labels.append(expense['created_at__date'].__str__())
        dataset_a.append(expense['total'])
    for transaction in transactions:
        dataset_b.append(transaction['total'])


    return {
        'labels': labels,
        'dataset_a': dataset_a,
        'dataset_b': dataset_b,
        'value_a': value_a,
        'value_b': value_b,
        'title': 'Expenses',
        'subtitle': ''
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
        'title': 'Transactions',
        'subtitle': ''
    }



class QueryForm():
    def __init__(self, request, *args, **kwargs):
        self._request = request
        self._user = request.user
        self._init_query_param()

    class QueryParam():
        def __init__(self, start_date, end_date, tag, *args, **kwargs):
            self.start_date = start_date.strftime('%Y-%m-%d') if start_date is not None else ''
            self.end_date = end_date.strftime('%Y-%m-%d') if end_date is not None else ''
            try: 
                self.tag = models.Tag.objects.get(name=tag)
            except:
                self.tag = None

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
        queryset = models.Expense.objects.filter_by_user(self._user)
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
        queryset = models.Transaction.objects.filter_by_user_flag(self._user)
        try:
            if self._start_date is not None:
                queryset = queryset.filter(transactioninfo__created_at__gte=self._start_date)
            if self._end_date is not None:
                queryset = queryset.filter(transactioninfo__created_at__lte=self._end_date)
        except:
            return []
        return queryset

    def get_group_transactions(self):
        queryset = models.Transaction.objects.filter_by_user_flag(self._user, private=False)
        try:
            if self._start_date is not None:
                queryset = queryset.filter(expense__created_at__gte=self._start_date)
            if self._end_date is not None:
                queryset = queryset.filter(expense__created_at__lte=self._end_date)
            if self._tag is not None:
                queryset = queryset.filter(expense__tag__name=self._tag)
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
        self.amount = debt.get_balance(user)
        self.color = 'danger' if self.amount < 0 else 'success'
        self.private_transactions = models.Transaction.objects.filter_by_users_flag(user, self.other_user)
        self.group_transactions = models.Transaction.objects.filter_by_users_flag(user, self.other_user, False)




