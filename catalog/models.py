from django.db import models
from users.models import CommonAction



class ProductUnit(CommonAction):
    unit_name = models.CharField(max_length=100,unique=True,null=True,blank=True)
    unit_short_name = models.CharField(max_length=20,unique=True,null=True,blank=True)

    class Meta: 
        db_table = 'productunits'
        ordering = ['-created_at']
        verbose_name        = 'ProductUnit'
        verbose_name_plural = 'ProductUnits'
        
    def __str__(self):
        return str(self.unit_name)


class Category(CommonAction):
    category_name=models.CharField(max_length=100,null=True,blank=True)
    category_code=models.CharField(max_length=20,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    image       = models.ImageField(upload_to='categories/', null=True, blank=True, default=None) 
    vat_amounts = models.FloatField(default=0)
    vat_percentage = models.FloatField(default=0)

    class Meta: 
        db_table = 'categorys'
        ordering = ['-created_at']
        verbose_name        = 'Category'
        verbose_name_plural = 'Categorys'

    def __str__(self):
        return str(self.category_name)


class SubCategory(CommonAction):
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    subcategory_name=models.CharField(max_length=100,null=True,blank=True)
    subcategory_code=models.CharField(max_length=20,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    image       = models.ImageField(upload_to='sub_categories/', null=True, blank=True, default=None) 


    class Meta: 
        db_table = 'subcategorys'
        ordering = ['-created_at']
        verbose_name        = 'SubCategory'
        verbose_name_plural = 'SubCategorys'
    
    def __str__(self):
        return str(self.subcategory_name)
    
class Brand(CommonAction):
    brand_name=models.CharField(max_length=100,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    image       = models.ImageField(upload_to='brands/', null=True, blank=True, default=None) 

    class Meta: 
        db_table = 'brands'
        ordering = ['-created_at']
        verbose_name        = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return str(self.brand_name)


class ColorVariation(CommonAction):
    color_name=models.CharField(max_length=1000,null=True,blank=True)
    description=models.CharField(max_length=1000,null=True,blank=True)


    class Meta: 
        db_table = 'colorvariations'
        ordering = ['-created_at']
        verbose_name        = 'ColorVariation'
        verbose_name_plural = 'ColorVariations'

    def __str__(self):
        return str(self.color_name)
    
class AttributeVariation(CommonAction):
    name=models.CharField(max_length=1000,null=True,blank=True)
    values=models.CharField(max_length=1000,null=True,blank=True)
    class Meta: 
        db_table = 'attributevariation'
        ordering = ['-created_at']
        verbose_name        = 'AttributeVariation'
        verbose_name_plural = 'AttributeVariations'

    def __str__(self):
        return str(self.name)+' '+str(self.values)