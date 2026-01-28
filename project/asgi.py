# """
# ASGI config for project project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# application = get_asgi_application()

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# Note the path: app_name.folder_name.file_name
from app.websocketLogic.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})