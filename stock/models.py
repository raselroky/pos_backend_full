from django.db import models
from users.models import CommonAction
from catalog.models import Brand,Category,SubCategory,ProductUnit,AttributeVariation,ColorVariation
from products.models import Product,ProductBarcodes,ProductVariantAttribute
from branch.models import Branch


PRODUCT_TYPE=(
    ('None','None'),
    ('Single','Single'),
    ('Variable','Variable'),
    ('Combo','Combo')
)

STOCK_TYPE=(
    ('Purchase','Purchase'),
    ('Sales','Sales'),
    ('Purchase Return','Purchase Return'),
    ('Sales Return','Sales Return'),
    ('Damage','Damage'),
    ('Transfer','Transfer'),
    ('Adjustment','Adjustment'),
    ('Opening','Opening')
)

class Stocks(CommonAction):
    product_variant = models.ForeignKey(ProductVariantAttribute, related_name='product_stocks',on_delete=models.CASCADE,null=True,blank=True)

    total_qty       = models.FloatField(default=0) 
    sold_qty        = models.FloatField(default=0) 
    hold_qty        = models.FloatField(default=0) 
    available_qty   = models.FloatField(default=0)
    transfering_qty = models.FloatField(default=0)
    warranty        = models.PositiveIntegerField(default=0)
    purchase_price  = models.FloatField(default=0)
    selling_price   = models.FloatField(default=0)
    discount_percentage = models.FloatField(default=0)
    remark       = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'products_stocks'
        verbose_name = "Stock"
        verbose_name_plural = "Stocks" 
        indexes = [
        models.Index(fields=['-product_variant', '-created_at'], name='products_stocks_idx'),
        ]

    def __str__(self):
        return str(self.product_variant)

class StockHistory(CommonAction):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    price    = models.FloatField(default=0) 
    log_type = models.CharField(max_length=50, choices=STOCK_TYPE, default='None')
    reference= models.PositiveIntegerField(default=None, null=True, blank=True) 

    class Meta:
        db_table = 'products_stock_history'
        verbose_name = "Stock History"
        verbose_name_plural = "Stock History"
        indexes = [
            models.Index(fields=['-stock','-created_at']),
        ]

    def __str__(self):
        return str(self.stock)




class StockAdjustment(CommonAction):
    stock = models.ForeignKey(Stocks, related_name='stock_adjustments', on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.FloatField(default=0)
    reason = models.CharField(max_length=300, blank=True, null=True)
    accept_branch=models.ForeignKey(Branch,related_name='accept_branchs',on_delete=models.CASCADE,null=True,blank=True)
    given_branch=models.ForeignKey(Branch,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = 'stock_adjustment'
        verbose_name = "Stock Adjustment"
        verbose_name_plural = "Stock Adjustments"
    
    def __str__(self):
        return f"{self.stock.product_variant.product.product_name} - {self.quantity}"

class StockTransfer(CommonAction):
    stock = models.ForeignKey(Stocks, related_name='stock_tarnsfer', on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.FloatField(default=0)
    reason = models.CharField(max_length=300, blank=True, null=True)
    accept_branch=models.ForeignKey(Branch,related_name='accept_branch',on_delete=models.CASCADE,null=True,blank=True)
    given_branch=models.ForeignKey(Branch,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = 'stock_tarnsfer'
        verbose_name = "Stock Transfer"
        verbose_name_plural = "Stock Transfers"
    
    def __str__(self):
        return f"{self.stock.product_variant.product.product_name} - {self.quantity}"




