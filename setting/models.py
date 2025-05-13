from django.db import models
from users.models import CommonAction
from branch.models import Branch
from users.models import Users

class BarcodeSetting(CommonAction):
    barcode_enable=models.BooleanField(default=False)
    barcode_logo=models.ImageField(upload_to='barcode_logo/', null=True, blank=True, default=None) 
    assign_branch = models.ForeignKey(Branch,on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return str(self.barcode_enable)

class InvoiceSetting(CommonAction):
    prefix=models.CharField(max_length=100,null=True,blank=True)
    invoice_logo=models.ImageField(upload_to='invoice_logo/', null=True, blank=True, default=None)
    assign_branch = models.ForeignKey( Branch,on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.prefix)


class BannerSetting(CommonAction):
    branch=models.ForeignKey(Branch,on_delete=models.CASCADE,null=True,blank=True)
    banner_image=models.ImageField(upload_to='banner_image/', null=True, blank=True, default=None) 

    def __str__(self):
        return str(self.branch.branch_name)


class EmailSetting(CommonAction):
    staff=models.ManyToManyField(Users,blank=True)
    messsage=models.TextField(null=True,blank=True)

    def __str__(self):
        return str(self.staff.email)


