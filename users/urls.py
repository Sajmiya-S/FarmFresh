from django.urls import path
from .views import *

urlpatterns = [
    path('',homepage,name='home'),
    path('login',signin,name='login'),
    path('logout',signout,name='logout'),
    path('signup',signup,name='signup'),
    path('profile',profilepage,name='profile'),
    path('editpro/<int:pid>',editprofile,name='editp'),
    path('about',aboutpage,name='about'),
    path('address/',saveaddress,name='addr'),
    path('viewaddr/',viewaddress,name='viewaddr'),
    path('editaddr/<int:aid>/',editaddress,name='editaddr'),
    path('deladdr/<int:aid>/',deleteaddress,name='deladdr'),
    
]