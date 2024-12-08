from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    remaining_leave_days = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=15.00
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"

@receiver(post_save, sender=User)
def _post_save_receiver(sender, instance, created, **kwargs):
    """
    Signal receiver function to create an Employee instance when a new User is created.
    """
    if created:
        Employee.objects.create(user=instance)
    
    
