# Generated by Django 3.2.14 on 2022-07-28 08:51

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='source',
            new_name='storage',
        ),
        migrations.AlterField(
            model_name='task',
            name='fail_reason',
            field=models.TextField(blank=True),
        ),
    ]
