from rest_framework import serializers
from .models import AdditionalExpense,Purchase,PurchaseReturn,PurchaseHistory,PurchaseReturnHistory
from products.serializers import ProductDetailsSerializer,ProductVariantAttributeDetailsSerializer
from contacts.serializers import ContactDetailsSerializer
from products.models import Product,ProductVariantAttribute,ProductBarcodes
from products.serializers import ProductBarcodesDetailsSerializer,ProductBarcodesSerializer
from stock.models import Stocks,StockHistory
from stock.serializers import StocksDetailsSerializer,StocksSerializer
from contacts.models import Contact

class AdditionalExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model=AdditionalExpense
        fields='__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all())
    class Meta:
        model=Purchase
        fields='__all__'

class PurchaseDetailsSerializer(serializers.ModelSerializer):
    product_variant = serializers.SerializerMethodField()
    supplier=ContactDetailsSerializer(read_only=True)
    additional_expense=AdditionalExpenseSerializer(read_only=True)
    purchase_barcodes=serializers.SerializerMethodField()
    return_barcodes=serializers.SerializerMethodField()
    purchase_history=serializers.SerializerMethodField()
    stock=serializers.SerializerMethodField()

    def get_purchase_barcodes(self,obj):
        inv=obj.invoice_no
        #print(inv)
        barcodes=ProductBarcodes.objects.filter(inv=inv,product_status='Purchased')
        return ProductBarcodesSerializer(barcodes, many=True).data
    def get_return_barcodes(self,obj):
        inv=obj.invoice_no
        #print(inv)
        barcode=ProductBarcodes.objects.filter(inv=inv,product_status='Purchase Return')
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
        
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
    def get_purchase_history(self,obj):
        #print(obj.invoice_no)
        purchase_historys=PurchaseHistory.objects.filter(purchase__invoice_no=obj.invoice_no)
        #print(purchase_historys)
        return PurchaseHistoryDetailsSerializer2(purchase_historys,many=True).data
    
    def get_stock(selg,obj):
        inv=obj.invoice_no
        product_variant_ids = PurchaseHistory.objects.filter(purchase=obj).values_list('product_variant', flat=True)
        #print(product_variants)
        stocks = Stocks.objects.filter(product_variant__id__in=product_variant_ids)
        #print(stocks)
        return StocksSerializer(stocks,many=True).data
    class Meta:
        model=Purchase
        fields='__all__'

class PurchaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=PurchaseHistory
        fields='__all__'

class PurchaseHistoryDetailsSerializer(serializers.ModelSerializer):

    product_variant= ProductVariantAttributeDetailsSerializer(read_only=True)
    purchase=PurchaseDetailsSerializer(read_only=True)
    class Meta:
        model=PurchaseHistory
        fields='__all__'

class PurchaseHistoryDetailsSerializer2(serializers.ModelSerializer):
    product_variant= ProductVariantAttributeDetailsSerializer(read_only=True)
    barcodes_purchase=serializers.SerializerMethodField()

    def get_barcodes_purchase(self,obj):
        inv=obj.purchase.invoice_no
        barcode=ProductBarcodes.objects.filter(inv=inv,product_status='Purchased')
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
    class Meta:
        model=PurchaseHistory
        fields='__all__'


class PurchaseReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model=PurchaseReturn
        fields='__all__'



class PurchaseReturnHistorySerializer(serializers.ModelSerializer):
    barcodes_return=serializers.SerializerMethodField()

    def get_barcodes_return(self,obj):
        inv=obj.purchase_return.purchase.invoice_no
        barcode=ProductBarcodes.objects.filter(inv=inv,product_status='Purchase Return')
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
    class Meta:
        model=PurchaseReturnHistory
        fields='__all__'

class PurchaseReturnDetailsSerializer(serializers.ModelSerializer):
    purchase=PurchaseDetailsSerializer(read_only=True)
    purchase_return_history=PurchaseReturnHistorySerializer(many=True,read_only=True)
    class Meta:
        model=PurchaseReturn
        fields='__all__'

class PurchaseReturnHistoryDetailsSerializer(serializers.ModelSerializer):
    purchase_return=PurchaseReturnDetailsSerializer(read_only=True)
    purchase_history=PurchaseHistoryDetailsSerializer(read_only=True)

    class Meta:
        model=PurchaseReturnHistory
        fields='__all__'