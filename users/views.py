from django.http import HttpResponse
from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.models import User
from .models import Profile , MenuItem , Order
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import qrcode
import io
import base64
from django.contrib.auth import logout as auth_logout
from decimal import Decimal

def register(request):
    if request.method == "POST":
        role = request.POST.get('role')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        department = request.POST.get('department')
        course = request.POST.get('course')
        roll_no = request.POST.get('roll_no')
        staff_id = request.POST.get('staff_id')

        # ✅ Basic password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # ✅ Username logic (using email or name)
        username = email  

        # ✅ Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name
        )

        # ✅ Create Profile depending on role
        Profile.objects.create(
            user=user,
            role=role,
            contact_number=phone,
            department=department if role == 'student' else None,
            course=course if role == 'student' else None,
            roll_no=roll_no if role == 'student' else None,
            staff_id=staff_id if role == 'staff' else None
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'users/register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")  # login ke baad dashboard p jyga
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "users/login.html")



# @login_required
def dashboard(request):
    
    latest_order = None
    qr_image_base64 = None
    order_id_display = "N/A"

    try:
        # लॉग-इन यूज़र का सबसे हाल का ऑर्डर ढूंढें
        # आप स्टेटस के हिसाब से भी फ़िल्टर कर सकते हैं (जैसे सिर्फ 'Placed', 'Preparing', 'Ready')
        latest_order = Order.objects.filter(user=request.user).latest('created_at')
        
        if latest_order:
            order_id_display = latest_order.order_id_display # Display ID का इस्तेमाल करें
            # QR कोड के लिए डेटा (Display ID का इस्तेमाल करें)
            qr_data = str(order_id_display)
            
            # मेमोरी में QR कोड जेनरेट करें
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            
            # इमेज को Base64 स्ट्रिंग में बदलें
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Order.DoesNotExist:
        # अगर यूज़र का कोई ऑर्डर नहीं है
        latest_order = None

    context = {
        'order': latest_order, # पूरा ऑर्डर ऑब्जेक्ट भेजें
        'qr_image': qr_image_base64,
        'order_id_display': order_id_display,
    }
    return render(request, 'users/dashboard.html', context)
    

def menu(request):
    # 1. URL से 'category' पैरामीटर निकालें
    category_filter = request.GET.get('category')

    # 2. आइटम्स को फ़िल्टर करें
    if category_filter:
        # अगर कैटेगरी है, तो फिल्टर करें
        items = MenuItem.objects.filter(is_available=True, category=category_filter)
    else:
        # अगर कोई कैटेगरी नहीं है (या 'All' चुना है), तो सारे दिखाएं
        items = MenuItem.objects.filter(is_available=True)

    # 3. मॉडल से कैटेगरी चॉइसेस निकालें (बटन्स के लिए)
    categories = MenuItem.CATEGORY_CHOICES # Assuming CATEGORY_CHOICES is defined in MenuItem model

    # 4. टेम्पलेट को डेटा भेजें
    context = {
        'items': items,                 # फ़िल्टर्ड आइटम्स
        'categories': categories,       # सभी कैटेगरी (कोड और नाम)
        'current_category': category_filter # अभी कौन सी कैटेगरी एक्टिव है
    }
    return render(request, 'users/menu.html', context)


# Payment ke liye 
@login_required # पेमेंट के लिए लॉगिन ज़रूरी है
def payment(request):
    cart = request.session.get('cart', {})
    if not cart:
        # अगर कार्ट खाली है तो मेनू पर वापस भेजें
        messages.error(request, "Your cart is empty. Cannot proceed to payment.")
        return redirect('menu')

    cart_total = Decimal('0.00')
    cart_items_for_display = [] # टेम्पलेट में दिखाने के लिए लिस्ट

    # कार्ट आइटम्स प्रोसेस करें और टोटल कैलकुलेट करें
    for item_id, item_data in cart.items():
        item_total = Decimal(str(item_data.get('price', 0))) * item_data.get('quantity', 0)
        cart_total += item_total
        cart_items_for_display.append({
            'name': item_data.get('name'),
            'quantity': item_data.get('quantity'),
            'total_price': item_total
        })

    tax = cart_total * Decimal('0.05') # 5% टैक्स का उदाहरण
    grand_total = cart_total + tax

    context = {
        'cart_items': cart_items_for_display, # टेम्पलेट में आइटम्स दिखाने के लिए
        'subtotal': cart_total,
        'tax': tax,
        'grand_total': grand_total, # पेमेंट पेज पर दिखाने वाला फाइनल अमाउंट
    }
    return render(request, "users/payment.html", context)

# --- Cart Management Views ---
def add_to_cart(request, item_id):
    """Adds an item to the session cart or increases its quantity."""
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart = request.session.get('cart', {}) # Get cart from session, or create empty dict
    item_id_str = str(item_id) # Use string for dictionary key

    quantity = int(request.POST.get('quantity', 1)) # Get quantity from form, default 1

    if item_id_str in cart:
        cart[item_id_str]['quantity'] += quantity
    else:
        cart[item_id_str] = {
            'name': item.name,
            'price': float(item.price), # Store price as float for JSON compatibility
            'quantity': quantity,
            'image_url': item.image.url if item.image else '' # Store image URL
        }

    request.session['cart'] = cart # Save updated cart back to session
    messages.success(request, f"Added {item.name} to your cart.")
    return redirect('menu') # Redirect back to the menu page

def cart(request):
    """Displays the items in the cart and calculates totals."""
    cart = request.session.get('cart', {})
    cart_items = {}
    cart_total = 0
    
    # Process cart items for display and calculate totals
    for item_id, item_data in cart.items():
        item_data['total_price'] = item_data['price'] * item_data['quantity']
        cart_items[item_id] = item_data
        cart_total += item_data['total_price']

    tax = cart_total * 0.05 # Example 5% tax
    grand_total = cart_total + tax

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'users/cart.html', context)

def update_cart(request, item_id):
    """Increases or decreases the quantity of an item in the cart."""
    cart = request.session.get('cart', {})
    item_id_str = str(item_id) # Ensure key is string

    if item_id_str in cart and request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            cart[item_id_str]['quantity'] += 1
        elif action == 'decrease':
            if cart[item_id_str]['quantity'] > 1:
                cart[item_id_str]['quantity'] -= 1
            else:
                # If quantity becomes 0, remove the item
                del cart[item_id_str]
        
        request.session['cart'] = cart # Save changes
        messages.info(request, "Cart updated.")

    return redirect('cart') # Redirect back to the cart page

def remove_from_cart(request, item_id):
    """Removes an item completely from the cart."""
    cart = request.session.get('cart', {})
    item_id_str = str(item_id) # Ensure key is string

    if item_id_str in cart and request.method == 'POST':
        item_name = cart[item_id_str]['name'] # Get name for message
        del cart[item_id_str]
        request.session['cart'] = cart # Save changes
        messages.warning(request, f"Removed {item_name} from your cart.")

    return redirect('cart') # Redirect back to the cart page

# Logout function ke liye 
def logout(request):
    auth_logout(request)
    return redirect('index')

def place_order(request):
# You can pass context if needed
    return render(request, 'users/dashboard.html')

def track_order(request):
    return render(request, 'users/dashboard.html')




def index(request):
    trending_items = MenuItem.objects.filter(is_trending=True, is_available=True)
    return render(request, 'users/index.html', {'trending_items': trending_items})
