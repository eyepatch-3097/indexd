from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from catalog.models import Item, List


def home(request):
    if request.user.is_authenticated:
        recent_items = Item.objects.filter(created_by=request.user).order_by("-created_at")[:5]
        user_lists = List.objects.filter(owner=request.user)

        return render(
            request,
            "core/home.html",
            {
                "recent_items": recent_items,
                "user_lists": user_lists,
            },
        )
    else:
        # logged-out landing (simple for now)
        return render(request, "core/landing.html")