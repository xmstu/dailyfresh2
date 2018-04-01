from django.contrib.auth.decorators import login_required
from django.views.generic import  View


# 单继承
from django_redis import get_redis_connection


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
