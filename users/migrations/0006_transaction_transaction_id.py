# Generated by Django 2.0.5 on 2018-05-03 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20180503_0600'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_id',
            field=models.TextField(blank=True, max_length='200'),
        ),
    ]
