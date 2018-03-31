# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone
import django.core.validators
import tinymce.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], max_length=30)),
                ('first_name', models.CharField(blank=True, verbose_name='first name', max_length=30)),
                ('last_name', models.CharField(blank=True, verbose_name='last name', max_length=30)),
                ('email', models.EmailField(blank=True, verbose_name='email address', max_length=254)),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('is_delete', models.SmallIntegerField(default=False, verbose_name='是否删除')),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', verbose_name='groups', related_name='user_set', blank=True, to='auth.Group')),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', related_query_name='user', verbose_name='user permissions', related_name='user_set', blank=True, to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': '用户',
                'verbose_name': '用户',
                'db_table': 'df_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('is_delete', models.SmallIntegerField(default=False, verbose_name='是否删除')),
                ('receiver_name', models.CharField(verbose_name='收件人', max_length=20)),
                ('receiver_mobile', models.CharField(verbose_name='联系电话', max_length=11)),
                ('detail_addr', models.CharField(verbose_name='详细地址', max_length=256)),
                ('zip_code', models.CharField(null=True, verbose_name='邮政编码', max_length=6)),
                ('is_default', models.BooleanField(default=False, verbose_name='默认地址')),
                ('user', models.ForeignKey(verbose_name='所属用户', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '用户收货地址',
                'verbose_name': '用户收货地址',
                'db_table': 'df_address',
            },
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('is_delete', models.SmallIntegerField(default=False, verbose_name='是否删除')),
                ('gender', models.SmallIntegerField(default=0, choices=[(0, '男'), (1, '女')])),
                ('desc', tinymce.models.HTMLField(null=True, verbose_name='商品描述')),
            ],
            options={
                'verbose_name_plural': '测试模型',
                'verbose_name': '测试模型',
                'db_table': 'df_test',
            },
        ),
    ]
