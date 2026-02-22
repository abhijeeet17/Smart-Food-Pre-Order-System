from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    registration_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    semester = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registration_number})"


class FoodStall(models.Model):
    """Represents a food stall on campus"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_open = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='stall_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class BreakTimeSlot(models.Model):
    """Available break time slots for ordering"""
    SLOT_CHOICES = [
        ('10:00-10:30', '10:00 AM - 10:30 AM'),
        ('12:00-12:30', '12:00 PM - 12:30 PM'),
        ('13:00-13:30', '1:00 PM - 1:30 PM'),
        ('15:00-15:30', '3:00 PM - 3:30 PM'),
        ('17:00-17:30', '5:00 PM - 5:30 PM'),
    ]
    slot_time = models.CharField(max_length=20, choices=SLOT_CHOICES, unique=True)
    max_capacity = models.IntegerField(default=50)

    def __str__(self):
        return self.get_slot_time_display()

    def current_orders(self):
        """Count orders for this slot today"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.orders.filter(order_date=today, status__in=['pending', 'confirmed', 'ready']).count()

    def is_available(self):
        return self.current_orders() < self.max_capacity


class FoodItem(models.Model):
    """A food item available at a stall"""
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Snacks'),
        ('beverages', 'Beverages'),
        ('dinner', 'Dinner'),
    ]
    stall = models.ForeignKey(FoodStall, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='snacks')
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    preparation_time = models.IntegerField(default=10, help_text="Prep time in minutes")

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class Order(models.Model):
    """A student's food order"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    stall = models.ForeignKey(FoodStall, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(BreakTimeSlot, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField(auto_now_add=True)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.student.username}"

    def calculate_total(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    """Individual items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"

    def subtotal(self):
        return self.quantity * self.price_at_order

    def save(self, *args, **kwargs):
        if not self.price_at_order:
            self.price_at_order = self.food_item.price
        super().save(*args, **kwargs)


class DemandRecord(models.Model):
    """Stores historical demand data for AI training"""
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='demand_records')
    date = models.DateField()
    time_slot = models.ForeignKey(BreakTimeSlot, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()   # 0=Monday, 6=Sunday
    quantity_ordered = models.IntegerField(default=0)
    predicted_demand = models.IntegerField(default=0)

    class Meta:
        unique_together = ['food_item', 'date', 'time_slot']

    def __str__(self):
        return f"{self.food_item.name} on {self.date} at {self.time_slot}"
