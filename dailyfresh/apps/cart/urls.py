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

from apps.cart.views import CartAddView, CartUpdateView, CartDeleteView, CartInfoView

urlpatterns = [
    url(r'^add', CartAddView.as_view(), name='add'),
    url(r'^update', CartUpdateView.as_view(), name='update'),
    url(r'^delete', CartDeleteView.as_view(), name='delete'),

    url(r'^$', CartInfoView.as_view(), name='cart'),
]
