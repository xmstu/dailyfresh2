from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from celery_tasks.tasks import *
from utils.common import BaseCartView


class IndexView(BaseCartView):

    def get(self, request):
        """显示首页"""

        # 每次访问首页url时就生成首页的静态文件
        generate_static_index_html.delay()
        # 读取缓存:
        context = cache.get('index_page_data')
        if context is None:
            print('没有缓存数据,从mysql中读取')
            # 查询首页中要显示的数据
            # 所有的商品类别
            categories = GoodsCategory.objects.all()

            # 轮播图商品
            slide_skus = IndexSlideGoods.objects.all().order_by('index')

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
                imgs_skus = IndexCategoryGoods.objects.filter(
                    category=c, display_type=1).order_by('index')

                # 动态地给类别新增实例属性
                c.text_skus = text_skus
                # 动态地给类别新增实例属性
                c.imgs_skus = imgs_skus
                # print(img_skus)
                # print('-'*50)
            # 定义模板显示的数据

            context = {
                'categories': categories,
                'slide_skus': slide_skus,
                'promotions': promotions,
            }
        else:
            print('首页:使用缓存')

        cart_count = super().get_cart_count(request)
        # print(cart_count)

        # 更新context字典添加cart_count的值
        context.update(cart_count=cart_count)

        # 响应请求,显示模板
        return render(request, 'index.html', context)


class DetailView(BaseCartView):
    """商品详情界面"""

    def get(self, request, sku_id):

        # print(sku_id)
        # print('+'*50)

        # 查询数据库中的数据
        # 所有的类别
        categories = GoodsCategory.objects.all()

        # 当前要显示的商品sku
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reversed('goods:index'))

        # 新品推荐
        new_skus = GoodsSKU.objects.filter(category=sku.category)\
                    .order_by('-create_time')[0:2]  # 取出最新添加两个数据作为新品推荐(列表切片)
        # 详情

        # todo:其他规格的商品sku
        other_skus = GoodsSKU.objects.filter(spu=sku.spu).exclude(id=sku_id)
        # print(other_skus)
        # print('='*50)

        # 通过BaseCartView的get_cart_count方法获取cart_count数量
        cart_count = super().get_cart_count(request)

        # todo:保存用户浏览的商品记录到redis中
        strict_redis = get_redis_connection('default')
        key = 'history_%s' % request.user.id
        # 先删除列表中已经存在的商品id;
        # 防止这种情况:用户重复点击同一样商品,那么按业务逻辑来说,不应该直接添加该历史记录,应该先删已经存在的商品id的历史记录
        strict_redis.lrem(key, 0, sku_id)
        # 删除重复的商品历史记录后,再添加新的历史记录到列表的左侧,确保列表去重
        strict_redis.lpush(key, sku_id)
        # 最多保存5个商品浏览记录(包含头尾)
        strict_redis.ltrim(key, 0, 4)

        # category_name = sku.category.name
        # print(category_name)
        # print('='*50)

        # todo:保存用户浏览的商品记录到redis中
        context = {
            'sku': sku,
            'categories':categories,
            'new_skus':new_skus,
            'cart_count':cart_count,
            'other_skus':other_skus,
        }

        return render(request, 'detail.html', context)


class ListView(BaseCartView):
    """商品列表界面"""

    def get(self, request, category_id, page_num):

        # 获取请求参数:获取排序条件
        sort = request.GET.get('sort')
        # todo:查询数据库中的数据
        # 所有的类别
        categories = GoodsCategory.objects.all()
        # 当前类别对象
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return redirect(reversed('goods:index'))

        # 当前类别所有的商品
        if sort == 'price':
            skus = GoodsSKU.objects.filter(category=category).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(category=category).order_by('-sales')
        else:
            skus = GoodsSKU.objects.filter(category=category)
            sort = 'default'

        # 创建分页对象
        # 参数1：所有数据
        # 参数2：每页显示多少条
        paginator = Paginator(skus, 5)
        # 页码列表:[1,2,3,4]
        page_range = paginator.page_range
        try:
            page = paginator.page(page_num)
        except EmptyPage:
            page = paginator.page(1)

        # 新品推荐
        new_skus = GoodsSKU.objects.filter(category=category)\
                    .order_by('-create_time')[0:2]

        # 获取购物车商品数量
        cart_count = super().get_cart_count(request)

        # 分页数据

        context = {
            'category':category,
            'categories':categories,
            'page':page,
            'new_skus':new_skus,
            'cart_count':cart_count,
            'page_range':page_range,
            'sort':sort,
        }

        return render(request, 'list.html', context)