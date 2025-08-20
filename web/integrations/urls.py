from django.urls import path
from . import views

app_name = "integrations"

urlpatterns = [
    path("", views.index, name="integrations_index"),
    path("manage/", views.manage, name="manage"),
    path("dropbox/connect/", views.dropbox_connect, name="dropbox_connect"),
    path("dropbox/callback/", views.dropbox_callback, name="dropbox_callback"),
    path("dropbox/disconnect/", views.dropbox_disconnect, name="dropbox_disconnect"),
    path("dropbox/me/", views.dropbox_me, name="dropbox_me"),
    # debug view removed
]
