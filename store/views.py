from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Product, Review, Category, Cart, CartItems,Order, OrderItem
from .serializer import ProductSerializer, ReviewSerializer, CategorySerializer,CartSerializer,OrderSerializer,OrderItemSerializer,OrderItemStatusUpdateSerializer,ReviewSerializerAll
from django.db import transaction
from rest_framework.generics import ListAPIView

from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework import generics


import json
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt 
# CartSerializer, CartItemSerializer

class ProductListCreateAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()

        size = request.query_params.get('size', None)
        if size:
            products = products.filter(size__icontains=size)
        
        user=request.query_params.get('user', None)
        if user:
            products = products.filter(user__username=user)


        color = request.query_params.get('color', None)
        if color:
            products = products.filter(color__icontains=color)

        category = request.query_params.get('category', None)
        if category:
            products = products.filter(category__name=category)

        brand = request.query_params.get('brand', None)
        if brand:
            products = products.filter(brand__icontains=brand)
        
        alldata = request.query_params.get('all', None)

        
        if alldata:
            serializer = ProductSerializer(products,many=True)
            return Response(serializer.data)

        paginator = PageNumberPagination()
        paginator.page_size = 12  # Number of products per page
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        print(request.user)
        if serializer.is_valid():
            print('valid')
            serializer.save(user=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductFilterByCategoryAPIView(APIView):
    def get(self, request):
        category = request.query_params.get('category', None)
        if category:
            products = Product.objects.filter(category__name=category)
        else:
            products = Product.objects.all()
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class TopProductsAPIView(APIView):
    def get(self, request):
        top_products = Product.objects.all().order_by('-created_at')[:8]
        
        serializer = ProductSerializer(top_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductDetailAPIView(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class AllReviewView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializerAll
    pagination_class= None





class ReviewListCreateAPIView(APIView):
    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, product_id):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product_id=product_id, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailAPIView(APIView):
    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class CheckProductInOrderHistoryAPIView(APIView):
    def get(self, request, product_id):
        user = request.user
        product_in_order = OrderItem.objects.filter(order__user=user, product_id=product_id).exists()

        return Response({'product_in_order_history': product_in_order}, status=status.HTTP_200_OK)



class CategoryView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





class CartView(APIView):
    def get(self, request):
        cart = Cart.objects.filter(user=request.user, ordered=False).first()
        if cart:
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        size = request.data.get('size')
        color = request.data.get('color')

        # Check if the product exists
        product = get_object_or_404(Product, id=product_id)

        # Get or create the cart for the user
        cart, created = Cart.objects.get_or_create(user=user, ordered=False)

        # Check if the cart item already exists
        cart_item, item_created = CartItems.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'size': size, 'color': color}
        )

        if not item_created:
            # If the item is already in the cart, update the quantity, size, and color
            cart_item.quantity += int(quantity)
            if size:
                cart_item.size = size
            if color:
                cart_item.color = color
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, item_id):
        cart_item = get_object_or_404(CartItems, id=item_id, cart__user=request.user)
        quantity = request.data.get('quantity', cart_item.quantity)
        size = request.data.get('size', cart_item.size)
        color = request.data.get('color', cart_item.color)

        cart_item.quantity = quantity
        cart_item.size = size
        cart_item.color = color
        cart_item.save()

        cart = cart_item.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, item_id):
        cart_item = get_object_or_404(CartItems, id=item_id, cart__user=request.user)
        cart_item.delete()

        cart = cart_item.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderItemBySellerView(ListAPIView):
    serializer_class = OrderItemSerializer
    pagination_class= None
    

    def get_queryset(self):
        seller_name = self.request.query_params.get('seller', None)
        if seller_name:
            return OrderItem.objects.filter(seller__username=seller_name)
        return OrderItem.objects.none()

# class CheckoutAPIView(APIView):
#     @transaction.atomic
#     def post(self, request):
#         user = request.user
#         cart = get_object_or_404(Cart, user=user, ordered=False)

#         if cart.items.count() == 0:
#             return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

#         order = Order.objects.create(user=user)
#         total = 0

#         for cart_item in cart.items.all():
#             # Update product quantity in the database
#             product = cart_item.product
#             if product.quantity < cart_item.quantity:
#                 return Response({"detail": f"Not enough {product.name} in stock."}, status=status.HTTP_400_BAD_REQUEST)

#             product.quantity -= cart_item.quantity
#             product.save()

#             # Create OrderItem
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 size=cart_item.size,
#                 color=cart_item.color,
#                 price=cart_item.product.price * cart_item.quantity
#             )

#             total += order_item.price

#         # Update the total price of the order
#         order.total = total
#         order.save()

#         # Mark the cart as ordered
#         cart.ordered = True
#         cart.save()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# class CheckoutAPIView(APIView):
#     @transaction.atomic
#     def post(self, request):
#         user = request.user
#         cart = get_object_or_404(Cart, user=user, ordered=False)

#         if cart.items.count() == 0:
#             return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

#         order = Order.objects.create(user=user)
#         total = 0

#         for cart_item in cart.items.all():
#             product = cart_item.product
#             if product.quantity < cart_item.quantity:
#                 return Response({"detail": f"Not enough {product.name} in stock."}, status=status.HTTP_400_BAD_REQUEST)

#             product.quantity -= cart_item.quantity
#             product.save()

#             # Create OrderItem
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 size=cart_item.size,
#                 color=cart_item.color,
#                 price=cart_item.product.price * cart_item.quantity
#             )

#             total += order_item.price

#             # Update seller's order history
#             if product.user:  # Ensure that the product has a seller
#                 # Create or update the seller's order
#                 seller_order, created = Order.objects.get_or_create(
#                     user=product.user,
#                     ordered_at=order.ordered_at,
#                     defaults={'total': 0}
#                 )
#                 seller_order.total += order_item.price
#                 seller_order.save()

#         order.total = total
#         order.save()

#         cart.ordered = True
#         cart.save()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)






    

class CustomerOrderHistoryAPIView(ListAPIView):
    serializer_class = OrderSerializer
    pagination_class = None
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-ordered_at')



class SellerOrderHistoryAPIView(ListAPIView):
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self):
        
        if self.request.user.groups.filter(name='Sellers').exists():
            return Order.objects.filter(user=self.request.user).order_by('-ordered_at')
        return Order.objects.none() 



class AdminOrderListAPIView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.all().order_by('-ordered_at')


class AdminOrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.data.get('status')  # Assuming status is passed in the request data
            if new_status:
                order.status = new_status
                order.save()
                return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# View to handle product status change by admin
class AdminProductStatusUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            new_status = request.data.get('status')  # Assuming status is passed in the request data
            if new_status:
                product.status = new_status
                product.save()
                return Response({'message': 'Product status updated successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)







# class UpdateOrderStatusView(APIView):

#     def post(self, request, order_id):
#         try:
#             order_item = OrderItem.objects.get(id=order_id)
#             status_value = request.data.get('status', None)
            
#             if status_value not in dict(OrderItem.STATUS_CHOICES).keys():
#                 return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

#             order_item.status = status_value
#             order_item.save()

#             return Response({"message": "Status updated successfully"}, status=status.HTTP_200_OK)
#         except OrderItem.DoesNotExist:
#             return Response({"error": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)
        

class UpdateOrderItemStatus(APIView):

    def get(self, request, order_item_id, *args, **kwargs):
        try:
            # Get the order item and ensure the requesting user is the seller
            order_item = OrderItem.objects.get(id=order_item_id, seller=request.user)
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and return the current order item details, including the status
        serializer = OrderItemStatusUpdateSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle POST request to update the order item status
    def post(self, request, order_item_id, *args, **kwargs):
        try:
            # Get the order item and ensure the requesting user is the seller
            order_item = OrderItem.objects.get(id=order_item_id, seller=request.user)
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and update the status
        serializer = OrderItemStatusUpdateSerializer(order_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Status updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







# payment
STORE_ID = "zerok67a720d7546c8"
STORE_PASSWORD = "zerok67a720d7546c8@ssl"
SSL_SANDBOX_URL = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data  # Get JSON data from request

        # Payment Details
        payment_data = {
            "store_id": STORE_ID,
            "store_passwd": STORE_PASSWORD,
            "total_amount": data.get("amount"),  # Amount to be paid
            "currency": "BDT",
            "tran_id": f"txn_{request.user.id}_{data.get('order_id')}",  # Unique transaction ID
            "success_url": f"http://127.0.0.1:8000/store/payment/success/{request.user.id}/",
            "fail_url": "http://127.0.0.1:8000/store/payment/fail/",
            "cancel_url": "http://127.0.0.1:8000/store/payment/cancel/",
            "cus_name": request.user.username,
            "cus_email": request.user.email,
            "cus_phone": data.get("phone"),
            "cus_add1": data.get("address"),
            "cus_city": data.get("city"),
            "cus_country": "Bangladesh",
            "shipping_method": "NO",
            "product_name": "E-commerce Products",
            "product_category": "General",
            "product_profile": "general",
        }

        # Request Payment Session from SSLCommerz
        response = requests.post(SSL_SANDBOX_URL, data=payment_data)
        response_data = response.json()

        if response_data.get("status") == "SUCCESS":
            return Response({"payment_url": response_data["GatewayPageURL"]}, status=200)
        return Response({"error": "Payment session failed"}, status=400)



class CheckoutAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user, ordered=False)
        
        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total
        total = sum([item.product.price * item.quantity for item in cart.items.all()])

        # Create the order
        order = Order.objects.create(
            user=user,
            total=total,
            status='pending',  # New orders will be in pending status
        )

        # Move CartItems to OrderItems
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                size=item.size,
                color=item.color,
                price=item.product.price,
                seller=item.product.user
            )

        # Mark cart as ordered
        cart.ordered = True
        cart.save()

        # Clear the cart
        cart.items.all().delete()

        return Response({"message": "Order placed successfully. Pending approval by admin."}, status=status.HTTP_201_CREATED)


# class PaymentSuccessView(APIView):
#     # def get(self, request):
#     #     return Response({"message": "Payment Successful!", "data": request.query_params})
#     @transaction.atomic
#     def post(self,pk , request):
#         user = User.objects.get(pk=pk)
#         cart = get_object_or_404(Cart, user=user, ordered=False)
        
#         if cart.items.count() == 0:
#             return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

#         # Calculate total
#         total = sum([item.product.price * item.quantity for item in cart.items.all()])

#         # Create the order
#         order = Order.objects.create(
#             user=user,
#             total=total,
#             status='pending',  # New orders will be in pending status
#         )

#         # Move CartItems to OrderItems
#         for item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 size=item.size,
#                 color=item.color,
#                 price=item.product.price,
#                 seller=item.product.user
#             )

#         # Mark cart as ordered
#         cart.ordered = True
#         cart.save()

#         # Clear the cart
#         cart.items.all().delete()

#         return Response({"message": "Order placed successfully. Pending approval by admin."}, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):
    
    def post(self, request, pk):  # Fix argument order
        user = get_object_or_404(User, pk=pk)
        cart = get_object_or_404(Cart, user=user, ordered=False)

        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total
        total = sum([item.product.price * item.quantity for item in cart.items.all()])

        # Create the order
        order = Order.objects.create(
            user=user,
            total=total,
            status='pending',
        )

        # Move CartItems to OrderItems
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                size=item.size,
                color=item.color,
                price=item.product.price,
                seller=item.product.user
            )

        # Mark cart as ordered
        cart.ordered = True
        cart.save()

        # Clear the cart
        cart.items.all().delete()

        return redirect("http://localhost:5173/profile/orderhistory")


class PaymentFailView(APIView):
    def post(self, request):
        return redirect("http://localhost:5173/cart")  



class PaymentCancelView(APIView):
    def post(self, request):
        return redirect("http://localhost:5173/cart")  