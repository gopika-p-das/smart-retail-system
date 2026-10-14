from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Products & Inventory
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/add/', views.sale_add, name='sale_add'),
    path('sales/delete/<int:pk>/', views.sale_delete, name='sale_delete'),

    # Suppliers
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/edit/<int:pk>/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete, name='supplier_delete'),

    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),

    # ML & Optimization
    path('demand-prediction/', views.demand_prediction, name='demand_prediction'),
    path('inventory-optimization/', views.inventory_optimization, name='inventory_optimization'),
    path('inventory-optimization/<int:pk>/', views.optimization_detail, name='optimization_detail'),

    # Reports
    path('reports/', views.reports_view, name='reports'),
]