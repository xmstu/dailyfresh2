from django.contrib.auth.models import AbstractUser
from django.db import models
from tinymce.models import HTMLField

from utils.models import BaseModel
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

# Create your models here.


# AbstractUser:django提供的用户模型类,包含基本的用户名,密码,是否激活等相关信息
class User(AbstractUser, BaseModel):
    """用户模型类"""

    def generate_active_token(self):
        """生成激活令牌"""
        # Serializer()生成序列化器，传入密码和过期时间
        # dumps()生成user_id加密后的token，传入封装user_id的字典
        # 返回token字符串
        serializer = Serializer(settings.SECRET_KEY, 3600)
        token = serializer.dumps({"confirm":self.id})  # 返回bytes类型
        return token.decode()

    class Meta(object):
        # 指定表名
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Address(BaseModel):
    """地址"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"
        verbose_name = '用户收货地址'
        verbose_name_plural = verbose_name


# apps/user/models.py
# class TestModel(models.Model):
#     """测试"""
#
#     ORDER_STATUS_CHOICES = (
#         (1, "待支付"),
#         (2, "待发货"),
#         (3, "待收货"),
#         (4, "待评价"),
#         (5, "已完成"),
#     )
#
#     status = models.SmallIntegerField(default=1,
#                                       verbose_name='订单状态',
#                                       choices=ORDER_STATUS_CHOICES)
#
    # class Meta(object):
    #     db_table = 'df_test'
    #     # 指定模型在后台显示的名称
    #     verbose_name = '测试模型'
    #     # 去除后台显示的名称默认添加的 's'
    #     verbose_name_plural = verbose_name


class TestModel(BaseModel):
    """测试用"""
    GENDER_CHOICES = (
        (0,'男'),
        (1,'女'),
    )
    gender = models.SmallIntegerField(default=0, choices=GENDER_CHOICES)
    desc = HTMLField(verbose_name='商品描述', null=True)

    class Meta(object):
        db_table = 'df_test'
        # 指定模型在后台显示的名称
        verbose_name = '测试模型'
        # 去除后台显示的名称默认添加的 's'
        verbose_name_plural = verbose_name
