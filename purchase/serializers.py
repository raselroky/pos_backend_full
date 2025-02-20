from rest_framework import serializers
from .models import AdditionalExpense,Purchase,PurchaseReturn,PurchaseHistory,PurchaseReturnHistory
from products.serializers import ProductDetailsSerializer,ProductVariantAttributeDetailsSerializer
from contacts.serializers import ContactDetailsSerializer
from products.models import Product,ProductVariantAttribute

class AdditionalExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model=AdditionalExpense
        fields='__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Purchase
        fields='__all__'

class PurchaseDetailsSerializer(serializers.ModelSerializer):
    product_variant = serializers.SerializerMethodField()
    supplier=ContactDetailsSerializer(read_only=True)
    additional_expense=AdditionalExpenseSerializer(read_only=True)

    def get_product_variant(self,obj):
        purchase_history=PurchaseHistory.objects.filter(purchase__id=obj.id)
        if purchase_history:
            purchase_history_get=PurchaseHistory.objects.filter(purchase__id=obj.id).first()
            product_variant_id=purchase_history_get.product_variant.id
            product_variant=ProductVariantAttribute.objects.filter(id=product_variant_id)
            if product_variant:
                product_variant_get=ProductVariantAttribute.objects.filter(id=product_variant_id).first()
                return ProductVariantAttributeDetailsSerializer(product_variant_get).data
            return None
        return None
    class Meta:
        model=Purchase
        fields='__all__'

class PurchaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=PurchaseHistory
        fields='__all__'

class PurchaseHistoryDetailsSerializer(serializers.ModelSerializer):
    from catalog.serializers import BrandSerializer,ColorVariationSerializer,AttributeVariationSerializer,ProductUnitSerializer
    product_variant= ProductVariantAttributeDetailsSerializer(read_only=True)
    purchase=PurchaseDetailsSerializer(read_only=True)
    class Meta:
        model=PurchaseHistory
        fields='__all__'



class PurchaseReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model=PurchaseReturn
        fields='__all__'

class PurchaseReturnDetailsSerializer(serializers.ModelSerializer):
    # product_variant = ProductVariantAttributeDetailsSerializer(read_only=True)
    # supplier=ContactDetailsSerializer(read_only=True)
    # additional_expense=AdditionalExpenseSerializer(read_only=True)
    purchase=PurchaseDetailsSerializer(read_only=True)
    class Meta:
        model=PurchaseReturn
        fields='__all__'


class PurchaseReturnHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model=PurchaseReturnHistory
        fields='__all__'


class PurchaseReturnHistoryDetailsSerializer(serializers.ModelSerializer):
    purchase_return=PurchaseReturnDetailsSerializer(read_only=True)
    purchase_history=PurchaseHistoryDetailsSerializer(read_only=True)

    class Meta:
        model=PurchaseReturnHistory
        fields='__all__'