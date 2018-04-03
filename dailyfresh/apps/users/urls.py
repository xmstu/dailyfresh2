"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from apps.users import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^login$', views.LoginView.as_view(), name='login'),         # 登录
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),         # 登出
    url(r'^active/(?P<token>.+)$', views.ActiveView.as_view(), name='active'),#激活

    url(r'^address$', views.UserAddressView.as_view(),name='address'),
    url(r'^orders/(?P<page_num>\d+)$', views.UserOrderView.as_view(),name='orders'),
    url(r'^$', views.UserInfoView.as_view(),name='info'),
]
