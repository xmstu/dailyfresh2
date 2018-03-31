from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsSKU


class CartAddView(View):

    def post(self, request):
        """添加商品到购物车"""

        # 判断用户是否登录
        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'errmsg':'请先登录'})

        # 接受数据:user_id,sku_id,count
        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # print(user_id, sku_id, count)
        # print('+'*50)

        # 检验参数all
        if not all([count, sku_id]):
            return JsonResponse({'code':2, 'errmsg':'请填完所有参数'})

        # 判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist as e:
            print(e)
            return JsonResponse({'code':3,'errmsg':'商品不存在'})

        # 判断count是否是整数
        try:
            count = int(count)
        except Exception as e:
            print(e)
            return JsonResponse({'code':4, 'errmsg':'购买数量必须为整数'})

        # 判断库存
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
