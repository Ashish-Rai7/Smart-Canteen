from django.contrib import admin
from .models import MenuItem
# Menu Items ke liye 
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_available', 'is_trending')
    list_filter = ('category', 'is_available', 'is_trending')
    search_fields = ('name',)
    list_editable = ('price', 'is_available', 'is_trending') # Allows editing these directly in the list view
    
    