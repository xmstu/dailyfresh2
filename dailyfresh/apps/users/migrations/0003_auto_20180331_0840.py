# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180326_1831'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='testmodel',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='delete',
            new_name='is_delete',
        ),
    ]
