from django.db import models
from django.core.exceptions import ValidationError


class User(models.Model):
    mail = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15,unique=True)
    adhar_no= models.CharField(max_length=16,unique=True)
    profilefill = models.CharField(max_length=3)

    def clean(self):
        if User.objects.filter(adhar_no=self.adhar_no).exclude(pk=self.pk).exists():
            raise ValidationError("Adhar Number already exists.")
        if User.objects.filter(phone=self.phone).exclude(pk=self.pk).exists():
            raise ValidationError("Phone Number already exists.")
        if User.objects.filter(mail=self.mail).exclude(pk=self.pk).exists():
            raise ValidationError("Email already exists.")

class AppliedUserScheme(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_scheme = models.CharField(max_length=255)
