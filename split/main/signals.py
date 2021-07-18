
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from . import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
User = get_user_model()

# create a transaction for each user inside a group
@receiver(post_save, sender=models.Expense)
def post_expense(sender, instance, **kwargs):
    sender = models.Membership.objects.get(user=instance.created_by, group=instance.group)
    receivers = models.Membership.objects.filter(group=instance.group).exclude(pk=sender.pk)
    # the amount split 
    amount = round(instance.amount / (receivers.count() + 1), 2)
    for receiver in receivers:
        models.Transaction.objects.create(
            sender=sender.user,
            receiver=receiver.user,
            amount=amount,
            debt=models.Debt.objects.get_by_users(sender.user, receiver.user),
            expense=instance,
        )

# make a deposit, after each transaction, to adjust the debt
@receiver(post_save, sender=models.Transaction)
def post_transaction(sender, instance, **kwargs):
    debt = instance.debt
    debt.deposit(instance.sender, instance.amount)
    debt.save()

# adjust/restore debt
@receiver(post_delete, sender=models.Transaction)
def post_delete_transaction(sender,instance, **kwargs):
    try:
        debt = instance.debt
        debt.deposit(instance.receiver, instance.amount)
        debt.save()
    except:
        pass

# if it doesn't exist, create a debt with every member of a group
@receiver(post_save, sender=models.Membership)
def post_membership(sender, instance, **kwargs):

    debtors = models.Membership.objects.filter(group=instance.group).exclude(pk=instance.pk)
    
    for debtor in debtors:
        try:
            models.Debt.objects.get_by_users(instance.user, debtor.user)
        except ObjectDoesNotExist:
            models.Debt.objects.create(
                debtor=debtor.user,
                creditor=instance.user,
                amount=0,
            )
              