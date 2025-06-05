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
    color_attribute=serializers.SerializerMethodField()
    variation_attribute=serializers.SerializerMethodField()

    def get_color_attribute(self,obj):
        #print(obj)
        product_variant = ProductVariantAttribute.objects.filter(product=obj).first()
        #print(product_variant)
        if product_variant and product_variant.color_attribute:
            
            return {
                "id":product_variant.color_attribute.id,
                "color_name":product_variant.color_attribute.color_name,
            }
        return None
    def get_variation_attribute(self,obj):
        product_variant = ProductVariantAttribute.objects.filter(product=obj).first()
        if product_variant and product_variant.variation_attribute:
            
            return {
                "id":product_variant.variation_attribute.id,
                "name":product_variant.variation_attribute.name,
                "values":product_variant.variation_attribute.values
            }
        return None
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
                "description":obj.category.description,
                "vat_percentage":obj.category.vat_percentage,
                "vat_amounts":obj.category.vat_amounts
            }
        return None
    def get_sub_category(self,obj):
        if obj.sub_category:
            if obj.sub_category.category:
                return {
                    "category":{
                        "id":obj.sub_category.category.id,
                        "category_name":obj.sub_category.category.category_name,
                        "vat_percentage":obj.sub_category.category.vat_percentage,
                        "vat_amounts":obj.sub_category.category.vat_amounts
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
    category_name=serializers.SerializerMethodField()
    subcategory_name=serializers.SerializerMethodField()
    brand_name=serializers.SerializerMethodField()
    unit_name =serializers.SerializerMethodField()
    color_name=serializers.SerializerMethodField()
    name=serializers.SerializerMethodField()
    values=serializers.SerializerMethodField()

    def get_category_name(self,obj):
        if obj.category:
            return obj.category.category_name
            
        return None
    def get_subcategory_name(self,obj):
        if obj.sub_category:
            return obj.sub_category.subcategory_name
                
        return None
    def get_brand_name(self,obj):
        if obj.brand:
            return obj.brand.brand_name
               
        return None
    def get_unit_name(self,obj):
        if obj.unit:
            return obj.unit.unit_name
                
        return None
    
    def get_color_name(self, obj):
        pv = ProductVariantAttribute.objects.filter(product=obj).first()
        if pv and pv.color_attribute:
            return pv.color_attribute.color_name
        return None

    def get_name(self, obj):
        pv = ProductVariantAttribute.objects.filter(product=obj).first()
        if pv and pv.variation_attribute:
            return pv.variation_attribute.name
        return None

    def get_values(self, obj):
        pv = ProductVariantAttribute.objects.filter(product=obj).first()
        if pv and pv.variation_attribute:
            return pv.variation_attribute.values
        return None
    
    class Meta:
        model=Product
        fields=['id','product_name','sku','category_name','subcategory_name','brand_name','unit_name','color_name','name','values','file','weight','product_type','country','vat_percentage','vat_amount']


class ProductVariantAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductVariantAttribute
        fields='__all__'


class ProductVariantAttributeDetailsSerializer(serializers.ModelSerializer):
    
    product = ProductDetailsSerializer(read_only=True)
    color_attribute = ColorVariationSerializer(read_only=True)
    variation_attribute = AttributeVariationSerializer(read_only=True)
    stocks=serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        # Get the user object from the related 'created_by' ForeignKey
        if obj.created_by:
            return obj.created_by.email
        return None  # Return None if no user is associated

    def get_updated_by(self, obj):
        # Get the user object from the related 'updated_by' ForeignKey
        if obj.updated_by:
            return  obj.updated_by.email
        return None

    def get_stocks(self,obj):
        from stock.models import Stocks
        
        st=Stocks.objects.filter(product_variant__id=obj.id)
        if st.exists():
            
            st_get=Stocks.objects.filter(product_variant=obj).first()
            if st_get:
               return {
                "id":st_get.id,
                "product_variant_id":st_get.product_variant.id,
                "product_variant_name":st_get.product_variant.product.product_name,
                "purchase_price":st_get.purchase_price,
                "selling_price":st_get.selling_price,
                "total_qty":st_get.total_qty,
                "sold_qty":st_get.sold_qty,
                "hold_qty":st_get.hold_qty,
                "available_qty":st_get.available_qty,
                "transfering_qty":st_get.transfering_qty,
                "discount_percentage":st_get.discount_percentage
                }
            return None
        return None
    class Meta:
        model=ProductVariantAttribute
        fields='__all__'



class ProductBarcodesSerializer(serializers.ModelSerializer):
    
    barcode=serializers.CharField(required=False)
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        # Get the user object from the related 'created_by' ForeignKey
        if obj.created_by:
            return obj.created_by.email
        return None  # Return None if no user is associated

    def get_updated_by(self, obj):
        # Get the user object from the related 'updated_by' ForeignKey
        if obj.updated_by:
            return  obj.updated_by.email
        return None
    
    class Meta:
        model=ProductBarcodes
        fields='__all__'


class ProductBarcodesDetailsSerializer(serializers.ModelSerializer):
    product_variant=ProductVariantAttributeDetailsSerializer(read_only=True)
    class Meta:
        model=ProductBarcodes
        fields='__all__'