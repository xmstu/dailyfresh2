from django.db import models

# 注意： 如果没有指定模型类为抽象的，则服务器运行会出错，如下：
#
#   ERRORS:
#   user.User.basemodel_ptr: (fields.E300) Field defines a relation with model 'BaseModel',
#   which is either not installed, or is abstract.


class BaseModel(models.Model):
    """模型类基类"""

    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 最后修改时间
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    # 删除标识,BooleanField等价于SmallIntegerField
    # delete = models.BooleanField(default=False, verbose_name='是否删除')
    delete = models.SmallIntegerField(default=False, verbose_name='是否删除')

    class Meta(object):
        # 需要指定基类模型类为抽象的，否则迁移生成表时会出错
        abstract = True