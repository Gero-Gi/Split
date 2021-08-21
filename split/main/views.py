from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from . import models
from . import utils
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse

from django.contrib.auth import get_user_model
User=get_user_model()

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'main/dashboard.html'

    def get_context_data(self, **kwargs):
        query_form = utils.QueryForm(self.request)
        expenses = query_form.get_expenses()

        transactions = query_form.get_private_transactions()
        tags = models.Tag.objects.all()

        group_transactions_spent = query_form.get_group_transactions()
        group_transactions_spent = group_transactions_spent.filter(
            receiver=self.request.user)

        return {
            'expenses': expenses[:4],
            'expenses_chart': utils.get_expenses_spent_chart(group_transactions_spent),
            'expense_total': expenses.total_amount(),

            'transactions': transactions[:4],
            'transactions_chart': utils.get_private_transactions_chart(transactions),
            'transaction_total': transactions.total_amount(),

            'balance': models.Debt.objects.balance(self.request.user),
            'n_groups': models.Membership.objects.filter(user=self.request.user).count(),
            'n_debts': models.Debt.objects.filter_by_user(user=self.request.user).count(),
            'n_transactions': transactions.count(),

            'query_param': query_form.get_params(),
            'tags': tags,

            'debts': models.Debt.objects.filter_by_user(self.request.user),
            'groups': models.EGroup.objects.filter(membership__user=self.request.user),
        }


class GroupView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'main/group_view.html'
    queryset = models.EGroup.objects.all()
    context_object_name = 'group'
    http_method_names = ['get', 'post']

    def test_func(self):
        return True

    def get_membership(self):
        return models.Membership.objects.filter(group=self.get_object()).get(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query_form = utils.QueryForm(self.request)

        expenses = query_form.get_expenses().filter(
            group=self.get_object()).order_by('-created_at')
        paginator = Paginator(expenses, 10)
        page_num = self.request.GET.get('page', 1)
        paginated_expenses = paginator.get_page(page_num)

        user_membership = self.get_membership()
        ctx.update({
          

            'paginated_expenses': paginated_expenses,
            'expenses': expenses,
            'transactions': query_form.get_group_transactions().filter(expense__group=self.get_object()).filter(receiver=self.request.user),
            # 'group_admin': True,
            'group_admin': user_membership.is_admin,
            'user_membership': user_membership,
            'memberships': models.Membership.objects.filter(group=self.get_object()).exclude(pk=user_membership.pk),

        })
        return ctx

    def post(self, request, *args, **kwargs):
        if 'leave_group' in request.POST:
            self.get_membership().delete()
            return HttpResponseRedirect(reverse('dashboard'))

        if 'delete_group' in request.POST:
            self.get_object().delete()
            return HttpResponseRedirect(reverse('dashboard'))

        if 'delete_expense' in request.POST:
            models.Expense.objects.get(
                id=int(request.POST.get('value'))).delete()

        if 'remove_member' in request.POST:
            models.Membership.objects.filter(group=self.get_object()).get(user__pk=int(request.POST.get('value'))).delete()

        if 'make_admin' in request.POST:
            mebership = models.Membership.objects.filter(group=self.get_object()).get(user__pk=int(request.POST.get('value')))
            mebership.is_admin = True
            mebership.save()

        if 'add_member' in request.POST:
            email = request.POST.get('email', None)
            if email is not None:
                try:
                    models.Membership.objects.filter(group=self.get_object()).get(user__email=email)
                except:
                    models.Membership.objects.create(
                        user=User.objects.get(email=email),
                        group=self.get_object(),
                    )

        if 'add_expense' in request.POST:
            pass
        
        return HttpResponseRedirect(reverse('group', kwargs={'pk': self.get_object().pk}))