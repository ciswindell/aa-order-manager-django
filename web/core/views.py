from django.shortcuts import render  # pylint: disable=import-error
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def dashboard(request):
    """Dashboard view - relies on context processor for integration status."""
    context = {
        "user": request.user,
        "is_staff": request.user.is_staff,
    }
    return render(request, "core/dashboard.html", context)
