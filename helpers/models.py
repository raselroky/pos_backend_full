from django.db import models
from django.utils.translation import gettext_lazy as _


from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_%(class)ss', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_%(class)ss', null=True, blank=True)

    class Meta:
        abstract = True
    #is_active = models.BooleanField(default=True)

    # class Meta:
    #     abstract = True
    #     app_label = 'base'
    
# class CommonAction(models.Model):
#     created_by = models.ForeignKey("Users", related_name="%(app_label)s_%(class)s_created_by", related_query_name="%(app_label)s_%(class)s_created_by", on_delete=models.SET_NULL, null=True, blank=True, default=None)
#     updated_by = models.ForeignKey("Users", related_name="%(app_label)s_%(class)s_updated_by", related_query_name="%(app_label)s_%(class)s_updated_by", on_delete=models.SET_NULL, null=True, blank=True, default=None)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

#     class Meta:
#         abstract = True

class CustomQuerySetManager(models.QuerySet):
    def filter_by_query(self,query_dict):
        return self.filter(**query_dict)