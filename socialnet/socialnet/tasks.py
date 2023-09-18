from celery import shared_task
from django.core.mail import send_mail
import time


@shared_task
def send_registration_email(user_email, code):

    """Отправка сообщения по email с кодом подтверждения"""

    subject = 'Код подтверждения регистрации'
    message = f'Добро пожаловать в нашу социальную сеть!\nhttp://195.133.147.22/\nВаш код подтверждения: {code}'
    from_email = 'artsonik365@gmail.com'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_block_email(user_email):

    """Отправка сообщения по email - блокировка аккаунта"""

    time.sleep(10)  # эмуляция загруженности сервера

    subject = 'Ваш аккаунт заблокирован!'
    message = f'К сожалению Ваш аккаунт заблокирован...\nhttp://195.133.147.22/\n' \
              f'Свяжитесь с поддержкой для решения этой проблемы - artsonik365@gmail.com'
    from_email = 'artsonik365@gmail.com'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_unblock_email(user_email):

    """Отправка сообщения по email - разблокировка аккаунта"""

    time.sleep(10)  # эмуляция загруженности сервера

    subject = 'Ваш аккаунт разблокирован!'
    message = f'У нас хорошие новости - Ваш аккаунт разблокирован!\nhttp://195.133.147.22/\n'
    from_email = 'artsonik365@gmail.com'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
