from django.conf.urls.static import static, settings
from django.urls import path
from . import views


urlpatterns = [

    path('', views.index, name='index'),

    path('profile_page', views.profile_page, name='profile_page'),
    path('profile_page/post-<int:pk_post>', views.profile_page_post, name='profile_page_post'),
    path('profile_page/repost-<int:pk_repost>', views.profile_page_repost, name='profile_page_repost'),
    path('profile_page/grop-repost-<int:pk_repost>', views.profile_page_group_repost, name='profile_page_group_repost'),
    path('profile_page/post-<int:pk_post>/repost', views.profile_page_post_repost, name='profile_page_post_repost'),
    path('profile_page/post-<int:pk_group_post>/group_repost', views.profile_page_post_group_repost, name='profile_page_post_group_repost'),
    path('profile_page/followers', views.profile_page_followers, name='profile_page_followers'),
    path('profile_page/following', views.profile_page_following, name='profile_page_following'),
    path('profile_page/photo', views.profile_page_photo, name='profile_page_photo'),
    path('profile_page/photo/show-<int:pk_photo>', views.profile_page_photo_show, name='profile_page_photo_show'),

    path('block_page', views.block_page, name='block_page'),

    path('profile_page/report/post-<int:pk_post>', views.profile_page_report_post,name='profile_page_report_post'),
    path('profile_page/report/repost-<int:pk_post>', views.profile_page_report_repost,name='profile_page_report_repost'),
    path('profile_page/report/group_post-<int:pk_post>', views.profile_page_report_group_post, name='profile_page_report_group_post'),
    path('profile_page/report/group_repost-<int:pk_post>', views.profile_page_report_group_repost, name='profile_page_report_group_repost'),
    path('profile_page/report/photo-<int:pk_post>', views.profile_page_report_photo, name='profile_page_report_photo'),

    path('user-<int:pk>', views.another_user_page, name='another_user_page'),
    path('user-<int:pk>/post-<int:pk_post>', views.another_user_page_post, name='another_user_page_post'),
    path('user-<int:pk>/repost-<int:pk_repost>', views.another_user_page_repost, name='another_user_page_repost'),
    path('user-<int:pk>/grop-repost-<int:pk_repost>', views.another_user_page_group_repost, name='another_user_page_group_repost'),
    path('user-<int:pk>/followers', views.another_user_page_followers, name='another_user_page_followers'),
    path('user-<int:pk>/following', views.another_user_page_following, name='another_user_page_following'),
    path('user-<int:pk>/photo', views.another_user_page_photo, name='another_user_page_photo'),
    path('user-<int:pk>/photo/show-<int:pk_photo>', views.another_user_page_photo_show, name='another_user_page_photo_show'),

    path('settings_page/edit_profile', views.settings_page_edit_profile, name='settings_page_edit_profile'),

    path('login_page', views.login_page, name='login_page'),
    path('logout_page', views.logout_page, name='logout_page'),
    path('registration_page', views.registration_page, name='registration_page'),
    path('security_code', views.security_code, name='security_code'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
