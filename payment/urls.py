from django.urls import path
from .views import *


urlpatterns = [
    path('paymenthandler/',paymenthandler,name='paymenthandler')
]