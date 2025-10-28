from django.db import models
from django.contrib.auth.models import User
# from .models import MenuItem
ROLE_CHOICES = (
    ('student' , 'Student'),
    ('teacher' , 'Teacher'),
    ('admin','Admin'),
    ('staff','Staff'),
    ('guest' , 'Guest'),
    ('course' , 'Course'),
    ('roll_no', 'Roll_No'),
    ('staff_id' , 'Staff_id')
)

DEPARTMENT_CHOICES = (
    ('cs' , 'Computer Science'),
    ('it' , 'Information Technology'),
    ('ml' , 'Machine Learning'),
    ('ee' , 'Electronics Engineering'),
    ('ce' , 'Civil Engineering'),
    ('mba' , 'MBA'),
    ('bba' , 'BBA'),
    ('mca' , 'MCA'),
    ('bca' , 'BCA'),
    ('none' , 'None')
)


# Extra fields in my profile 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='none')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    roll_no = models.CharField(max_length=50, null=True, blank=True)
    staff_id = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"


# Menu Items ke liye model

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('veg', 'Veg'),
        ('nonveg', 'Non-Veg'),
        ('beverage', 'Beverage'),
        ('snack', 'Snack'),
        ('desert', 'Desert'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    # Order Tracking ke liye 
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('Placed', 'Order Placed'),
        ('Preparing', 'In the Kitchen'),
        ('Ready', 'Ready for Pickup'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # items = models.ManyToManyField(MenuItem, through='OrderItem') # If using ManyToMany
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Placed')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    order_id_display = models.CharField(max_length=20, unique=True, blank=True) # For display like HC12345

    def save(self, *args, **kwargs):
        if not self.order_id_display:
            # Generate a unique display ID when saving for the first time
            super().save(*args, **kwargs) # Save first to get the PK (id)
            self.order_id_display = f"HC{self.pk + 10000}" # Example: HC10001
            kwargs.pop('force_insert', None) # Avoid re-inserting
            super().save(*args, **kwargs) # Save again with the display ID
        else:
            super().save(*args, **kwargs)

        def __str__(self):
            return f"Order {self.order_id_display} by {self.user.username}"
        
        # Order Item Model
    class OrderItem(models.Model):
        order = models.ForeignKey('Order', on_delete=models.CASCADE)
        item = models.ForeignKey(MenuItem, on_delete=models.PROTECT) # Protect item if order exists
        quantity = models.PositiveIntegerField(default=1)
        price = models.DecimalField(max_digits=6, decimal_places=2) # Price at the time of order
    
        def save(self, *args, **kwargs):
            # Store the item's current price when saving
            if not self.pk: # Only on creation
                self.price = self.item.price
            super().save(*args, **kwargs)
    
        def get_total_item_price(self):
            return self.quantity * self.price
    
        def __str__(self):
            return f"{self.quantity} of {self.item.name} in order {self.order.order_id_display}"

