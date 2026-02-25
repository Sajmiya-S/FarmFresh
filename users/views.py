from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
from .forms import *
from shop.models import Cart
from django.core.mail import send_mail
from django.conf import settings

            # ========================= #
            #   HOME & AUTHENTICATION   #
            # ========================= #

# Render the home page
def homepage(request):
    return render(request, 'home.html')

# Register a new customer and creates an empty cart for the customer
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()                         
            customer = Customer.objects.create(customer=user)
            Cart.objects.create(customer=customer)    
             
            messages.success(request, 'User registered Successfully!!!')
            return redirect(signin)
    else:
        form = RegistrationForm()

    return render(request, 'signup.html', {'form': form})

# Login user using username & password
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'User logged in successfully!!!')
            return redirect(homepage)
        else:
            messages.warning(request, 'No such user')

    return render(request, 'login.html')

# Logout the currently logged-in user
def signout(request):
    logout(request)
    messages.success(request, 'User logged out successfully!!!')
    return redirect(signin)


            # ========================= #
            #   ABOUT / CONTACT PAGE    #
            # ========================= #

# Save user enquiry / message
def aboutpage(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent successfully!")
            return redirect(homepage)

    form = MessageForm()
    return render(request, 'about.html', {'form': form})


            # ========================= #
            #     PROFILE MANAGEMENT    #
            # ========================= #

# Display logged-in user's profile
def profilepage(request):
    user = request.user
    pro = Customer.objects.get(customer=user)
    return render(request, 'profile.html', {'pro': pro})

# Edit customer profile details
def editprofile(request, pid):
    profile = Customer.objects.get(id=pid)

    if request.method == 'POST':
        next_page = request.POST.get('next','')
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            subject = 'Welcome'
            message = """🎉 Welcome to FarmFresh!

                            Hi {request.user},

                            Thank you for registering with us.

                            We’re excited to have you on board! Explore our products and enjoy a seamless shopping experience.

                            If you have any questions, contact our support team.
                            """
            from_email = settings.EMAIL_HOST_USER
            to_list = [form.data['email']]
            send_mail(subject,message,from_email,to_list,fail_silently=True) 
            messages.success(request, 'Profile updated successfully')
            if next_page:
                return redirect(next_page)
            return redirect(profilepage)

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'editpro.html', {'form': form, 'pro': profile,'next': request.GET.get('next','')})


            # ======================== #
            #    ADDRESS MANAGEMENT    #
            # ======================== #

# Save a new delivery address for the logged-in customer
def saveaddress(request):
    if request.method == 'POST':
        next_page = request.POST.get('next')
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.customer = request.user.customer
            address.save()

            messages.success(request, "Address saved successfully")

            return redirect(next_page or viewaddress)

    else:
        form = AddressForm()

    return render(request, 'address.html', {'form': form,'next': request.GET.get('next')})


# View all saved addresses of the customer 
def viewaddress(request):
    customer = Customer.objects.get(customer=request.user)
    addr = Address.objects.filter(customer=customer)
    count = 0
    for i in addr:
        count += 1
    return render(request, 'viewaddress.html', {'addr': addr,'count':count})

# Edit an existing address
def editaddress(request, aid):
    addr = Address.objects.get(id=aid)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=addr)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully')
            return redirect(viewaddress)
    else:
        form = AddressForm(instance=addr)

    return render(request, 'editaddress.html', {'form': form, 'addr': addr})

# Delete an address
def deleteaddress(request, aid):
    addr = Address.objects.get(id=aid)
    if request.method == 'POST':
        addr.delete()
        messages.info(request, 'Address deleted')

    return redirect(viewaddress)