from django.contrib import admin

# Register your models here.
from django.core.cache import cache

from apps.goods.models import *
from celery_tasks.tasks import generate_static_index_html


class BaseAdmin(admin.ModelAdmin):
    """模型类管理父类"""

    def save_model(self, request, obj, form, change):
        """后台管理员保存对象数据时使用"""
        print(obj, type(obj))
        print('='*50)
        super().save_model(request, obj, form, change)
        # obj.save()
        # 重新生成首页静态页面
        generate_static_index_html.delay()
        # 删除缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """后台管理员删除对象数据时使用"""
        # print(obj, type(obj))
        # print('-'*50)
        super().delete_model(request,obj)
        # obj.delete()
        # 重新生成首页静态页面
        generate_static_index_html.delay()
        # 删除缓存数据
        cache.delete('index_page_data')


class GoodsCategoryAdmin(BaseAdmin):
    pass


class GoodsSPUAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


class IndexSlideGoodsAdmin(BaseAdmin):
    pass


class IndexPromotionAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsAdmin(BaseAdmin):
    pass


# admin.site.register(GoodsImage)

admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)

admin.site.register(IndexPromotion, IndexPromotionAdmin)
admin.site.register(IndexSlideGoods, IndexSlideGoodsAdmin)
admin.site.register(IndexCategoryGoods, IndexCategoryGoodsAdmin)