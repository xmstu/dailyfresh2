import re

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired

from apps.goods.models import GoodsSKU
from celery_tasks.tasks import send_active_email
# Create your views here.
from django.views.generic import View

from apps.users.models import User, Address
from dailyfresh import settings
from utils.common import LoginRequiredViewMixin


class RegisterView(View):
    """类视图,处理注册"""

    def get(self, request):
        """处理get请求"""
        # 获取注册页面
        return render(request, 'register.html')

    def post(self, request):
        """处理post请求"""
        # 处理注册逻辑

        # 获取请求参数(用户名,密码,确认密码,邮箱,勾选用户协议)
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        cpwd = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 校验参数合法性
        # 逻辑判断 0 0.0 '' None [] () {}  -> False
        # all: 所有的变量都为True, all函数才返回True, 否则返回False
        if not all([username, pwd, cpwd, email, allow]):
            print('*' * 10)
            return render(request, 'register.html', {'message': '请填满所有参数'})

        # 判断两次输入的密码是否一致
        if pwd != cpwd:
            print('-' * 10)
            return render(request, 'register.html', {'message': '两次输入的密码不一致'})

        # 判断邮箱格式是否正确
        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            print('/' * 10)
            return render(request, 'register.html', {'message': '邮箱格式不正确'})

        # 判断是否勾选了用户协议
        if allow != 'on':
            print('+' * 10)
            return render(request, 'register.html', {'message': '请先同意用户协议'})

        # 业务处理
        # 保存用户到数据库中
        # create_user: 是django提供的方法,会对密码进行加密后再保存到数据库
        try:
            print('=' * 50)
            user = User.objects.create_user(username=username,
                                     email=email,
                                     password=pwd)
            # 创建用户时，django默认用户为激活状态，要将其改为未激活状态
            User.objects.filter(id=user.id).update(is_active=False)
        except IntegrityError as e:
            print(e)
            return render(request, 'register.html', {'message': '用户名已存在'})

        # todo:给用户发送激活邮件
        # 参数1：密钥
        # 参数2：过期时间，1小时
        s = Serializer(settings.SECRET_KEY, 3600)
        # 加密
        token = user.generate_active_token()
        # 方式一：使用Django发送激活邮件，但耗时长，需要几分钟，用户体验差
        # self.send_active_email(username, email, token)
        # 方式二:使用celery异步发送邮件
        send_active_email.delay(username, email, token)

        return redirect(reverse("users:login"))

    # todo:给用户发送邮件
    @staticmethod
    def send_active_email(username, email, token):
        """
        发送激活邮件
        :param username: 注册的用户
        :param email: 注册用户的邮箱
        :param token: 对字典{'confirm'：用户id} 加密后的结果
        :return:
        """
        subject = '天天生鲜注册激活'  # 邮件标题
        message = ''  # 邮件正文
        from_email = settings.EMAIL_FROM  # 发送着
        recipient_list = [email]  # 接受者列表
        # 邮件正文
        html_message = '<h3>尊敬的%s:</h3> 欢迎注册天天生鲜' \
                       '请点击以下链接激活你的账号:<br/>' \
                       '<a href="http://127.0.0.1:8000/users/active/%s">' \
                       'http://127.0.0.1:8000/users/active/%s</a>' \
                       % (username, token, token)

        # 调用django的send_mail方法发送邮件
        send_mail(subject=subject, message=message,
                  from_email=from_email, recipient_list=recipient_list,
                  html_message=html_message)


class LoginView(View):
    """类视图,处理登录"""

    def get(self, request):
        """进入登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        """处理登录逻辑"""
        # 获取登录参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 校验参数合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '请将所有参数填满'})

        # 通过 django 提供的authenticate方法，
        # 验证用户名和密码是否正确
        user = authenticate(username=username, password=password)

        # 用户名或密码不正确
        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码不正确'})

        # 注册账号未激活
        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '请先激活账号'})

        # 通过django的login方法，保存登录用户状态（使用session）
        login(request, user)

        # 获取是否勾选‘记住用户名’
        remember = request.POST.get('remember')

        # 判断是否勾上记住用户名和密码
        if remember != 'on':
            # 没有勾选,不需记住cookie信息,浏览会话结束后过期
            request.session.set_expiry(0)
        else:
            # 已勾选,需要记住cookie信息,两周后过期
            request.session.set_expiry(None)

        # 获取next跳转参数
        next_url = request.GET.get('next', None)
        if next_url is None:
            # 响应请求，进入首页
            return redirect(reverse('goods:index'))
        else:
            return redirect(next_url)


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 由django用户认证系统完成，会清理cookie
        # 和session,request参数中有user对象
        logout(request)

        # 推出后跳转，由产品经理设计
        return redirect(reverse('goods:index'))


class ActiveView(View):

    def get(self, request, token):
        """激活注册账号"""
        # 对token进行解密
        try:
            s = Serializer(settings.SECRET_KEY, 3600)
            info = s.loads(token)
            user_id = info['confirm']
        except SignatureExpired:
            return HttpResponse('激活链接已过期')

        # 修改激活状态字段
        User.objects.filter(id=user_id).update(is_active=True)
        # 激活成功进入登录界面
        return redirect(reverse("users:login"))


class UserAddressView(LoginRequiredViewMixin, View):
    """用户中心--地址界面"""

    # /users/address
    def get(self, request):
        """显示用户地址"""
        user = request.user
        try:
            # 查询用户地址：根据创建时间排序，最近的时间在最前，取第1个地址
            # address = Address.objects.filter(user=user).order_by('-create_time')[0]
            # address = user.address_set.order_by('-create_time')[0]
            # address = user.address_set.latest('create_time')
            address = user.address_set.latest('create_time')
        except Exception:
            address = None

        data = {
            'address':address,
            'which_page':3
        }
        return render(request, 'user_center_site.html', data)

    def post(self, request):
        """增加用户地址"""

        # 获取用户表单填写的数据
        receiver_name = request.POST.get('receiver')
        detail_address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')

        # 因为Address表是外键约束至user表的,因此要获取登录的user对象
        user = request.user
        # 邮政编码不是强制添加的,因此可以不用加以判断
        if not all([receiver_name, detail_address, mobile]):
            return render(request, 'user_center_site.html', {'errmsg':'参数不完整'})
        Address.objects.create(
            receiver_name=receiver_name,
            detail_addr=detail_address,
            zip_code=zip_code,
            receiver_mobile=mobile,
            user=user,
        )
        # 提交表单成功后,重定向到本页面
        return redirect(reverse('users:address'))


class UserOrderView(LoginRequiredViewMixin, View):
    """用户中心--订单显示界面"""

    # /users/order
    def get(self, request):
        data = {'which_page': 2}
        return render(request, 'user_center_order.html', data)


class UserInfoView(LoginRequiredViewMixin, View):
    """用户中心--用户信息界面"""

    # /users/info
    def get(self, request):

        # 获取用户对象
        user = request.user

        # 查询用户最新添加的地址
        try:
            address = user.address_set.latest('create_time')
            # address = user.address_set.order_by('-create_time')[0]
        except Address.DoesNotExist as e:
            print(e)
            address = None

        # 从Redis数据库中查询出用户浏览过的商品记录
            # 格式: history_用户id : [商品id1 商品id2 ...]
            # 例:   history_1: [3, 1, 2]
        strict_redis = get_redis_connection('default')
        key = 'history_%s' % request.user.id
        # 最多只查看最近浏览过的5条记录
        goods_ids = strict_redis.lrange(key, 0, 4)
        # 获取到的商品id:[3, 1, 2]
        print(goods_ids)

        # 需求：保证经过数据库查询后，依然是[3, 1, 2]
        skus = []  # 保存用户历史浏览记录,保存的商品顺序与redis中查询的商品id顺序一致
        for id in goods_ids:
            try:
                sku = GoodsSKU.objects.filter(id=id)
                skus.append(sku)
            except GoodsSKU.DoesNotExist as e:
                print(e)

        # 定义模板数据
        data = {
            'address':address,
            'which_page': 1,
            'skus':skus
        }

        return render(request, 'user_center_info.html', data)

