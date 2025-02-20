from rest_framework import serializers
from .models import Sale,SaleHistory,SaleReturn,SaleReturnHistory
from products.models import ProductVariantAttribute
from products.serializers import ProductVariantAttributeDetailsSerializer
from stock.models import Stocks
from stock.serializers import StocksDetailsSerializer

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Sale
        fields='__all__'

class SaleDetailsSerializer(serializers.ModelSerializer):
    stock=serializers.SerializerMethodField()
    def get_stock(self,obj):
        sale_history=SaleHistory.objects.filter(sale__id=obj.id)
        if sale_history:
            sale_history_get=SaleHistory.objects.filter(sale__id=obj.id).first()
            stock_id=sale_history_get.product_variant.id
            print(stock_id)
            product_variants=Stocks.objects.filter(id=stock_id)
            if product_variants:
                product_variant_get=Stocks.objects.filter(id=stock_id).first()
                return StocksDetailsSerializer(product_variant_get).data
            return None
        return None
    
    class Meta:
        model=Sale
        fields='__all__'

# class SaleDetailsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Sale
#         fields='__all__'

class SaleHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=SaleHistory
        fields='__all__'

class SaleReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model=SaleReturn
        fields='__all__'


class SaleReturnHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=SaleReturnHistory
        fields='__all__'
        
class SaleReturnDetailsSerializer(serializers.ModelSerializer):
    sale=SaleDetailsSerializer(read_only=True)
    class Meta:
        model=SaleReturn
        fields='__all__'