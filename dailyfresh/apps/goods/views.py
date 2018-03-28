from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
from django.views.generic import View

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods


class IndexView(View):

    def get(self, request):
        """显示首页"""

        # 查询首页中要显示的数据
        # 所有的商品类别
        categories = GoodsCategory.objects.all()

        # 轮播图商品
        slide_goods = IndexSlideGoods.objects.all().order_by('index')

        # 促销活动数据
        try:
            promotions = IndexPromotion.objects.all()[0:2]  # 只获取2个促销活动
        except Exception as e:
            print(e)

        # 类别商品数据

        for c in categories:
            # 查询当前类别所有的文字商品和图片商品
            text_skus = IndexCategoryGoods.objects.filter(
                category=c, display_type=0).order_by('index')
            # 查询某一类别下的图片类别商品
            img_skus = IndexCategoryGoods.objects.filter(
                category=c, display_type=1).order_by('index')

            # 动态地给类别新增实例属性
            c.text_skus = text_skus
            # 动态地给类别新增实例属性
            c.img_skus = img_skus

        # 购物车商品数量
        cart_count = 0

        # 定义模板显示的数据
        context = {
            'categories':categories,
            'slide_goods':slide_goods,
            'promotions':promotions,
            'cart_count':cart_count,
        }

        # 响应请求,显示模板
        return render(request, 'index.html', context)
