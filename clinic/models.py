from django.db import models
from django.contrib.auth.models import User


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Patient(models.Model):
    salutation = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="patients/images/", null=True, blank=True)

    def __str__(self):
        return self.name



class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()
    address = models.TextField()

    # 🔥 NEW FIELDS
    bio = models.TextField(blank=True)
    hobbies = models.CharField(max_length=255, blank=True)
    qualification = models.CharField(max_length=255, blank=True)

    image = models.ImageField(upload_to="doctors/images/", blank=True, null=True)
    document = models.FileField(upload_to="doctors/docs/", blank=True, null=True)

    is_profile_completed = models.BooleanField(default=False)

    password = models.CharField(max_length=255)


    def __str__(self):
        return self.name

