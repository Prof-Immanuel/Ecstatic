from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class LoanApplication(models.Model):
    REPAYMENT_OPTIONS = [
        ('1week', '1 week - 15% interest'),
        ('2weeks', '2 weeks - 20% interest'),
        ('3weeks', '3 weeks - 30% interest'),
        ('4weeks', '4 weeks - 40% interest'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_reason = models.TextField()
    collateral = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    repayment_duration = models.CharField(
        max_length=7,
        choices=REPAYMENT_OPTIONS,
        default='1week'
    )
    nrc_number = models.CharField(max_length=50, default='unknown')  # ✅ New field
    phone_number = models.CharField(max_length=50, default='null')  # ✅ New field
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.amount}"

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    content = models.TextField()  # The testimonial content
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation
    approved = models.BooleanField(default=False)  # Admin approval status

    def __str__(self):
        return f"Testimonial by {self.user.first_name} {self.user.last_name}"