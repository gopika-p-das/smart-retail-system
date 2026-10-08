from django import forms
from .models import Product, Supplier, Customer, Sale

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name', 'category', 'supplier', 'unit_price',
            'stock_quantity', 'reorder_level', 'reorder_quantity',
            'delivery_time_days', 'delivery_status'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20', 'min': '0'}),
            'reorder_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50', 'min': '1'}),
            'delivery_time_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5', 'min': '1'}),
            'delivery_status': forms.Select(attrs={'class': 'form-select'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'contact_number', 'email', 'address']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Company Name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'supplier@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'phone', 'email']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'sale_date', 'units_sold']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'units_sold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of units', 'min': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        units_sold = cleaned_data.get('units_sold')

        if product and units_sold:
            if units_sold > product.stock_quantity:
                raise forms.ValidationError(f"Cannot sell {units_sold} units! Only {product.stock_quantity} available in stock.")
        return cleaned_data