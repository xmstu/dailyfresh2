# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goodscategory',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='goodsimage',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='goodssku',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='goodsspu',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='indexcategorygoods',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='indexpromotion',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='indexslidegoods',
            old_name='delete',
            new_name='is_delete',
        ),
    ]
