from django.http import HttpResponse
from django.shortcuts import render,redirect
from pymongo import MongoClient
from datetime import datetime
from django.contrib import messages
import json

def login(request):

    client = MongoClient("mongodb://localhost:27017/")
    db = client['Project']
    coll= db['Signup']

    if request.method == "POST":

        # email = request.POST.get('email')
        # password = request.POST.get('password')

        email = request.POST['email']
        password = request.POST['password']

    
        for i in coll.find({'Email':email},{'Email':1,'Password':1 ,'_id':0}):
            Email = i['Email']
            Password = i['Password']
        

        if email==Email and password==Password:
            request.session['email'] = email
            return render(request,"index.html")
        else:
            return HttpResponse("Email or Password Incorrect")
        
    return render(request,"login.html")  


def signup(request):

    client = MongoClient("mongodb://localhost:27017/")
    db = client['Project']
    coll= db['Signup']

    if request.method == "POST": 

        name = request.POST.get('name').title()
        phone = int(request.POST.get('phone'))
        email = request.POST.get('email')
        address = request.POST.get('address').title()
        area = request.POST.get('area').title()
        pincode = int(request.POST.get('pincode'))
        password = request.POST.get('password')
    
        #query = {"_id" : phone,"Name" : name,"Phone_no" : phone,"Email" : email,"Address" : address,"Area" : area,'Pincode' : pincode,"Password" : password}
        x = datetime.now()
        query = {"Name" : name,"Phone_no" : phone,"Email" : email,"Address" : address,"Area" : area,'Pincode' : pincode,"JointDate" : x.strftime("%x"),
        "JointTime" : x.strftime("%X %p"),"Password" : password}

        coll.insert_one(query)
        return render(request,"login.html")

    return render(request,"signup.html")

def home(request):
    return render(request,"index.html")


def dashboard(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['Project']
    cart = db['Cart']
    signupData = db['Signup']


    if request.method == "POST":
       
        prices = {
        'Bonless_Chicken': 400,
        'Breast_Ribs': 450,
        'Chicken_legs': 350,
        'Leg_Quarter': 250,
        'Whole_Legs': 550,
        'Eggs': 160,
        'Drumstick': 360,
        'Keema': 160,
        'Lolipop': 210,
        'Wings': 160
       }

        email = request.session.get('email')

        if not email:
            return HttpResponse("You are not logged in. Please log in first.")

        user = signupData.find_one({'Email': email}, {'_id': 0})

        if not user:
            return HttpResponse("User not found.")

        Name = user.get('Name')
        Phone_no = user.get('Phone_no')
        Email = user.get('Email')
        Address = user.get('Address')
        Area = user.get('Area')
        Pincode = user.get('Pincode')

        new_items = []
        
        for product_name in prices.keys():
            quantity = int(request.POST.get(product_name, 0))
            if quantity > 0:
                price = prices[product_name]
                total = quantity * price
                
                new_items.append({
                    "Type": product_name,
                    "Quantity": quantity,
                    "Price": price,
                    "Total": total
                })    

        x = datetime.now()
        query = {
            "Customer_Name" : Name,
            "Phone_no" : Phone_no,
            "Email" : Email,
            "Address" : Address,
            "Area" : Area,
            "Pincode" : Pincode,
            "Order" : new_items,
            "OrderDate" : x.strftime("%x"),
            "OrderTime" : x.strftime("%X %p")   
        }

        if query:
            # Insert the entire order as a single document in the database
            cart.insert_one(query)
            # Pass the full order data to the template for rendering
            #return render(request, "dashboard.html", {"data": new_items})
            return render(request, "dashboard.html")
         
        else:
            # Handle the case where no items are selected
            return render(request, "dashboard.html", {"message": "No items were selected."})

    return render(request,"dashboard.html")   


def remove_from_cart(request):
    if request.method == "POST":
        client = MongoClient("mongodb://localhost:27017/")
        db = client['Project']
        cart = db['Cart']
        
        # Get user email from session
        email = request.session.get('email')
        if not email:
            return HttpResponse("You are not logged in. Please log in first.")
        
        # Get the index of item to remove
        item_index = int(request.POST.get('item_index', 0))
        
        # Find user's cart
        user_cart = cart.find_one({"Email": email})
        if user_cart and 'items' in user_cart:
            # Get current items
            items = user_cart['items']
            
            # Remove the item at specified index if it exists
            if 0 <= item_index < len(items):
                items.pop(item_index)
                
                # Update cart with remaining items
                cart.update_one(
                    {"Email": email},
                    {
                        "$set": {
                            "items": items,
                            "last_updated": datetime.now()
                        }
                    }
                )
                messages.success(request, "Item removed from cart successfully!")
            else:
                messages.error(request, "Item not found in cart.")
        else:
            messages.error(request, "Cart is empty.")
            
    return redirect('dashboard')



def order(request):

    client = MongoClient("mongodb://localhost:27017/")
    db = client['Project']
    cart = db['Cart']
    order = db['Order']

    email = request.session.get('email')

    data = cart.find({'Email' : email})
    userData = []
    
    for i in data:
        date = i.get('OrderDate')
        time = i.get('OrderTime')
        id = str(i.get('_id'))

        orders = i.get('Order', [])  # Ensure 'Order' exists and is a list
        
        if orders and isinstance(orders, list):  # Check if list is not empty

            
            order_item = orders[0]  # Access the first item safely
            
            type = order_item.get('Type', 'Unknown')
            quantity = order_item.get('Quantity', 0)
            price = order_item.get('Price', 0.0)
            total = order_item.get('Total', 0.0)
            userData.append({"Id":id,"Date" : date,"Time":time,"Type":type,"Quantity":quantity,"Price" : price,"Total":total})    

    
    user = cart.find_one({'Email' : email},{'_id':0})
    Name = user.get('Customer_Name','Unknown')
    Phone_no = user.get('Phone_no',0.0)
    Email = user.get('Email','Unkonwn')
    Address = user.get('Address',0.0)
    Area = user.get('Area',0.0)
    Pincode = user.get('Pincode',0.0)

    new_items = []

    if request.method=="POST":

        type = request.POST.get('type','Unknown')
        quantity = int(request.POST.get('quantity',0))
        price = float(request.POST.get('price',0))
        total = float(request.POST.get('total',0))
        payment = request.POST.get('payment','Unknown')
        new_items.append({"Type":type,"Quantity":quantity,"Price" : price,"Total":total})

        x = datetime.now()

        query = {
            "Customer_Name" : Name,
            "Phone_no" : Phone_no,
            "Email" : Email,
            "Address" : Address,
            "Area" : Area,
            "Pincode" : Pincode,
            "Order" : new_items,
            "Payment_Mode" : payment,
            "OrderDate" : x.strftime("%x"),
            "OrderTime" : x.strftime("%X %p")   
        }

        order.insert_one(query)
  
    return render (request,"order.html",{"data" : userData})


from bson import ObjectId
from django.shortcuts import redirect

def delete(request):

    client = MongoClient("mongodb://localhost:27017/")
    db = client['Project']
    cart = db['Cart']
    email = request.session.get('email')

    if request.method == "POST":
        order_id = request.POST.get('id')

        if order_id:
            try:
                result = cart.delete_one({'_id': ObjectId(order_id), 'Email': email})

                if result.deleted_count == 0:
                    print("No matching order found.")
            except Exception as e:
                print(f"Error deleting order: {e}")

    return redirect('order')  # Redirect instead of rendering template



def about(request):
    return render(request,"about.html")


def contact(request):

    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['textarea']

        client = MongoClient("mongodb://localhost:27017/")
        db = client['Project']
        contact = db['Contact']
        query = {"FirstName" : fname,"LastName" : lname,"Email" : email,"Phone" : phone, "Message" : message}
        contact.insert_one(query)

    return render(request,"contact.html")

