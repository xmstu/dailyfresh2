# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': '用户收货地址', 'verbose_name': '用户收货地址'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name_plural': '用户', 'verbose_name': '用户'},
        ),
    ]
