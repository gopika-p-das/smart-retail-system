from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.supplier_name

class Customer(models.Model):
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name

    @property
    def total_purchases(self):
        return sum(sale.sales_value for sale in self.sales.all())

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Beverages', 'Beverages'),
        ('Bakery', 'Bakery'),
        ('Snacks', 'Snacks'),
        ('Dairy', 'Dairy'),
        ('Produce', 'Produce'),
        ('Frozen', 'Frozen'),
        ('Meat', 'Meat'),
        ('Health & Beauty', 'Health & Beauty'),
        ('Cleaning Supplies', 'Cleaning Supplies'),
    ]

    DELIVERY_STATUS_CHOICES = [
        ('On Time', 'On Time'),
        ('Delayed', 'Delayed'),
        ('Partial Delivery', 'Partial Delivery'),
    ]

    product_name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Current stock on hand")
    reorder_level = models.PositiveIntegerField(default=20, help_text="Threshold stock level")
    reorder_quantity = models.PositiveIntegerField(default=50, help_text="Default reorder batch quantity")
    delivery_time_days = models.PositiveIntegerField(default=5, help_text="Supplier lead time in days")
    delivery_status = models.CharField(max_length=50, choices=DELIVERY_STATUS_CHOICES, default='On Time')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return 'Critical'
        elif self.stock_quantity <= self.reorder_level:
            return 'Low Stock'
        return 'Normal'

    @property
    def stock_value(self):
        return round(float(self.unit_price) * self.stock_quantity, 2)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    sale_date = models.DateField(default=timezone.now)
    units_sold = models.PositiveIntegerField()
    sales_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.sales_value = round(float(self.product.unit_price) * self.units_sold, 2)
        if not self.pk:
            if self.product.stock_quantity >= self.units_sold:
                self.product.stock_quantity -= self.units_sold
            else:
                self.product.stock_quantity = 0
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.id} - {self.product.product_name} ({self.units_sold} units)"

class PredictionRecord(models.Model):
    RECOMMENDATION_CHOICES = [
        ('REORDER', 'REORDER'),
        ('MAINTAIN', 'MAINTAIN'),
        ('REDUCE', 'REDUCE'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    prediction_date = models.DateTimeField(auto_now_add=True)
    current_stock = models.IntegerField()
    lr_prediction = models.FloatField()
    rf_prediction = models.FloatField()
    predicted_demand = models.FloatField()
    model_used = models.CharField(max_length=50, default='Linear Regression')
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES)
    recommended_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.product_name} - {self.recommendation}"