from django.shortcuts import render,redirect
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.contrib import messages
from shop.models import Customer,Cart,CartItem,Order
from django.core.mail import send_mail


# Authorize razorpay client with API keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("razorpay_payment_id")
            razorpay_order_id = request.POST.get("razorpay_order_id")
            signature = request.POST.get("razorpay_signature")

            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            }

            # 🔐 Verify Signature
            razorpay_client.utility.verify_payment_signature(params_dict)

            # 💰 Capture Payment (amount must be in paise)
            razorpay_order = razorpay_client.order.fetch(razorpay_order_id)
            amount_paise = razorpay_order['amount']

            razorpay_client.payment.capture(payment_id, amount_paise)

            order_id = request.session.pop('order_id', None)
            amount = amount_paise / 100
            
            if order_id:
                order = Order.objects.get(id=order_id)
                CartItem.objects.filter(
                    cart__customer=order.customer
                ).delete()

            customer = Customer.objects.get(customer=request.user)
            subject = 'Order confirmation'
            message = f"""
                            
                            🎉 Order Confirmed!

                            Hi {request.user},

                            Thank you for shopping with us.

                            Order ID: {order_id}
                            Payment Status: Successful
                            Total Paid: ₹{amount}

                            Your order is now being processed.

                            If you have any questions, contact our support team.

                            """
            from_email = settings.EMAIL_HOST_USER
            to_list=[customer.email]

            send_mail(subject,message,from_email,to_list)

            messages.success(request, "Payment Successful")
            return redirect('odet',oid = order_id)  # change to your success url

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed")
            return redirect('porder')

        except Exception as e:
            messages.error(request, "Something went wrong")
            return redirect('porder')

    return HttpResponseBadRequest()
