from django.db import models

# Create your models here.
class Amount(models.Model):
    amount = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return f"ksh {self.amount}"
    
class Payment(models.Model):
    mpesareciept = models.CharField(max_length=10, unique=True)
    

    def __str__(self):
        return self.mpesareciept
    
class Voucher(models.Model):
    code = models.CharField(unique=True, max_length= 6)
    
    def __str__(self):
        return self.code
    