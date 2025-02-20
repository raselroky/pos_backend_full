from rest_framework import serializers
from .models import Product,ProductVariantAttribute,ProductBarcodes
from catalog.serializers import *
from catalog.models import *
from purchase.models import Purchase,PurchaseReturn


class ProductSerializer(serializers.ModelSerializer):
    sku=serializers.CharField(required=False)
    class Meta:
        model=Product
        fields='__all__'

class ProductDetailsSerializer(serializers.ModelSerializer):

    category=serializers.SerializerMethodField()
    sub_category=serializers.SerializerMethodField()
    brand=serializers.SerializerMethodField()
    unit =serializers.SerializerMethodField()
    #stock_quantity=serializers.SerializerMethodField()

    # def get_stock_quantity(self,obj):
    #     stock=int(obj.stock_quantity)
    #     purchase=Purchase.objects.filter(product__id=obj.id)
    #     if purchase.exists():
    #         purchase_get=Purchase.objects.get(product__id=obj.id)
    #         stock+=int(purchase_get.purchase_qunatity)
    #     purchase_return=PurchaseReturn.objects.filter(product__id=obj.id)
    #     if purchase_return.exists():
    #         purchase_return_get=PurchaseReturn.objects.get(product__id=obj.id)
    #         stock=stock-int(purchase_return_get.return_qunatity)
            
    #     return stock
    def get_category(self,obj):
        if obj.category:
            return {
                "id":obj.category.id,
                "category_name":obj.category.category_name,
                "description":obj.category.description
            }
        return None
    def get_sub_category(self,obj):
        if obj.sub_category:
            if obj.sub_category.category:
                return {
                    "category":{
                        "id":obj.sub_category.category.id,
                        "category_name":obj.sub_category.category.category_name
                        },
                    "id":obj.sub_category.id,
                    "sub_category_name":obj.sub_category.subcategory_name,
                    "description":obj.sub_category.description
                }
            return {
                "id":obj.sub_category.id,
                "sub_category_name":obj.sub_category.subcategory_name,
                "description":obj.sub_category.description
            }
        return None
    def get_brand(self,obj):
        if obj.brand:
            return {
                "id":obj.brand.id,
                "brand_name":obj.brand.brand_name,
                "description":obj.brand.description
            }
        return None
    def get_unit(self,obj):
        if obj.unit:
            return {
                "id":obj.unit.id,
                "unit_name":obj.unit.unit_name,
                "unit_short_name":obj.unit.unit_short_name
            }
        return None
    class Meta:
        model=Product
        fields='__all__'


class ProductDetailsSerializer2(serializers.ModelSerializer):
    category=serializers.SerializerMethodField()
    sub_category=serializers.SerializerMethodField()
    brand=serializers.SerializerMethodField()
    unit =serializers.SerializerMethodField()
    
    def get_category(self,obj):
        if obj.category:
            return obj.category.category_name
            
        return None
    def get_sub_category(self,obj):
        if obj.sub_category:
            return obj.sub_category.subcategory_name
                
        return None
    def get_brand(self,obj):
        if obj.brand:
            return obj.brand.brand_name
               
        return None
    def get_unit(self,obj):
        if obj.unit:
            return obj.unit.unit_name
                
        return None
    class Meta:
        model=Product
        fields='__all__'

class ProductVariantAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductVariantAttribute
        fields='__all__'


class ProductVariantAttributeDetailsSerializer(serializers.ModelSerializer):
    product = ProductDetailsSerializer(read_only=True)
    color_attribute = ColorVariationSerializer(read_only=True)
    variation_attribute = AttributeVariationSerializer(read_only=True)
    class Meta:
        model=ProductVariantAttribute
        fields='__all__'



class ProductBarcodesSerializer(serializers.ModelSerializer):
    barcode=serializers.CharField(required=False)
    class Meta:
        model=ProductBarcodes
        fields='__all__'


class ProductBarcodesDetailsSerializer(serializers.ModelSerializer):
    product_variant=ProductVariantAttributeDetailsSerializer(read_only=True)
    class Meta:
        model=ProductBarcodes
        fields='__all__'