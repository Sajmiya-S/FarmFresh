from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('shopnow',categories,name='catz'),
    path('catwise/<int:cid>',categorywise,name='cwise'),
    path('allp',allproducts,name='shop'),
    path('pro/<pid>',productdetails,name='pdet'),
    path('add2cart/<int:pid>',addtocart,name='add2cart'),
    path('cart',viewcart,name='cart'),
    path('delcart/<int:id>',deletecartItem,name='remove'),
    path('upcart/<int:id>/<str:op>',updatecartItem,name='update'),
    path('clrcart',clearcart,name='clear'),
    path('orders',vieworders,name='order'),
    path('orderdet/<int:oid>',orderdetails,name='odet'),
    path('delorder/<int:oid>',cancelorder,name='cancel'),
    path('plorder',placeorder,name='porder'),
]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)