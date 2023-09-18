from django.conf.urls.static import static, settings
from django.urls import path
from . import views


urlpatterns = [

    path('', views.news, name='news'),
    path('notification', views.notification, name='notification'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


