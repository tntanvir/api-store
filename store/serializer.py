from rest_framework import serializers

from .models import Product,Review,Category,Cart,CartItems,Order, OrderItem
from authore.serializer import UserSerializer,MoreInfoSerializer
from authore.models import MoreInfo
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField()  
    user = UserSerializer(read_only=True)
    size = serializers.ListField(child=serializers.CharField())
    color = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Product
        fields = '__all__'

    def validate_category(self, value):
        try:
            category = Category.objects.get(name=value)
            return category
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist")

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        category = Category.objects.get(name=category_name)
        validated_data['category'] = category
        return super().create(validated_data)


    

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
  
    class Meta:
        model = Review
        fields = '__all__'
   
class ReviewSerializerAll(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    usermore = serializers.SerializerMethodField()
  
    class Meta:
        model = Review
        fields = '__all__'
   
    def get_usermore(self, obj):
        # Access the MoreInfo object related to the User
        more_info = MoreInfo.objects.filter(user=obj.user).first()
        if more_info:
            return MoreInfoSerializer(more_info).data
        return None 

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subTotal =serializers.SerializerMethodField('product_price')
    class Meta:
        model = CartItems
        fields = ['id','cart','product','quantity','subTotal','color','size']

    def product_price(self, cartitem:CartItems):
        return cartitem.product.price*cartitem.quantity
    

class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items=CartItemSerializer(many=True)
    total_main =serializers.SerializerMethodField('total')

    class Meta:
        model = Cart
        fields = ['id','user','items','total_main','ordered']

    def total(self,cart:Cart):
        items=cart.items.all()
        total = sum([item.product.price*item.quantity for item in items])
        return total
    
# order

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'size', 'color', 'price','status']



STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    usermore = serializers.SerializerMethodField()

    status = serializers.ChoiceField(choices=STATUS_CHOICES, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user','usermore', 'ordered_at', 'total', 'items', 'status']
    def get_usermore(self, obj):
        # Access the MoreInfo object related to the User
        more_info = MoreInfo.objects.filter(user=obj.user).first()
        if more_info:
            return MoreInfoSerializer(more_info).data
        return None 

class AdminOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


# class OrderItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)  
#     subTotal = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'quantity', 'subTotal', 'color', 'size', 'price', 'seller','status']

#     def get_subTotal(self, order_item: OrderItem):
#         return order_item.price * order_item.quantity
    

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  
    subTotal = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'size', 'color', 'price', 'status','subTotal']

    # Function to update status
    def get_subTotal(self, order_item: OrderItem):
        return order_item.price * order_item.quantity
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class OrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['status']


