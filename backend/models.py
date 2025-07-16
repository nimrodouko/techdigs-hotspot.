from django.db import models

# Create your models here.
class Amount(models.Model):
    amount = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return f"ksh {self.amount}"