from django.db import models
from users.models import CommonAction
from branch.models import Branch
from users.models import Users

class BarcodeSetting(CommonAction):
    barcode_enable=models.BooleanField(default=False)
    barcode_logo=models.JSONField(default=list,blank=True,null=True)
    assign_branch = models.ForeignKey(Branch,on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return str(self.barcode_enable)

class InvoiceSetting(CommonAction):
    prefix=models.CharField(max_length=100,null=True,blank=True)
    invoice_logo=models.JSONField(default=list,blank=True,null=True)
    assign_branch = models.ForeignKey( Branch,on_delete=models.SET_NULL, null=True, blank=True)
    is_active=models.BooleanField(default=False)
    invoice_email= models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.prefix)


class BannerSetting(CommonAction):
    branch=models.ForeignKey(Branch,on_delete=models.CASCADE,null=True,blank=True)
    banner_image=models.JSONField(default=list,blank=True)

    def __str__(self):
        return str(self.branch.branch_name)



class GeneralSetting(CommonAction):
    software_name=models.CharField(max_length=200,null=True,blank=True)
    company_logo=models.JSONField(default=list,blank=True,null=True) 
    company_address=models.TextField(null=True,blank=True)
    company_phone=models.CharField(max_length=15,null=True,blank=True)
    favicon_icon=models.JSONField(default=list,blank=True,null=True)
    company_name=models.CharField(max_length=250,null=True,blank=True)
    company_short_name=models.CharField(max_length=100,null=True,blank=True)
    admin_email=models.CharField(max_length=500,null=True,blank=True)
    currency=models.CharField(max_length=100,null=True,blank=True)


    email_backend = models.CharField(max_length=500,default='django.core.mail.backends.smtp.EmailBackend')
    email_host = models.CharField(max_length=500,null=True,blank=True)
    email_port = models.IntegerField(null=True,blank=True)
    email_use_tls = models.BooleanField(default=False)
    email_host_user = models.CharField(max_length=500,null=True,blank=True)
    email_host_password = models.CharField(max_length=500,null=True,blank=True)
    email_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


