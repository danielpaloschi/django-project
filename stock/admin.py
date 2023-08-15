from django.contrib import admin
from .models import Stock, DayDataStock, User
from django.contrib.auth.admin import UserAdmin

fields = list(UserAdmin.fieldsets)
fields.append(
    ("Stocks", {'fields': ('stocks_symbols','profile_pic',)})
)
UserAdmin.fieldsets = tuple(fields)


# Register your models here.
admin.site.register(Stock)
admin.site.register(DayDataStock)
admin.site.register(User, UserAdmin)
#