from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required

from groups.models import GroupPosts, GroupRePosts, GroupPostsComment, GroupPostsCommentAuthor, GroupRePostsComment
from account.models import Profile, Posts, PostsComment, RePosts, RePostsComment, Notification
from usermessages.models import Dialog

from account.forms import CommentPhotoForm

from itertools import chain


@login_required(login_url='/')
def news(request):

    """Страница общих новостей пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Добавить комментарий

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            need_post = request.POST['post_id']

            new_comment = PostsComment()
            new_comment.posts = Posts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            need_post = Posts.objects.get(id=request.POST['post_id'])

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=need_post.author.profile_id)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему посту!'
            new_notification.type_object = 'post_comment'
            new_notification.object_id = request.POST['post_id']
            new_notification.content_type = ContentType.objects.get_for_model(Posts)
            new_notification.save()

            return redirect('news')

    # Добавить комментарий к посту группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group':

            need_post = request.POST['post_id']

            new_comment = GroupPostsComment()
            new_comment.posts = GroupPosts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('news')

    # Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

            if request.user.id != need_post.author.profile_id:

                new_notification = Notification()
                new_notification.from_user = Profile.objects.get(profile_id=need_post.author.profile_id)
                new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
                new_notification.message = '- пользователю понравился ваш пост!'
                new_notification.type_object = 'post_like'
                new_notification.object_id = request.POST['post_id']
                new_notification.content_type = ContentType.objects.get_for_model(Posts)
                new_notification.save()

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Кнопка поставить / отменить лайк / пост группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_group':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_group':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete-group':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий к репосту группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete-group':

            comment_id = request.POST['comment_id']
            comment_delete = GroupRePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Добавить комментарий к репосту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

            need_repost = request.POST['post_id']

            new_comment = RePostsComment()
            new_comment.reposts = RePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            need_repost = RePosts.objects.get(id=request.POST['post_id'])

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=need_repost.author.profile_id)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему репосту!'
            new_notification.type_object = 'repost_comment'
            new_notification.object_id = request.POST['post_id']
            new_notification.content_type = ContentType.objects.get_for_model(RePosts)
            new_notification.save()

            return redirect('news')

    # Кнопка удалить комментарий к репосту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = RePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Добавить комментарий к репосту группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group_repost':

            need_repost = request.POST['post_id']

            new_comment = GroupRePostsComment()
            new_comment.reposts = GroupRePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            need_repost = GroupRePosts.objects.get(pk=request.POST['post_id'])

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=need_repost.author.profile_id)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему репосту группы!'
            new_notification.type_object = 'group_repost_comment'
            new_notification.object_id = request.POST['post_id']
            new_notification.content_type = ContentType.objects.get_for_model(GroupRePosts)
            new_notification.save()

            return redirect('news')

    user = f'{request.user.first_name} {request.user.last_name}'
    following = Profile.objects.get(user=request.user.id).following.all()
    comment_form = CommentPhotoForm

    # Создаем список новостей

    post_and_repost = []

    for follow_person in following:

        posts = Posts.objects.filter(author=follow_person.id)
        reposts = RePosts.objects.filter(author=follow_person.id)

        group_reposts = GroupRePosts.objects.filter(author=follow_person.id)

        post_and_repost += sorted(chain(posts, reposts, group_reposts), key=lambda x: x.date, reverse=True)
        post_and_repost = [post for post in post_and_repost if post.author.user != request.user]

    group_posts = GroupPosts.objects.filter(author__followers=request.user)
    post_and_repost += group_posts

    notification = Posts.objects.filter(author__profile_id=1)
    post_and_repost += notification

    post_and_repost = sorted(post_and_repost, key=lambda x: x.date, reverse=True)

    # Добавить 3 последних комментария к постам и репостам

    for target_post in post_and_repost:

        if type(target_post) == Posts:
            target_post.comments = reversed(PostsComment.objects.filter(posts=target_post).order_by('-date')[:3])

        elif type(target_post) == RePosts:
            target_post.comments = reversed(
                RePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

        elif type(target_post) == GroupPosts:
            comments_user = GroupPostsComment.objects.filter(posts=target_post)
            comments_author = GroupPostsCommentAuthor.objects.filter(posts=target_post)
            target_post.comments = list(sorted(chain(comments_user, comments_author), key=lambda x: x.date))[-3:]

        elif type(target_post) == GroupRePosts:
            target_post.comments = reversed(
                GroupRePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

    # Создаем список случайных новостей

    randon_post_and_repost = []

    posts = Posts.objects.all()
    reposts = RePosts.objects.all()

    group_posts = GroupPosts.objects.all()
    group_reposts = GroupRePosts.objects.all()

    randon_post_and_repost += sorted(chain(posts, reposts, group_posts, group_reposts), key=lambda x: x.date, reverse=True)
    randon_post_and_repost = [post for post in randon_post_and_repost if post.author.user != request.user]

    randon_post_and_repost = sorted(randon_post_and_repost, key=lambda x: x.date, reverse=True)
    randon_post_and_repost = ''

    # Добавить 3 последних комментария к постам и репостам

    for target_post in randon_post_and_repost:

        if type(target_post) == Posts:
            target_post.comments = reversed(
                PostsComment.objects.filter(posts=target_post).order_by('-date')[:3])

        elif type(target_post) == RePosts:
            target_post.comments = reversed(
                RePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

        elif type(target_post) == GroupPosts:
            comments_user = GroupPostsComment.objects.filter(posts=target_post)
            comments_author = GroupPostsCommentAuthor.objects.filter(posts=target_post)
            target_post.comments = list(sorted(chain(comments_user, comments_author), key=lambda x: x.date))[-3:]

        elif type(target_post) == GroupRePosts:
            target_post.comments = reversed(
                GroupRePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

    user_notification = Notification.objects.filter(from_user__profile_id=request.user.id).order_by('-date')[:3]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': 'Новости',
        'user': user,
        'post_and_repost': post_and_repost,
        'randon_post_and_repost': randon_post_and_repost[:10],
        'comment_form': comment_form,
        'user_notification': user_notification,
    }

    return render(request, 'news/all_news.html', data)


@login_required(login_url='/')
def notification(request):

    """Страница просмотра оповещений"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user_notification = Notification.objects.filter(from_user__profile_id=request.user.id).order_by('-date')
    user = f'{request.user.first_name} {request.user.last_name}'

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': 'Новости',
        'user': user,
        'user_notification': user_notification,
    }

    return render(request, 'news/notification.html', data)
