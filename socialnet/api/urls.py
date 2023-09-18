from django.conf.urls.static import static, settings
from django.urls import path, include
from .views import *
from rest_framework import routers

router = DefaultRouter()
router.register(r'profile_page/posts', ProfilePagePostsListView, basename='posts')

app_name = 'api'

urlpatterns = [

    path('api_urls', APIURLSView.as_view(), name='api_urls'),
    path('', ProfilePageView.as_view(), name='profile_page'),
    path('profile_page/posts/', ProfilePagePostsListView.as_view(), name='profile_page_posts'),
    path('profile_page/post-<int:pk_post>', ProfilePostsView.as_view(), name='profile_page_post'),
    path('profile_page/repost-<int:pk_repost>', ProfileRePostsView.as_view(), name='profile_page_repost'),

    path('profile_page/followers', ProfileFollowersView.as_view(), name='profile_page_followers'),
    path('profile_page/following', ProfileFollowingView.as_view(), name='profile_page_following'),
    path('profile_page/photo', ProfilePhotoView.as_view(), name='profile_page_photo'),
    path('profile_page/photo/show-<int:pk_photo>', ProfileShowPhotoView.as_view(), name='profile_page_photo_show'),

    path('user-<int:pk>', UserView.as_view(), name='another_user_page'),
    path('user-<int:pk>/post-<int:pk_post>', UserPostView.as_view(), name='user_post'),
    path('user-<int:pk>/repost-<int:pk_repost>', UserRePostView.as_view()),

    path('user-<int:pk>/followers', UserFollowersView.as_view(), name='user_followers'),
    path('user-<int:pk>/following', UserFollowingView.as_view(), name='user_following'),
    path('user-<int:pk>/photo', UserPhotoView.as_view(), name='user_photo'),
    path('user-<int:pk>/photo/show-<int:pk_photo>', UserPhotoShowView.as_view(), name='user_photo_show'),

    path('login_page', LoginPageView.as_view(), name='login_page'),

    path('logout_page', LogoutPageView.as_view(), name='logout_page'),
    path('registration_page', RegistrationPageView.as_view(), name='registration_page'),

    path('messages/', MessagesView.as_view(), name='messages'),
    path('messages/dialogs/', DialogListView.as_view(), name='dialog_list'),
    path('messages/dialog-<int:dialog_id>/', MessagesFromDialogView.as_view(), name='dialog'),

    path('news/', NewsView.as_view(), name='news'),

    path('groups/', GroupsView.as_view(), name='groups'),
    path('groups/group-<int:group_id>', GroupView.as_view(), name='group'),

    path('group-<int:group_id>/followers', GroupFollowersView.as_view(), name='group_followers'),
    path('group-<int:group_id>/team', GroupTeamView.as_view(), name='group_team'),

    path('group-<int:group_id>/post-<int:pk_post>', GroupPostView.as_view(), name='group_post'),
    path('group-<int:group_id>/photo', GroupPhotoView.as_view(), name='group_photo'),
    path('group-<int:group_id>/photo/show-<int:pk_photo>', GroupPhotoShowView.as_view(), name='group_photo_show'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
