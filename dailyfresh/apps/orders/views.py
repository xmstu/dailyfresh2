from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.common import LoginRequiredViewMixin


class OrderPlaceView(View):

    def post(self, request):
        """进入确认订单界面"""

        # 获取请求参数：sku_ids
        sku_ids = request.POST.getlist('sku_ids')
        # [1, 2]  -> 1,2
        sku_ids_str = ','.join(sku_ids)

        # 校验参数不能为空
        if not sku_ids:
            # 回到购物车界面
            return redirect(reverse('cart:info'))

        # 获取用户地址信息(此处使用最新添加的地址)
        user = request.user
        try:
            address = Address.objects.filter(
                user=user).latest('create_time')
        except:
            address = None

        skus = []           # 订单中所有的商品
        total_count = 0     # 商品总数量
        total_amount = 0    # 商品总金额

        # todo: 查询购物车中的所有的商品
        strict_redis = get_redis_connection()
        # strict_redis = StrictRedis()
        # cart_1 = {1: 2, 2: 2}
        # 字典: 键值,都是bytes类型
        cart_dict = strict_redis.hgetall('cart_%s' % request.user.id)
        # 循环操作每一个订单商品
        for sku_id in sku_ids:
            # 查询一个商品对象
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                # 回到购物车界面
                return redirect(reverse('cart:info'))

            # 获取商品数量和小计金额(需要进行数据类型转换)
            sku_count = cart_dict.get(sku_id.encode())  # str -> bytes
            sku_count = int(sku_count)  # bytes -> int
            sku_amount = sku_count * sku.price   # 商品小计金额

            # 新增实例属性,以便在模板界面中显示
            sku.count = sku_count
            sku.sku_amount = sku_amount

            # 添加商品对象到列表中
            skus.append(sku)

            # 累计商品总数量和总金额
            total_count += sku.count
            total_amount += sku_amount

        # 运费(运费模块)
        trans_cost = 10
        # 实付金额
        total_pay = trans_cost + total_amount

        # 定义模板显示的字典数据
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'trans_cost': trans_cost,
            'total_pay': total_pay,
            'address': address,
            'sku_ids_str': sku_ids_str,
        }

        # 响应结果: 返回确认订单html界面
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredViewMixin, View):
    """提交订单(创建订单必须保持事务原子性,要么所有事务一起提交成功,要么一起失败)"""

    @transaction.atomic
    def post(self, request):
        # 登录判断
        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'message':'请先登录'})

        # 获取请求参数：address_id, pay_method, sku_ids_str
        address_id = request.POST.get('address_id')
        pay_method = request.POST.get('pay_method')
        sku_ids_str = request.POST.get('sku_ids_str')
        user = request.user

        # 校验参数不能为空
        if not all([address_id, pay_method, sku_ids_str]):
            return JsonResponse({'code':2, 'message':'参数不能为空'})

        # 类型转换：str -> 列表
        sku_ids = sku_ids_str.split(',')

        # 判断地址是否存在
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code':3, 'message':'地址不能为空'})

        # todo: 修改订单信息表: 保存订单数据到订单信息表中,同时创建一个保存点
        point = transaction.savepoint()
        try:
            total_count = 0
            total_amount = 0
            trans_cost = 0
            # 订单号
            order_id = datetime.now().strftime('%Y%M%D%H%M%S') \
                       + str(request.user.id)

            # 保存订单数据到订单信息表中(订单信息表添加一条记录)
            order = OrderInfo.objects.create(
                order_id=order_id,
                total_count=total_count,
                total_amount=total_amount,
                trans_cost=trans_cost,
                pay_method=pay_method,
                user=user,
                address=address
            )

            # 从Redis查询出购物车数据
            strict_redis = get_redis_connection()
            # 注意: 返回的是字典, 键值都为bytes类型
            # cart_1 = {1: 2, 2: 2}
            key = 'cart_%s' % request.user.id
            cart_dict = strict_redis.hgetall(key)

            # todo: 核心业务: 遍历每一个商品, 并保存到订单商品表
            for sku_id in sku_ids:
                # 查询订单中的每一个商品
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                except:

                    # 回滚到上面的保存点:撤销订单信息表的修改
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code': 4, 'message': '商品不存在'})

                # 获取商品数量，并判断库存
                sku_count = cart_dict.get(sku_id.encode())
                sku_count = int(sku_count)
                if sku_count > sku.stock:
                    # 回滚到上面的保存点:撤销订单信息表的修改
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code':5, 'message':'库存不足'})

                # todo: 修改订单商品表: 保存订单商品到订单商品表
                OrderGoods.objects.create(
                    count = sku_count,
                    price = sku.price,
                    sku=sku,
                    order=order,
                )

                # todo: 修改商品sku表: 减少商品库存, 增加商品销量
                sku.stock -= sku_count
                sku.sales += sku_count
                sku.save()

                # 累加商品数量和总金额
                total_count += sku_count
                total_amount += sku.price * sku_count

            # todo: 修改订单信息表: 修改商品总数量和总金额
            order.total_count = total_count
            order.total_amount = total_amount
            order.save()

        except Exception as e:
            print(e)
            transaction.savepoint_rollback(point)
            return JsonResponse({'code':6, 'message':'创建订单失败'})

        # 提交事务
        transaction.savepoint_commit(point)

        # 订单创建成功后,从Redis中删除购物车中的商品
        # cart_1 = {1: 2, 2: 2}
        # redis命令: hdel cart_1 1 2
        strict_redis.hdel(key, *sku_ids)

        # 订单创建成功， 响应请求，返回json
        return JsonResponse({'code':0, 'message':'创建订单成功'})