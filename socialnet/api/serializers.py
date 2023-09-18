from rest_framework import serializers
from account.models import Profile, Photo, PhotoComment, Posts, PostsComment, RePosts, RePostsComment, User
from usermessages.models import Messages, MessagePhoto, Dialog
from groups.models import *
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from rest_framework import status


class APIURLSSerializer(serializers.Serializer):
    user_page = serializers.HyperlinkedIdentityField(view_name='api:another_user_page')
    followers = serializers.HyperlinkedIdentityField(view_name='api:user_followers')
    following = serializers.HyperlinkedIdentityField(view_name='api:user_following')
    photo = serializers.HyperlinkedIdentityField(view_name='api:user_photo')

    def get_messages(self, obj):
        request = self.context.get('request')
        if obj:
            return request.build_absolute_uri(reverse('api:messages'))
        return None

    def get_dialog(self, obj):
        request = self.context.get('request')
        if obj:
            return request.build_absolute_uri(reverse('api:dialog', args=[obj.pk]))
        return None


class ProfileDetailSerializer(serializers.ModelSerializer):
    followers = serializers.HyperlinkedIdentityField(view_name='api:user_followers')
    following = serializers.HyperlinkedIdentityField(view_name='api:user_following')
    photo = serializers.HyperlinkedIdentityField(view_name='api:user_photo')
    messages = serializers.SerializerMethodField()
    dialog_list = serializers.SerializerMethodField()
    profile_page_posts = serializers.SerializerMethodField()
    login_page = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    news = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
        "profile_id", 'followers', "following", "photo", "first_name", "last_name", "age", "user_status", "user_admin",
        "avatar", "user", 'messages', 'dialog_list', 'profile_page_posts', 'login_page', 'groups', 'news')

    def get_messages(self, obj):
        # Возвращаем ссылку на сообщения пользователя
        return self.context.get('request').build_absolute_uri(reverse('api:messages'))

    def get_profile_page_posts(self, obj):
        # Возвращаем ссылку на сообщения пользователя
        return self.context.get('request').build_absolute_uri(reverse('api:profile_page_posts'))

    def get_dialog_list(self, obj):
        # Возвращаем ссылку на список диалогов пользователя
        return self.context.get('request').build_absolute_uri(reverse('api:dialog_list'))

    def get_groups(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:groups'))

    def get_news(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:news'))

    def get_login_page(self, obj):
        request = self.context.get('request')
        # Проверяем, залогинен ли пользователь
        if not request.user.is_authenticated:
            return request.build_absolute_uri(reverse('api:login_page'))
        return None


class ProfileFollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'followers')


class ProfileFollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'following')


class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('author', 'photo')


class ProfilePostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ('id', 'author', 'date', 'content', 'like_post', 'photo_post')


class ProfilePostsListSerializer(serializers.ModelSerializer):
    profile_page_post = serializers.SerializerMethodField()
    profile_page_repost = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = (
        'id', 'author', 'date', 'content', 'like_post', 'photo_post', 'profile_page_post', 'profile_page_repost')

    def get_profile_page_post(self, obj):
        post_id = obj.id
        # Возвращаем ссылку на сообщения пользователя
        return self.context.get('request').build_absolute_uri(reverse('api:profile_page_post', args=[post_id]))

    def get_profile_page_repost(self, obj):
        repost_id = obj.id
        # Возвращаем ссылку на сообщения пользователя
        return self.context.get('request').build_absolute_uri(reverse('api:profile_page_repost', args=[repost_id]))


class ProfileRePostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RePosts
        fields = ('author', 'date', 'content')


class UserSerializer(serializers.ModelSerializer):
    followers = serializers.HyperlinkedIdentityField(view_name='api:user_followers')
    following = serializers.HyperlinkedIdentityField(view_name='api:user_following')
    photo = serializers.HyperlinkedIdentityField(view_name='api:user_photo')

    class Meta:
        model = Profile
        fields = '__all__'


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ()


class UserRePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ()


class UserFollowersSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar')
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'user')

    def get_user(self, obj):
        request = self.context.get('request')
        if obj:
            return request.build_absolute_uri(reverse('api:another_user_page', args=[obj.profile.pk]))
        return None


class UserFollowingSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar')
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'user')

    def get_user(self, obj):
        request = self.context.get('request')
        if obj.profile:
            return request.build_absolute_uri(reverse('api:another_user_page', args=[obj.profile.profile_id]))
        return None


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('photo',)


class UserPostSerializer(serializers.ModelSerializer):
    profile_page_post = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ('author', 'date', 'content', 'like_post', 'photo_post')


class LoginPageSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('Учетная запись пользователя неактивна.')
            else:
                raise serializers.ValidationError('Неверные учетные данные.')
        else:
            raise serializers.ValidationError('Введите имя пользователя и пароль.')

        return data


class LogoutPageSerializer(serializers.Serializer):
    pass


class RegistrationPageSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirmation = serializers.CharField()

    def validate(self, data):
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')

        if password and password_confirmation:
            if password != password_confirmation:
                raise serializers.ValidationError('Пароли не совпадают.')
        else:
            raise serializers.ValidationError('Введите пароль и подтверждение пароля.')

        return data


class MessagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagePhoto
        fields = ('author', 'photo')


class MessagesSerializer(serializers.ModelSerializer):
    # photo_post = MessagePhotoSerializer(many=True)

    class Meta:
        model = Messages
        fields = ('dialog', 'author', 'content', 'photo_post', 'date', 'read')


class MessagesFromDialogSerializer(serializers.ModelSerializer):
    photo_post = MessagePhotoSerializer(many=True)

    class Meta:
        model = Messages
        fields = ('dialog', 'author', 'content', 'photo_post', 'date', 'read')


class DialogListSerializer(serializers.ModelSerializer):
    dialog = serializers.SerializerMethodField()

    class Meta:
        model = Dialog
        fields = ('creator', 'user_list', 'last_message', 'last_message_text', 'last_message_time', 'dialog')

    def get_dialog(self, obj):
        dialog_id = obj.id
        # Возвращаем ссылку на сообщения пользователя
        return self.context.get('request').build_absolute_uri(reverse('api:dialog', args=[dialog_id]))


class GroupSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    group_followers = serializers.SerializerMethodField()
    group_team = serializers.SerializerMethodField()
    group_post = serializers.SerializerMethodField()
    group_photo = serializers.SerializerMethodField()
    group_photo_show = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
        'profile_id', 'user', 'first_name', 'team', 'description', 'followers', 'avatar', 'group', 'group_followers',
        'group_team', 'group_post', 'group_photo', 'group_photo_show')

    def get_group(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:group', args=[obj.pk]))

    def get_group_followers(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:group_followers', args=[obj.pk]))

    def get_group_team(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:group_team', args=[obj.pk]))

    def get_group_post(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:group_post', args=[obj.profile_id, obj.pk]))

    def get_group_photo(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:group_photo', args=[obj.pk]))

    def get_group_photo_show(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:group_photo_show', args=[obj.profile_id, obj.pk]))


class GroupFollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('followers',)


class GroupTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('team',)


class GroupPostsSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    author_url = serializers.SerializerMethodField()

    class Meta:
        model = GroupPosts
        fields = ('author_url', 'author', 'date', 'content', 'like_post', 'photo_post')

    def get_author(self, obj):
        return obj.author.first_name

    def get_author_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:another_user_page', args=[obj.author.pk]))


class GroupPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPhoto
        fields = ('author', 'date', 'photo', 'like', 'description')


class ProfileShowPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('author', 'date', 'photo')


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ('author', 'date', 'content', 'photo_post')


class UserRePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RePosts
        fields = ('author', 'date', 'content')


class UserPhotoShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('author', 'date', 'photo')
