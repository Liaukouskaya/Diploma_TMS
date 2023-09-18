from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin1234567890/', admin.site.urls),
    path('', include('account.urls')),
    path('news/', include('news.urls')),
    path('search/', include('search.urls')),
    path('groups/', include('groups.urls')),
    path('messages/', include('usermessages.urls')),
    path('useradmin/', include('useradmin.urls')),
    path('api/', include('api.urls')),

]

handler404 = 'socialnet.views.error_404_view'
