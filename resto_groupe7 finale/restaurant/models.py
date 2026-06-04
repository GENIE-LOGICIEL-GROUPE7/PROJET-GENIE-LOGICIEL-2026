from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Role(models.Model):
    role_name   = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.role_name
    class Meta: verbose_name='Role'; verbose_name_plural='Roles'


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='users')
    def __str__(self): return self.username
    class Meta: verbose_name='Utilisateur'; verbose_name_plural='Utilisateurs'


class EmployeeProfile(models.Model):
    DEPT=[('cuisine','Cuisine'),('service','Service'),
          ('direction','Direction'),('stock','Stock'),('admin','Administration')]
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone         = models.CharField(max_length=20, blank=True)
    salary        = models.FloatField(default=0.0)
    hire_date     = models.DateField(auto_now_add=True)
    department    = models.CharField(max_length=50, choices=DEPT, default='service')
    is_active_emp = models.BooleanField(default=True)
    def calculate_payroll(self): return round(self.salary * 0.85, 2)
    def get_monthly_report(self):
        m = timezone.now().month
        orders = Order.objects.filter(waiter=self.user, date__month=m).count()
        return {'employee': self.user.get_full_name() or self.user.username,
                'department': self.department, 'salary': self.salary,
                'net_salary': self.calculate_payroll(), 'orders_served': orders}
    def __str__(self): return f'Profil de {self.user.username}'
    class Meta: verbose_name='Profil Employe'


class Category(models.Model):
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    def __str__(self): return self.label
    class Meta: verbose_name='Categorie'; ordering=['order','label']


class Product(models.Model):
    name         = models.CharField(max_length=200)
    price        = models.FloatField()
    description  = models.TextField(blank=True)
    category     = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_available = models.BooleanField(default=True)
    image        = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    def toggle_availability(self):
        self.is_available = not self.is_available; self.save()
    def __str__(self): return f'{self.name} ({self.price:.0f} FCFA)'
    class Meta: verbose_name='Produit'; ordering=['category','name']


class PriceHistory(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price  = models.FloatField()
    new_price  = models.FloatField()
    changed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.product.name}: {self.old_price}>{self.new_price}'


class Stock(models.Model):
    UNITS=[('kg','kg'),('g','g'),('L','L'),('cl','cl'),('unite','Unite'),('portion','Portion')]
    item_name = models.CharField(max_length=200)
    quantity  = models.FloatField(default=0.0)
    unit      = models.CharField(max_length=20, choices=UNITS, default='unite')
    threshold = models.FloatField(default=10.0)
    product   = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='stocks')
    def update_quantity(self, delta):
        old = self.quantity
        self.quantity = max(0, self.quantity + delta); self.save()
        StockLog.objects.create(stock=self, old_qty=old, new_qty=self.quantity, delta=delta)
        if self.quantity <= self.threshold: self.trigger_alert()
        return self.quantity
    def check_threshold(self): return self.quantity <= self.threshold
    def trigger_alert(self):
        from django.core.mail import send_mail
        try:
            send_mail(f'Alerte Stock: {self.item_name}',
                      f'Quantite: {self.quantity} {self.unit} (seuil: {self.threshold})',
                      'noreply@rms.cm', ['manager@rms.cm'], fail_silently=True)
        except Exception: pass
    def __str__(self): return f'{self.item_name}: {self.quantity} {self.unit}'
    class Meta: verbose_name='Stock'


class StockLog(models.Model):
    stock      = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='logs')
    old_qty    = models.FloatField()
    new_qty    = models.FloatField()
    delta      = models.FloatField()
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.stock.item_name}: {self.old_qty}>{self.new_qty}'
    class Meta: ordering=['-updated_at']


class Recipe(models.Model):
    product      = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='recipe')
    cooking_time = models.IntegerField(default=15)
    chef         = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='recipes')
    instructions = models.TextField(blank=True)
    def check_all_ingredients_available(self):
        return all(ri.check_availability() for ri in self.ingredients.all())
    def __str__(self): return f'Recette: {self.product.name}'
    class Meta: verbose_name='Recette'


class RecipeIngredient(models.Model):
    recipe       = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    stock        = models.ForeignKey(Stock, on_delete=models.PROTECT)
    required_qty = models.FloatField()
    unit         = models.CharField(max_length=20)
    def check_availability(self): return self.stock.quantity >= self.required_qty
    def deduct_from_stock(self):
        if self.check_availability():
            self.stock.update_quantity(-self.required_qty); return True
        return False
    def __str__(self): return f'{self.stock.item_name} ({self.required_qty}{self.unit})'
    class Meta: unique_together=[('recipe','stock')]


class Table(models.Model):
    STATUS=[('available','Disponible'),('occupied','Occupee'),('reserved','Reservee')]
    number   = models.IntegerField(unique=True)
    capacity = models.IntegerField(default=4)
    status   = models.CharField(max_length=20, choices=STATUS, default='available')
    def is_available(self): return self.status == 'available'
    def release(self): self.status='available'; self.save()
    def __str__(self): return f'Table {self.number} ({self.capacity} pers.)'
    class Meta: verbose_name='Table'; ordering=['number']


class Order(models.Model):
    TYPE_CHOICES=[('onsite','Sur place'),('delivery','Livraison'),('takeaway','A emporter')]
    STATUS_CHOICES=[('pending','En attente'),('preparing','En preparation'),
                    ('ready','Pret'),('delivered','Livre/Servi'),
                    ('cancelled','Annule'),('paid','Paye')]
    date         = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.FloatField(default=0.0)
    order_type   = models.CharField(max_length=20, choices=TYPE_CHOICES, default='onsite')
    table        = models.ForeignKey(Table, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
    waiter       = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders_taken')
    notes        = models.TextField(blank=True)
    def calculate_total(self):
        self.total_amount = sum(l.subtotal for l in self.lines.all()); self.save()
        return self.total_amount
    def generate_invoice(self):
        return {'order_id':self.id,'date':self.date.strftime('%d/%m/%Y %H:%M'),
                'type':self.get_order_type_display(),
                'table':str(self.table) if self.table else 'Livraison',
                'waiter':self.waiter.username if self.waiter else '—',
                'lines':[{'product':l.product.name,'qty':l.quantity,
                          'price':l.unit_price,'subtotal':l.subtotal}
                         for l in self.lines.all()],
                'total':self.total_amount}
    def notify_kitchen(self):
        from restaurant.signals import order_ready_signal
        order_ready_signal.send(sender=self.__class__, order=self)
    def __str__(self): return f'Commande #{self.id} - {self.get_status_display()}'
    class Meta: verbose_name='Commande'; ordering=['-date']


class OrderLine(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity   = models.IntegerField(default=1)
    unit_price = models.FloatField(default=0.0)
    subtotal   = models.FloatField(default=0.0)
    def save(self, *args, **kwargs):
        self.unit_price = self.product.price
        self.subtotal   = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    def __str__(self): return f'{self.quantity}x {self.product.name}'
    class Meta: verbose_name='Ligne de Commande'


class Delivery(models.Model):
    STATUS=[('assigned','Assigne'),('en_route','En route'),
            ('arrived','Arrive'),('delivered','Livre'),('failed','Echec')]
    order          = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    address        = models.TextField()
    estimated_time = models.IntegerField(default=30)
    status         = models.CharField(max_length=20, choices=STATUS, default='assigned')
    driver         = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='deliveries')
    delivery_time  = models.DateTimeField(null=True, blank=True)
    def confirm_delivery(self):
        from django.utils import timezone as tz
        self.status='delivered'; self.delivery_time=tz.now(); self.save()
        self.order.status='delivered'; self.order.save()
    def __str__(self): return f'Livraison #{self.id} - Commande #{self.order.id}'
    class Meta: verbose_name='Livraison'


class Revenue(models.Model):
    date           = models.DateField(unique=True)
    total_orders   = models.IntegerField(default=0)
    gross_amount   = models.FloatField(default=0.0)
    supply_expense = models.FloatField(default=0.0)
    @property
    def net_revenue(self): return round(self.gross_amount - self.supply_expense, 2)
    @classmethod
    def get_best_sellers(cls, limit=5):
        from django.db.models import Sum
        return (OrderLine.objects.values('product__name')
                .annotate(total=Sum('quantity')).order_by('-total')[:limit])
    def __str__(self): return f'Revenue {self.date}: {self.gross_amount:.0f} FCFA'
    class Meta: verbose_name='Revenue'; ordering=['-date']
