from django.urls import re_path
from . import consumers # This looks for consumers.py in the same folder

websocket_urlpatterns = [
    # The 'as_asgi()' is crucial!
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]