from django.db import models
from django.utils import timezone


class AuthInfo(models.Model):
    phone = models.CharField(max_length=50)
    msg = models.CharField(max_length=20)
    counter = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def publish(self):
        self.save()

    def __str__(self):
        return self.phone
