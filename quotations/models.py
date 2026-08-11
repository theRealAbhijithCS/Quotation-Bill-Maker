from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    display_name = models.CharField(max_length=150, blank=True, help_text="Display Name")
    phone_primary = models.CharField(max_length=20, blank=True, help_text="Primary Phone Number (Required)")
    phone_secondary = models.CharField(max_length=20, blank=True, null=True, help_text="Secondary Phone Number (Optional)")
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    profile_picture_url = models.TextField(blank=True, help_text="External image URL fallback")

    def get_full_display_name(self):
        if self.display_name:
            return self.display_name
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    def __str__(self):
        return f"{self.get_full_display_name()} ({self.email or self.username})"


class Bill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bills")
    bill_number = models.CharField(max_length=50, unique=True, db_index=True, help_text="Unique locked bill identifier")
    quotation_title = models.CharField(max_length=200, default="Labour Quotation")
    company_name = models.CharField(max_length=200, default="M4 Interior & Architect")
    architect_name = models.CharField(max_length=150, blank=True, default="")
    project_title = models.CharField(max_length=200, default="Home 1")
    client_name = models.CharField(max_length=150, db_index=True)
    client_phone = models.CharField(max_length=20, help_text="Primary Client Phone")
    client_phone_secondary = models.CharField(max_length=20, blank=True, null=True, help_text="Secondary Client Phone")
    bill_date = models.DateField()
    
    items = models.JSONField(default=list, help_text="Dynamic line items list")
    
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_in_words = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True, default="Quotation valid for 30 days.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_number} - {self.client_name} ({self.grand_total})"
