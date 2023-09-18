from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from groups.models import Group, GroupPosts, GroupRePosts, GroupPostsComment, GroupRePostsComment, GroupPostsCommentAuthor
from account.models import Profile, Posts, PostsComment, RePosts, RePostsComment, Notification
from usermessages.models import Dialog

from account.forms import CommentPhotoForm

from itertools import chain


@login_required(login_url='/')
def search(request):

    """Страница поиска"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('search_result', search_text)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Поиск',
        'comment_form': comment_form,
    }

    return render(request, 'search/search.html', data)


@login_required(login_url='/')
def search_result(request, text_search):

    """Страница общий результат поиска"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('search_result', search_text)

    # Кнопка подписаться

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=pk))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- потзователь подпиcался на вас!'
            new_notification.type_object = 'follow'
            new_notification.object_id = pk
            new_notification.content_type = ContentType.objects.get_for_model(Profile)
            new_notification.save()

    # Кнопка отменить подписку

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

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

            return redirect('search_result', text_search)

    # Добавить комментарий к посту группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group':

            need_post = request.POST['post_id']

            new_comment = GroupPostsComment()
            new_comment.posts = GroupPosts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('search_result', text_search)

    # Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

            if need_post.author.profile_id != request.user.id:

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

            return redirect('search_result', text_search)

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

            return redirect('search_result', text_search)

    user = f'{request.user.first_name} {request.user.last_name}'
    i_following = Profile.objects.get(user=request.user.id).following.all()
    comment_form = CommentPhotoForm

    search_people = []
    search_people_all = ''

    # Если запрос состоит из 1 слова

    if len(text_search.split()) == 1:

        search_people += Profile.objects.filter(first_name__iregex=text_search)
        search_people += Profile.objects.filter(last_name__iregex=text_search)
        search_people += Profile.objects.filter(profile_info__iregex=text_search)

        if text_search.lower() in ['люди', 'профили', 'аккаунты', 'пользователи', 'человеки']:

            search_people += Profile.objects.all()

        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

        search_people_count = len(search_people)
        search_people_all = '' if search_people_count <= 5 else search_people_count - 5

        search_people = search_people[:5]

    # Если запрос состоит из 2 слов

    if len(text_search.split()) == 2:

        text_search_list = text_search.split()

        search_people += Profile.objects.filter(first_name__iregex=text_search_list[0], last_name__iregex=text_search_list[1])
        search_people += Profile.objects.filter(first_name__iregex=text_search_list[1], last_name__iregex=text_search_list[0])
        search_people += Profile.objects.filter(profile_info__iregex=text_search)

        if text_search.lower() in ['все люди', 'профили пользователей', 'все аккаунты', 'все пользователи']:

            search_people += Profile.objects.all()

        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

        search_people_count = len(search_people)
        search_people_all = '' if search_people_count <= 5 else search_people_count - 5

        search_people = search_people[:5]

    # Создаем список поиска по постам

    post_and_repost = []

    posts = Posts.objects.filter(content__iregex=text_search)
    reposts = RePosts.objects.filter(content__iregex=text_search)

    group_posts = GroupPosts.objects.filter(content__iregex=text_search)
    group_reposts = GroupRePosts.objects.filter(content__iregex=text_search)

    post_and_repost += sorted(chain(posts, reposts, group_posts, group_reposts), key=lambda x: x.date, reverse=True)
    post_and_repost = [post for post in post_and_repost if post.author.user != request.user]

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

    group = []
    group += Group.objects.filter(first_name__iregex=text_search)
    group += Group.objects.filter(group_info__iregex=text_search)

    if text_search.lower() in ['группы', 'группа', 'все группы', 'сообщества', 'все сообщества']:
        group += Group.objects.all()

    group = list(set(group))

    search_group_count = len(group)
    search_group_all = '' if search_group_count <= 5 else search_group_count - 5

    group = group[:5]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Результат поиска',
        'text_search': text_search,
        'i_following': i_following,
        'comment_form': comment_form,
        'group': group,
        'search_group_all': search_group_all,
        'search_people': search_people,
        'search_people_all': search_people_all,
        'post_and_repost': post_and_repost,
    }

    return render(request, 'search/search_result.html', data)


@login_required(login_url='/')
def search_result_people(request, text_search):

    """Страница результат поиска профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('search_result', search_text)

    # Кнопка подписаться

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=pk))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- потзователь подпиcался на вас!'
            new_notification.type_object = 'follow'
            new_notification.object_id = pk
            new_notification.content_type = ContentType.objects.get_for_model(Profile)
            new_notification.save()

    # Кнопка отменить подписку

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    i_following = Profile.objects.get(user=request.user.id).following.all()
    comment_form = CommentPhotoForm

    search_people = []

    # Если запрос состоит из 1 слова

    if len(text_search.split()) == 1:

        search_people += Profile.objects.filter(first_name__iregex=text_search)
        search_people += Profile.objects.filter(last_name__iregex=text_search)
        search_people += Profile.objects.filter(profile_info__iregex=text_search)

        if text_search.lower() in ['люди', 'профили', 'аккаунты', 'пользователи', 'человеки']:

            search_people += Profile.objects.all()

        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

    # Если запрос состоит из 2 слов

    if len(text_search.split()) == 2:

        text_search_list = text_search.split()

        search_people += Profile.objects.filter(first_name__iregex=text_search_list[0], last_name__iregex=text_search_list[1])
        search_people += Profile.objects.filter(first_name__iregex=text_search_list[1], last_name__iregex=text_search_list[0])
        search_people += Profile.objects.filter(profile_info__iregex=text_search)

        if text_search.lower() in ['все люди', 'профили пользователей', 'все аккаунты', 'все пользователи']:

            search_people += Profile.objects.all()

        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Результат поиска',
        'i_following': i_following,
        'comment_form': comment_form,
        'search_people': search_people,
    }

    return render(request, 'search/search_result.html', data)


def search_result_group(request, text_search):

    """Страница результат поиска групп"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('search_result', search_text)

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    group = []
    group += Group.objects.filter(first_name__iregex=text_search)
    group += Group.objects.filter(group_info__iregex=text_search)

    if text_search.lower() in ['группы', 'группа', 'все группы', 'сообщества', 'все сообщества']:

        group += Group.objects.all()

    group = list(set(group))

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Результат поиска',
        'comment_form': comment_form,
        'group': group,
    }

    return render(request, 'search/search_result.html', data)
