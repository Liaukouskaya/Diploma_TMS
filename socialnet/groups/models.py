from django.contrib.auth.models import User
from django.db import models

from account.models import Profile


class Group(models.Model):

    """Модель группы"""

    profile_id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)

    team = models.ManyToManyField(User, related_name='team', blank=True)
    group_info = models.TextField(max_length=500, blank=True)
    group_status = models.TextField(blank=True)

    followers = models.ManyToManyField(User, related_name='group_followers', blank=True)

    avatar = models.ImageField(upload_to='avatars/', default='avatars/standard-avatar.jpg')

    # методы

    def __str__(self):
        return f'{self.first_name}'

    @property
    def photo_url(self):
        """Возвращает ссылку на изображение"""
        if self.avatar and hasattr(self.avatar, 'url'): return self.avatar.url

    def get_absolute_url(self):
        """Определение ссылки на объект модели"""
        return f'/avatars/{self.profile_id}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class GroupPhoto(models.Model):

    """Модель фотоальбома группы"""

    author = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='photo/')
    like = models.ManyToManyField(User, related_name='group_like', blank=True)
    description = models.TextField(blank=True)

    # методы

    def __str__(self):
        return f'{self.author} / {self.date}'

    @property
    def photo_url(self):
        """Возвращает ссылку на изображение"""
        if self.photo and hasattr(self.photo, 'url'): return self.photo.url

    def get_absolute_url(self):
        """Определение ссылки на объект модели"""
        return f'/photo/{self.pk}'

    def set_like(self, profile):
        """Поставить лайк"""
        self.like.add(profile.user)

    def set_unlike(self, profile):
        """Отменить лайк"""
        self.like.remove(profile.user)

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'


class GroupPhotoComment(models.Model):

    """Модель комментариев к фотографии группы"""

    photo = models.ForeignKey(GroupPhoto, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    # методы

    def __str__(self):
        return f'{self.author} / {self.photo}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class GroupPhotoCommentAuthor(models.Model):

    """Модель комментариев к фотографии группы - автор группы"""

    photo = models.ForeignKey(GroupPhoto, on_delete=models.CASCADE)
    author = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    # методы

    def __str__(self):
        return f'{self.author} / {self.photo}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class GroupPosts(models.Model):

    """Модель записей в ленте группы"""

    author = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    like_post = models.ManyToManyField(User, related_name='group_like_post', blank=True)
    photo_post = models.ManyToManyField(GroupPhoto, related_name='group_photo_post', blank=True)
    type_object = 'GroupPosts'

    # методы

    def __str__(self):
        return f'{self.author} / {self.date}'

    def set_like_post(self, profile):
        """Поставить лайк"""
        self.like_post.add(profile.user)

    def set_unlike_post(self, profile):
        """Отменить лайк"""
        self.like_post.remove(profile.user)

    def add_photo_in_post(self, photo):
        """Добавить фото в пост"""
        self.photo_post.add(photo.id)

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class GroupPostsComment(models.Model):

    """Модель комментариев к постам группы"""

    posts = models.ForeignKey(GroupPosts, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    # методы

    def __str__(self):
        return f'{self.author} / {self.posts}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class GroupPostsCommentAuthor(models.Model):

    """Модель комментариев к постов группы - автор группы"""

    posts = models.ForeignKey(GroupPosts, on_delete=models.CASCADE)
    author = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    # методы

    def __str__(self):
        return f'{self.author} / {self.posts}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class GroupRePosts(models.Model):

    """Модель репостов в ленте группы"""

    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(GroupPosts, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    type_object = 'GroupRePosts'

    # методы

    def __str__(self):
        return f'{self.author} / {self.__class__}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Репост'
        verbose_name_plural = 'Репосты'


class GroupRePostsComment(models.Model):

    """Модель комментариев репостов группы"""

    reposts = models.ForeignKey(GroupRePosts, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    # методы

    def __str__(self):
        return f'{self.author} / {self.reposts}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Комментарий репоста'
        verbose_name_plural = 'Комментарии репостов'
