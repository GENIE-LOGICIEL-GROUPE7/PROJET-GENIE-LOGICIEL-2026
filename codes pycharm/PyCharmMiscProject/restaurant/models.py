from django.db import models
from django.contrib.auth.models import AbstractUser


# --- MODULE 5.1 : USER & ROLE ---
class Role(models.Model):
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)


groups = models.ManyToManyField(
    'auth.Group',
    related_name='restaurant_user_groups',  # Un nom unique
    blank=True
)
user_permissions = models.ManyToManyField(
    'auth.Permission',
    related_name='restaurant_user_permissions',  # Un nom unique
    blank=True
)


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    salary = models.FloatField()
    hire_date = models.CharField(max_length=50)


# --- MODULE 5.3 : PRODUCT & CATEGORY ---
class Category(models.Model):
    Label = models.CharField(max_length=100)

    def __str__(self):
        return self.Label


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Create your models here.
