from django.contrib import admin
from .models import Role, User, EmployeeProfile, Category, Product

admin.site.register(User)
admin.site.register(Role)
admin.site.register(EmployeeProfile)
admin.site.register(Category)
admin.site.register(Product)

# Register your models here.
