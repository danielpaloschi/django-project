# Generated by Django 4.2.4 on 2023-08-14 20:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_user_stocks_symbols'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_stocks',
        ),
    ]
