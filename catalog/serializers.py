from rest_framework import serializers
from .models import ProductUnit,Brand,Category,SubCategory,ColorVariation,AttributeVariation

class ProductUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductUnit
        fields='__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields='__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=SubCategory
        fields='__all__'

class SingleCategorySerializer(serializers.ModelSerializer):
    subcategory=serializers.SerializerMethodField()

    def get_subcategory(self,obj):
        sub=SubCategory.objects.filter(category__id=obj.id)
        if sub.exists():
            sub2=SubCategorySerializer(sub,many=True).data
            return sub2
        return None
    class Meta:
        model=Category
        fields='__all__'

class SubCategoryDetailsSerializer(serializers.ModelSerializer):
    category=serializers.SerializerMethodField()

    def get_category(self,obj):
        if obj.category:
            return {
                "id":obj.category.id,
                "category_name":obj.category.category_name,
                "category_code":obj.category.category_code,
                "description":obj.category.description
            }
        return None
    class Meta:
        model=SubCategory
        fields='__all__'


class ColorVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model=ColorVariation
        fields='__all__'

class AttributeVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model=AttributeVariation
        fields='__all__'