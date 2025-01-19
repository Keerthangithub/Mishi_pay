# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Supplier, SaleOrder, StockMovement
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from decimal import Decimal


def index(request):
    sale_orders = SaleOrder.objects.all()  # or whatever query fits your use case
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    stock_movements = StockMovement.objects.all()
    context={
        'sale_orders':sale_orders,
        'products':products,
        'suppliers':suppliers,
        'stock_movements':stock_movements,
    }
    return render(request, 'index.html', context)


# Add Product
def add_product(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = float(request.POST.get('price'))
        stock_quantity = request.POST.get('stock_quantity')
        supplier_id = request.POST.get('supplier')

        # Validation for duplicate product
        if Product.objects.filter(name=name).exists():
            messages.error(request, "Product with this name already exists.")
            return redirect('add_product')

        try:
            supplier = Supplier.objects.get(id=supplier_id)
            
            product = Product(
                name=name,
                description=description,
                category=category,
                price=float(price),
                stock_quantity=int(stock_quantity),
                supplier=supplier
            )
            print("stock_quantity",type(product.stock_quantity))
            print("price",type(product.price))
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('list_products')
        except Supplier.DoesNotExist:
            messages.error(request, "Invalid supplier selected.")

    suppliers = Supplier.objects.all()
    return render(request, 'add_product.html', {'suppliers': suppliers})

# List Products
def list_products(request):
    products = Product.objects.all()
    for i in products:
        print("dt",type(i.stock_quantity))
    return render(request, 'list_products.html', {'products': products})

def add_supplier(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Check for duplicate email and phone
        if Supplier.objects.filter(email=email).exists():
            messages.error(request, "A supplier with this email already exists.")
            return redirect('add_supplier')
        
        if Supplier.objects.filter(phone=phone).exists():
            messages.error(request, "A supplier with this phone number already exists.")
            return redirect('add_supplier')

        # Validate email format
        try:
            EmailValidator()(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('add_supplier')

        # Add supplier to the database
        supplier = Supplier.objects.create(name=name, email=email, phone=phone, address=address)
        messages.success(request, f'Supplier {name} added successfully.')
        return redirect('list_suppliers')
    
    return render(request, 'add_supplier.html')

def list_suppliers(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers
    }
    return render(request, 'list_suppliers.html', context)


def add_stock_movement(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        movement_type = request.POST.get('movement_type')
        notes = request.POST.get('notes')
        print(type(quantity))
        quantity = float(quantity)
        print("quantity",type(quantity),quantity)
        try:
            product = Product.objects.get(id=product_id)

            # Validation: Ensure stock doesn't go negative for outgoing stock
            print('e1')
            if movement_type == 'Out' and int(product.stock_quantity) < int(quantity):
                messages.error(request, "Not enough stock to fulfill the outgoing movement.")
                return redirect('add_stock_movement')

            # Update the stock quantity based on movement type
            if movement_type == 'In':
                print("error-2")
                print("quantity",type(quantity))
                print("product.stock_quantity",type(product.stock_quantity))
                product.stock_quantity += quantity
                print("the end")
                
            elif movement_type == 'Out':
                product.stock_quantity -= quantity

            # Save updated product

            product.price = float(str(product.price))
            product.save()
            print('e2-after save')
            # Create a new stock movement entry
            StockMovement.objects.create(
                product=product,
                quantity=quantity,
                movement_type=movement_type,
                notes=notes
            )

            messages.success(request, f"Stock movement ({movement_type}) recorded successfully.")
            return redirect('list_products')  # Redirect to product list after adding stock movement

        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('add_stock_movement')

    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'add_stock_movement.html', context)

from bson import Decimal128
# Create Sale Order
def create_sale_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        try:
            product = Product.objects.get(id=product_id)

            # Ensure there is enough stock for the sale
            if product.stock_quantity < quantity:
                messages.error(request, "Not enough stock for this sale.")
                return redirect('create_sale_order')

            # Calculate total price
            # print('price',type(product.price))
            # print('quantity',type(quantity))
            # print('total_price',type(product.price * quantity))
            # print('total_price',type(total_price))
            total_price = float(str(product.price))  * quantity

            # Create SaleOrder object
            sale_order = SaleOrder.objects.create(
                product=product,
                quantity=quantity,
                total_price=total_price,
                status='Pending'  # Default status
            )

            # Update product stock
            product.stock_quantity=product.stock_quantity - quantity
            product.price = float(str(product.price))
            product.save()

            messages.success(request, f"Sale order {sale_order.id} created successfully.")
            return redirect('list_sale_orders')

        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('create_sale_order')

    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'create_sale_order.html', context)

# List Sale Orders
def list_sale_orders(request):
    sale_orders = SaleOrder.objects.all()
    context = {
        'sale_orders': sale_orders
    }
    return render(request, 'list_sale_orders.html', context)


# Cancel Sale Order
def cancel_sale_order(request, order_id):
    try:
        sale_order = SaleOrder.objects.get(id=order_id)

        # Update the sale order status
        sale_order.status = 'Cancelled'
        sale_order.save()

        # Revert the stock level back
        product = sale_order.product
        product.stock_quantity += sale_order.quantity
        product.save()

        messages.success(request, f"Sale order {order_id} has been cancelled.")
        return redirect('list_sale_orders')

    except SaleOrder.DoesNotExist:
        messages.error(request, "Sale order not found.")
        return redirect('list_sale_orders')


def complete_sale_order(request, order_id):
    try:
        sale_order = SaleOrder.objects.get(id=order_id)

        # Update the sale order status
        sale_order.status = 'Completed'
        sale_order.save()

        # Stock is already deducted when the order was created, so no further action needed
        messages.success(request, f"Sale order {order_id} has been completed.")
        return redirect('list_sale_orders')

    except SaleOrder.DoesNotExist:
        messages.error(request, "Sale order not found.")
        return redirect('list_sale_orders')


# Stock Level Check
def stock_level_check(request):
    # products = Product.objects.annotate(total_stock=Sum('stock_quantity'))
    products = Product.objects.all()
    
    context = {
        'products': products
    }
    return render(request, 'stock_level_check.html', {'products': products})