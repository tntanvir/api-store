from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField


SIZE = (
    ('m', 'M'),
    ('l', 'L'),
    ('xl', 'XL'),
    ('lg', 'Lg'),
    ('xxl', 'XXL')
)

COLOR = (
    ('red', 'Red'),
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('yellow', 'Yellow'),
    ('orange', 'Orange'),
    ('purple', 'Purple'),
    ('pink', 'Pink'),
    ('brown', 'Brown'),
    ('gray', 'Gray'),
    ('black', 'Black'),
    ('white', 'White')
)

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.URLField(max_length=300)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    size = MultiSelectField(choices=SIZE, max_length=100)
    color = MultiSelectField(choices=COLOR, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

STAR = [
    ('⭐', '⭐'),
    ('⭐⭐', '⭐⭐'),
    ('⭐⭐⭐', '⭐⭐⭐'),
    ('⭐⭐⭐⭐', '⭐⭐⭐⭐'),
    ('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.CharField(choices=STAR, max_length=10)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    ordered = models.BooleanField(default=False)
    time=models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Cart of {self.user.username} - Total: {self.time}"

class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    size = models.CharField(choices=SIZE, max_length=100, null=True, blank=True)
    color = models.CharField(choices=COLOR, max_length=100, null=True, blank=True)


# order 
STATUS_CHOICES = [
         ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    ordered_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending' ,blank=True,null=True)
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, related_name='seller', on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',null=True,blank=True)

   
    def __str__(self):
        return f"{self.product.name} - ({self.quantity}) -  {self.status}"
   




