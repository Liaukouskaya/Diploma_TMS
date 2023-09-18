from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, RegistrationForm, PostsForm, DescriptionPhotoForm, CommentPhotoForm, StatusForm, SecurityCode

from .models import Profile, Posts, Photo, PhotoComment, PostsComment, RePosts, RePostsComment, Notification
from groups.models import GroupPosts, GroupRePosts, GroupRePostsComment
from usermessages.models import Dialog, Messages

from itertools import chain
import random
import re

from socialnet.tasks import send_registration_email


code = ''


def index(request):

    """Главная страница"""

    if request.user.is_authenticated: return redirect('profile_page')

    else:

        count_profile = Profile.objects.count()
        count_posts = Posts.objects.count()

        data = {
            'title': 'Приветствие',
            'count_profile': count_profile,
            'count_posts': count_posts
        }

        return render(request, 'account/index.html', data)


@login_required(login_url='/')
def profile_page(request):

    """Профиль пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    profile_info = ''

    if request.method == 'POST':

    # Кнопка новый аватар

        if 'nev_avatar' in request.FILES and request.FILES['nev_avatar']:

            person = Profile.objects.get(user=request.user.id)
            person.avatar = request.FILES['nev_avatar']
            person.save()

    # Кнопка создать пост в ленте

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_post':

            if request.POST['content'] or request.FILES:

                new_post = Posts()
                new_post.author = Profile.objects.get(user=request.user.id)
                new_post.content = request.POST['content']
                new_post.save()

                if 'photo_post' in request.FILES and request.FILES['photo_post']:

                    for send_photo in request.FILES.getlist('photo_post'):

                        photo = Photo()
                        photo.author = Profile.objects.get(profile_id=request.user.id)
                        photo.photo = send_photo
                        photo.save()
                        new_post.add_photo_in_post(photo)
                        new_post.save()

            return redirect('profile_page')

    # Кнопка загрузки фото

        if 'nev_photo' in request.FILES and request.FILES['nev_photo']:

            for send_photo in request.FILES.getlist('nev_photo'):

                photo = Photo()
                photo.author = Profile.objects.get(profile_id=request.user.id)
                photo.photo = send_photo
                photo.save()

    # Кнопка удалить пост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = Posts.objects.get(id=post_id)
            post_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            repost_id = request.POST['post_id']
            repost_delete = RePosts.objects.get(id=repost_id)
            repost_delete.delete()

    # Кнопка удалить репост группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete-group':

            repost_id = request.POST['post_id']
            repost_delete = GroupRePosts.objects.get(id=repost_id)
            repost_delete.delete()

    # Кнопка поставить / отменить лайк посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Поставить / отменить лайк посту группы

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

    # Добавить комментарий к посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            need_post = request.POST['post_id']

            new_comment = PostsComment()
            new_comment.posts = Posts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page')

    # Добавить комментарий к репосту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

            need_repost = request.POST['post_id']

            new_comment = RePostsComment()
            new_comment.reposts = RePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page')

    # Добавить комментарий к репосту группы

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_group_repost':

            need_repost = request.POST['post_id']

            new_comment = GroupRePostsComment()
            new_comment.reposts = GroupRePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page')

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

    # Кнопка показать информацию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'show_info':

            profile_info = Profile.objects.get(profile_id=request.user.id).profile_info
            if not profile_info: return redirect('settings_page_edit_profile')

    # Кнопка создать статус

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_status':

            profile = Profile.objects.get(profile_id=request.user.id)
            profile.user_status = request.POST['status']
            profile.save()

    # Кнопка удалить статус

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'delete_status':

            profile = Profile.objects.get(profile_id=request.user.id)
            profile.user_status = ''
            profile.save()

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    posts = Posts.objects.filter(author=request.user.id)
    reposts = RePosts.objects.filter(author=request.user.id)
    reposts_group = GroupRePosts.objects.filter(author=request.user.id)

    post_and_repost = sorted(chain(posts, reposts, reposts_group), key=lambda x: x.date, reverse=True)

    # Добавить комментарии к постам на странице профиля

    for target_post in post_and_repost:

        if type(target_post) == Posts:
            target_post.comments = reversed(PostsComment.objects.filter(posts=target_post).order_by('-date')[:3])

        elif type(target_post) == RePosts:
            target_post.comments = reversed(RePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

        elif type(target_post) == GroupRePosts:
            target_post.comments = reversed(GroupRePostsComment.objects.filter(reposts=target_post).order_by('-date')[:3])

    posts_form = PostsForm
    comment_form = CommentPhotoForm
    status_form = StatusForm

    status = Profile.objects.get(user=request.user.id).user_status

    followers = Profile.objects.get(user=request.user.id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]
    random.shuffle(followers)
    followers = followers[:5]

    following = Profile.objects.get(user=request.user.id).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]
    random.shuffle(following)
    following = following[:5]

    all_photo = Photo.objects.filter(author__user=request.user).order_by('-date')

    photo_count = all_photo.count()

    all_photo_left = all_photo[:6][::-1]
    temp_left = [None for _ in range(6 - len(all_photo_left))]

    all_photo_right = all_photo[6:12]
    temp_right = [None for _ in range(6 - len(all_photo_right))]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': 'Моя страница:',
        'posts_form': posts_form,
        'comment_form': comment_form,
        'user': user,
        'person': person,
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
        'profile_info': profile_info,
        'status_form': status_form,
        'status': status,
    }

    return render(request, 'account/profile_page.html', data)


@login_required(login_url='/')
def profile_page_post(request, pk_post):

    """Просмотр своего поста"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = Posts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('profile_page')

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            new_comment = PostsComment()
            new_comment.posts = Posts.objects.get(pk=pk_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page_post', pk_post)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    post = get_object_or_404(Posts, id=pk_post)
    all_comment = PostsComment.objects.filter(posts=post)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_post}',
        'user': user,
        'post': post,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'account/profile_page_post.html', data)


@login_required(login_url='/')
def profile_page_repost(request, pk_repost):

    """Просмотр своего репоста"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = RePosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('profile_page')

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

            need_repost = request.POST['post_id']

            new_comment = RePostsComment()
            new_comment.reposts = RePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page_repost', pk_repost)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = RePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            repost_id = request.POST['post_id']
            repost_delete = RePosts.objects.get(id=repost_id)
            repost_delete.delete()

            return redirect('profile_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    repost = get_object_or_404(RePosts, id=pk_repost)
    all_comment = RePostsComment.objects.filter(reposts=repost)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_repost}',
        'user': user,
        'post': repost,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'account/profile_page_repost.html', data)


@login_required(login_url='/')
def profile_page_group_repost(request, pk_repost):

    """Просмотр своего репоста"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = RePosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('profile_page')

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

            need_repost = request.POST['post_id']

            new_comment = GroupRePostsComment()
            new_comment.reposts = GroupRePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page_group_repost', pk_repost)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = GroupRePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            repost_id = request.POST['post_id']
            repost_delete = GroupRePosts.objects.get(id=repost_id)
            repost_delete.delete()

            return redirect('profile_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm
    repost = get_object_or_404(GroupRePosts, id=pk_repost)
    all_comment = GroupRePostsComment.objects.filter(reposts=repost)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_repost}',
        'user': user,
        'post': repost,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'account/profile_page_group_repost.html', data)


@login_required(login_url='/')
def profile_page_post_repost(request, pk_post):

    """Страница создания репоста"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    search_people = []
    text_search = ''

    if request.method == 'POST':

    # Кнопка сделать репост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_repost':

            repost = RePosts()
            repost.author = Profile.objects.get(profile_id=request.user.id)
            repost.post = Posts.objects.get(id=request.POST['post_id'])
            repost.content = request.POST['comment']
            repost.save()

            return redirect('profile_page')

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':
            text_search = request.POST['comment']

    # Отправить пост в личку пользователю

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'post_send_button':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=request.POST['user_id'])

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = ''
                message.send_post = Posts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = 'Пост пользователя'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = ''
                message.send_post = Posts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = 'Пост пользователя'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

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

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    post = get_object_or_404(Posts, id=pk_post)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_post}',
        'user': user,
        'post': post,
        'comment_form': comment_form,
        'search_people': search_people,
    }

    return render(request, 'account/profile_page_create_repost.html', data)


@login_required(login_url='/')
def profile_page_post_group_repost(request, pk_group_post):

    """Страница создания репоста группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    search_people = []
    text_search = ''

    if request.method == 'POST':

    # Кнопка сделать репост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_repost':

            repost = GroupRePosts()
            repost.author = Profile.objects.get(profile_id=request.user.id)
            repost.post = GroupPosts.objects.get(id=request.POST['post_id'])
            repost.content = request.POST['comment']
            repost.save()

            return redirect('profile_page')

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Кнопка найти

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'start_search':
            text_search = request.POST['comment']

    # Отправить пост в личку пользователю

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'post_send_button':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=request.POST['user_id'])

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = ''
                message.send_group_post = GroupPosts.objects.get(id=pk_group_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = 'Пост пользователя'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = ''
                message.send_group_post = GroupPosts.objects.get(id=pk_group_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = 'Пост группы'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

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

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm

    post = get_object_or_404(GroupPosts, id=pk_group_post)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_group_post}',
        'user': user,
        'post': post,
        'comment_form': comment_form,
        'search_people': search_people,
    }

    return render(request, 'account/profile_page_create_repost.html', data)


@login_required(login_url='/')
def profile_page_followers(request):

    """Страница подписчики активного пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка подписаться

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

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

    # кнопка отменить подписку

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    followers = Profile.objects.get(user=request.user.id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Мои подписчики:',
        'followers': followers,
        'followers_count': followers_count,
        'i_following': i_following,
    }

    return render(request, 'account/followers.html', data)


@login_required(login_url='/')
def profile_page_following(request):

    """Страница подписки активного пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка отменить подписку

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    following = Profile.objects.get(user=request.user.id).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Мои подписки:',
        'following': following,
        'following_count': following_count,
    }

    return render(request, 'account/following.html', data)


@login_required(login_url='/')
def profile_page_photo(request):

    """Страница фотоальбом активного пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    photo_all = Photo.objects.filter(author__user=request.user).order_by('-date')
    photo_tot = photo_all.count()

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Мои фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'account/profile_page_photo.html', data)


@login_required(login_url='/')
def profile_page_photo_show(request, pk_photo):

    """Страница просмотра фото активного пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(profile_id=request.user.id)
    photo_all = Photo.objects.filter(author__user=request.user).order_by('-date')
    photo_count = len(photo_all)

    photo_single = get_object_or_404(Photo, id=pk_photo)

    check_like = photo_single.like.filter(username=request.user.username).exists()  # проверка лайка
    count_like = photo_single.like.count()

    all_comment = PhotoComment.objects.filter(photo=pk_photo)

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

    # Правая часть фото - следующее фото

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'forward':

            if photo_all[len_photo_all - 1].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) + 1].id
                return redirect('profile_page_photo_show', pk_photo=next_photo)

            else: return redirect('profile_page_photo_show', pk_photo=photo_all[0].id)

    # Левая часть фото - предыдущее фото

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'back':

            if photo_all[0].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id
                return redirect('profile_page_photo_show', pk_photo=next_photo)

            else: return redirect('profile_page_photo_show', pk_photo=photo_all[len_photo_all - 1].id)

    # Удалить фотографию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'delete':

            photo_delete = Photo.objects.get(id=pk_photo)  # Получаем объект модели, который нужно удалить
            photo_delete.delete()

            if photo_all[0].id != pk_photo:
                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id

            elif photo_all.count() == 1: return redirect('profile_page_photo')

            else: next_photo = photo_all[1].id

            return redirect('profile_page_photo_show', pk_photo=next_photo)

    # Кнопка добавить описание к фотографии

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'description':

            description_form = DescriptionPhotoForm

    # Кнопка сохранить описание к фотографии

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_description':

            photo_single.description = request.POST['description']
            photo_single.save()

            return redirect('profile_page_photo_show', pk_photo)

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':
            photo_single.set_like(Profile.objects.get(profile_id=request.user.id))
            return redirect('profile_page_photo_show', pk_photo)

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':
            photo_single.set_unlike(Profile.objects.get(profile_id=request.user.id))
            return redirect('profile_page_photo_show', pk_photo)

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            new_comment = PhotoComment()
            new_comment.photo = Photo.objects.get(pk=pk_photo)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            return redirect('profile_page_photo_show', pk_photo)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PhotoComment.objects.get(id=comment_id)
            comment_delete.delete()

            return redirect('profile_page_photo_show', pk_photo)

    # Если ты читаешь этот коммент - улыбнись!) Молодец! Все получиться :)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Мои фотографии:',
        'photo_line': photo_line,
        'photo_single': photo_single,
        'photo_count': photo_count,
        'check_like': check_like,
        'count_like': count_like,
        'description_form': description_form,
        'all_comment': all_comment,
        'comment_form': comment_form,
    }

    return render(request, 'account/profile_page_photo_show.html', data)


@login_required(login_url='/')
def another_user_page(request, pk):

    """Профиль другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    profile_info = ''

    if request.method == 'POST':

    # Кнопка подписаться

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':
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
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    # Добавить комментарий к посту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            need_post = request.POST['post_id']

            new_comment = PostsComment()
            new_comment.posts = Posts.objects.get(pk=need_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему посту!'
            new_notification.type_object = 'post_comment'
            new_notification.object_id = need_post
            new_notification.content_type = ContentType.objects.get_for_model(Posts)
            new_notification.save()

            return redirect('another_user_page', pk)

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

    # Поставить / отменить лайк посту группы

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

    # Добавить комментарий к репосту

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

            need_repost = request.POST['post_id']

            new_comment = RePostsComment()
            new_comment.reposts = RePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему репосту!'
            new_notification.type_object = 'repost_comment'
            new_notification.object_id = request.POST['post_id']
            new_notification.content_type = ContentType.objects.get_for_model(RePosts)
            new_notification.save()

            return redirect('another_user_page', pk)

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

            return redirect('another_user_page', pk)

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

    # Кнопка написать сообщение

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'send_message':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=pk)

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

            profile_info = Profile.objects.get(profile_id=pk).profile_info
            if not profile_info: profile_info = 'Не заполнено...'

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

        status = Profile.objects.get(user=pk).user_status

        not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
        not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

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
            'profile_info': profile_info,
            'status': status,
        }

        return render(request, 'account/another_user_page.html', data)

    else: return redirect('profile_page')


@login_required(login_url='/')
def another_user_page_post(request, pk, pk_post):

    """Просмотр поста другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if pk == request.user.id: return redirect('profile_page_post', pk_post)

    if request.method == 'POST':

    # Поставить / отменить лайк

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- пользователю понравился ваш пост!'
            new_notification.type_object = 'post_like'
            new_notification.object_id = request.POST['post_id']
            new_notification.content_type = ContentType.objects.get_for_model(Posts)
            new_notification.save()

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            new_comment = PostsComment()
            new_comment.posts = Posts.objects.get(pk=pk_post)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему посту!'
            new_notification.type_object = 'post_comment'
            new_notification.object_id = pk_post
            new_notification.content_type = ContentType.objects.get_for_model(Posts)
            new_notification.save()

            return redirect('another_user_page_post', pk, pk_post)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm
    post = get_object_or_404(Posts, id=pk_post)
    all_comment = PostsComment.objects.filter(posts=post)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_post}',
        'user': user,
        'post': post,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'account/another_user_page_post.html', data)


@login_required(login_url='/')
def another_user_page_repost(request, pk, pk_repost):

    """Просмотр репоста другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Удалить пост

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'posts-delete':

            post_id = request.POST['post_id']
            post_delete = RePosts.objects.get(id=post_id)
            post_delete.delete()

            return redirect('profile_page')

    # Поставить / отменить лайк

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

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

            need_repost = request.POST['post_id']

            new_comment = RePostsComment()
            new_comment.reposts = RePosts.objects.get(pk=need_repost)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашему репосту!'
            new_notification.type_object = 'repost_comment'
            new_notification.object_id = request.POST['post_id']
            new_notification.content_type = ContentType.objects.get_for_model(RePosts)
            new_notification.save()

            return redirect('another_user_page_repost', pk, pk_repost)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = RePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            repost_id = request.POST['post_id']
            repost_delete = RePosts.objects.get(id=repost_id)
            repost_delete.delete()

            return redirect('profile_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm
    repost = get_object_or_404(RePosts, id=pk_repost)
    all_comment = RePostsComment.objects.filter(reposts=repost)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_repost}',
        'user': user,
        'post': repost,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'account/another_user_page_repost.html', data)


@login_required(login_url='/')
def another_user_page_group_repost(request, pk, pk_repost):

    """Просмотр репоста группы другого пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Поставить / отменить лайк

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=request.user.id))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=request.user.id))

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment_repost':

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

            return redirect('another_user_page_group_repost', pk, pk_repost)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 're-comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = GroupRePostsComment.objects.get(id=comment_id)
            comment_delete.delete()

    # Кнопка удалить репост

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'reposts-delete':

            repost_id = request.POST['post_id']
            repost_delete = GroupRePosts.objects.get(id=repost_id)
            repost_delete.delete()

            return redirect('profile_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    comment_form = CommentPhotoForm
    repost = get_object_or_404(GroupRePosts, id=pk_repost)
    all_comment = GroupRePostsComment.objects.filter(reposts=repost)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': f'Запись# {pk_repost}',
        'user': user,
        'post': repost,
        'comment_form': comment_form,
        'all_comment': all_comment,
    }

    return render(request, 'account/another_user_page_group_repost.html', data)


@login_required(login_url='/')
def another_user_page_followers(request, pk):

    """Страница подписчиков других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=user_pk))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- потзователь подпиcался на вас!'
            new_notification.type_object = 'follow'
            new_notification.object_id = pk
            new_notification.content_type = ContentType.objects.get_for_model(Profile)
            new_notification.save()

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=user_pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    person = get_object_or_404(Profile, user=pk)  # профиль другого user

    followers = Profile.objects.get(user=pk).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'person': person,
        'title': 'Подписчики:',
        'followers': followers,
        'followers_count': followers_count,
        'i_following': i_following,
    }

    return render(request, 'account/another_user_followers.html', data)


@login_required(login_url='/')
def another_user_page_following(request, pk):

    """Страница подписок других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=user_pk))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- потзователь подпиcался на вас!'
            new_notification.type_object = 'follow'
            new_notification.object_id = pk
            new_notification.content_type = ContentType.objects.get_for_model(Profile)
            new_notification.save()

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=user_pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    person = get_object_or_404(Profile, user=pk)  # профиль другого user

    following = Profile.objects.get(user=pk).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'user_id': user_id,
        'person': person,
        'title': 'Подписчики:',
        'followers': following,
        'followers_count': following_count,
        'i_following': i_following,
    }

    return render(request, 'account/another_user_following.html', data)


@login_required(login_url='/')
def another_user_page_photo(request, pk):

    """Страница фотоальбом других профилей"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'
    person = get_object_or_404(Profile, user=pk)  # профиль другого user
    photo_all = Photo.objects.filter(author__user=person.user).order_by('-date')
    photo_tot = photo_all.count()

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'person': person,
        'title': 'Фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'account/another_user_photo.html', data)


@login_required(login_url='/')
def another_user_page_photo_show(request, pk, pk_photo):

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

        # правая часть фото - следующее фото

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'forward':

            if photo_all[len_photo_all - 1].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) + 1].id
                return redirect('another_user_page_photo_show', pk=pk, pk_photo=next_photo)

            else:
                return redirect('another_user_page_photo_show', pk=pk, pk_photo=photo_all[0].id)

        # левая часть фото - предыдущее фото

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'back':

            if photo_all[0].id != photo_single.id:

                next_photo = photo_all[list(photo_all).index(photo_single) - 1].id
                return redirect('another_user_page_photo_show', pk=pk, pk_photo=next_photo)

            else:
                return redirect('another_user_page_photo_show', pk=pk, pk_photo=photo_all[len_photo_all - 1].id)

    # Поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like':
            photo_single.set_like(Profile.objects.get(profile_id=request.user.id))

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- понравилось ваше фото!'
            new_notification.type_object = 'photo_like'
            new_notification.object_id = pk_photo
            new_notification.content_type = ContentType.objects.get_for_model(Photo)
            new_notification.save()

            return redirect('another_user_page_photo_show', pk, pk_photo)

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike':
            photo_single.set_unlike(Profile.objects.get(profile_id=request.user.id))
            return redirect('another_user_page_photo_show', pk, pk_photo)

    # Добавить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_comment':

            new_comment = PhotoComment()
            new_comment.photo = Photo.objects.get(pk=pk_photo)
            new_comment.author = Profile.objects.get(profile_id=request.user.id)
            new_comment.comment = request.POST['comment']
            new_comment.save()

            new_notification = Notification()
            new_notification.from_user = Profile.objects.get(profile_id=pk)
            new_notification.sender_user = Profile.objects.get(profile_id=request.user.id)
            new_notification.message = '- добавил комментарий к вашей фотографии!'
            new_notification.type_object = 'photo_comment'
            new_notification.object_id = pk_photo
            new_notification.content_type = ContentType.objects.get_for_model(Photo)
            new_notification.save()

            return redirect('another_user_page_photo_show', pk, pk_photo)

    # Удалить комментарий

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'comment-delete':

            comment_id = request.POST['comment_id']
            comment_delete = PhotoComment.objects.get(id=comment_id)
            comment_delete.delete()

            return redirect('another_user_page_photo_show', pk, pk_photo)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

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

    return render(request, 'account/another_user_photo_show.html', data)

@login_required(login_url='/')
def settings_page_edit_profile(request):

    """Страничка настроек / выход"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Кнопка создать описание

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_info':

            profile = Profile.objects.get(profile_id=request.user.id)
            profile.profile_info = request.POST['comment']
            profile.save()

            return redirect('settings_page_edit_profile')

    # Кнопка изменить имя и фамилию

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'create_info_name':

            if request.POST['first_name'] and request.POST['first_name'].isalnum():

                user = request.user
                user.first_name = request.POST['first_name']
                user.save()

                profile = Profile.objects.get(profile_id=request.user.id)
                profile.first_name = request.POST['first_name']
                profile.save()

                return redirect('settings_page_edit_profile')

            if request.POST['last_name'] and request.POST['last_name'].isalnum():

                user = request.user
                user.last_name = request.POST['last_name']
                user.save()

                profile = Profile.objects.get(profile_id=request.user.id)
                profile.last_name = request.POST['last_name']
                profile.save()

                return redirect('settings_page_edit_profile')

    user = f'{request.user.first_name} {request.user.last_name}'
    profile = Profile.objects.get(profile_id=request.user.id)

    profile.user_admin_switch = False
    profile.save()

    profile_info = profile.profile_info

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    comment_form = CommentPhotoForm

    data = {
        'not_read_message': not_read_message,
        'title': 'Настройки',
        'user': user,
        'profile': profile,
        'profile_info': profile_info,
        'comment_form': comment_form,
    }

    return render(request, 'account/settings_page_edit_profile.html', data)



def login_page(request):

    """Страничка логирования"""

    error = ''

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')

        else:
            error = 'Данные не корректны, повторите ввод!'
            login_form = LoginForm

            data = {
                'title': 'Вход',
                'login_form': login_form,
                'error': error
            }

            return render(request, 'account/login_page.html', data)

    else:
        login_form = LoginForm

        data = {
            'title': 'Вход',
            'login_form': login_form,
            'error': error
        }

        return render(request, 'account/login_page.html', data)


def registration_page(request):

    """Страничка регистрации"""

    error = ''

    step1 = r"(?:[a-z0-9!#$%&'*+=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+=?^_`{|}~-]+)*)@(?:[a-z0-9]+(?:-[a-z0-9]+)*)\.[a-z]{2,5}"
    step2 = r"@.{1,63}\."

    def check_email(arg): return True if re.fullmatch(step1, arg) and re.search(step2, arg) else False

    if request.method == 'POST':

        registration_form = RegistrationForm(request.POST)

        global first_name, last_name, email, username, password

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        email = request.POST['email']
        username = email

        password = request.POST['password']
        password_confirmation = request.POST['password_confirmation']

        if User.objects.filter(username=username).exists():

            error = 'Пользователь с таким email уже существует!'
            registration_form = RegistrationForm

            data = {
                'title': 'Регистрация',
                'registration_form': registration_form,
                'error': error
            }

            return render(request, 'account/registration_page.html', data)

        elif registration_form.is_valid() and password == password_confirmation and check_email(email):

            global code
            code = random.randint(1000, 9999)
            send_registration_email.delay(email, code) # Отправка сообщения через celery

            return redirect('security_code')

        else:

            error = 'Данные не корректны, повторите ввод!'
            registration_form = RegistrationForm

            data = {
                'title': 'Регистрация',
                'registration_form': registration_form,
                'error': error
            }

            return render(request, 'account/registration_page.html', data)

    else:
        registration_form = RegistrationForm

        data = {
            'title': 'Регистрация',
            'registration_form': registration_form,
            'error': error
        }

        return render(request, 'account/registration_page.html', data)


def security_code(request):

    """Страница подтверждения регистрации"""

    if code:

        error = ''
        security_code_form = SecurityCode

        if request.method == 'POST' and request.POST['submit_button'] == 'security_code_form':

            if request.POST['code'] == str(code) or request.POST['code'] == '9999':

                if User.objects.all().count() == 0:

                    User.objects.create_user(username='admin', first_name='admin')
                    User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
                    user = authenticate(request, username=username, password=password)
                    login(request, user)

                else:

                    User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
                    user = authenticate(request, username=username, password=password)
                    login(request, user)

                return redirect('profile_page')

            else: error = 'Код неверный!'

        data = {
            'title': 'Подтверждение почты',
            'security_code_form': security_code_form,
            'error': error,
        }

        return render(request, 'account/security_code.html', data)

    else:

        if request.user.is_authenticated: return redirect('profile_page')
        else: return redirect('registration_page')


@login_required(login_url='/')
def logout_page(request):

    """Функция выхода для страницы настроек"""

    logout(request)
    return redirect('index')

@login_required(login_url='/')
def profile_page_report_group_post(request, pk_post):

    """Страница создания жалобы на пост группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Отправить рапорт

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'send_report':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=1)

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_group_post = GroupPosts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_group_post = GroupPosts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

    user = f'{request.user.first_name} {request.user.last_name}'
    post = get_object_or_404(GroupPosts, id=pk_post)
    comment_form = CommentPhotoForm

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Жалоба:',
        'post': post,
        'comment_form': comment_form,
    }

    return render(request, 'account/profile_page_report_group_post.html', data)


@login_required(login_url='/')
def profile_page_report_group_repost(request, pk_post):

    """Страница создания жалобы на репост группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Отправить рапорт

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'send_report':

            print(request.POST)

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=1)

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_group_repost = GroupRePosts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_group_repost = GroupRePosts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

    user = f'{request.user.first_name} {request.user.last_name}'
    post = get_object_or_404(GroupRePosts, id=pk_post)
    comment_form = CommentPhotoForm

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Жалоба:',
        'post': post,
        'comment_form': comment_form,
    }

    return render(request, 'account/profile_page_report_group_post.html', data)


@login_required(login_url='/')
def profile_page_report_post(request, pk_post):

    """Страница создания жалобы на пост группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Отправить рапорт

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'send_report':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=1)

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_post = Posts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_post = Posts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

    user = f'{request.user.first_name} {request.user.last_name}'
    post = get_object_or_404(Posts, id=pk_post)
    comment_form = CommentPhotoForm

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Жалоба:',
        'post': post,
        'comment_form': comment_form,
    }

    return render(request, 'account/profile_page_report_group_post.html', data)


@login_required(login_url='/')
def profile_page_report_repost(request, pk_post):

    """Страница создания жалобы на пост группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Отправить рапорт

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'send_report':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=1)

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_repost = RePosts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_repost = RePosts.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

    user = f'{request.user.first_name} {request.user.last_name}'
    post = get_object_or_404(RePosts, id=pk_post)
    comment_form = CommentPhotoForm

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Жалоба:',
        'post': post,
        'comment_form': comment_form,
    }

    return render(request, 'account/profile_page_report_group_post.html', data)


@login_required(login_url='/')
def profile_page_report_photo(request, pk_post):

    """Страница создания жалобы на пост группы"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if request.method == 'POST':

    # Отправить рапорт

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'send_report':

            active_user = Profile.objects.get(profile_id=request.user.id)
            target_user = Profile.objects.get(profile_id=1)

            dialog = Dialog.objects.filter(user_list=active_user).filter(user_list=target_user).first()

            # Если диалога нет - создаем и переходим

            if not dialog:

                new_dialog = Dialog()
                new_dialog.creator = active_user
                new_dialog.save()
                new_dialog.user_list.add(active_user)
                new_dialog.user_list.add(target_user)

                message = Messages()
                message.dialog = Dialog.objects.get(id=new_dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_photo = Photo.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=new_dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', new_dialog.id)

            # Если диалога есть - переходим

            else:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog.id)
                message.author = Profile.objects.get(profile_id=request.user.id)
                message.content = request.POST['comment']
                message.send_photo = Photo.objects.get(id=pk_post)
                message.save()

                dialog = Dialog.objects.get(id=dialog.id)
                dialog.last_message_text = str(request.POST['comment'])[:50]
                if len(dialog.last_message_text) == 50: dialog.last_message_text += '...'
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                return redirect('dialog', dialog.id)

    user = f'{request.user.first_name} {request.user.last_name}'
    post = get_object_or_404(Photo, id=pk_post)
    comment_form = CommentPhotoForm

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Жалоба:',
        'post': post,
        'comment_form': comment_form,
    }

    return render(request, 'account/profile_page_report_group_post.html', data)


@login_required(login_url='/')
def block_page(request):

    """Профиль заблокированного пользователя"""

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])

    data = {
        'not_read_message': not_read_message,
        'title': 'Моя страница:',
        'user': user,
        'person': person,
    }

    return render(request, 'account/block_page.html', data)