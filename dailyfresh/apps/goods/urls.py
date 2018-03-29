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
from django.contrib import admin

from apps.goods import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index', views.IndexView.as_view(), name='index'),
    url(r'^detail/(?P<sku_id>\d+)$', views.DetailView.as_view(), name='detail'),
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)$', views.ListView.as_view(), name='list'),
]
