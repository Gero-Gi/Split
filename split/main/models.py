from django.db import models
from django.contrib.auth import get_user_model
from . import managers
from datetime import datetime

User = get_user_model()


class EGroup(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False, blank=True)
    group = models.ForeignKey(EGroup, on_delete=models.CASCADE)
    joined_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return '{}-{}'.format(self.user, self.group)


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    icon_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Expense(models.Model):
    group = models.ForeignKey(EGroup, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    description = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    tag = models.ForeignKey(Tag, null=True, blank=True,
                            on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=datetime.now)

    objects = managers.ExpenseQuerySet.as_manager()

    def __str__(self):
        return 'exp-{}-{}'.format(self.id, self.group)


class Debt(models.Model):
    debtor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='debtors')
    creditor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='creditors')
    # if amount < 0 creditor is in debt
    # else debtor is in debt
    amount = models.FloatField()

    objects = managers.DebtQuerySet.as_manager()

    def __str__(self):
        return '{}-{}'.format(self.debtor, self.creditor)

    def deposit(self, user, amount):
        if user.id == self.debtor.id:
            self.amount -= amount
        elif user.id == self.creditor.id:
            self.amount += amount

    def get_other_user(self, user):
        if self.debtor.id == user.id:
            return self.creditor
        return self.debtor

    def get_balance(self, user):
        if user.id == self.creditor.id:
            return round(self.amount, 2)
        return round(-self.amount, 2)


class Transaction(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='receivers')
    amount = models.FloatField()
    debt = models.ForeignKey(Debt, null=True, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, null=True, on_delete=models.CASCADE)

    objects = managers.TransactionQuerySet.as_manager()

    def __str__(self):
        return 'trs-{}-{}-{}'.format(self.id, self.sender, self.receiver)

    def is_self_transaction(self):
        return self.sender.id == self.receiver.id


class TransactionInfo(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.transaction
