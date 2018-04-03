from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import  View


# 单继承
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU


class LoginRequiredView(View):
    """判断是否有登录"""

    # 重写as_view方法,对返回的view_fun函数进行login_required装饰
    @classmethod
    def as_view(cls, **initkwargs):
        # 获取视图函数
        view_fun = super().as_view(**initkwargs)
        # 通过方法调用的方法，对视图函数进行装饰
        return login_required(view_fun)


# 多继承:Mixin:扩展功能,新增
class LoginRequiredViewMixin(object):
    """判断是否有登录"""

    # 重写as_view方法,对返回的view_fun函数进行login_required装饰
    @classmethod
    def as_view(cls, **initkwargs):
        # 获取视图函数
        view_fun = super().as_view(**initkwargs)
        # 通过方法调用的方法，对视图函数进行装饰
        return login_required(view_fun)


class BaseCartView(View):

    def not_authenticated(self, request):
        # 判断登录状态
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})

    def get_param(self, request):
        # 获取请求参数
        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        sku = self.get_sku(sku_id)
        params = {'user_id':user_id, 'sku_id':sku_id, 'count':count, 'sku':sku}
        return params

    def not_all(self, *args):
        # 参数合法性判断
        if not all(args):
            return JsonResponse({'code': 2, 'errmsg': '参数不能为空'})

    def get_sku(self, sku_id):
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
            return sku
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '商品不存在'})

    def get_count(self, count):
        try:
            count = int(count)
            return count
        except Exception as e:
            print(e)
            return JsonResponse({'code': 4, 'errmsg': '购买数量需要为整数'})

    def is_more_than_stock(self, sku, count):
        if count > sku.stock:
            return JsonResponse({'code': 5, 'errmsg': '库存不足'})

    def post(self, request, command):

        # 判断是否登录
        self.not_authenticated(request)

        # 获取参数
        params = self.get_param(request)
        user_id, sku_id, count, sku = params['user_id'], \
                                 params['sku_id'], \
                                 params['count'], \
                                 params['sku']

        if command == 'update':
            # 判断参数是否完整
            self.not_all(sku_id, count)
            # 判断购物数量是否为整数
            count = self.get_count(count)
            # 库存判断
            self.is_more_than_stock(sku, count)
            params.update(count=count)

        elif command == 'delete':
            # 判断参数是否完整
            self.not_all(sku_id)

        elif command == 'add':
            # 判断参数是否完整
            self.not_all(sku_id, count)
            # 判断购物数量是否为整数
            count = self.get_count(count)
            params.update(count=count)

        return params

    def get_cart_count(self, request):
        """获取购物车"""
        cart_count = 0
        # 判断是否登录
        if request.user.is_authenticated():
            # 获取当前登录用户添加到购物车的商品的总数量
            strict_redis = get_redis_connection()
            # 获取cart_id列表,与用户id一一对应
            key = 'cart_%s' % request.user.id
            # 获取所有购物车的商品数量,返回一个列表,是每个商品的购买数量
            vals = strict_redis.hvals(key)

            for count in vals:
                cart_count += int(count)

            return cart_count
