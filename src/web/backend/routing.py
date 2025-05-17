from django.urls import re_path 
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/socket-server/?$', consumers.TaskConsumer.as_asgi()),
    re_path(r'^ws/?$', consumers.StewartPlatformConsumer.as_asgi()),
]