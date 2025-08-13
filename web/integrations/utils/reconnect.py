from django.contrib import messages


def prompt_dropbox_reconnect(request) -> None:
    messages.warning(request, "Dropbox connection failed. Please reconnect.")
