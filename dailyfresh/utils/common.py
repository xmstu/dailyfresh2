from django.contrib.auth.decorators import login_required
from django.views.generic import  View


# 单继承
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

