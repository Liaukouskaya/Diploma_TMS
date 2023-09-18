from django.contrib import admin

from .models import Profile, Posts, RePosts, Photo, PostsComment, RePostsComment, PhotoComment, Notification
from usermessages.models import Dialog, Messages, MessagePhoto

from groups.models import Group, GroupPosts, GroupRePosts, GroupPhoto, GroupPostsComment
from groups.models import GroupPhotoComment, GroupPhotoCommentAuthor, GroupPostsCommentAuthor, GroupRePostsComment

# Профиль

admin.site.register(Profile)
admin.site.register(Posts)
admin.site.register(RePosts)
admin.site.register(Photo)
admin.site.register(PostsComment)
admin.site.register(RePostsComment)
admin.site.register(PhotoComment)
admin.site.register(Notification)

# Сообщения

admin.site.register(Dialog)
admin.site.register(Messages)
admin.site.register(MessagePhoto)

# Группы

admin.site.register(Group)
admin.site.register(GroupPosts)
admin.site.register(GroupRePosts)
admin.site.register(GroupPhoto)
admin.site.register(GroupPostsComment)
admin.site.register(GroupPhotoComment)
admin.site.register(GroupPhotoCommentAuthor)
admin.site.register(GroupPostsCommentAuthor)
admin.site.register(GroupRePostsComment)
