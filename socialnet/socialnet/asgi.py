# """
# ASGI config for socialnet project.
#
# It exposes the ASGI callable as a module-level variable named ``application``.
#
# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# """
#
# import os
#
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialnet.settings')
#
# application = get_asgi_application()






# import os
#
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialnet.settings')
#
# django_asgi_app = get_asgi_application()
#
# application = ProtocolTypeRouter({
#     'http': django_asgi_app,
# })

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import usermessages.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialnet.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(usermessages.routing.websocket_urlpatterns)
    ),
})

