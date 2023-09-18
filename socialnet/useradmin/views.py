from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required

from account.models import Profile, Posts, Photo, PhotoComment, PostsComment, RePosts, RePostsComment
from groups.models import Group, GroupPosts, GroupRePosts, GroupPostsComment, GroupRePostsComment, GroupPostsCommentAuthor
from groups.models import GroupPhoto, GroupPhotoCommentAuthor, GroupPhotoComment
from usermessages.models import Dialog, Messages, MessagePhoto

from account.forms import PostsForm, CommentPhotoForm

from itertools import chain
import random

from socialnet.tasks import send_block_email, send_unblock_email


@login_required(login_url='/')
def settings_page(request):

    """Страничка настроек / выход"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    profile = Profile.objects.get(profile_id=request.user.id)

    profile.user_admin_switch = True
    profile.save()

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'title': 'Настройки',
        'user': user,
        'profile': profile,
    }

    return render(request, 'useradmin/admin_settings_page.html', data)


@login_required(login_url='/')
def admin_search(request):

    """Страница поиска"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('admin_search_result', search_text)

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Поиск',
        'comment_form': comment_form,
    }

    return render(request, 'useradmin/admin_search.html', data)


@login_required(login_url='/')
def admin_search_result(request, text_search):

    """Страница общий результат поиска"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('admin_search_result', search_text)

    # Кнопка удалить пост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = Posts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            post_id = request.POST['repost_id']
            post_delete = RePosts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить пост группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-group-delete':

            post_id = request.POST['posts_group_id']
            post_delete = GroupPosts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить репост группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-group-delete':

            post_id = request.POST['reposts_group_id']
            post_delete = GroupRePosts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий к репосту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = RePostsComment.objects.get(id=comment_id)
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

    user = f'{request.user.first_name} {request.user.last_name}'
    i_following = Profile.objects.get(user=request.user.id).following.all()
    comment_form = CommentPhotoForm

    search_people = []
    search_people_all = ''

    # Если запрос состоит из 1 слова

    if len(text_search.split()) == 1:

        search_people += Profile.objects.filter(first_name__iregex=text_search)
        search_people += Profile.objects.filter(last_name__iregex=text_search)
        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

        search_people_count = len(search_people)
        search_people_all = '' if search_people_count <= 5 else search_people_count - 5

        search_people = search_people[:5]

    # Если запрос состоит из 2 слов

    if len(text_search.split()) == 2:

        text_search_list = text_search.split()

        search_people += Profile.objects.filter(first_name__iregex=text_search_list[0], last_name__iregex=text_search_list[1])
        search_people += Profile.objects.filter(first_name__iregex=text_search_list[1], last_name__iregex=text_search_list[0])
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
    group = Group.objects.filter(first_name__iregex=text_search)

    search_group_count = len(group)
    search_group_all = '' if search_group_count <= 5 else search_group_count - 5

    group = group[:5]

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

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

    return render(request, 'useradmin/admin_search_result.html', data)


@login_required(login_url='/')
def admin_search_result_people(request, text_search):

    """Страница результат поиска профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('admin_search_result', search_text)

    user = f'{request.user.first_name} {request.user.last_name}'
    i_following = Profile.objects.get(user=request.user.id).following.all()
    comment_form = CommentPhotoForm

    search_people = []

    # Если запрос состоит из 1 слова

    if len(text_search.split()) == 1:

        search_people += Profile.objects.filter(first_name__iregex=text_search)
        search_people += Profile.objects.filter(last_name__iregex=text_search)
        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

    # Если запрос состоит из 2 слов

    if len(text_search.split()) == 2:

        text_search_list = text_search.split()

        search_people += Profile.objects.filter(first_name__iregex=text_search_list[0], last_name__iregex=text_search_list[1])
        search_people += Profile.objects.filter(first_name__iregex=text_search_list[1], last_name__iregex=text_search_list[0])
        search_people = [person for person in set(search_people) if person.profile_id != request.user.id]

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Результат поиска',
        'i_following': i_following,
        'comment_form': comment_form,
        'search_people': search_people,
    }

    return render(request, 'useradmin/admin_search_result.html', data)


def admin_search_result_group(request, text_search):

    """Страница результат поиска групп"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':

            search_text = request.POST['comment']
            return redirect('admin_search_result', search_text)

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    group = []
    group = Group.objects.filter(first_name__iregex=text_search)

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Результат поиска',
        'comment_form': comment_form,
        'group': group,
    }

    return render(request, 'useradmin/admin_search_result.html', data)


@login_required(login_url='/')
def admin_another_user_page(request, pk):

    """Профиль другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = Posts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            post_id = request.POST['repost_id']
            post_delete = RePosts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить репост группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-group-delete':

            post_id = request.POST['reposts_group_id']
            post_delete = GroupRePosts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий к репосту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = RePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить комментарий к репосту группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete-group':

            comment_id = request.POST['comment_id']
            comment_delete = GroupRePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка добавить пользователя в администраторы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'add_admin':

            need_person = Profile.objects.get(profile_id=pk)
            need_person.user_admin = True
            need_person.save()

    # Кнопка забрать права администратора

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'remove_admin':

            need_person = Profile.objects.get(profile_id=pk)
            need_person.user_admin = False
            need_person.save()

    # Кнопка заблокировать пользователя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'block':

            need_person = Profile.objects.get(profile_id=pk)
            need_person.block = True
            need_person.save()

            email = need_person.user.username
            send_block_email.delay(email)

    # Кнопка разблокировать пользователя

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unblock':

            need_person = Profile.objects.get(profile_id=pk)
            need_person.block = False
            need_person.save()

            email = need_person.user.username
            send_unblock_email.delay(email)

    if request.user.id != pk:

        user = f'{request.user.first_name} {request.user.last_name}'
        person = get_object_or_404(Profile, user=pk)                         # профиль другого user

        posts = Posts.objects.filter(author=pk)
        reposts = RePosts.objects.filter(author=pk)
        reposts_group = GroupRePosts.objects.filter(author=pk)

        post_and_repost = sorted(chain(posts, reposts, reposts_group), key=lambda x: x.date, reverse=True)

        # Добавить комментарии к постам на странице профиля

        for target_post in post_and_repost:

            if type(target_post) == Posts:
                target_post.comments = reversed(PostsComment.objects.filter(posts=target_post).order_by('-date')[:3])

            elif type(target_post) == RePosts:
                target_post.comments = reversed(
                    RePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

            elif type(target_post) == GroupRePosts:
                target_post.comments = reversed(
                    GroupRePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

        follower = person.followers.filter(username=request.user.username).exists()             # проверка подписки
        followers = Profile.objects.get(user=pk).followers.all()
        followers_count = followers.count()
        followers = [Profile.objects.get(profile_id=target.id) for target in followers]
        random.shuffle(followers)
        followers = followers[:5]
        following = Profile.objects.get(user=pk).following.all()
        following_count = following.count()
        following = [Profile.objects.get(profile_id=target.id) for target in following]
        random.shuffle(following)
        following = following[:5]

        all_photo = Photo.objects.filter(author__user=person.user).order_by('-date')

        photo_count = all_photo.count()

        all_photo_left = all_photo[:6][::-1]
        temp_left = [None for _ in range(6 - len(all_photo_left))]

        all_photo_right = all_photo[6:12]
        temp_right = [None for _ in range(6 - len(all_photo_right))]

        comment_form = CommentPhotoForm

        not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
        not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

        data = {
            'not_read_message': not_read_message,
            'title': f'Пользователь #{pk}',
            'user': user,
            'person': person,
            'follower': follower,
            'post_and_repost': post_and_repost,
            'followers': followers,
            'following': following,
            'followers_count': followers_count,
            'following_count': following_count,
            'photo_count': photo_count,
            'all_photo_left': all_photo_left,
            'temp_left': temp_left,
            'all_photo_right': all_photo_right,
            'temp_right': temp_right,
            'comment_form': comment_form,
        }

        return render(request, 'useradmin/admin_another_user_page.html', data)

    else: return redirect('profile_page')


@login_required(login_url='/')
def admin_another_user_page_followers(request, pk):

    """Страница подписчиков других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    person = get_object_or_404(Profile, user=pk)  # профиль другого user

    followers = Profile.objects.get(user=pk).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'person': person,
        'title': 'Подписчики:',
        'followers': followers,
        'followers_count': followers_count,
    }

    return render(request, 'useradmin/admin_another_user_followers.html', data)


@login_required(login_url='/')
def admin_another_user_page_following(request, pk):

    """Страница подписок других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    person = get_object_or_404(Profile, user=pk)  # профиль другого user

    following = Profile.objects.get(user=pk).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'person': person,
        'title': 'Подписчики:',
        'followers': following,
        'followers_count': following_count,
    }

    return render(request, 'useradmin/admin_another_user_following.html', data)


@login_required(login_url='/')
def admin_another_user_page_photo(request, pk):

    """Страница фотоальбом других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    person = get_object_or_404(Profile, user=pk)  # профиль другого user
    photo_all = Photo.objects.filter(author__user=person.user).order_by('-date')
    photo_tot = photo_all.count()

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'useradmin/admin_another_user_photo.html', data)


@login_required(login_url='/')
def admin_another_user_page_photo_show(request, pk, pk_photo):

    """Страница просмотра фото других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if pk == request.user.id: return redirect('profile_page_photo_show', pk_photo)

    user = f'{request.user.first_name} {request.user.last_name}'
    person = get_object_or_404(Profile, user=pk)
    photo_all = Photo.objects.filter(author__user=person.user).order_by('-date')
    photo_single = get_object_or_404(Photo, id=pk_photo)

    check_like = photo_single.like.filter(username=request.user.username).exists()  # проверка лайка
    count_like = photo_single.like.count()

    all_comment = PhotoComment.objects.filter(photo=pk_photo)
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

    # Правая часть фото - следующее фото

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'forward':

            if photo_all[len_photo_all - 1].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) + 1].id
                return redirect('admin_another_user_page_photo_show', pk=pk, pk_photo=next_photo)

            else:
                return redirect('admin_another_user_page_photo_show', pk=pk, pk_photo=photo_all[0].id)

    # Левая часть фото - предыдущее фото

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'back':

            if photo_all[0].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id
                return redirect('admin_another_user_page_photo_show', pk=pk, pk_photo=next_photo)

            else:
                return redirect('admin_another_user_page_photo_show', pk=pk, pk_photo=photo_all[len_photo_all - 1].id)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PhotoComment.objects.get(id=comment_id)
            comment_delete.delete()

            return redirect('admin_another_user_page_photo_show', pk, pk_photo)

    # Удалить фотографию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'delete':

            photo_delete = Photo.objects.get(id=pk_photo)  # Получаем объект модели, который нужно удалить
            photo_delete.delete()

            if photo_all[0].id != pk_photo:
                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id

            elif photo_all.count() == 1: return redirect('admin_another_user_page_photo')

            else: next_photo = photo_all[1].id

            return redirect('admin_another_user_page_photo_show', pk=pk, pk_photo=next_photo)

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Фотографии:',
        'photo_line': photo_line,
        'photo_single': photo_single,
        'check_like': check_like,
        'count_like': count_like,
        'all_comment': all_comment,
        'comment_form': comment_form,
    }

    return render(request, 'useradmin/admin_another_user_photo_show.html', data)


@login_required(login_url='/')
def admin_another_user_page_post(request, pk, pk_post):

    """Просмотр поста другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if pk == request.user.id: return redirect('profile_page_post', pk_post)

    if request.method == 'POST':

    # Кнопка удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = Posts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('admin_another_user_page', pk)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    post = get_object_or_404(Posts, id=pk_post)
    all_comment = PostsComment.objects.filter(posts=post)

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_post}',
        'user': user,
        'post': post,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'useradmin/admin_another_user_page_post.html', data)


@login_required(login_url='/')
def admin_another_user_page_repost(request, pk, pk_repost):

    """Просмотр репоста другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Удалить комментарий

        if 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = RePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить репост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            post_id = request.POST['repost_id']
            post_delete = RePosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('admin_another_user_page', pk)

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm
    repost = get_object_or_404(RePosts, id=pk_repost)
    all_comment = RePostsComment.objects.filter(reposts=repost)

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_repost}',
        'user': user,
        'post': repost,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'useradmin/admin_another_user_page_repost.html', data)


@login_required(login_url='/')
def admin_another_user_page_group_repost(request, pk, pk_repost):

    """Просмотр репоста группы другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Удалить репост группы

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-group-delete':

            post_id = request.POST['reposts_group_id']
            post_delete = GroupRePosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('admin_another_user_page', pk)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = GroupRePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm
    repost = get_object_or_404(GroupRePosts, id=pk_repost)
    all_comment = GroupRePostsComment.objects.filter(reposts=repost)

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_repost}',
        'user': user,
        'post': repost,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'useradmin/admin_another_user_page_group_repost.html', data)


@login_required(login_url='/')
def admin_group_view(request, group_id):

    """Просмотр группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = GroupPosts.objects.get(id=post_id)
            post_delete.delete()

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

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

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
    }

    return render(request, 'useradmin/admin_group_page.html', data)


@login_required(login_url='/')
def admin_group_followers(request, group_id):

    """Страница подписчиков группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    group = get_object_or_404(Group, profile_id=group_id)

    followers = Group.objects.get(profile_id=group_id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'group': group,
        'title': 'Подписчики:',
        'followers': followers,
        'followers_count': followers_count,
    }

    return render(request, 'useradmin/admin_group_followers.html', data)


@login_required(login_url='/')
def admin_groups_post(request, group_id, pk_post):

    """Просмотр поста группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка удалить пост группы

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-group-delete':

            post_id = request.POST['post_id']
            post_delete = GroupPosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('admin_group_view', group_id)

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

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': f'Пост {pk_post}',
        'group': group,
        'post': post,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'useradmin/admin_group_page_post.html', data)


@login_required(login_url='/')
def admin_groups_photo(request, group_id):

    """Просмотр всех фото группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    group = get_object_or_404(Group, profile_id=group_id)
    photo_all = GroupPhoto.objects.filter(author=group).order_by('-date')
    photo_tot = photo_all.count()

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'group': group,
        'title': 'Фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'useradmin/admin_group_page_photo.html', data)


@login_required(login_url='/')
def admin_groups_photo_show(request, group_id, pk_photo):

    """Страница просмотра фото группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    group = get_object_or_404(Group, profile_id=group_id)
    photo_all = GroupPhoto.objects.filter(author=group_id)
    photo_count = len(photo_all)
    photo_single = get_object_or_404(GroupPhoto, id=pk_photo)

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

    # Правая часть фото - следующее фото

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'forward':

            if photo_all[len_photo_all - 1].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) + 1].id
                return redirect('admin_groups_photo_show', group_id=group_id, pk_photo=next_photo)

            else: return redirect('admin_groups_photo_show', group_id=group_id, pk_photo=photo_all[0].id)

    # Левая часть фото - предыдущее фото

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'back':

            if photo_all[0].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id
                return redirect('admin_groups_photo_show', group_id=group_id, pk_photo=next_photo)

            else: return redirect('admin_groups_photo_show', group_id=group_id, pk_photo=photo_all[len_photo_all - 1].id)

    # Удалить фотографию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'delete':

            photo_delete = GroupPhoto.objects.get(id=pk_photo)  # Получаем объект модели, который нужно удалить
            photo_delete.delete()

            if photo_all[0].id != pk_photo:
                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id

            elif photo_all.count() == 1: return redirect('admin_groups_photo', group_id)

            else: next_photo = photo_all[1].id

            return redirect('admin_groups_photo_show', group_id=group_id, pk_photo=next_photo)

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

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'group': group,
        'title': 'Фотографии сообщества:',
        'photo_line': photo_line,
        'photo_single': photo_single,
        'photo_count': photo_count,
        'all_comment': all_comment,
    }

    return render(request, 'useradmin/admin_group_page_photo_show.html', data)


@login_required(login_url='/')
def dialog_all(request):

    """Страница всех сообщений админа"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'

    all_dialogs = Dialog.objects.filter(user_list=Profile.objects.get(profile_id=1)).order_by('-last_message_time')

    for dialog in all_dialogs:
        if not Messages.objects.filter(dialog=dialog.id).exists():
            dialog_to_del = Dialog.objects.get(id=dialog.id)
            dialog_to_del.delete()

    all_dialogs = Dialog.objects.filter(user_list=Profile.objects.get(profile_id=1)).order_by('-last_message_time')

    for target_dialog in all_dialogs:

        target_dialog.another_user = \
            [profile for profile in target_dialog.user_list.all() if profile.profile_id != 1][0]

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Мои ообщения',
        'all_dialogs': all_dialogs
    }

    return render(request, 'useradmin/admin_all_dialogs.html', data)



@login_required(login_url='/')
def admin_dialog(request, dialog_id):

    """Страница диалог с админом"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    start_slice = -10

    if request.method == 'POST':

    # Кнопка написать сообщение

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_message':

            # Если в запросе текст или фото

            if request.POST['content'] or request.FILES:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog_id)
                message.author = Profile.objects.get(profile_id=1)
                message.content = request.POST['content']
                message.save()

                dialog = get_object_or_404(Dialog, id=dialog_id)

                if message.content == '' and request.FILES: dialog.last_message_text = 'Фото'
                else: dialog.last_message_text = str(request.POST['content'])[:50]

                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'

                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                # Если фото в запросе

                if 'photo_post' in request.FILES and request.FILES['photo_post']:

                    for send_photo in request.FILES.getlist('photo_post'):

                        photo = MessagePhoto()
                        photo.author = Profile.objects.get(profile_id=1)
                        photo.photo = send_photo
                        photo.save()
                        message.add_photo_in_post(photo)
                        message.save()

            return redirect('admin_dialog', dialog_id)

        # Кнопка удалить сообщение

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'message-delete':

            message_id = request.POST['message_id']
            message_id = int(message_id)

            # Если сообщение не последнее в спике

            if message_id != Messages.objects.latest('date').id:

                message_id = Messages.objects.get(id=message_id)
                message_id.delete()

            # Если сообщение последнее

            else:

                message_id = Messages.objects.get(id=message_id)
                message_id.delete()
                message = Messages.objects.latest('date')

                dialog = Dialog.objects.get(id=dialog_id)
                dialog.last_message_text = message.content[:50]
                dialog.last_message = message

                if dialog.last_message_text == ' ': dialog.last_message_text = 'Фото'
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'

                dialog.last_message_time = message.date
                dialog.save()

        # Пост - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_post':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_post':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

        # Репост - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_repost':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_repost':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

        # Репост группы - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_group_post':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_group_post':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

        # Репост группы - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_group_repost':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_group_repost':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

        # Обновить страницу при прокрутке вверх

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'add_message_list':

            start_slice = int(request.POST['slice']) - 5

    user = f'{request.user.first_name} {request.user.last_name}'
    posts_form = PostsForm
    comment_form = CommentPhotoForm

    for message in Messages.objects.filter(dialog=dialog_id):
        if message.author.profile_id != 1:
            message.read = True
            message.save()

    all_dialogs = Dialog.objects.filter(user_list=Profile.objects.get(profile_id=1)).order_by('-last_message_time')

    for target_dialog in all_dialogs:

        target_dialog.another_user = \
            [profile for profile in target_dialog.user_list.all() if profile.profile_id != 1][0]

    messages_all = list(Messages.objects.filter(dialog=dialog_id).order_by('date'))
    messages = list(messages_all)[start_slice:]

    another_user = Dialog.objects.get(id=dialog_id).user_list.exclude(profile_id=1).first()

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Диалог',
        'messages': messages,
        'posts_form': posts_form,
        'comment_form': comment_form,
        'start_slice': start_slice,
        'all_dialogs': all_dialogs,
        'another_user': another_user,
    }

    return render(request, 'useradmin/admin_single_dialog.html', data)


def create_notification(request):

    if request.method == 'POST':

        # Кнопка создать оповещение

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_post':

            if request.POST['content'] or request.FILES:

                new_post = Posts()
                new_post.author = Profile.objects.get(user=1)
                new_post.content = request.POST['content']
                new_post.save()

                if 'photo_post' in request.FILES and request.FILES['photo_post']:

                    for send_photo in request.FILES.getlist('photo_post'):
                        photo = Photo()
                        photo.author = Profile.objects.get(profile_id=1)
                        photo.photo = send_photo
                        photo.save()
                        new_post.add_photo_in_post(photo)
                        new_post.save()

            return redirect('create_notification')

        # Кнопка удалить пост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = Posts.objects.get(id=post_id)
            post_delete.delete()

        # Кнопка поставить / отменить лайк посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

        # Добавить комментарий к посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            need_post = request.POST['post_id']

            new_comment = PostsComment()
            new_comment.posts = Posts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=1)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('create_notification')

        # Кнопка удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    user = f'{request.user.first_name} {request.user.last_name}'
    posts_form = PostsForm
    comment_form = CommentPhotoForm
    post_and_repost = Posts.objects.filter(author=1).order_by('-date')

    for target_post in post_and_repost:

        target_post.comments = reversed(PostsComment.objects.filter(posts=target_post).order_by('-date')[:3])

    not_read_message = Dialog.objects.filter(user_list__profile_id=1).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != 1])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Оповещения',
        'posts_form': posts_form,
        'comment_form': comment_form,
        'post_and_repost': post_and_repost,
    }

    return render(request, 'useradmin/create_notification.html', data)
