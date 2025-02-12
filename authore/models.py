from django.db import models
from django.contrib.auth.models import User
# Create your models here.


ACCOUNT_TYPE=(('admin', 'admin'),('seller', 'seller'),('buyer','buyer'))

class MoreInfo(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.URLField(max_length=200)
    name=models.CharField(max_length=30)
    phone=models.CharField(max_length=13)
    location=models.CharField(max_length=200)
    user_type=models.CharField(choices=ACCOUNT_TYPE, max_length=10,blank=True,null=True)

    def __str__(self):
        return self.name
