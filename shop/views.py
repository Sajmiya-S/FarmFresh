from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from users.views import homepage
from users.models import Customer,Address
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from payment.views import *
import razorpay


            # ========================= #
            # CATEGORY & PRODUCT VIEWS  #
            # ========================= #

# Display all product categories
def categories(request):
    catz = Category.objects.all()
    return render(request, 'catz.html', {'catz': catz})

# Show products belonging to a specific category
def categorywise(request, cid):
    pro = Product.objects.filter(category=cid)
    return render(request, 'cwise.html', {'pro': pro})

# Show all products in random order
def allproducts(request):
    allp = Product.objects.all().order_by('?')
    return render(request, 'allp.html', {'allp': allp})

# Show single product details
def productdetails(request, pid):
    pro = Product.objects.get(id=pid)
    allp = Product.objects.all().order_by('?')[:5]
    recentlyviewed(request,pid)
    rvw = request.session.get('rvw',{})
    rvw_list = []
    for id,item in rvw.items():
        if id != str(pid):
            try:
                p = Product.objects.get(id=id)
                rvw_list.append(p) 
            except Product.DoesNotExist:
                continue
    return render(request, 'prodetails.html', {'pro': pro, 'allp': allp,'rvw':rvw_list})


# Show recently viewed Products
def recentlyviewed(request,pid):
    pro = Product.objects.get(id=pid)
    rvw = request.session.get('rvw',{})
    pid =str(pid)

    rvw.pop(pid, None)

    rvw[pid] = {
        'name': pro.name,
        'price': float(pro.price),
        'pic': pro.pic.url
    }

    if len(rvw) > 5:
        rvw.pop(next(iter(rvw))) 

    request.session['rvw'] = rvw



            # ========================= #
            #      CART MANAGEMENT      #
            # ========================= #

# Add product to cart or Buy Now(Increases quantity if item already exists)
@login_required(login_url='/login')
def addtocart(request, pid):
    customer = Customer.objects.get(customer=request.user)
    cart = Cart.objects.get(customer=customer)
    pro = Product.objects.get(id=pid)

    qty = int(request.POST.get('quantity', 1))
    action = request.POST.get('action')

    if action == 'cart':
        item, created = CartItem.objects.get_or_create(cart=cart, product=pro)
        item.quantity = item.quantity + qty if not created else qty
        item.save()
        messages.success(request, 'Item added to the cart')
        return redirect(productdetails,pid)
    elif action == 'buy':
        return redirect(f'{reverse('porder')}?pid={pro.id}&qty={qty}')
    return redirect(allproducts)

# Display all cart items
@login_required(login_url='/login')
def viewcart(request):
    customer = Customer.objects.get(customer=request.user)
    cart = Cart.objects.get(customer=customer)
    items = CartItem.objects.filter(cart=cart)
    return render(request, 'mycart.html', {'items': items, 'cart': cart})

   
# Update cart item quantity    
@login_required(login_url='/login')
def updatecartItem(request, id, op):
    item = CartItem.objects.get(id=id)

    if op == 'inc':  # inc : increase quantity
        item.quantity += 1
        item.save()
    elif op == 'dec' and item.quantity > 1:  # dec : decrease quantity
        item.quantity -= 1
        item.save()
    else:
        item.delete() # delete if quantity reaches zero
    return redirect(viewcart)

# Remove a single cart item
@login_required(login_url='/login')
def deletecartItem(request, id):
    CartItem.objects.get(id=id).delete()
    return redirect(viewcart)

# Remove all items from cart
@login_required(login_url='/login')
def clearcart(request):
    customer = Customer.objects.get(customer=request.user)
    cart = Cart.objects.get(customer=customer)
    CartItem.objects.filter(cart=cart).delete()
    return redirect(viewcart)


            # ========================= #
            #          ORDERS           #
            # ========================= #



# Create a new order
@login_required(login_url='/login')
def placeorder(request):
    customer = Customer.objects.get(customer=request.user)
    address = Address.objects.filter(customer=customer)
    qty = int(request.GET.get('quantity', 1))
    pay = request.session.get('pay',{})
    
    total_items = 0
    total_price = 0
    items =[]

    pid = request.GET.get('pid')
    if pid:
        pro = Product.objects.get(id=pid)
        total_items = qty
        total_price = pro.price * qty
        print(pro.name)
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            addr_id = request.POST.get('address_id')
            addr = Address.objects.get(id=addr_id)
            order = Order.objects.create(customer=customer,address=addr)
            
            OrderItem.objects.create(
                        order=order,product=pro,quantity=qty,price=pro.price
                    )
           
            request.session['order_id'] = order.id

            if payment_method == 'cod':
                pay[str(order.id)] ={
                    'method' : 'cod',
                    'amount' : float(total_price)
                    }
                request.session['pay'] = pay
                messages.success(request,'Order placed successfully')

                subject = 'order confirmation'
                message = f"""
                            🎉 Order Confirmed!

                            Hi {request.user},

                            Thank you for your order.

                            Order ID: {order.id}
                            Payment Method: Cash on Delivery
                            Amount Payable: ₹{total_price}

                            Your order has been successfully placed.
                            Please keep the exact amount ready at the time of delivery.
                            """
                from_email = settings.EMAIL_HOST_USER
                to_list=[customer.email]

                send_mail(subject,message,from_email,to_list)

                return redirect(orderdetails,oid=order.id)
            else:
                pay[str(order.id)] ={
                    'method' : 'pay online',
                    'amount':float(total_price)
                    }
                request.session['pay'] = pay
                # Create a Razorpay order
                amount = int(float(pro.price) * qty * 100)

                razorpay_order = razorpay_client.order.create({
                    'amount': amount,
                    'currency': 'INR',
                    'payment_capture': 0
                })

                # order id of newly created order.
                razorpay_order_id = razorpay_order['id']
                callback_url = request.build_absolute_uri('/payment/paymenthandler/')

                order_id = request.session.get('order_id')

                # Pass these details to frontend
                context = {
                    'razorpay_order_id':razorpay_order_id,
                    'razorpay_merchant_key':settings.RAZORPAY_KEY_ID,
                    'razorpay_amount': amount,
                    'currency':'INR',
                    'callback_url':callback_url,
                    'total_items' : qty,
                    'total_price' : pro.price * qty,
                    'order_id':order_id
                }
                messages.warning(request,"You’ve selected the online payment option. Please complete the payment to proceed with your order.")
                return render(request,'payment.html',context=context)
            
        items.append({
            'product': pro,
            'quantity': qty,
            'sub_total': pro.price * qty
        })

        total_items = qty
        total_price = pro.price * qty
        
    else:
        cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(cart=cart)

        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            addr_id = request.POST.get('address_id')
            addr = Address.objects.get(id=addr_id)
            order = Order.objects.create(customer=customer,address=addr)
            
            request.session['order_id'] = order.id

            for item in cart_items:
                items.append(
                    OrderItem.objects.create(
                        order=order,product=item.product,quantity=item.quantity,price=item.product.price
                    ))
                total_items += item.quantity
                total_price += item.sub_total
            
            
            if payment_method == 'cod':
                pay[str(order.id)] ={
                    'method' : 'cod',
                    'amount' : float(total_price)
                    }
                request.session['pay'] = pay
                clearcart(request)
                messages.success(request,'Order placed successfully')
                
                subject = 'Order confirmation'
                message = f"""
                            🎉 Order Confirmed!

                            Hi {request.user},

                            Thank you for your order.

                            Order ID: {order.id}
                            Payment Method: Cash on Delivery
                            Amount Payable: ₹{total_price}

                            Your order has been successfully placed.

                            Please keep the exact amount ready at the time of delivery.

                            """
                from_email = settings.EMAIL_HOST_USER
                to_list=[customer.email]

                send_mail(subject,message,from_email,to_list)

                return redirect(orderdetails,oid=order.id)
            else:
                pay[str(order.id)] ={
                    'method' : 'pay online',
                    'amount': float(total_price)
                    }
                request.session['pay'] = pay

                if total_price <= 0:
                    messages.error(request, "Your cart is empty.")
                    return redirect(viewcart)

                # Create a Razorpay order
                amount = int(float(total_price) * 100)

                razorpay_order = razorpay_client.order.create({
                    'amount': amount,
                    'currency': 'INR',
                    'payment_capture': 0
                })

                # order id of newly created order.

                razorpay_order_id = razorpay_order['id']
                callback_url = request.build_absolute_uri('/payment/paymenthandler/')


                # Pass these details to frontend
                context = {
                    'razorpay_order_id':razorpay_order_id,
                    'razorpay_merchant_key':settings.RAZORPAY_KEY_ID,
                    'razorpay_amount': amount,
                    'currency':'INR',
                    'callback_url':callback_url,
                    'total_items':total_items,
                    'total_price':total_price
                }

                return render(request,'payment.html',context=context)
            
            
        for item in cart_items:        
            items.append({
                'product': item.product,
                'quantity': item.quantity,
                'sub_total': item.sub_total
                })
            total_items += item.quantity
            total_price += item.sub_total




    return render(request,'placeorder.html',{'profile':customer,'address':address,'items':items,'total_items':total_items,'total_price':total_price})

# View all orders of the logged-in customer
@login_required(login_url='/login')
def vieworders(request):
    customer = Customer.objects.get(customer=request.user)
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    pending = Order.objects.filter(customer=customer,status='Pending').order_by('-order_date')
    shipped = Order.objects.filter(customer=customer,status='Shipped').order_by('-order_date')
    delivered = Order.objects.filter(customer=customer,status='Delivered').order_by('-order_date')
    pay = request.session.get('pay')

    return render(request,'vieworders.html',{'customer':customer,'orders':orders,'pending':pending,'shipped':shipped,'delivered':delivered,'pay':pay})

# View details of a single order
@login_required(login_url='/login')
def orderdetails(request,oid):
    usr = Customer.objects.get(customer=request.user)
    order = Order.objects.get(id=oid,customer=usr)
    address = order.address
    items = []
    total_items = 0
    total_price = 0
    items = OrderItem.objects.filter(order=order)
    for item in items:
        total_items += item.quantity
        total_price += item.sub_total

    pay = request.session.get('pay', {})
    payment_info = pay.get(str(oid))

    return render(request,'orderdetails.html',{'usr':usr,'address':address,'order':order,'items':items,'total_items':total_items,'total_price':total_price,'pay':payment_info})


# Cancel an order
@login_required(login_url='/login')
def cancelorder(request,oid):
    customer = Customer.objects.get(customer=request.user)
    order = Order.objects.get(id=oid)
    pay = request.session.get('pay')
    if pay[str(order.id)]['method'] == 'pay online':
        subject = 'Order cancellation'
        message = f"""
                    ❌ Order Cancelled Successfully

                        Hi {request.user},

                        Your order has been cancelled as requested.

                        Order ID: {order.id}
                        Payment Method: Online (Razorpay)
                        Amount Paid: ₹{pay[str(order.id)]['method']}

                        Your refund has been initiated.
                        The amount will be credited to your original payment method within 5–7 business days.

                        If you have any questions, feel free to contact our support team.

                    """
        from_email = settings.EMAIL_HOST_USER
        to_list=[customer.email]

        send_mail(subject,message,from_email,to_list)
    elif pay[str(order.id)]['method'] == 'cod':
        subject = 'Order cancellation'
        message = f"""
                    ❌ Order Cancelled Successfully

                        Hi {request.user},

                            Your order has been cancelled.

                            Order ID: {order.id}
                            Payment Method: Cash on Delivery

                            Since this was a COD order, no payment was charged.

                            We hope to serve you again soon!

                    """
        from_email = settings.EMAIL_HOST_USER
        to_list=[customer.email]

        send_mail(subject,message,from_email,to_list)

    order.delete()

    messages.warning(request,'Order cancelled')
    return redirect(vieworders)

    