# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20180326_1831'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordergoods',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='orderinfo',
            old_name='delete',
            new_name='is_delete',
        ),
    ]
