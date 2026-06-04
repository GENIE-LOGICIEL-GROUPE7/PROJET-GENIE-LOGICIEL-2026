from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (Role, User, EmployeeProfile, Category, Product, PriceHistory,
                     Stock, StockLog, Recipe, RecipeIngredient,
                     Table, Order, OrderLine, Delivery, Revenue)

admin.site.site_header = 'Restaurant Groupe 7 - Administration'
admin.site.site_title  = 'RMS Admin'
admin.site.index_title = 'Panneau de Controle'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_name','description']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['username','email','role','is_active']
    list_filter   = ['role','is_active','is_staff']
    search_fields = ['username','email']
    fieldsets = BaseUserAdmin.fieldsets + (('Role RMS',{'fields':('role',)}),)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display  = ['user','department','salary','hire_date','is_active_emp']
    list_filter   = ['department','is_active_emp']
    list_editable = ['salary','is_active_emp']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['label','order','nb_products']
    list_editable = ['order']
    def nb_products(self,obj): return obj.products.count()
    nb_products.short_description='Produits'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name','category','price','is_available','updated_at']
    list_filter   = ['category','is_available']
    search_fields = ['name']
    list_editable = ['price','is_available']

class RecipeIngredientInline(admin.TabularInline):
    model=RecipeIngredient; extra=2; fields=['stock','required_qty','unit']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display=['product','chef','cooking_time']
    inlines=[RecipeIngredientInline]

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display  = ['item_name','quantity','unit','threshold','alerte','product']
    list_editable = ['quantity','threshold']
    def alerte(self,obj): return '🔴 CRITIQUE' if obj.check_threshold() else '✅ OK'
    alerte.short_description='Alerte'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display=['number','capacity','status']
    list_editable=['status']

class OrderLineInline(admin.TabularInline):
    model=OrderLine; extra=0; readonly_fields=['unit_price','subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ['id','date','waiter','table','order_type','status','total_amount']
    list_filter     = ['status','order_type']
    readonly_fields = ['total_amount','date']
    inlines         = [OrderLineInline]
    actions         = ['mark_ready','mark_delivered']
    def mark_ready(self,req,qs): qs.update(status='ready')
    def mark_delivered(self,req,qs): qs.update(status='delivered')
    mark_ready.short_description='Marquer Pret'
    mark_delivered.short_description='Marquer Livre'

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display=['date','total_orders','gross_amount','supply_expense','get_net']
    def get_net(self,obj): return obj.net_revenue
    get_net.short_description='Net (FCFA)'

for m in [PriceHistory,StockLog,RecipeIngredient,OrderLine,Delivery]:
    admin.site.register(m)
