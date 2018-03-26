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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('delete', models.SmallIntegerField(verbose_name='是否删除', default=False)),
                ('count', models.IntegerField(verbose_name='购买数量', default=1)),
                ('price', models.DecimalField(max_digits=10, verbose_name='单价', decimal_places=2)),
                ('comment', models.TextField(verbose_name='评价信息', default='')),
            ],
            options={
                'db_table': 'df_order_goods',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='修改时间', auto_now=True)),
                ('delete', models.SmallIntegerField(verbose_name='是否删除', default=False)),
                ('order_id', models.CharField(serialize=False, verbose_name='订单号', primary_key=True, max_length=64)),
                ('total_count', models.IntegerField(verbose_name='商品总数', default=1)),
                ('total_amount', models.DecimalField(max_digits=10, verbose_name='商品总金额', decimal_places=2)),
                ('trans_cost', models.DecimalField(max_digits=10, verbose_name='运费', decimal_places=2)),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], verbose_name='支付方式', default=1)),
                ('status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], verbose_name='订单状态', default=1)),
                ('trade_no', models.CharField(verbose_name='支付编号', default='', max_length=100, blank=True, unique=True, null=True)),
            ],
            options={
                'db_table': 'df_order_info',
            },
        ),
    ]
