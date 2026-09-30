from django.contrib import admin

from .models import Category, IceCream, Topping, Wrapper

admin.site.register([Category, IceCream, Topping, Wrapper])
