from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('redoc/', TemplateView.as_view(template_name='redoc.html'),
         name='redoc'),
    path('redoc/openapi-schema.yml',
         TemplateView.as_view(template_name='openapi-schema.yml'),
         name='openapi'),
]
