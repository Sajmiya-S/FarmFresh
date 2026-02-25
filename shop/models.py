from django.db import models
from users.models import Customer,Address

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    pic = models.ImageField(upload_to='catz')

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=15)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField()
    pic = models.ImageField(null=True,upload_to='product_pictures')

    def __str__(self):
        return self.name
    

class Order(models.Model):
    ch = (
            ('Pending', 'Pending'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered')
    )
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,null=True)
    address = models.ForeignKey(Address,on_delete=models.CASCADE,null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=ch,default='Pending')

    def __str__(self):
        return str(self.customer)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

    @property
    def sub_total(self):
        return (self.quantity * self.price)

    def __str__(self):
        return self.product.name

class Cart(models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE)

    @property
    def total_items(self):
        count = 0
        for i in self.items.all():
            count += i.quantity
        return count
    
    @property
    def total_price(self):
        total= 0
        for i in self.items.all():
            total += i.product.price * i.quantity
        return total
    
    @property
    def grand_total(self):
        return self.total_price + 40
    
    def __str__(self):
        return str(self.customer)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items',null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def sub_total(self):
        return (self.quantity * self.product.price)

    def __str__(self):
        return str(self.cart)