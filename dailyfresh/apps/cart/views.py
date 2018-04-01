from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsSKU
from utils.common import LoginRequiredViewMixin


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


class CartUpdateView(LoginRequiredViewMixin, View):

    def post(self, request):
        """修改购物车商品数量"""

        # 判断登录状态
        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'errmsg':'请先登录'})

        # 获取请求参数
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 参数合法性判断
        if not all([sku_id, count]):
            return JsonResponse({'code':2, 'errmsg':'参数不能为空'})

        # 查询数据库获取sku对象
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code':3, 'errmsg':'商品不存在'})

        # 判断购物数量是否为整数
        try:
            count = int(count)
        except Exception as e:
            print(e)
            return JsonResponse({'code':4, 'errmsg':'购买数量需要为整数'})

        # 库存判断
        if count > sku.stock:
            return JsonResponse({'code': 5, 'errmsg': '库存不足'})

        # todo:业务处理：保存购物车商品数量
        strict_redis = get_redis_connection()
        key = 'cart_%s' % request.user.id
        strict_redis.hset(key, sku_id, count)

        # 响应json
        return JsonResponse({'code': 0, 'message': '修改商品数量成功',})


class CartDeleteView(LoginRequiredViewMixin, View):

    def post(self, request):
        """删除购物车中的商品"""

        # 判断是否有登录
        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'errmsg':'请先登录'})

        # 获取请求参数:sku_id
        sku_id = request.POST.get('sku_id')

        # 查询数据库获取sku对象,如果获取不到sku对象,那么就返回错误码
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '商品不存在'})

        # 业务处理:从redis中删除商品
        strict_redis = get_redis_connection()
        key = 'cart_%s' % request.user.id
        strict_redis.hdel(key, sku_id)

        # 响应请求
        return JsonResponse({'code':0, 'message':'删除成功!'})