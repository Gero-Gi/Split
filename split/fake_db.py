from django.db.models.query import InstanceCheckMeta
from main import models as split
from auth_app.models import User
from faker import Faker
import random
from django.core.files import File
from datetime import datetime

faker = Faker()

MALE_PIC_PATH = 'man.png'
FEMALE_PIC_PATH = 'woman.png'

GROUPS_PIC = [
    'home.png',
    'work.png',
    'team.png',
]


class FakeDB():
    _tags = {
        'bills': 'receipt_long',
        'groceries': 'storefront',
        'loan': 'supervisor_account',
        'party': 'celebration',
        'medical': 'medical_services',
        'rent': 'villa',
        'gas': 'local_gas_station',
        'other': 'attach_money',
        'gift': 'card_giftcard',
    }
    _group_users = [
        [0, 1, 2, 3], [2, 3, 4, 5], [3, 6, 7, 8, 9]
    ]
    _group_names = ['Home', 'Work', 'Team']
    _user_expences_group = 40
    _user_transaction = 8

    tags = []
    users = []
    groups = []

    def clean_db(self):
        User.objects.filter(is_superuser=False).delete()
        split.EGroup.objects.all().delete()
        split.Debt.objects.all().delete()
        split.Tag.objects.all().delete()

    def populate(self):
        print('cleaning database...')
        self.clean_db()

        print('populating tags...')
        self.populate_tags()

        print('populating users...')
        self.populate_users()

        print('populating groups...')
        self.populate_groups()

        print('populating memberships...')
        self.populate_membership()

        print('populating expenses...')
        self.populate_expenses()

        print('populating transactions...')
        self.populate_transactions()

        print('database populated successfully!')
        print(self.users[3].email)
      

    def populate_tags(self):
        for name, icon in self._tags.items():
            self.tags.append(split.Tag.objects.create(
                name=name,
                icon_name=icon
            ))

    def populate_users(self):
        for i in range(10):
            if(i < 5):
                first_name = faker.first_name_male()
                img_path = MALE_PIC_PATH
            else:
                first_name = faker.first_name_female()
                img_path = FEMALE_PIC_PATH

            last_name = faker.last_name()
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email='{}.{}@gmail.com'.format(first_name, last_name).lower(),
            )
            user.set_password('password')
            user.image.save('{}-{}.png'.format(user.id,
                            datetime.now()), File(open(img_path, 'rb')))
            user.save()
            self.users.append(user)

    def populate_groups(self):
        i = 0
        for name in self._group_names:
            group = split.EGroup.objects.create(
                name=name,)
            group.image.save('{}-{}.png'.format(group.id,
                             datetime.now()), File(open(GROUPS_PIC[i], 'rb')))
            group.save()
            self.groups.append(group)
            i += 1

    def populate_membership(self):
        i = 0
        for p in self._group_users:
            admin = True
            for index in p:
                split.Membership.objects.create(
                    user=self.users[index],
                    is_admin=admin,
                    group=self.groups[i]
                )
                admin = False
            i += 1

    def populate_expenses(self):
        for user in self.users:
            for membership in split.Membership.objects.filter(user=user):
                # expense for each group
                for i in range(self._user_expences_group):
                    split.Expense.objects.create(
                        group=membership.group,
                        created_by=user,
                        description=faker.text(max_nb_chars=160),
                        created_at=faker.date_time_between(
                            start_date='-1y', end_date='now'),
                        amount=round(random.randrange(10.0, 150.0)),
                        tag=random.choice(self.tags)
                    )

    def populate_transactions(self):
        for sender in self.users:
            debts = split.Debt.objects.filter_by_user(sender)
            for debt in debts:
                receiver = debt.get_other_user(sender)
                for i in range(self._user_transaction):
                    transaction = split.Transaction.objects.create(
                        sender=sender,
                        receiver=receiver,
                        amount=round(random.randrange(10.0, 30.0)),
                        debt=debt,
                        expense=None,
                    )
                    split.TransactionInfo.objects.create(
                        transaction=transaction,
                        description=faker.text(max_nb_chars=160),
                        created_at=faker.date_time_between(
                            start_date='-1y', end_date='now')
                    )
