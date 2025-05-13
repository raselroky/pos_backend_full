from django.db import models
from contacts.models import Contact,pay_term_types
from users.models import CommonAction
from products.models import Product,ProductVariantAttribute



PURCHASE_STATUS=(
    ('Please Select','Please Select'),
    ('Received','Received'),
    ('Pending','Pending'),
    ('Ordered','Ordered')
)

PAYMENT_METHOD=(
    ('Select Payment Method','Select Payment Method'),
    ('Cash','Cash'),
    ('Check','Check'),
    ('Bank-Card','Bank-Card'),
    ('Bkash','Bkash'),
    ('Nagad','Nagad'),
    ('Upay','Upay')
)
DISCOUNT_TYPE=(
    ('Select Type','Select Type'),
    ('Percentage','Percentage'),
    ('Flat','Flat')
)


class Purchase(CommonAction):
    supplier            = models.ForeignKey(Contact,related_name="purchase",  on_delete=models.SET_NULL, blank=True, null=True)
    total_amount        = models.FloatField(default=0)
    discount_amount     = models.FloatField(default=0) 
    discount_percent    = models.FloatField(default=0) 
    discount_type       = models.CharField(max_length=100,choices=DISCOUNT_TYPE,default='Select Type')
    payment_method      = models.CharField(max_length=100,choices=PAYMENT_METHOD,default='Select Payment Method')
    vat_amount          = models.FloatField(default=0)
    sub_total           = models.FloatField(default=0) 
    grand_total         = models.FloatField(default=0) 
    paid_amount         = models.FloatField(default=0)
    due_amount          = models.FloatField(default=0)
    invoice_no          = models.CharField(max_length=20, unique=True)
    reference           = models.CharField(max_length=100, null=True, blank=True)
    remark              = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'purchase'
        ordering = ['-created_at']
        verbose_name = "Purchase"
        verbose_name_plural = "Purchase" 
        indexes = [
            models.Index(fields=['-supplier','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.invoice_no)


class PurchaseHistory(CommonAction):
    product_variant = models.ForeignKey(ProductVariantAttribute, related_name="purchase_history", on_delete=models.SET_NULL, blank=True, null=True)
    purchase        = models.ForeignKey(Purchase, related_name="purchase_history", on_delete=models.SET_NULL, blank=True, null=True)
    purchase_quantity= models.FloatField(default=0) 
    demaged_quantity= models.FloatField(default=0)
    good_quantity   = models.FloatField(default=0)
    unit_price      = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0) 
    discount_percent= models.FloatField(default=0) 
    discount_type   = models.CharField(max_length=100,choices=DISCOUNT_TYPE,default='Select Type')
    total_amount_iv = models.FloatField(default=0)
    total_amount_wv = models.FloatField(default=0)
    vat_amounts     = models.FloatField(default=0)
    warranty        = models.PositiveIntegerField(default=0)
    remark          = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'purchase_history'
        ordering = ['-created_at']
        verbose_name = "Purchase"
        verbose_name_plural = "Purchase Histories" 
        indexes = [
            models.Index(fields=['-product_variant','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.purchase)+" -> "+str(self.product_variant)

class PurchaseReturn(CommonAction):
    purchase            = models.ForeignKey(Purchase, related_name='purchase_returns', on_delete=models.CASCADE)
    return_no           = models.CharField(max_length=30, unique=True)
    return_date         = models.DateField(auto_now_add=False,blank=True,null=True)
    total_return_qty    = models.FloatField(default=0)
    total_refund_amount = models.FloatField(default=0)  
    remark              = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'purchase_return'
        ordering = ['-created_at']
        verbose_name = "Purchase Return"
        verbose_name_plural = "Purchase Returns"
        indexes = [
            models.Index(fields=['-purchase','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.purchase.invoice_no)
     
class PurchaseReturnHistory(CommonAction):
    purchase_return = models.ForeignKey(PurchaseReturn, related_name="purchase_return_history", on_delete=models.CASCADE)
    purchase_history= models.ForeignKey(PurchaseHistory, related_name='purchase_return_details', on_delete=models.CASCADE)
    return_qty      = models.FloatField(default=0)  # Quantity returned 
    refund_amount   = models.FloatField(default=0)  # Refund amount for the returned product
    remark          = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'purchase_return_history'
        ordering = ['-created_at']
        verbose_name = "Purchase Return History"
        verbose_name_plural = "Purchase Return Histories"
        indexes = [
            models.Index(fields=['-purchase_return','purchase_history','-created_at']),
        ]

    def __str__(self):
        return '%s' % str(self.purchase_return)


class AdditionalExpense(CommonAction):
    expense_name=models.CharField(max_length=1000,null=True,blank=True)
    amount=models.FloatField(default=0)
    reason=models.CharField(max_length=1000,null=True,blank=True,help_text='purchase, loan, advance, agreemnt, etc')



    class Meta: 
        db_table = 'additionalexpenses'
        ordering = ['-created_at']
        verbose_name        = 'AdditionalExpense'
        verbose_name_plural = 'AdditionalExpenses'


    def __str__(self):
        return str(self.expense_name)

