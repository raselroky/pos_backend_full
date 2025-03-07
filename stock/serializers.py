from rest_framework import serializers
from .models import Stocks,StockHistory,StockAdjustment,StockTransfer
from catalog.serializers import BrandSerializer,ColorVariationSerializer,AttributeVariationSerializer,ProductUnitSerializer
from products.serializers import ProductDetailsSerializer,ProductVariantAttributeDetailsSerializer

class StocksSerializer(serializers.ModelSerializer):
    class Meta:
        model=Stocks
        fields='__all__'

class StocksDetailsSerializer(serializers.ModelSerializer):
    product_variant=ProductVariantAttributeDetailsSerializer(read_only=True)
    class Meta:
        model=Stocks
        fields='__all__'


class StocksHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=StockHistory
        fields='__all__'

class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=StockAdjustment
        fields='__all__'

class StockAdjustmentDetailsSerializer(serializers.ModelSerializer):
    stock=StocksDetailsSerializer(many=True,read_only=True)
    class Meta:
        model=StockAdjustment
        fields='__all__'

class StockTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model=StockTransfer
        fields='__all__'

class StockTransferDetailsSerializer(serializers.ModelSerializer):
    stock=StocksDetailsSerializer(many=True,read_only=True)
    class Meta:
        model=StockTransfer
        fields='__all__'