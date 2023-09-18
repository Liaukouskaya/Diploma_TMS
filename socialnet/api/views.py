from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from account.models import Profile, Photo, Posts, RePosts
from groups.models import *
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.routers import DefaultRouter


class APIURLSView(generics.RetrieveAPIView):
    serializer_class = APIURLSSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ProfilePageView(generics.ListCreateAPIView):
    serializer_class = ProfileDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise NotFound("Profile not found.")
        return [profile]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ProfileFollowersView(generics.ListAPIView):
    serializer_class = ProfileFollowersSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        followers = user.profile.followers.all()
        return followers


class ProfileFollowingView(generics.ListAPIView):
    serializer_class = ProfileFollowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        return profile.following.all()


class ProfilePhotoView(generics.ListAPIView, generics.RetrieveAPIView):
    serializer_class = ProfilePhotoSerializer

    def get_queryset(self):
        user = self.request.user
        return Photo.objects.filter(author=user.profile)


class ProfilePagePostsListView(generics.ListAPIView):
    serializer_class = ProfilePostsListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Posts.objects.filter(author=user.profile)


class ProfilePostsView(generics.RetrieveAPIView):
    serializer_class = ProfilePostsSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'pk_post'

    def get_queryset(self):
        user = self.request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise NotFound("Profile not found.")
        return Posts.objects.filter(author=profile)

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get(self.lookup_url_kwarg)
        obj = get_object_or_404(queryset, pk=pk)
        return obj


class ProfileRePostsView(generics.RetrieveAPIView):
    serializer_class = ProfileRePostsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = RePosts.objects.all()
    lookup_url_kwarg = 'pk_repost'


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'pk'
    queryset = Profile.objects.all()


class UserFollowersView(generics.ListAPIView):
    serializer_class = UserFollowersSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.profile.followers.all()


class UserFollowingView(generics.ListAPIView):
    serializer_class = UserFollowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.profile.following.exclude(profile=user.profile)


class UserPhotoView(generics.ListAPIView, generics.RetrieveAPIView):
    serializer_class = UserPhotoSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Photo.objects.filter(author=user.profile)


class LoginPageView(generics.GenericAPIView):
    serializer_class = LoginPageSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        return Response({'detail': 'Вы успешно вошли в систему.'}, status=status.HTTP_200_OK)


class LogoutPageView(generics.GenericAPIView):
    serializer_class = LogoutPageSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logout(request)

        return Response({'detail': 'Вы успешно вышли из системы.'}, status=status.HTTP_200_OK)


class RegistrationPageView(generics.GenericAPIView):
    serializer_class = RegistrationPageSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Дополнительная логика обработки регистрации

        return Response({'detail': 'Вы успешно зарегистрировались.'}, status=status.HTTP_201_CREATED)


class MessagesView(generics.ListAPIView):
    serializer_class = MessagesSerializer

    def get_queryset(self):
        user = self.request.user
        return Messages.objects.filter(author=user.profile)


class MessagesFromDialogView(generics.ListAPIView):
    serializer_class = MessagesFromDialogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        # Получить первичный ключ диалога из параметра URL-шаблона
        dialog_id = self.kwargs['dialog_id']

        # Получить диалог или вернуть 404, если диалог не найден
        dialog = get_object_or_404(Dialog, id=dialog_id)

        # Получить все сообщения из указанного диалога
        messages = Messages.objects.filter(dialog=dialog)

        return messages


class DialogListView(generics.ListAPIView):
    serializer_class = DialogListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user.profile
        # Получаем все диалоги, в которых участвует текущий пользователь
        dialogs = Dialog.objects.filter(user_list=user)
        return dialogs


class GroupsView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    lookup_url_kwarg = 'group_id'


class GroupTeamView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupTeamSerializer
    lookup_url_kwarg = 'group_id'


class GroupFollowersView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupFollowersSerializer
    lookup_url_kwarg = 'group_id'


class GroupPostView(generics.RetrieveAPIView):
    queryset = GroupPosts.objects.all()
    serializer_class = GroupPostsSerializer
    lookup_url_kwarg = 'pk_post'


class GroupPhotoView(generics.RetrieveAPIView):
    queryset = GroupPhoto.objects.all()
    serializer_class = GroupPhotoSerializer
    lookup_url_kwarg = 'group_id'


class GroupPhotoShowView(generics.RetrieveAPIView):
    queryset = GroupPhoto.objects.all()
    serializer_class = GroupPhotoSerializer
    lookup_url_kwarg = 'pk_photo'


class ProfileShowPhotoView(generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    serializer_class = ProfileShowPhotoSerializer
    lookup_url_kwarg = 'pk_photo'


class UserPostView(generics.RetrieveAPIView):
    queryset = Posts.objects.all()
    serializer_class = UserPostSerializer
    lookup_url_kwarg = 'pk_post'


class UserRePostView(generics.RetrieveAPIView):
    queryset = RePosts.objects.all()
    serializer_class = UserRePostSerializer
    lookup_url_kwarg = 'pk_repost'


class UserPhotoShowView(generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    serializer_class = UserPhotoShowSerializer
    lookup_url_kwarg = 'pk_photo'


class NewsView(generics.ListAPIView):
    serializer_class = GroupPostsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        following_users = user.profile.following.all()
        return GroupPosts.objects.filter(author__user__in=following_users)
