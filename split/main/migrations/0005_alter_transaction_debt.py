# Generated by Django 3.2.5 on 2021-08-17 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210716_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='debt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.debt'),
        ),
    ]
