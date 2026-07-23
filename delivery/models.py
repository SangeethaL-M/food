from django.db import models
from django.contrib.auth.models import User
from orders.models import Order

class DeliveryAssignment(models.Model):
    delivery_partner = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_assignment')
    is_accepted = models.BooleanField(default=False)
    earning = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery #{self.order.id} - Partner: {self.delivery_partner.username}"