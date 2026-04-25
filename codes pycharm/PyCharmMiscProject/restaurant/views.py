from   django.shortcuts import render
from .models import Product

def menu_view(request): # <-- Vérifie bien ce nom
    plats = Product.objects.all()
    return render(request, 'restaurant/menu.html', {'plats': plats})
def home_view(request):
    return render(request, 'restaurant/home.html')
# Create your views here.

