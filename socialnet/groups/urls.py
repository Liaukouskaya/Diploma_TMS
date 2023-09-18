from django.conf.urls.static import static, settings
from django.urls import path
from . import views


urlpatterns = [

    path('', views.groups, name='groups'),
    path('group-<int:group_id>', views.group_view, name='group_view'),

    path('group-<int:group_id>/followers', views.group_followers, name='group_followers'),
    path('group-<int:group_id>/team', views.group_team, name='group_team'),

    path('group-<int:group_id>/post-<int:pk_post>', views.groups_post, name='groups_post'),
    path('group-<int:group_id>/photo', views.groups_photo, name='groups_photo'),
    path('group-<int:group_id>/photo/show-<int:pk_photo>', views.groups_photo_show, name='groups_photo_show'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


