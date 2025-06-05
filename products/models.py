from django.db import models
from users.models import CommonAction
from catalog.models import ProductUnit,Brand,Category,SubCategory,ColorVariation,AttributeVariation
import uuid
from django.conf import settings


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

class Product(CommonAction):
    product_name        = models.CharField(max_length=500,null=True,blank=True)
    sku                 = models.CharField(max_length=50,unique=True)
    unit                = models.ForeignKey(ProductUnit,on_delete=models.CASCADE,null=True,blank=True)
    category            = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    sub_category        = models.ForeignKey(SubCategory,on_delete=models.SET_NULL,null=True,blank=True)
    brand               = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True,blank=True)
    images              = models.ImageField(upload_to='products/', null=True, blank=True, default=None)
    file                = models.JSONField(default=list,blank=True)
    weight              = models.FloatField(default=0,help_text='Grams')
    product_type        = models.CharField(max_length=20,choices=PRODUCT_TYPE,default='None',null=True,blank=True)
    country             = models.CharField(max_length=100,help_text='Which countrys product',null=True,blank=True)
    vat_percentage      = models.FloatField(default=0)
    vat_amount          = models.FloatField(default=0)
    description         = models.TextField(null=True,blank=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'products'

        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return str(self.product_name)


class ProductVariantAttribute(CommonAction):
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)
    color_attribute=models.ForeignKey(ColorVariation,on_delete=models.SET_NULL,null=True,blank=True)
    variation_attribute=models.ForeignKey(AttributeVariation,on_delete=models.CASCADE,null=True,blank=True)

    class Meta: 
        db_table = 'productvariantattributes'
        ordering = ['-created_at']
        verbose_name        = 'ProductVariantAttribute'
        verbose_name_plural = 'ProductVariantAttributes'

    def __str__(self):
        product_name = self.product.product_name if self.product else "No Product"
        color = str(self.color_attribute) if self.color_attribute else "No Color"
        variation = str(self.variation_attribute) if self.variation_attribute else "No Variation"

        return f"{product_name} ({color}, {variation})"

class ProductBarcodes(CommonAction):
    PRODUCT_STATUS = (
        ('Select Status','Select Status'),
        ('Sold', "Sold"), 
        ('Purchased', "Purchased"),
        ('Sales Return', "Sales Return"), 
        ('Purchase Return', "Purchase Return"),  
        ('Damage', "Damage"),
        ('Quotation','Quotation')
    )
    
    inv=models.CharField(max_length=500,null=True,blank=True)
    inv_sold=models.CharField(max_length=500,null=True,blank=True)
    inv_quotation=models.CharField(max_length=500,null=True,blank=True)
    inv_return_no=models.CharField(max_length=500,null=True,blank=True)
    product_variant     = models.ForeignKey(ProductVariantAttribute, on_delete=models.CASCADE, null=True, blank=True)
    product_status      = models.CharField(max_length=50, choices=PRODUCT_STATUS, default='Select Status')
    expired_date        = models.DateField(null=True,blank=True)
    barcode             = models.CharField(max_length=1000, unique=True)
    barcode_image       = models.ImageField(upload_to='barcodes/', null=True, blank=True, default=None) 
    sold_at             = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    purchased_at        = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    sales_return_at     = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    purchase_return_at  = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    quotation_at        = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    remarks             = models.TextField(null=True, blank=True)

    class Meta:
        db_table            = 'product_barcodes'
        verbose_name        = "Product Barcode"
        verbose_name_plural = "Product Barcodes"

    
    def __str__(self):
        product_name = self.product_variant.product.product_name if self.product_variant and self.product_variant.product else "No Product"
        return f"Barcode: {self.barcode} - {product_name}"
