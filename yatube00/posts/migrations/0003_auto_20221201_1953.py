# Generated by Django 2.2.19 on 2022-12-01 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20221201_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='name',
            new_name='title',
        ),
    ]
