from rest_framework import serializers
from .models import Stocks,StockHistory,StockAdjustment,StockTransfer
from catalog.serializers import BrandSerializer,ColorVariationSerializer,AttributeVariationSerializer,ProductUnitSerializer
from products.serializers import ProductDetailsSerializer,ProductVariantAttributeDetailsSerializer,ProductBarcodesDetailsSerializer
from products.models import ProductBarcodes
from django.db.models import Q


class StocksSerializer(serializers.ModelSerializer):
    class Meta:
        model=Stocks
        fields='__all__'



class StocksHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=StockHistory
        fields='__all__'

class StocksDetailsSerializer(serializers.ModelSerializer):
    product_variant=ProductVariantAttributeDetailsSerializer(read_only=True)
    stock_history=serializers.SerializerMethodField()
    barcodes=serializers.SerializerMethodField()
    def get_barcodes(self,obj):
        #print(obj.product_variant)
        barcode=ProductBarcodes.objects.filter(product_variant=obj.product_variant)
        
        return ProductBarcodesDetailsSerializer(barcode,many=True).data
    def get_stock_history(self,obj):
        #print(obj.product_variant)
        history=StockHistory.objects.filter(stock__product_variant=obj.product_variant)
        #print(history)
        return StocksHistorySerializer(history,many=True).data
    class Meta:
        model=Stocks
        fields='__all__'

class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=StockAdjustment
        fields='__all__'

class StockAdjustmentDetailsSerializer(serializers.ModelSerializer):
    stock=StocksDetailsSerializer(read_only=True)
    accept_branch=serializers.SerializerMethodField()
    given_branch=serializers.SerializerMethodField()
    def get_accept_branch(slef,obj):
        if obj.accept_branch:
            return {
                "id":obj.accept_branch.id,
                "branch":obj.accept_branch.branch_name,
                "country":obj.accept_branch.country.country_name
            }
        return None
    def get_given_branch(slef,obj):
        if obj.given_branch:
            return {
                "id":obj.given_branch.id,
                "branch":obj.given_branch.branch_name,
                "country":obj.given_branch.country.country_name
            }
        return None
    class Meta:
        model=StockAdjustment
        fields='__all__'

class StockTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model=StockTransfer
        fields='__all__'

class StockTransferDetailsSerializer(serializers.ModelSerializer):
    stock=StocksDetailsSerializer(read_only=True)
    accept_branch=serializers.SerializerMethodField()
    given_branch=serializers.SerializerMethodField()
    def get_accept_branch(slef,obj):
        if obj.accept_branch:
            return {
                "id":obj.accept_branch.id,
                "branch":obj.accept_branch.branch_name,
                "country":obj.accept_branch.country.country_name
            }
        return None
    def get_given_branch(slef,obj):
        if obj.given_branch:
            return {
                "id":obj.given_branch.id,
                "branch":obj.given_branch.branch_name,
                "country":obj.given_branch.country.country_name
            }
        return None
    class Meta:
        model=StockTransfer
        fields='__all__'