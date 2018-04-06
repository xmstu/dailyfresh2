from datetime import datetime
from time import sleep

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
            order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(request.user.id)
            print(order_id)
            print('*'*50)
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


class OrderPayView(View):

    def post(self, request):

        """订单支付"""

        # 判断用户是否登录
        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'message':'用户未登录'})

        # 获取订单id
        order_id = request.POST.get('order_id')
        print(order_id)
        print('-'*50)
        # 判断订单是否有效(没有支付)
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          status=1,  # 状态1未支付
                                          user=request.user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code':2, 'message':'无效订单'})

        # 调用第三方sdk,实现支付功能
        # (1)初始化sdk
        # print(222222222222222222222)
        from alipay import AliPay
        app_private_key_string = open('/home/python/PycharmProjects/dailyfresh/apps/orders/app_private_key.pem').read()
        print(app_private_key_string)
        # print(333333333333333333333333)
        alipay_public_key_string = open('/home/python/PycharmProjects/dailyfresh/apps/orders/alipay_pubilc_key.pem').read()
        print(alipay_public_key_string)
        # print(1111111111111)
        alipay = AliPay(
            appid="2016091100486098",  # 沙箱id
            app_notify_url=None,  # 默认回调url
            # 应用的私钥
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥,验证支付宝回传消息使用,不是你自己的公钥
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",   # RSA或者RSA2,不要使用rsa
            debug=True  # 默认false,如果是true表示使用沙箱环境
        )

        # (2)调用支付接口
        # 支付总金额

        total_pay = order.trans_cost + order.total_amount
        # 支付返回的支付结果参数
        order_str = alipay.api_alipay_trade_page_pay(
            subject="天天生鲜爱支付订单",
            out_trade_no=order_id,
            # 需要使用str类型,不能使用浮点型
            total_amount=str(total_pay),
        )

        # 定义支付引导界面,并返回给浏览器
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_str
        # print(order_str)
        # print(pay_url)
        # print('+'*50)

        return JsonResponse({'code':0, 'pay_url':pay_url})


class CheckPayView(View):

    def post(self, request):
        # print(111111111111)
        # 判断用户是否登录
        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'message':'用户未登录'})

        # 获取要查询的订单id
        order_id = request.POST.get('order_id')

        # 判断订单是否有效(未支付)
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code':2, 'message':'无效订单'})
        if not order_id:
            return JsonResponse({'code':3, 'message':'订单id不能为空'})

        # print(22222222222222)
        # 调用 第三方sdk, 实现支付功能
        # (1) 初始化sdk
        from alipay import AliPay
        app_private_key_string = open("/home/python/PycharmProjects/dailyfresh/apps/orders/app_private_key.pem").read()
        print(app_private_key_string)

        alipay_public_key_string = open("/home/python/PycharmProjects/dailyfresh/apps/orders/alipay_pubilc_key.pem").read()
        print(alipay_public_key_string)

        alipay = AliPay(
            appid="2016091100486098",  # 沙箱应用
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2  # 不要使用rsa
            debug=True  # 默认False  True: 表示使用测试环境(沙箱环境)
        )

        # 调用第三方sdk查询订单支付结果
        '''
         {
            "trade_no": "2017032121001004070200176844",
            "code": "10000",
            "invoice_amount": "20.00",
            "open_id": "20880072506750308812798160715407",
            "fund_bill_list": [
              {
                "amount": "20.00",
                "fund_channel": "ALIPAYACCOUNT"
              }
            ],
            "buyer_logon_id": "csq***@sandbox.com",
            "send_pay_date": "2017-03-21 13:29:17",
            "receipt_amount": "20.00",
            "out_trade_no": "out_trade_no15",
            "buyer_pay_amount": "20.00",
            "buyer_user_id": "2088102169481075",
            "msg": "Success",
            "point_amount": "0.00",
            "trade_status": "TRADE_SUCCESS",
            "total_amount": "20.00"
          },
        '''
        while True:
            result_dict = alipay.api_alipay_trade_query(out_trade_no=order_id)
            code = result_dict.get('code')
            trade_status = result_dict.get('trade_status')
            trade_no = result_dict.get('trade_no')

            # 10000: 接口调用成功
            if code == '10000' and trade_status == 'TRADE_SUCCESS':
                # 支付成功
                order.status = 4  # 待评价
                order.trade_no = trade_no
                order.save()  # 修改订单信息表
                return JsonResponse({'code': 0, 'message': '支付成功'})
            elif (code == '10000' and trade_status == 'WAIT_BUYER_PAY') or code == '40004':
                # 等待买家付款
                # 40004: 支付暂时失败, 过一会可以成功
                sleep(2)
                print(code)
                continue
            else:
                print(code)
                return JsonResponse({'code': 4, 'message': '支付失败'})


class CommentView(View):

    def get(self, request, order_id):
        """显示订单商品评价界面"""
        user = request.user
        print(order_id)
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        # 根据订单的状态获取订单的状态标题, 并动态新增一个实例属性
        order.status_name = OrderInfo.ORDER_STATUS[order.status]

        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_id=order_id)

        for order_sku in order_skus:
            # 计算商品的小计金额
            amount = order_sku.count * order_sku.price
            # 动态给order_sku增加属性amount,保存商品小计
            order_sku.amount = amount

        # 动态给order增加属性order_skus, 保存订单商品信息
        order.order_skus = order_skus

        # 使用模板
        return render(request, "order_comment.html", {"order": order})

    def post(self, request, order_id):
        """订单商品评论"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        # 获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        # 循环获取订单中商品的评论内容
        for i in range(1, total_count + 1):
            # 获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i)  # sku_1 sku_2
            # 获取评论的商品的内容
            comment = request.POST.get('comment_%d' % i, '')  # comment_1 comment_2
            try:
                order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue

            # 保存评论到订单商品表
            order_goods.comment = comment
            order_goods.save()

        # 修改订单的状态为“已完成”
        order.status = 5  # 已完成
        order.save()

        return redirect(reverse("users:orders", args=[1]))