from rest_framework import serializers
from .models import Sale,SaleHistory,SaleReturn,SaleReturnHistory,Quotation,QuotationHistory
from products.models import ProductVariantAttribute,ProductBarcodes
from products.serializers import ProductVariantAttributeDetailsSerializer,ProductBarcodesDetailsSerializer
from stock.models import Stocks
from stock.serializers import StocksDetailsSerializer
from contacts.serializers import ContactDetailsSerializer
from contacts.models import Contact
from django.db.models import Q


class SaleSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all())
    class Meta:
        model=Sale
        fields='__all__'


class SaleHistorySerializer(serializers.ModelSerializer):
    product_variant_id=serializers.SerializerMethodField()
    def get_product_variant_id(self,obj):
        if obj.product_variant.product_variant.id:
            return obj.product_variant.product_variant.id
        return None
    class Meta:
        model=SaleHistory
        fields='__all__'

class SaleDetailsSerializer(serializers.ModelSerializer):
    stock=serializers.SerializerMethodField()
    sale_history=SaleHistorySerializer(read_only=True,many=True)
    barcodes_sold=serializers.SerializerMethodField()
    customer=ContactDetailsSerializer(read_only=True)
    def get_barcodes_sold(self,obj):
        inv=obj.invoice_no
        #print(inv)
        barcode=ProductBarcodes.objects.filter(Q(inv_sold=inv,product_status='Sold') | Q(inv_sold=inv))
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
    
    def get_stock(self,obj):
        sale_history=SaleHistory.objects.filter(sale__id=obj.id)
        if sale_history:
            sale_history_get=SaleHistory.objects.filter(sale__id=obj.id).first()
            stock_id=sale_history_get.product_variant.id
            product_variants=Stocks.objects.filter(id=stock_id)
            if product_variants:
                product_variant_get=Stocks.objects.filter(id=stock_id).first()
                return StocksDetailsSerializer(product_variant_get).data
            return None
        return None
    
    class Meta:
        model=Sale
        fields='__all__'

class SaleReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model=SaleReturn
        fields='__all__'


class SaleReturnHistorySerializer(serializers.ModelSerializer):
    barcodes_return=serializers.SerializerMethodField()

    def get_barcodes_return(self,obj):
        #print(obj)
        barcode=ProductBarcodes.objects.filter(inv_sold=obj.sale_return.sale.invoice_no,product_status='Sales Return')
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
    class Meta:
        model=SaleReturnHistory
        fields='__all__'
        
class SaleReturnDetailsSerializer(serializers.ModelSerializer):
    sale=SaleDetailsSerializer(read_only=True)
    sale_return_history=serializers.SerializerMethodField()

    def get_sale_return_history(self,obj):
        #print(obj)
        sale_returns=SaleReturnHistory.objects.filter(sale_return__return_no=obj.return_no)
        serializer=SaleReturnHistorySerializer(sale_returns,many=True)
        return serializer.data
    class Meta:
        model=SaleReturn
        fields='__all__'
    



### quotation ###



class QuotationSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all())
    class Meta:
        model=Quotation
        fields='__all__'


class QuotationHistorySerializer(serializers.ModelSerializer):
    product_variant_id=serializers.SerializerMethodField()
    def get_product_variant_id(self,obj):
        if obj.product_variant.product_variant.id:
            return obj.product_variant.product_variant.id
        return None
    class Meta:
        model=QuotationHistory
        fields='__all__'

class QuotationDetailsSerializer(serializers.ModelSerializer):
    stock=serializers.SerializerMethodField()
    quotation_history=QuotationHistorySerializer(read_only=True,many=True)
    barcodes_sold=serializers.SerializerMethodField()
    customer=ContactDetailsSerializer(read_only=True)
    def get_barcodes_sold(self,obj):
        inv=obj.invoice_no
        #print(inv)
        barcode=ProductBarcodes.objects.filter(Q(inv_quotation=inv,product_status='Quotation') | Q(inv_quotation=inv))
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
    
    def get_stock(self,obj):
        quotation_history=QuotationHistory.objects.filter(quotation__id=obj.id)
        if quotation_history:
            quotation_history_get=QuotationHistory.objects.filter(quotation__id=obj.id).first()
            stock_id=quotation_history_get.product_variant.id
            product_variants=Stocks.objects.filter(id=stock_id)
            if product_variants:
                product_variant_get=Stocks.objects.filter(id=stock_id).first()
                return StocksDetailsSerializer(product_variant_get).data
            return None
        return None
    
    class Meta:
        model=Quotation
        fields='__all__'