from django import forms
from .models import User, Role, EmployeeProfile, Product, Stock, Recipe, RecipeIngredient, Order, Delivery

W = lambda t,**kw: {'class':'form-control','placeholder':t,**kw}
WS = lambda: {'class':'form-select'}

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs=W('Nom utilisateur')))
    password = forms.CharField(widget=forms.PasswordInput(attrs=W('Mot de passe')))

class UserCreateForm(forms.ModelForm):
    password  = forms.CharField(widget=forms.PasswordInput(attrs=W('Mot de passe')))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=W('Confirmer')),label='Confirmer')
    role      = forms.ModelChoiceField(queryset=Role.objects.all(), widget=forms.Select(attrs=WS()))
    class Meta:
        model=User; fields=['username','email','first_name','last_name']
        widgets={f:forms.TextInput(attrs=W(f)) for f in ['username','email','first_name','last_name']}
    def clean(self):
        d=super().clean()
        if d.get('password')!=d.get('password2'):
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return d

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product; fields=['name','price','description','category','is_available','image']
        widgets={
            'name':forms.TextInput(attrs=W('Nom du plat')),
            'price':forms.NumberInput(attrs={**W('Prix FCFA'),'min':'0','step':'50'}),
            'description':forms.Textarea(attrs={**W('Description'),'rows':'3'}),
            'category':forms.Select(attrs=WS()),
            'is_available':forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
    def clean_price(self):
        p=self.cleaned_data.get('price')
        if p is not None and p<=0: raise forms.ValidationError('Le prix doit etre > 0 FCFA.')
        return p

class StockForm(forms.ModelForm):
    class Meta:
        model=Stock; fields=['item_name','quantity','unit','threshold','product']
        widgets={
            'item_name':forms.TextInput(attrs=W('Nom article')),
            'quantity':forms.NumberInput(attrs={**W('Quantite'),'min':'0','step':'0.1'}),
            'unit':forms.Select(attrs=WS()),
            'threshold':forms.NumberInput(attrs={**W('Seuil'),'min':'0'}),
            'product':forms.Select(attrs=WS()),
        }

class StockUpdateForm(forms.Form):
    quantity = forms.FloatField(min_value=0,
        widget=forms.NumberInput(attrs={**W('Nouvelle quantite'),'min':'0','step':'0.1'}))

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model=EmployeeProfile; fields=['phone','salary','department']
        widgets={
            'phone':forms.TextInput(attrs=W('Telephone')),
            'salary':forms.NumberInput(attrs={**W('Salaire FCFA'),'min':'0'}),
            'department':forms.Select(attrs=WS()),
        }
