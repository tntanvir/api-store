from django.urls import path
from .views import ProductDetailAPIView, ProductListCreateAPIView, ReviewListCreateAPIView, ReviewDetailAPIView, CategoryView, TopProductsAPIView,CartView,CheckoutAPIView,CustomerOrderHistoryAPIView, SellerOrderHistoryAPIView,CheckProductInOrderHistoryAPIView,ProductFilterByCategoryAPIView,AdminOrderListAPIView, AdminOrderStatusUpdateAPIView,AdminProductStatusUpdateAPIView ,OrderItemBySellerView,UpdateOrderItemStatus,InitiatePaymentView,PaymentSuccessView,PaymentFailView,PaymentCancelView,AllReviewView

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('category/', CategoryView.as_view(), name='category'),
    path('product/category/', ProductFilterByCategoryAPIView.as_view(), name='category'),

    path('products/reviews/', AllReviewView.as_view(), name='reviewsall'),
    path('products/<int:product_id>/reviews/', ReviewListCreateAPIView.as_view(), name='product-reviews'),
    path('reviews/<int:review_id>/', ReviewDetailAPIView.as_view(), name='review-detail'),
    path('order-history/check-product/<int:product_id>/', CheckProductInOrderHistoryAPIView.as_view(), name='check-product-in-order-history'),
    path('products/top/', TopProductsAPIView.as_view(), name='top-products'),
    path('cart/', CartView.as_view(), name='cart'),  
    path('cart/item/<int:item_id>/', CartView.as_view(), name='cart-item'),  
    path('orders/filter-by-seller/', OrderItemBySellerView.as_view(), name='orderitem-by-seller'),

     path('orders/update-status/<int:order_item_id>/', UpdateOrderItemStatus.as_view(), name='update-order-status'),

    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('orders/history/customer/', CustomerOrderHistoryAPIView.as_view(), name='customer-order-history'),
    path('seller-order-history/', SellerOrderHistoryAPIView.as_view(), name='seller-order-history'),
    path('admin/porducthistory/', AdminOrderListAPIView.as_view(), name='admin-history')  ,

    path('admin/orders/<int:order_id>/status/', AdminOrderStatusUpdateAPIView.as_view(), name='admin-order-status-update'),
    path('admin/products/<int:product_id>/status/', AdminProductStatusUpdateAPIView.as_view(), name='admin-product-status-update'),




    path("payment/", InitiatePaymentView.as_view(), name="initiate_payment"),
    path("payment/success/<int:pk>/", PaymentSuccessView.as_view(), name="payment_success"),
    path("payment/fail/", PaymentFailView.as_view(), name="payment_fail"),
    path("payment/cancel/", PaymentCancelView.as_view(), name="payment_cancel"),
    
    
]