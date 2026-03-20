from rest_framework import serializers
from .models import Category, Product, Review
from django.db.models import Avg


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