import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.core.cache import cache
from django.utils import timezone
from django.http import JsonResponse
from .models import (User, Role, EmployeeProfile, Category, Product, PriceHistory,
                     Stock, StockLog, Recipe, RecipeIngredient,
                     Table, Order, OrderLine, Delivery, Revenue)
from .forms import (LoginForm, UserCreateForm, ProductForm, StockForm,
                    StockUpdateForm, EmployeeProfileForm)

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        if user and user.is_active:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.username} !')
            return redirect(request.GET.get('next','dashboard'))
        messages.error(request, 'Identifiants invalides.')
    return render(request, 'auth/login.html', {'form':form})

@login_required
def logout_view(request):
    logout(request); messages.info(request,'Deconnexion reussie.'); return redirect('login')

@login_required
def user_list(request):
    users = User.objects.select_related('role','profile').all()
    return render(request,'auth/user_list.html',{'users':users})

@login_required
@transaction.atomic
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        if User.objects.filter(username=form.cleaned_data['username']).exists():
            messages.error(request,"Ce nom d'utilisateur existe deja.")
        else:
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = form.cleaned_data.get('role')
            user.save()
            EmployeeProfile.objects.create(user=user)
            messages.success(request,f'Utilisateur {user.username} cree.')
            return redirect('user_list')
    return render(request,'auth/user_form.html',{'form':form})

def menu_view(request):
    categories = (Category.objects.prefetch_related('products')
                  .filter(products__is_available=True).distinct().order_by('order'))
    return render(request,'menu/menu.html',{'categories':categories})

@login_required
def product_list(request):
    categories = Category.objects.prefetch_related('products').all()
    return render(request,'products/list.html',{'categories':categories})

@login_required
@transaction.atomic
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method=='POST' and form.is_valid():
        p = form.save()
        messages.success(request,f'Produit {p.name} cree (#{p.id}).')
        return redirect('product_list')
    return render(request,'products/form.html',{'form':form,'title':'Ajouter un Produit'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method=='POST' and form.is_valid():
        old_price = product.price
        product = form.save()
        if old_price != product.price:
            PriceHistory.objects.create(product=product,old_price=old_price,new_price=product.price)
        messages.success(request,f'Produit {product.name} modifie.')
        return redirect('product_list')
    return render(request,'products/form.html',{'form':form,'title':'Modifier','product':product})

@login_required
def product_toggle(request, pk):
    p = get_object_or_404(Product, pk=pk); p.toggle_availability()
    messages.info(request,f'{p.name} est maintenant {"disponible" if p.is_available else "indisponible"}.')
    return redirect('product_list')

@login_required
def product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method=='POST':
        name=p.name; p.delete()
        messages.success(request,f'Produit {name} supprime.'); return redirect('product_list')
    return render(request,'products/confirm_delete.html',{'product':p})

@login_required
def recipe_manage(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    recipe, _ = Recipe.objects.get_or_create(product=product)
    stocks = Stock.objects.all()
    if request.method=='POST':
        action = request.POST.get('action')
        if action=='save_recipe':
            recipe.cooking_time=int(request.POST.get('cooking_time',15))
            recipe.instructions=request.POST.get('instructions',''); recipe.save()
            messages.success(request,'Recette sauvegardee.')
        elif action=='add_ingredient':
            sid=request.POST.get('stock_id'); qty=request.POST.get('required_qty',0)
            unit=request.POST.get('unit','g')
            if sid and float(qty)>0:
                stock=get_object_or_404(Stock,id=sid)
                RecipeIngredient.objects.update_or_create(
                    recipe=recipe,stock=stock,defaults={'required_qty':float(qty),'unit':unit})
                messages.success(request,'Ingredient ajoute.')
        elif action=='remove_ingredient':
            RecipeIngredient.objects.filter(id=request.POST.get('ri_id'),recipe=recipe).delete()
            messages.info(request,'Ingredient retire.')
    return render(request,'recipes/form.html',{'recipe':recipe,'product':product,'stocks':stocks})

@login_required
def table_list(request):
    return render(request,'orders/tables.html',{'tables':Table.objects.all()})

@login_required
def order_list(request):
    orders=Order.objects.select_related('table','waiter').prefetch_related('lines').all()[:50]
    return render(request,'orders/list.html',{'orders':orders})

@login_required
@transaction.atomic
def order_create(request):
    tables   = Table.objects.filter(status='available')
    products = Product.objects.filter(is_available=True).select_related('category')
    if request.method=='POST':
        table_id=request.POST.get('table_id'); order_type=request.POST.get('order_type','onsite')
        product_ids=request.POST.getlist('product_id'); quantities=request.POST.getlist('quantity')
        notes=request.POST.get('notes','')
        if not product_ids:
            messages.error(request,'Ajoutez au moins un produit.')
            return render(request,'orders/create.html',{'tables':tables,'products':products})
        order=Order.objects.create(table_id=table_id if table_id else None,
                                   waiter=request.user,order_type=order_type,notes=notes)
        if table_id: Table.objects.filter(id=table_id).update(status='occupied')
        for pid,qty in zip(product_ids,quantities):
            qty=int(qty)
            if qty<=0: continue
            product=get_object_or_404(Product,id=pid)
            stock=product.stocks.first()
            if stock and stock.quantity<qty:
                raise ValueError(f'Stock insuffisant pour {product.name}')
            if stock: stock.update_quantity(-qty)
            OrderLine.objects.create(order=order,product=product,quantity=qty)
        order.calculate_total(); order.notify_kitchen()
        messages.success(request,f'Commande #{order.id} creee !')
        return redirect('order_detail',pk=order.id)
    return render(request,'orders/create.html',{'tables':tables,'products':products})

@login_required
def order_detail(request, pk):
    order=get_object_or_404(Order,pk=pk)
    return render(request,'orders/detail.html',{'order':order,'invoice':order.generate_invoice()})

@login_required
def kitchen_view(request):
    orders=(Order.objects.filter(status__in=['pending','preparing'])
            .prefetch_related('lines__product').order_by('date'))
    return render(request,'orders/kitchen.html',{'orders':orders})

@login_required
def order_update_status(request, pk):
    order=get_object_or_404(Order,pk=pk)
    if request.method=='POST':
        ns=request.POST.get('status')
        valid=dict(Order.STATUS_CHOICES)
        if ns in valid:
            order.status=ns; order.save()
            if ns=='delivered' and order.table: order.table.release()
            messages.success(request,f'Statut: {valid[ns]}')
    return redirect(request.POST.get('next','kitchen_view'))

@login_required
def stock_list(request):
    stocks=Stock.objects.select_related('product').all()
    alerts=[s for s in stocks if s.check_threshold()]
    return render(request,'stock/list.html',{'stocks':stocks,'alerts':alerts})

@login_required
def stock_create(request):
    form=StockForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        s=form.save(); messages.success(request,f'Article {s.item_name} ajoute.')
        return redirect('stock_list')
    return render(request,'stock/form.html',{'form':form,'title':'Ajouter un Article'})

@login_required
def stock_update(request, pk):
    stock=get_object_or_404(Stock,pk=pk)
    if request.method=='POST':
        form=StockUpdateForm(request.POST)
        if form.is_valid():
            new_qty=form.cleaned_data['quantity']; delta=new_qty-stock.quantity
            stock.update_quantity(delta)
            messages.success(request,f'Stock {stock.item_name} = {new_qty} {stock.unit}')
            return redirect('stock_list')
    else:
        form=StockUpdateForm(initial={'quantity':stock.quantity})
    return render(request,'stock/update.html',{'stock':stock,'form':form})

@login_required
def stock_history(request, pk):
    stock=get_object_or_404(Stock,pk=pk)
    return render(request,'stock/history.html',{'stock':stock,'logs':stock.logs.order_by('-updated_at')[:50]})

@login_required
def hr_dashboard(request):
    employees=EmployeeProfile.objects.select_related('user').filter(is_active_emp=True)
    reports=[emp.get_monthly_report() for emp in employees]
    total=sum(r['net_salary'] for r in reports)
    return render(request,'hr/dashboard.html',{'employees':employees,'reports':reports,'total_payroll':total})

@login_required
def employee_detail(request, pk):
    emp=get_object_or_404(EmployeeProfile,pk=pk)
    orders=Order.objects.filter(waiter=emp.user).order_by('-date')[:10]
    return render(request,'hr/employee.html',{'emp':emp,'report':emp.get_monthly_report(),'orders':orders})

@login_required
def employee_edit(request, pk):
    emp=get_object_or_404(EmployeeProfile,pk=pk)
    form=EmployeeProfileForm(request.POST or None,instance=emp)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,'Profil mis a jour.')
        return redirect('employee_detail',pk=pk)
    return render(request,'hr/employee_form.html',{'form':form,'emp':emp})

@login_required
def dashboard(request):
    ck=f"dash_{timezone.now().strftime('%Y-%m-%d')}"
    data=cache.get(ck)
    if not data:
        today=timezone.now().date(); ot=Order.objects.filter(date__date=today)
        data={'total_today':float(ot.aggregate(t=Sum('total_amount'))['t'] or 0),
              'orders_count':ot.count(),'pending_count':ot.filter(status='pending').count(),
              'stock_alerts':Stock.objects.filter(quantity__lte=0).count(),
              'best_sellers':list(Revenue.get_best_sellers()),
              'monthly_revenue':list(Order.objects.filter(date__year=today.year)
                  .values('date__month').annotate(total=Sum('total_amount')).order_by('date__month'))}
        cache.set(ck,data,timeout=300)
    recent=Order.objects.select_related('waiter','table').order_by('-date')[:8]
    return render(request,'dashboard/index.html',
                  {'data':json.dumps(data,default=str),'raw':data,'recent_orders':recent})

@login_required
def dashboard_api(request):
    today=timezone.now().date()
    data={'monthly_revenue':list(Order.objects.filter(date__year=today.year)
              .values('date__month').annotate(total=Sum('total_amount')).order_by('date__month')),
          'best_sellers':list(Revenue.get_best_sellers())}
    return JsonResponse(data,safe=False)
# === AJOUTER CES 2 VUES A LA FIN DE views.py ===

def public_order_create(request):
    """Commande publique client - sans connexion requise."""
    categories = (Category.objects.prefetch_related('products')
                  .filter(products__is_available=True).distinct().order_by('order'))
    products = Product.objects.filter(is_available=True)

    if request.method == 'POST':
        order_type  = request.POST.get('order_type', 'onsite')
        product_ids = request.POST.getlist('product_id')
        quantities  = request.POST.getlist('quantity')
        notes       = request.POST.get('notes', '')

        has_items = any(int(q) > 0 for q in quantities if q)
        if not has_items:
            messages.error(request, 'Selectionnez au moins un plat.')
            return render(request, 'orders/public_order.html',
                          {'categories': categories, 'products': products})

        with transaction.atomic():
            order = Order.objects.create(
                waiter=None,
                order_type=order_type,
                notes=notes
            )
            for pid, qty in zip(product_ids, quantities):
                qty = int(qty)
                if qty <= 0:
                    continue
                product = get_object_or_404(Product, id=pid)
                stock = product.stocks.first()
                if stock and stock.quantity < qty:
                    messages.error(request, f'Stock insuffisant pour {product.name}')
                    order.delete()
                    return render(request, 'orders/public_order.html',
                                  {'categories': categories, 'products': products})
                if stock:
                    stock.update_quantity(-qty)
                OrderLine.objects.create(order=order, product=product, quantity=qty)
            order.calculate_total()
            order.notify_kitchen()

        return redirect('public_order_confirm', pk=order.id)

    return render(request, 'orders/public_order.html',
                  {'categories': categories, 'products': products})


def public_order_confirm(request, pk):
    """Page de confirmation commande publique."""
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/public_confirm.html', {'order': order})
