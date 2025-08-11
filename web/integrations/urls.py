from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="integrations_index"),
    path("dropbox/connect/", views.dropbox_connect, name="dropbox_connect"),
    path("dropbox/callback/", views.dropbox_callback, name="dropbox_callback"),
    path("dropbox/disconnect/", views.dropbox_disconnect, name="dropbox_disconnect"),
    path("dropbox/me/", views.dropbox_me, name="dropbox_me"),
    path("dropbox/list/", views.dropbox_list, name="dropbox_list"),
]
