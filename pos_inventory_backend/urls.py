
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('branch/', include('branch.urls')),
    path('contacts/', include('contacts.urls')),
    path('catalogs/', include('catalog.urls')),
    path('products/', include('products.urls')),
    path('purchase/', include('purchase.urls')),
    path('sell/',include('sell.urls')),
    path('stock/',include('stock.urls')),
    path('notifications/',include('notifications.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
