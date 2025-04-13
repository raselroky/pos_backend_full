from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid
from users.managers import CustomUserManager, DeletedUserManager
from django.contrib.auth.models import Permission

GENDER = (
            ('Please Select','Please Select'),
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Others', 'Others'),
        )

class Users(AbstractUser):
         

    id              = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    photo           = models.ImageField(upload_to="profile_pic/", null=True, blank=True)
    email           = models.EmailField(unique=True, max_length=170)
    gender          = models.CharField(choices=GENDER, default='Please Select', max_length=100)
    phone           = models.CharField(max_length=15, null=True, blank=True,default="")
    age             = models.CharField(max_length=3, null=True, blank=True,default="")
    modified        = models.DateTimeField(auto_now=True)
    is_superadmin   = models.BooleanField(default=False, null=True, blank=True)
    email_verified  = models.BooleanField(default=False, null=True, blank=True)
    role            = models.ManyToManyField("Roles", blank=True)

    branch          = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True,blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None 

    objects = CustomUserManager()
    deleted_objects = DeletedUserManager()
    
    class Meta: 
        db_table = 'users'
        ordering = ['-id']
        verbose_name        = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f' {self.email}'
      
class CommonAction(models.Model):
    created_by = models.ForeignKey("users.Users", related_name="%(app_label)s_%(class)s_created_by", related_query_name="%(app_label)s_%(class)s_created_by", on_delete=models.SET_NULL, null=True, blank=True, default=None)
    updated_by = models.ForeignKey("users.Users", related_name="%(app_label)s_%(class)s_updated_by", related_query_name="%(app_label)s_%(class)s_updated_by", on_delete=models.SET_NULL, null=True, blank=True, default=None)
    branch = models.ForeignKey("branch.Branch", related_name="%(app_label)s_%(class)s_branch", related_query_name="%(app_label)s_%(class)s_branch", on_delete=models.SET_NULL, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

class Roles(CommonAction):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    status   = models.BooleanField(default=True)
    
    class Meta: 
        db_table = 'roles'
        ordering = ['-created_at']
        verbose_name        = 'Role'
        verbose_name_plural = 'Roles'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

class Permissions(CommonAction):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    module = models.CharField(max_length=100, blank=True, null=True)
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    status       = models.BooleanField(default=True)
    
    class Meta: 
        db_table = 'permissions'
        ordering = ['-created_at']
        verbose_name        = 'Permission'
        verbose_name_plural = 'Permissions'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

class RolePermissions(CommonAction):
    role = models.ForeignKey("Roles", on_delete=models.CASCADE, blank=True, related_name="rolepermissions")
    permission = models.ManyToManyField(Permission,blank=True)
    
    class Meta: 
        db_table = 'rolepermissions'
        ordering = ['-created_at']
        verbose_name        = 'RolePermission'
        verbose_name_plural = 'RolePermissions'


    def __str__(self):
        return str(self.role.title)

class UserPermissions(CommonAction):
    user = models.ForeignKey("Users", on_delete=models.CASCADE, blank=True, related_name="userpermissions")
    permission = models.ManyToManyField(Permission, blank=True)
    
    class Meta: 
        db_table = 'userpermissions'
        ordering = ['-created_at']
        verbose_name        = 'UserPermission'
        verbose_name_plural = 'UserPermissions'


    def __str__(self):
        return str(self.user.email) + " - " + str(self.permission.title)
