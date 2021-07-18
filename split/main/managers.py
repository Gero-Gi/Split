from django.db import models
from django.db.models import Q


class DebtManager(models.Manager):
    # debt associated with user_a and user_b    
    def get_by_users(self, user_a, user_b):
        return self.get(
            (Q(debtor=user_a) & Q(creditor=user_b)) |
            (Q(debtor=user_b) & Q(creditor=user_a))
        )

    def filter_by_user(self, user):
        return self.filter(Q(debtor=user)|Q(creditor=user))


class TransactionManager(models.Manager):
    def filter_by_user(self, user):
        return self.filter(Q(sender=user)|Q(receiver=user))

    def filter_by_users(self, user, other_user):
        return self.filter((Q(sender=user) & Q(receiver=other_user))|
        (Q(sender=other_user) & Q(receiver=user)))

    def filter_by_users_flag(self, user, other_user, private=True):
        if private:
            return self.filter_by_users(user, other_user).filter(expense__isnull=True)
        return self.filter_by_users(user, other_user).filter(expense__isnull=False)