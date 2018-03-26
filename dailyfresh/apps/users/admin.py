from django.contrib import admin

# Register your models here.
from apps.users.models import *

admin.site.register(TestModel)
admin.site.register(User)