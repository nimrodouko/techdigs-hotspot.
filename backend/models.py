from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.
class Amount(models.Model):
    amount = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return f"ksh {self.amount}"
    
class Payment(models.Model):
    mpesareciept = models.CharField(max_length=10, unique=True, null=False, blank=False)
    created = models.DateTimeField(default = timezone.now)
    paid = models.BooleanField(default = False)
    
    def __str__(self):
        return self.mpesareciept
    

    @property
    def is_expired(self):
        
        expiry_time = self.created +timedelta(hours =3)
        return timezone.now() > expiry_time
        
    def remove_expired(self):
        if self.is_expired:
            self.delete()
            return True
        else:
            return False


    
    

    