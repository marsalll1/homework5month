from rest_framework import serializers, generics
from django.db.models import Avg
from .models import Category, Product, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def validate_text(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Review text must be at least 5 characters")
        return value

    def validate(self, data):
        if 'stars' in data:
            if data['stars'] < 1 or data['stars'] > 5:
                raise serializers.ValidationError("Stars must be between 1 and 5")
        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_title(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Title is too short")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'reviews', 'rating']

    def get_rating(self, obj):
        return obj.reviews.aggregate(avg=Avg('stars'))['avg']


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Category name must be at least 3 characters")
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Category already exists")
        return value


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ProductReviewsListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductWithReviewsSerializer