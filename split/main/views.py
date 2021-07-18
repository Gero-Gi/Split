from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from . import models
from . import utils

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name='main/dashboard.html'

    def get_context_data(self, **kwargs):
        # all expenses in each group
        query_form = utils.QueryForm(self.request)
        expenses = query_form.get_expenses()
        transactions = query_form.get_private_transactions()
        tags = models.Tag.objects.all()

        
        return {
            'expenses': expenses[:4],
            'expenses_chart': utils.get_expenses_chart(expenses),
            'expense_total': utils.get_total_amount(expenses),
            
            'transactions': transactions[:4],
            'transactions_chart': utils.get_private_transactions_chart(transactions),
            'transaction_total': utils.get_total_amount(transactions),

            'balance': utils.get_balance(self.request.user),
            'n_groups': models.Membership.objects.filter(user=self.request.user).count(),
            'n_debts': models.Debt.objects.filter_by_user(user=self.request.user).count(),
            'n_transactions': transactions.count(),
           
            'query_param':query_form.get_params(),
            'tags': tags,

            'debts': models.Debt.objects.filter_by_user(self.request.user),
     
            }

    



