from django.contrib import admin
from . import models

admin.site.register(models.EGroup)
admin.site.register(models.Membership)
admin.site.register(models.Transaction)
admin.site.register(models.TransactionInfo)
admin.site.register(models.Debt)
admin.site.register(models.Tag)
admin.site.register(models.Expense)