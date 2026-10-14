import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Product, Supplier, Customer, Sale, PredictionRecord
from .forms import ProductForm, SupplierForm, CustomerForm, SaleForm
from .ml_service import predict_and_optimize

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml_model', 'supermarket_demand_model.pkl')

# ================= AUTHENTICATION =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'inventory/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# ================= DASHBOARD =================
@login_required(login_url='login')
def dashboard(request):
    products = Product.objects.all()
    sales = Sale.objects.all().order_by('-sale_date')[:10]

    total_products = products.count()
    total_stock = products.aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    total_sales_value = Sale.objects.aggregate(Sum('sales_value'))['sales_value__sum'] or 0.0

    low_stock_products = [p for p in products if p.stock_quantity <= p.reorder_level]
    low_stock_count = len(low_stock_products)

    reorder_required_count = 0
    total_predicted_demand = 0.0

    for p in products:
        try:
            opt = predict_and_optimize(p)
            total_predicted_demand += opt['predicted_demand']
            if opt['recommendation'] == 'REORDER':
                reorder_required_count += 1
        except Exception:
            pass

    category_data = products.values('category').annotate(total=Sum('stock_quantity'))
    cat_labels = [c['category'] for c in category_data]
    cat_values = [c['total'] for c in category_data]

    top_selling = Sale.objects.values('product__product_name').annotate(total_sold=Sum('units_sold')).order_by('-total_sold')[:5]
    sales_labels = [s['product__product_name'] for s in top_selling]
    sales_values = [s['total_sold'] for s in top_selling]

    context = {
        'total_products': total_products,
        'total_stock': total_stock,
        'total_sales_value': round(float(total_sales_value), 2),
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5],
        'total_predicted_demand': round(total_predicted_demand, 1),
        'reorder_required_count': reorder_required_count,
        'recent_sales': sales,
        'cat_labels': json.dumps(cat_labels),
        'cat_values': json.dumps(cat_values),
        'sales_labels': json.dumps(sales_labels),
        'sales_values': json.dumps(sales_values),
    }
    return render(request, 'inventory/dashboard.html', context)

# ================= PRODUCTS =================
@login_required(login_url='login')
def products_list(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    products = Product.objects.all().order_by('-created_at')
    if query:
        products = products.filter(product_name__icontains=query)
    if category_filter:
        products = products.filter(category=category_filter)

    product_items = []
    for p in products:
        if status_filter and p.stock_status != status_filter:
            continue
        product_items.append(p)

    categories = [c[0] for c in Product.CATEGORY_CHOICES]
    return render(request, 'inventory/products.html', {
        'products': product_items,
        'categories': categories,
        'query': query,
        'selected_category': category_filter,
        'selected_status': status_filter
    })

@login_required(login_url='login')
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('products_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add New Product'})

@login_required(login_url='login')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.product_name}' updated!")
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required(login_url='login')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.product_name
    product.delete()
    messages.info(request, f"Product '{name}' deleted.")
    return redirect('products_list')

# ================= SALES =================
@login_required(login_url='login')
def sales_list(request):
    query = request.GET.get('q', '')
    sales = Sale.objects.all().order_by('-sale_date')
    if query:
        sales = sales.filter(product__product_name__icontains=query)
    return render(request, 'inventory/sales.html', {'sales': sales, 'query': query})

@login_required(login_url='login')
def sale_add(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            messages.success(request, f"Sale recorded! Stock updated. Current stock: {sale.product.stock_quantity}")
            return redirect('sales_list')
    else:
        form = SaleForm()
    return render(request, 'inventory/sale_form.html', {'form': form, 'title': 'Record New Sale'})

@login_required(login_url='login')
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale.delete()
    messages.info(request, "Sale record deleted.")
    return redirect('sales_list')

# ================= SUPPLIERS =================
@login_required(login_url='login')
def suppliers_list(request):
    query = request.GET.get('q', '')
    suppliers = Supplier.objects.all().order_by('-created_at')
    if query:
        suppliers = suppliers.filter(supplier_name__icontains=query)
    return render(request, 'inventory/suppliers.html', {'suppliers': suppliers, 'query': query})

@login_required(login_url='login')
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully!")
            return redirect('suppliers_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required(login_url='login')
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.supplier_name}' updated!")
            return redirect('suppliers_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required(login_url='login')
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    messages.info(request, "Supplier deleted.")
    return redirect('suppliers_list')

# ================= CUSTOMERS =================
@login_required(login_url='login')
def customers_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.all().order_by('-created_at')
    if query:
        customers = customers.filter(customer_name__icontains=query)
    return render(request, 'inventory/customers.html', {'customers': customers, 'query': query})

@login_required(login_url='login')
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully!")
            return redirect('customers_list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required(login_url='login')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.info(request, "Customer deleted.")
    return redirect('customers_list')

# ================= DEMAND PREDICTION =================
@login_required(login_url='login')
def demand_prediction(request):
    products = Product.objects.all()
    selected_product = None
    prediction_result = None

    product_id = request.GET.get('product_id')
    if product_id:
        selected_product = get_object_or_404(Product, pk=product_id)
        recent_sales_units = selected_product.sales.aggregate(Sum('units_sold'))['units_sold__sum'] or 0
        try:
            prediction_result = predict_and_optimize(selected_product)
            prediction_result['recent_sales'] = recent_sales_units
            PredictionRecord.objects.create(
                product=selected_product,
                current_stock=selected_product.stock_quantity,
                lr_prediction=prediction_result['lr_prediction'],
                rf_prediction=prediction_result['rf_prediction'],
                predicted_demand=prediction_result['predicted_demand'],
                recommendation=prediction_result['recommendation'],
                recommended_quantity=prediction_result['recommended_quantity']
            )
        except Exception as e:
            messages.error(request, f"Prediction error: {str(e)}")

    return render(request, 'inventory/demand_prediction.html', {
        'products': products,
        'selected_product': selected_product,
        'res': prediction_result
    })

# ================= INVENTORY OPTIMIZATION =================
@login_required(login_url='login')
def inventory_optimization(request):
    products = Product.objects.all()
    recom_filter = request.GET.get('recommendation', '')

    items = []
    reorder_count = 0
    overstocked_count = 0
    estimated_restock_cost = 0.0

    for p in products:
        try:
            opt = predict_and_optimize(p)
        except Exception:
            opt = {
                'predicted_demand': 0, 'lr_prediction': 0, 'rf_prediction': 0,
                'current_stock': p.stock_quantity, 'stock_difference': 0,
                'recommendation': 'MAINTAIN', 'recommended_quantity': 0,
                'stock_status': p.stock_status
            }

        if opt['recommendation'] == 'REORDER':
            reorder_count += 1
            estimated_restock_cost += float(opt.get('recommended_quantity', 0)) * float(p.unit_price)
        elif opt['recommendation'] == 'REDUCE':
            overstocked_count += 1

        if recom_filter and opt['recommendation'] != recom_filter:
            continue
        items.append({'product': p, 'opt': opt})

    total_products = products.count()
    healthy_stock_count = total_products - (reorder_count + overstocked_count)
    health_rate = round((healthy_stock_count / total_products * 100), 1) if total_products > 0 else 100

    return render(request, 'inventory/inventory_optimization.html', {
        'items': items,
        'selected_recom': recom_filter,
        'reorder_count': reorder_count,
        'overstocked_count': overstocked_count,
        'estimated_restock_cost': round(estimated_restock_cost, 2),
        'health_rate': health_rate,
    })

@login_required(login_url='login')
def optimization_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        opt = predict_and_optimize(product)
    except Exception:
        opt = {
            'predicted_demand': 0, 'lr_prediction': 0, 'rf_prediction': 0,
            'current_stock': product.stock_quantity, 'stock_difference': 0,
            'recommendation': 'MAINTAIN', 'recommended_quantity': 0,
            'stock_status': product.stock_status
        }

    max_val = max(opt['current_stock'], opt['predicted_demand'], 1)
    stock_bar = min(100, int((opt['current_stock'] / max_val) * 100))
    demand_bar = min(100, int((opt['predicted_demand'] / max_val) * 100))

    return render(request, 'inventory/optimization_detail.html', {
        'product': product,
        'opt': opt,
        'stock_bar': stock_bar,
        'demand_bar': demand_bar
    })

# ================= REPORTS =================
@login_required(login_url='login')
def reports_view(request):
    report_type = request.GET.get('type', 'sales')
    products = Product.objects.all()
    sales = Sale.objects.all().order_by('-sale_date')
    low_stock = [p for p in products if p.stock_quantity <= p.reorder_level]

    predictions = []
    for p in products:
        try:
            predictions.append({'product': p, 'opt': predict_and_optimize(p)})
        except Exception:
            pass

    return render(request, 'inventory/reports.html', {
        'report_type': report_type,
        'sales': sales,
        'products': products,
        'low_stock': low_stock,
        'predictions': predictions
    })