from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Group, GroupPhoto, GroupPosts, GroupPostsComment, GroupRePostsComment, GroupRePosts
from .models import GroupPostsCommentAuthor, GroupPhotoComment, GroupPhotoCommentAuthor

from account.models import Profile, Notification
from account.forms import PostsForm, DescriptionPhotoForm, CommentPhotoForm
from usermessages.models import Dialog

from itertools import chain
import random


@login_required(login_url='/')
def groups(request):

    """Страница групп общая"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка создать группу

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_group':

            new_group = Group()
            new_group.user = request.user
            new_group.first_name = request.POST['comment']
            new_group.save()

            return redirect('groups')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    user_group = Group.objects.filter(user=request.user)
    fallowing_group = Group.objects.filter(followers=request.user)
    admin_group = Group.objects.filter(team=request.user)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Группы',
        'comment_form': comment_form,
        'user_group': user_group,
        'fallowing_group': fallowing_group,
        'admin_group': admin_group,
    }

    return render(request, 'groups/groups.html', data)


@login_required(login_url='/')
def group_view(request, group_id):

    """Страница просмотра группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    group_info = ''

    if request.method == 'POST':

    # Кнопка новый аватар

        if 'nev_avatar' in request.FILES and request.FILES['nev_avatar']:

            group = Group.objects.get(profile_id=group_id)
            group.avatar = request.FILES['nev_avatar']
            group.save()

    # Кнопка создать пост в ленте

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_post':

            new_post = GroupPosts()
            new_post.author = Group.objects.get(profile_id=group_id)
            new_post.content = request.POST['content']
            new_post.save()

            if 'photo_post' in request.FILES and request.FILES['photo_post']:

                for send_photo in request.FILES.getlist('photo_post'):

                    photo = GroupPhoto()
                    photo.author = Group.objects.get(profile_id=group_id)
                    photo.photo = send_photo
                    photo.save()
                    new_post.add_photo_in_post(photo)
                    new_post.save()

            return redirect('group_view', group_id)

    # Кнопка удалить пост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = GroupPosts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка загрузки фото

        if 'nev_photo' in request.FILES and request.FILES['nev_photo']:

            for send_photo in request.FILES.getlist('nev_photo'):

                photo = GroupPhoto()
                photo.author = Group.objects.get(profile_id=group_id)
                photo.photo = send_photo
                photo.save()

    # Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий к посту - от создателя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group':

            need_post = request.POST['post_id']

            new_comment = GroupPostsCommentAuthor()
            new_comment.posts = GroupPosts.objects.get(pk=need_post)
            new_comment.author = Group.objects.get(pk=group_id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('group_view', group_id)

    # Добавить комментарий к посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            need_post = request.POST['post_id']

            new_comment = GroupPostsComment()
            new_comment.posts = GroupPosts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('group_view', group_id)

    # Кнопка удалить комментарий - от создателя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete-author':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPostsCommentAuthor.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка подписаться

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Group.objects.get(profile_id=group_id))

    # Кнопка отменить подписку

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Group.objects.get(profile_id=group_id))

    # Кнопка написать сообщение

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'send_message':

            group = Group.objects.get(profile_id=group_id)

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=group.user.id)

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else: return redirect('dialog', dialog.id)

    # Кнопка показать информацию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'show_info':

            group_info = Group.objects.get(profile_id=group_id).group_info
            if not group_info: group_info = 'Не заполнено...'

    # Кнопка создать описание

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_info':

            group = Group.objects.get(profile_id=group_id)
            group.group_info = request.POST['comment']
            group.save()

            return redirect('group_view', group_id)

    all_photo = GroupPhoto.objects.filter(author=group_id).order_by('-date')

    photo_count = all_photo.count()

    all_photo_left = all_photo[:6][::-1]
    temp_left = [None for _ in range(6 - len(all_photo_left))]

    all_photo_right = all_photo[6:12]
    temp_right = [None for _ in range(6 - len(all_photo_right))]

    user = f'{request.user.first_name} {request.user.last_name}'

    group = get_object_or_404(Group, profile_id=group_id)

    posts_form = PostsForm
    comment_form = CommentPhotoForm

    posts = GroupPosts.objects.filter(author__profile_id=group_id)
    post_and_repost = sorted(chain(posts), key=lambda x: x.date, reverse=True)

    team = Group.objects.get(profile_id=group_id).team.all()
    team = [target.id for target in team]

    # Добавить комментарии к постам на странице профиля

    for target_post in post_and_repost:

        if type(target_post) == GroupPosts:
            comments_user = GroupPostsComment.objects.filter(posts=target_post)
            comments_author = GroupPostsCommentAuthor.objects.filter(posts=target_post)
            target_post.comments = list(sorted(chain(comments_user, comments_author), key=lambda x: x.date))[-3:]

        elif type(target_post) == GroupRePosts:
            target_post.comments = reversed(GroupRePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

    follower = group.followers.filter(username=request.user.username).exists()              # проверка подписки

    followers = Group.objects.get(profile_id=group_id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    if followers_count < 10:

        if followers_count % 2 != 0:
            followers.append(None)
            followers_left = followers[:len(followers) // 2]
            followers_right = followers[len(followers) // 2:]

        else:
            followers_left = followers[:len(followers) // 2]
            followers_right = followers[len(followers) // 2:]

    else:
        random.shuffle(followers)
        followers_left = followers[:5]
        followers_right = followers[-5:]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': f'{group.first_name}',
        'group': group,
        'team': team,
        'posts_form': posts_form,
        'comment_form': comment_form,
        'post_and_repost': post_and_repost,
        'follower': follower,
        'followers_left': followers_left,
        'followers_right': followers_right,
        'followers_count': followers_count,
        'photo_count': photo_count,
        'all_photo_left': all_photo_left,
        'temp_left': temp_left,
        'all_photo_right': all_photo_right,
        'temp_right': temp_right,
        'group_info': group_info,
    }

    return render(request, 'groups/group_page.html', data)


@login_required(login_url='/')
def group_followers(request, group_id):

    """Страница подписчиков группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=user_pk))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=user_pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- потзователь подпиcался на вас!'
            new_notification.type_object = 'follow'
            new_notification.object_id = user_pk
            new_notification.content_type = ContentType.objects.get_for_model(Profile)
            new_notification.save()

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=user_pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    group = get_object_or_404(Group, profile_id=group_id)

    followers = Group.objects.get(profile_id=group_id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    team = Group.objects.get(profile_id=group_id).team.all()
    team = [target.id for target in team]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'group': group,
        'team': team,
        'title': 'Подписчики:',
        'i_following': i_following,
        'followers': followers,
        'followers_count': followers_count,
    }

    return render(request, 'groups/group_followers.html', data)


@login_required(login_url='/')
def group_team(request, group_id):

    """Страница подписчиков других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    search_people = []

    if request.method == 'POST':

    # Кнопка подписаться

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':


            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=user_pk))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=user_pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- потзователь подпиcался на вас!'
            new_notification.type_object = 'follow'
            new_notification.object_id = user_pk
            new_notification.content_type = ContentType.objects.get_for_model(Profile)
            new_notification.save()

    # Кнопка отменить подписку

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=user_pk))

    # Кнопка найти пользователей

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            text_search = request.POST['comment']

            # Если запрос состоит из 1 слова

            if len(text_search.split()) == 1:
                search_people += Profile.objects.filter(first_name__iregex=text_search)
                search_people += Profile.objects.filter(last_name__iregex=text_search)
                search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

            # Если запрос состоит из 2 слов

            elif len(text_search.split()) == 2:
                text_search_list = text_search.split()

                search_people += Profile.objects.filter(first_name__iregex=text_search_list[0],
                                                        last_name__iregex=text_search_list[1])
                search_people += Profile.objects.filter(first_name__iregex=text_search_list[1],
                                                        last_name__iregex=text_search_list[0])
                search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

    # Кнопка подписаться

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'add':

            user_pk = request.POST['user_id']
            group = get_object_or_404(Group, profile_id=group_id)
            group.team.add(User.objects.get(pk=user_pk))

    # Кнопка отменить подписку

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'remove':

            user_pk = request.POST['user_id']
            group = get_object_or_404(Group, profile_id=group_id)
            group.team.remove(User.objects.get(pk=user_pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    group = get_object_or_404(Group, profile_id=group_id)

    creator = Profile.objects.get(profile_id=group.user.id)

    team = Group.objects.get(profile_id=group_id).team.all()
    team = [Profile.objects.get(profile_id=target.id) for target in team]

    team_id = Group.objects.get(profile_id=group_id).team.all()
    team_id = [target.id for target in team_id]

    check_team = Profile.objects.get(profile_id=request.user.id)

    i_following = Profile.objects.get(user=request.user.id).following.all()

    comment_form = CommentPhotoForm

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'group': group,
        'title': 'Подписчики:',
        'creator': creator,
        'i_following': i_following,
        'team': team,
        'team_id': team_id,
        'check_team': check_team,
        'comment_form': comment_form,
        'search_people': search_people,
    }

    return render(request, 'groups/group_team.html', data)


@login_required(login_url='/')
def groups_photo(request, group_id):

    """Страница фотографий группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    group = get_object_or_404(Group, profile_id=group_id)
    photo_all = GroupPhoto.objects.filter(author=group).order_by('-date')
    photo_tot = photo_all.count()

    team = Group.objects.get(profile_id=group_id).team.all()
    team = [target.id for target in team]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'group': group,
        'team': team,
        'title': 'Фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'groups/group_page_photo.html', data)


@login_required(login_url='/')
def groups_photo_show(request, group_id, pk_photo):

    """Страница просмотра фото группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    group = get_object_or_404(Group, profile_id=group_id)
    photo_all = GroupPhoto.objects.filter(author=group_id)
    photo_count = len(photo_all)
    photo_single = get_object_or_404(GroupPhoto, id=pk_photo)

    check_like = photo_single.like.filter(username=request.user.username).exists()  # проверка лайка
    count_like = photo_single.like.count()

    description_form = ''
    comment_form = CommentPhotoForm

    # Слайдер на странице фотографий

    center_index = list(photo_all).index(photo_single)
    len_photo_all = len(photo_all)

    if len_photo_all <= 9:
        photo_line = photo_all

    elif center_index < 5:
        photo_line = photo_all[:5] + photo_all[5:9]

    elif center_index > len_photo_all - 5 and len_photo_all >= 7:
        photo_line = photo_all[len_photo_all - 9:len_photo_all - 3] + photo_all[len_photo_all - 3:]

    else:
        photo_line = photo_all[center_index - 4: center_index] + photo_all[center_index: center_index + 5]

    # Нажатие на фото для прокрутки на странице фотографий

    if request.method == 'POST':

    # правая часть фото - следующее фото

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'forward':

            if photo_all[len_photo_all - 1].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) + 1].id
                return redirect('groups_photo_show', group_id=group_id, pk_photo=next_photo)

            else: return redirect('groups_photo_show', group_id=group_id, pk_photo=photo_all[0].id)

    # левая часть фото - предыдущее фото

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'back':

            if photo_all[0].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id
                return redirect('groups_photo_show', group_id=group_id, pk_photo=next_photo)

            else: return redirect('groups_photo_show', group_id=group_id, pk_photo=photo_all[len_photo_all - 1].id)

    # Удалить фотографию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'delete':

            photo_delete = GroupPhoto.objects.get(id=pk_photo)  # Получаем объект модели, который нужно удалить
            photo_delete.delete()

            if photo_all[0].id != pk_photo:
                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id

            elif photo_all.count() == 1: return redirect('groups_photo', group_id)

            else: next_photo = photo_all[1].id

            return redirect('groups_photo_show', group_id=group_id, pk_photo=next_photo)

    # Кнопка добавить описание к фотографии

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'description':

            description_form = DescriptionPhotoForm

    # Кнопка сохранить описание к фотографии

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_description':

            photo_single.description = request.POST['description']
            photo_single.save()

            return redirect('groups_photo_show', group_id, pk_photo)

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':
            photo_single.set_like(Profile.objects.get(profile_id=request.user.id))
            return redirect('groups_photo_show', group_id, pk_photo)

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':
            photo_single.set_unlike(Profile.objects.get(profile_id=request.user.id))
            return redirect('groups_photo_show', group_id, pk_photo)

    # Добавить комментарий к посту - от создателя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group':

            new_comment = GroupPhotoCommentAuthor()
            new_comment.photo = GroupPhoto.objects.get(pk=pk_photo)
            new_comment.author = Group.objects.get(pk=group_id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('groups_photo_show', group_id, pk_photo)

    # Добавить комментарий к посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            new_comment = GroupPhotoComment()
            new_comment.photo = GroupPhoto.objects.get(pk=pk_photo)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('groups_photo_show', group_id, pk_photo)

    # Кнопка удалить комментарий - от создателя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete-author':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPhotoCommentAuthor.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPhotoComment.objects.get(id=comment_id)
            comment_delete.delete()

    comments_user = GroupPhotoComment.objects.filter(photo=pk_photo)
    comments_author = GroupPhotoCommentAuthor.objects.filter(photo=pk_photo)

    all_comment = list(sorted(chain(comments_user, comments_author), key=lambda x: x.date))

    team = Group.objects.get(profile_id=group_id).team.all()
    team = [target.id for target in team]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'group': group,
        'team': team,
        'title': 'Фотографии сообщества:',
        'photo_line': photo_line,
        'photo_single': photo_single,
        'photo_count': photo_count,
        'check_like': check_like,
        'count_like': count_like,
        'description_form': description_form,
        'all_comment': all_comment,
        'comment_form': comment_form,
    }

    return render(request, 'groups/group_page_photo_show.html', data)


@login_required(login_url='/')
def groups_post(request, group_id, pk_post):

    """Страница просмотра поста группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = GroupPosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('group_view', group_id)

    # Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий к посту - от создателя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group':

            need_post = request.POST['post_id']

            new_comment = GroupPostsCommentAuthor()
            new_comment.posts = GroupPosts.objects.get(pk=need_post)
            new_comment.author = Group.objects.get(pk=group_id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('groups_post', group_id, pk_post)

    # Добавить комментарий к посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            need_post = request.POST['post_id']

            new_comment = GroupPostsComment()
            new_comment.posts = GroupPosts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('groups_post', group_id, pk_post)

    # Кнопка удалить комментарий - от создателя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete-author':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPostsCommentAuthor.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = GroupPostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    user = f'{request.user.first_name} {request.user.last_name}'
    group = get_object_or_404(Group, profile_id=group_id)
    comment_form = CommentPhotoForm
    post = get_object_or_404(GroupPosts, id=pk_post)

    comments_user = GroupPostsComment.objects.filter(posts=post)
    comments_author = GroupPostsCommentAuthor.objects.filter(posts=post)
    all_comment = list(sorted(chain(comments_user, comments_author), key=lambda x: x.date))

    team = Group.objects.get(profile_id=group_id).team.all()
    team = [target.id for target in team]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': f'Пост {pk_post}',
        'group': group,
        'post': post,
        'team': team,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'groups/group_page_post.html', data)

