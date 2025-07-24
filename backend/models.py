from django.db import models

# Create your models here.
class Amount(models.Model):
    amount = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return f"ksh {self.amount}"
    
class Payment(models.Model):
    phonenumber = models.CharField(max_length = 12)
    checkoutrequestid = models.CharField(unique= True)
    amountpaid = models.IntegerField()

    def __str__(self):
        return self.checkoutrequestid
    
class Voucher(models.Model):
    code = models.CharField(unique=True, max_length= 6)
    duration = models.ForeignKey(Amount, on_delete=models.CASCADE)
    