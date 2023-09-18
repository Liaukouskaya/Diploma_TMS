from django.conf.urls.static import static, settings
from django.urls import path
from . import views


urlpatterns = [

    path('', views.settings_page, name='settings_page_admin'),

    path('search', views.admin_search, name='admin_search'),
    path('result-<str:text_search>', views.admin_search_result, name='admin_search_result'),
    path('result/people-<str:text_search>', views.admin_search_result_people, name='admin_search_result_people'),
    path('result/group-<str:text_search>', views.admin_search_result_group, name='admin_search_result_group'),

    path('dialog_all', views.dialog_all, name='dialog_all'),
    path('dialog-<int:dialog_id>', views.admin_dialog, name='admin_dialog'),

    path('user-<int:pk>', views.admin_another_user_page, name='admin_another_user_page'),
    path('user-<int:pk>/post-<int:pk_post>', views.admin_another_user_page_post, name='admin_another_user_page_post'),
    path('user-<int:pk>/repost-<int:pk_repost>', views.admin_another_user_page_repost, name='admin_another_user_page_repost'),
    path('user-<int:pk>/grop-repost-<int:pk_repost>', views.admin_another_user_page_group_repost, name='admin_another_user_page_group_repost'),
    path('user-<int:pk>/followers', views.admin_another_user_page_followers, name='admin_another_user_page_followers'),
    path('user-<int:pk>/following', views.admin_another_user_page_following, name='admin_another_user_page_following'),
    path('user-<int:pk>/photo', views.admin_another_user_page_photo, name='admin_another_user_page_photo'),
    path('user-<int:pk>/photo/show-<int:pk_photo>', views.admin_another_user_page_photo_show, name='admin_another_user_page_photo_show'),

    path('group-<int:group_id>', views.admin_group_view, name='admin_group_view'),
    path('group-<int:group_id>/followers', views.admin_group_followers, name='admin_group_followers'),
    path('group-<int:group_id>/post-<int:pk_post>', views.admin_groups_post, name='admin_groups_post'),
    path('group-<int:group_id>/photo', views.admin_groups_photo, name='admin_groups_photo'),
    path('group-<int:group_id>/photo/show-<int:pk_photo>', views.admin_groups_photo_show, name='admin_groups_photo_show'),

    path('create_notification', views.create_notification, name='create_notification'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




