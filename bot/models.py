import datetime

from django.db import models


class Company(models.Model):
    company_name = models.CharField(max_length=125, null=True, blank=True)
    Adress = models.CharField(max_length=125, null=True, blank=True)
    director_name = models.CharField(max_length=125, null=True, blank=True)
    director_number = models.CharField(max_length=55, null=True, blank=True)


class Profile(models.Model):
    full_name = models.CharField(max_length=125, null=True, blank=True)
    first_name = models.CharField(max_length=123, null=True, blank=True)
    username = models.CharField(max_length=125, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    discout = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=55, null=True, default='user')


class Product(models.Model):
    name = models.CharField(max_length=125, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)


class Savatcha(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    sold_price = models.IntegerField(null=True, default=0)
    status = models.CharField(max_length=55, null=True, default='progress')
    sold_date = models.DateField(auto_now_add=True)
    sold_discout = models.IntegerField(null=True, blank=True, default=0)

    @property
    def set_defaults(self):
        self.sold_price = self.product.price
        self.sold_discout = self.product.discount
        self.sold_price = self.product.price
        self.save()
