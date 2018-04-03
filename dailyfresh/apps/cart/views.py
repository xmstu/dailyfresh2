from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsSKU
from utils.common import LoginRequiredViewMixin, BaseCartView


class CartAddView(BaseCartView):

    def post(self, request, command='add'):
        """添加商品到购物车"""

        params = super().post(request, command)

        # 接受数据:user_id,sku_id,count
        user_id, sku_id, count, sku = params['user_id'], \
                                 params['sku_id'], \
                                 params['count'], \
                                 params['sku']

        # print(user_id, sku_id, count)
        # print('+'*50)

        # 添加商品到购物车,如果redis中已有该商品的id,那么就增加它的数量
        strict_redis = get_redis_connection()
        # strict_redis = StrictRedis()
        key = 'cart_%s' % user_id
        val = strict_redis.hget(key, sku_id)
        if val:
            count += int(val)

        # 库存逻辑判断
        if count > sku.stock:
            return JsonResponse({'code':5, 'errmsg':'库存不足'})

        # 操作redis数据库存储商品到购物车
        strict_redis.hset(key, sku_id, count)

        total_count = 0
        vals = strict_redis.hvals(key)
        for val in vals:
            total_count += int(val)

        context = {
            'code':0,
            'total_count':total_count,
        }

        return JsonResponse(context)


class CartInfoView(LoginRequiredViewMixin, View):
    """购物车显示界面:需要先登录"""

    def get(self, request):
        # 查询当前登录用户添加到购物车中的所有商品
        strict_redis = get_redis_connection()
        key = 'cart_%s' % request.user.id
        # 获取购物车中所有商品,返回一个字典,包含sku_id和对应的数量count
        cart_dict = strict_redis.hgetall(key)

        # 保存购物车中所有的商品对象
        skus = []
        # 商品总数量
        total_count = 0
        # 商品总金额
        total_amount = 0

        for sku_id, count in cart_dict.items():

            try:
                # 根据sku_id获取sku对象
                sku = GoodsSKU.objects.get(id=sku_id)
                # 列表中新增一个商品对象
                skus.append(sku)
            except Exception as e:
                print(e)

            # sku对象动态新增一个实例属性:count
            sku.count = int(count)
            # sku对象动态新增一个实例属性:amount
            sku.amount = sku.price * sku.count

            # 累加购物车中所有商品的数量和总金额
            total_count += sku.count
            total_amount += sku.amount

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
        }

        return render(request, 'cart.html', context)


class CartUpdateView(LoginRequiredViewMixin, BaseCartView):

    def post(self, request, command='update'):
        """修改购物车商品数量"""

        # print(CartUpdateView.mro())
        # print('-' * 50)

        params = super().post(request, command)
        sku_id = params['sku_id']
        count = params['count']

        # print(sku_id)
        # print(count)
        # print('-' * 50)

        # todo:业务处理：保存购物车商品数量
        strict_redis = get_redis_connection()
        key = 'cart_%s' % request.user.id
        strict_redis.hset(key, sku_id, count)

        # 响应json
        return JsonResponse({'code': 0, 'message': '修改商品数量成功',})


class CartDeleteView(LoginRequiredViewMixin, BaseCartView):

    def post(self, request, command='delete'):
        """删除购物车中的商品"""

        # 获取请求参数:sku_id
        sku_id = super().post(request, command)['sku_id']

        # 业务处理:从redis中删除商品
        strict_redis = get_redis_connection()
        key = 'cart_%s' % request.user.id
        strict_redis.hdel(key, sku_id)

        # 响应请求
        return JsonResponse({'code':0, 'message':'删除成功!'})