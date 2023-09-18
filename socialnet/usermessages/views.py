from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required

from .models import Dialog, Messages, MessagePhoto
from account.models import Profile, Posts, Notification
from groups.models import GroupPosts

from account.forms import PostsForm, CommentPhotoForm

from django.http import JsonResponse


@login_required(login_url='/')
def all_messages(request):

    """Страница всех сообщений пользователя"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    user = f'{request.user.first_name} {request.user.last_name}'

    if not Profile.objects.get(profile_id=request.user.id).user_admin_switch:

        user_or_admin = request.user.id

    else:
        user_or_admin = 1
        user = 'ADMIN'

    all_dialogs = Dialog.objects.filter(user_list=Profile.objects.get(profile_id=user_or_admin)).order_by('-last_message_time')

    for dialog in all_dialogs:
        if not Messages.objects.filter(dialog=dialog.id).exists():
            dialog_to_del = Dialog.objects.get(id=dialog.id)
            dialog_to_del.delete()

    all_dialogs = Dialog.objects.filter(user_list=Profile.objects.get(profile_id=user_or_admin)).order_by('-last_message_time')

    for target_dialog in all_dialogs:

        target_dialog.another_user = \
            [profile for profile in target_dialog.user_list.all() if profile.profile_id != user_or_admin][0]

    not_read_message = Dialog.objects.filter(user_list__profile_id=user_or_admin).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != user_or_admin])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Мои cобщения',
        'all_dialogs': all_dialogs,
        'user_or_admin': user_or_admin,
    }

    if user_or_admin != 1:

        return render(request, 'usermessages/all_dialogs.html', data)

    else:

        return render(request, 'usermessages/all_dialogs_admin.html', data)


@login_required(login_url='/')
def dialog(request, dialog_id):

    """Страница диалог с другим пользователем"""

    if Profile.objects.get(user=request.user.id).block: return redirect('block_page')

    if Profile.objects.get(profile_id=request.user.id) not in get_object_or_404(Dialog, id=dialog_id).user_list.all()\
            and not Profile.objects.get(profile_id=request.user.id).user_admin\
            and Profile.objects.get(profile_id=1) in get_object_or_404(Dialog, id=dialog_id).user_list.all():

        return redirect('all_messages')

    start_slice = -10
    user = f'{request.user.first_name} {request.user.last_name}'

    if not Profile.objects.get(profile_id=request.user.id).user_admin_switch:

        user_or_admin = request.user.id

    else:
        user_or_admin = 1
        user = 'ADMIN'

    if request.method == 'POST':

    # Кнопка написать сообщение

        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_message':

        # Если в запросе текст или фото

            if request.POST['content'] or request.FILES:

                message = Messages()
                message.dialog = Dialog.objects.get(id=dialog_id)
                message.author = Profile.objects.get(profile_id=user_or_admin)
                message.content = request.POST['content']
                message.save()

                dialog = get_object_or_404(Dialog, id=dialog_id)
                dialog.last_message_time = message.date
                dialog.last_message = message
                dialog.save()

                # Если фото в запросе

                if 'photo_post' in request.FILES and request.FILES['photo_post']:

                    for send_photo in request.FILES.getlist('photo_post'):

                        photo = MessagePhoto()
                        photo.author = Profile.objects.get(profile_id=user_or_admin)
                        photo.photo = send_photo
                        photo.save()
                        message.add_photo_in_post(photo)
                        message.save()

            return redirect('dialog', dialog_id)

    # Кнопка удалить сообщение

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'message-delete':

            message_id = request.POST['message_id']
            message_id = int(message_id)

            # Если сообщение не последнее в спике

            if message_id != Messages.objects.filter(dialog=dialog_id).last().id:

                message_id = Messages.objects.get(id=message_id)
                message_id.delete()

            # Если сообщение последнее

            else:

                message_id = Messages.objects.get(id=message_id)
                message_id.delete()

                if Messages.objects.filter(dialog=dialog_id).exists():

                    message = Messages.objects.filter(dialog=dialog_id).last()
                    dialog = Dialog.objects.get(id=dialog_id)
                    dialog.last_message = message
                    dialog.last_message_time = message.date
                    dialog.save()

                else:

                    dialog = get_object_or_404(Dialog, id=dialog_id)
                    dialog.delete()
                    return redirect('all_messages')

    # Пост - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_post':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=user_or_admin))

            if user_or_admin != need_post.author.profile_id:

                new_notification = Notification()
                new_notification.from_user = Profile.objects.get(profile_id=need_post.author.profile_id)
                new_notification.sender_user = Profile.objects.get(profile_id=user_or_admin)
                new_notification.message = '- пользователю понравился ваш пост!'
                new_notification.type_object = 'post_like'
                new_notification.object_id = request.POST['post_id']
                new_notification.content_type = ContentType.objects.get_for_model(Posts)
                new_notification.save()

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_post':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=user_or_admin))

    # Репост - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_repost':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=user_or_admin))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_repost':

            need_post = Posts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=user_or_admin))

    # Репост группы - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_group_post':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=user_or_admin))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_group_post':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=user_or_admin))

    # Репост группы - Кнопка поставить / отменить лайк

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_like_group_repost':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_like_post(Profile.objects.get(profile_id=user_or_admin))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'set_unlike_group_repost':

            need_post = GroupPosts.objects.get(id=request.POST['post_id'])
            need_post.set_unlike_post(Profile.objects.get(profile_id=user_or_admin))

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'dialog-delete':

            need_dialog = Dialog.objects.get(id=dialog_id)
            need_dialog.delete()
            return redirect('all_messages')

    # Обновить страницу при прокрутке вверх

        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'add_message_list':

            start_slice = int(request.POST['slice']) - 5

    posts_form = PostsForm
    comment_form = CommentPhotoForm

    another_user = get_object_or_404(Dialog, id=dialog_id).user_list.exclude(profile_id=user_or_admin).first()

    for message in Messages.objects.filter(dialog=dialog_id):
        if message.author.profile_id != user_or_admin:
            message.read = True
            message.save()

    messages_all = list(Messages.objects.filter(dialog=dialog_id).order_by('date'))
    messages = list(messages_all)[start_slice:]

    all_dialogs = Dialog.objects.filter(user_list=Profile.objects.get(profile_id=user_or_admin)).order_by('-last_message_time')

    for target_dialog in all_dialogs:

        target_dialog.another_user = \
            [profile for profile in target_dialog.user_list.all() if profile.profile_id != user_or_admin][0]

    dialog = get_object_or_404(Dialog, id=dialog_id)

    not_read_message = Dialog.objects.filter(user_list__profile_id=user_or_admin).filter(last_message__read=False)
    not_read_message = sum([1 for x in not_read_message if x.last_message.author.profile_id != user_or_admin])

    data = {
        'not_read_message': not_read_message,
        'user': user,
        'title': 'Диалог',
        'messages': messages,
        'posts_form': posts_form,
        'comment_form': comment_form,
        'start_slice': start_slice,
        'another_user': another_user,
        'all_dialogs': all_dialogs,
        'dialog': dialog,
    }

    if user_or_admin != 1:

        return render(request, 'usermessages/dialog.html', data)

    else:

        return render(request, 'useradmin/admin_single_dialog.html', data)


@login_required
def unread_messages(request):

    not_read_message = Dialog.objects.filter(user_list__profile_id=request.user.id).filter(last_message__read=False)
    unread_count = sum([1 for x in not_read_message if x.last_message.author.profile_id != request.user.id])
    return JsonResponse({'unread_count': unread_count})
