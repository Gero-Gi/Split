from django.db import models
from django.contrib.auth import get_user_model

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
    name = models.CharField(max_length=200)
    icon_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Expense(models.Model):
    group = models.ForeignKey(EGroup, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    description = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'exp-{}-{}'.format(self.id, self.group)


class Debt(models.Model):
    debtor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debtors')
    creditor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creditors')
    amount = models.FloatField()

    def __str__(self):
        return '{}-{}'.format(self.debtor, self.creditor)


class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receivers')
    amount = models.FloatField()
    debt = models.ForeignKey(Debt, on_delete = models.CASCADE)
    expense = models.ForeignKey(Expense, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return 'trs-{}-{}-{}'.format(self.id, self.sender, self.receiver)


class TransactionInfo(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction