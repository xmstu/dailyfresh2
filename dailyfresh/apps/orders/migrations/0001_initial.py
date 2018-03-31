# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('is_delete', models.SmallIntegerField(default=False, verbose_name='是否删除')),
                ('count', models.IntegerField(default=1, verbose_name='购买数量')),
                ('price', models.DecimalField(max_digits=10, verbose_name='单价', decimal_places=2)),
                ('comment', models.TextField(default='', verbose_name='评价信息')),
            ],
            options={
                'verbose_name_plural': '订单商品',
                'verbose_name': '订单商品',
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('is_delete', models.SmallIntegerField(default=False, verbose_name='是否删除')),
                ('order_id', models.CharField(verbose_name='订单号', serialize=False, primary_key=True, max_length=64)),
                ('total_count', models.IntegerField(default=1, verbose_name='商品总数')),
                ('total_amount', models.DecimalField(max_digits=10, verbose_name='商品总金额', decimal_places=2)),
                ('trans_cost', models.DecimalField(max_digits=10, verbose_name='运费', decimal_places=2)),
                ('pay_method', models.SmallIntegerField(default=1, verbose_name='支付方式', choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')])),
                ('status', models.SmallIntegerField(default=1, verbose_name='订单状态', choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')])),
                ('trade_no', models.CharField(blank=True, default='', verbose_name='支付编号', unique=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name_plural': '订单信息',
                'verbose_name': '订单信息',
                'db_table': 'df_order_info',
            },
        ),
    ]
