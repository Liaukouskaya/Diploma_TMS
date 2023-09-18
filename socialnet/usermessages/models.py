from django.db import models

from account.models import Profile, Posts, Photo, RePosts
from groups.models import GroupPosts, GroupRePosts


class Dialog(models.Model):

    """Модель диалога"""

    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    user_list = models.ManyToManyField(Profile, related_name='user_list', blank=True)
    last_message = models.ForeignKey('Messages', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    last_message_text = models.TextField(blank=True)
    last_message_time = models.DateTimeField(auto_now_add=True)

    # методы

    def __str__(self):
        return ' '.join([str(user) for user in self.user_list.all()])

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'


class MessagePhoto(models.Model):

    """Модель фотоальбома"""

    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photo/')

    # методы

    def __str__(self):
        return f'{self.author}'

    @property
    def photo_url(self):
        """Возвращает ссылку на изображение"""
        if self.photo and hasattr(self.photo, 'url'): return self.photo.url

    def get_absolute_url(self):
        """Определение ссылки на объект модели"""
        return f'/photo/{self.pk}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'


class Messages(models.Model):

    """Модель сообщений"""

    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    photo_post = models.ManyToManyField(MessagePhoto, related_name='photo_messages', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    send_photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True, related_name='messsage_send_photo')
    send_post = models.ForeignKey(Posts, on_delete=models.SET_NULL, null=True, blank=True, related_name='messsage_send_post')
    send_repost = models.ForeignKey(RePosts, on_delete=models.SET_NULL, null=True, blank=True, related_name='messsage_send_repost')
    send_group_post = models.ForeignKey(GroupPosts, on_delete=models.SET_NULL, null=True, blank=True, related_name='messsage_send_group_post')
    send_group_repost = models.ForeignKey(GroupRePosts, on_delete=models.SET_NULL, null=True, blank=True, related_name='messsage_send_group_repost')

    # методы

    def add_photo_in_post(self, photo):
        """Добавить фото в пост"""
        self.photo_post.add(photo.id)

    def __str__(self):
        return f'{self.dialog}'

    class Meta:
        """Отображение в админ панели"""
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
