from django.db import models
from contacts.models import Contact,pay_term_types
from users.models import CommonAction
from products.models import Product



PURCHASE_STATUS=(
    ('Please Select','Please Select'),
    ('Received','Received'),
    ('Pending','Pending'),
    ('Ordered','Ordered')
)
PAYMENT_METHOD=(
    ('None','None'),
    ('Cash','Cash'),
    ('Check','Check'),
    ('Bank-Card','Bank-Card'),
    ('Bkash','Bkash'),
    ('Nagad','Nagad'),
    ('Upay','Upay')
)
DISCOUNT_TYPE=(
    ('Please Select','Please Select'),
    ('Percentage','Percentage'),
    ('Fixed','Fixed')
)


class Sale(CommonAction):
    customer            = models.ForeignKey(Contact,related_name="sale",  on_delete=models.SET_NULL, blank=True, null=True)
    total_amount        = models.FloatField(default=0)
    discount_amount     = models.FloatField(default=0) 
    discount_percent    = models.FloatField(default=0) 
    vat_amount          = models.FloatField(default=0) #it will store all products vat sum amount from PurchaseHistory
    sub_total           = models.FloatField(default=0) 
    paid_amount         = models.FloatField(default=0)
    due_amount          = models.FloatField(default=0)
    invoice_no          = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'sale'
        ordering = ['-created_at']
        verbose_name = "Sale"
        verbose_name_plural = "Sale" 
        indexes = [
            models.Index(fields=['-customer','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.invoice_no)


class SaleHistory(CommonAction):
    sale            = models.ForeignKey(Sale, related_name="sale_history", on_delete=models.SET_NULL, blank=True, null=True)
    product_variant = models.ForeignKey("stock.Stocks", related_name="sale_history", on_delete=models.SET_NULL, blank=True, null=True)
    quantity        = models.FloatField(default=0)
    unit_price      = models.FloatField(default=0)
    selling_price   =models.FloatField(default=0)
    discount_amount = models.FloatField(default=0) 
    discount_percent= models.FloatField(default=0) 
    warranty        = models.PositiveIntegerField(default=0)
    remark          = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'sale_history'
        ordering = ['-created_at']
        verbose_name = "Sale_History"
        verbose_name_plural = "sale Historys" 
        indexes = [
            models.Index(fields=['-product_variant','sale','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.sale)+" -> "+str(self.product_variant)

class SaleReturn(CommonAction):
    sale                = models.ForeignKey(Sale, related_name='sale_returns', on_delete=models.CASCADE)
    return_no           = models.CharField(max_length=30, unique=True)
    return_date         = models.DateField(auto_now_add=False,blank=True,null=True)
    total_return_qty    = models.FloatField(default=0)  # Total quantity returned 
    total_refund_amount = models.FloatField(default=0)  # Amount refunded to the supplier
    remark              = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'sale_return'
        ordering = ['-created_at']
        verbose_name = "Sale Return"
        verbose_name_plural = "Sale Returns"
        indexes = [
            models.Index(fields=['-sale','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.return_no)
     
class SaleReturnHistory(CommonAction):
    sale_return     = models.ForeignKey(SaleReturn, related_name='sale_return_details', on_delete=models.CASCADE)
    sale_history    = models.ForeignKey(SaleHistory, related_name='sale_return_details', on_delete=models.CASCADE)
    return_qty      = models.FloatField(default=0)  # Quantity returned 
    refund_amount   = models.FloatField(default=0)  # Refund amount for the returned product
    remark          = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'sale_return_history'
        ordering = ['-created_at']
        verbose_name = "Sale Return History"
        verbose_name_plural = "Sale Return Histories"
        indexes = [
            models.Index(fields=['-sale_return','sale_history','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.sale_return)

