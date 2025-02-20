from django.db import models
from users.models import CommonAction

class Country(CommonAction):
    country_name = models.CharField(max_length=500,null=True,blank=True)
    country_code = models.CharField(max_length=500,null=True,blank=True)
    country_short_name = models.CharField(max_length=500,null=True,blank=True)

    class Meta: 
        db_table = 'countrys'
        ordering = ['-created_at']
        verbose_name        = 'Country'
        verbose_name_plural = 'Countrys'

    def __str__(self):
        return str(self.country_name)
    

class Branch(models.Model):
    created_by = models.ForeignKey("users.Users", related_name="branch_created_by", on_delete=models.SET_NULL, null=True, blank=True, default=None)
    updated_by = models.ForeignKey("users.Users", related_name="branch_updated_by", on_delete=models.SET_NULL, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    country = models.ForeignKey(Country,on_delete=models.SET_NULL, related_name="branch_country",null=True,blank=True)
    branch_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(max_length=100, null=True,blank=True)
    phone = models.CharField(max_length=20,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    company_name = models.CharField(max_length=100, null=True,blank=True)
    

    class Meta: 
        db_table = 'branchs'
        ordering = ['-created_at']
        verbose_name        = 'Branch'
        verbose_name_plural = 'Branchs'

    def __str__(self):
        return str(self.branch_name)

    



 