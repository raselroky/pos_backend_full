from django.db import models
from users.models import CommonAction,Users

contactor_types = (
    ('Please Select', 'Please Select'),
    ('Suppliers', 'Suppliers'),
    ('Customers', 'Customers'),
    ('Both', 'Both')
)
business_types = (
    ('Please Select', 'Please Select'),
    ('Individual/Personal', 'Individual/Personal'),
    ('Business/Group', 'Business/Group')
    
)
pay_term_types = (
    ('Please Select', 'Please Select'),
    ('Daily', 'Daily'),
    ('Weekly', 'Weekly'),
    ('Monthly','Monthly'),
    ('Yearly','Yearly')
    
)
class Contact(CommonAction):

    business_name=models.CharField(max_length=1000,null=True,blank=True)
    owner_name=models.CharField(max_length=1000,null=True,blank=True)
    contactor_type=models.CharField(max_length=1000,choices=contactor_types,default='Please Select')
    business_type=models.CharField(max_length=1000,choices=business_types,default='Please Select')

    conact_id=models.CharField(max_length=5000,null=True,blank=True)
    mobile=models.CharField(max_length=1000,null=True,blank=True)
    mobile2=models.CharField(max_length=1000,null=True,blank=True)
    email=models.CharField(max_length=1000,null=True,blank=True)

    refer=models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True)
    file_image= models.ImageField(upload_to="profile_pic/", null=True, blank=True)
    file      = models.JSONField(default=list,blank=True)

    tax_number=models.TextField(null=True,blank=True)
    opening_balance=models.FloatField(default=0)
    pay_term_amount=models.FloatField(default=0)
    pay_term_types=models.CharField(max_length=1000,choices=pay_term_types,default='Please Select')

    address=models.TextField(null=True,blank=True,help_text='area, city, state or zone, country, zip code')
    shipping_address=models.TextField(null=True,blank=True)

    sales_commission=models.TextField(null=True,blank=True)

    class Meta: 
        db_table = 'contacts'
        ordering = ['-created_at']
        verbose_name        = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        if self.business_name and self.email:
            return f'{self.business_name} {self.email}'
        elif(self.business_name and not self.email):
            return f'{self.business_name}'
        elif(not self.business_name and self.email):
            return f'{self.email}'
        elif(not self.business_name and not self.email):
            return f'{self.owner_name}'