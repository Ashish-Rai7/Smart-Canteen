from django.db import models

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('veg', 'Veg'),
        ('nonveg', 'Non-Veg'),
        ('beverage', 'Beverage'),
        ('snack', 'Snack'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name
