from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import models
from .forms import ItemCreateForm
from .models import Item, List, ListItem
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from .services import tmdb, openlibrary




@login_required
def add_item(request):
    if request.method == "POST":
        form = ItemCreateForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            chosen_list = form.cleaned_data.get("list")
            new_list_title = form.cleaned_data.get("new_list_title")

            # Determine which list to use, if any
            list_obj = None
            if new_list_title:
                list_obj = List.objects.create(
                    owner=request.user,
                    title=new_list_title,
                    is_public=form.cleaned_data.get("new_list_is_public", True),
                )
            elif chosen_list:
                list_obj = chosen_list

            # If we have a list, link the item to it
            if list_obj:
                # position: next available integer
                max_pos = (
                    list_obj.list_items.aggregate(models.Max("position"))["position__max"]
                    or 0
                )
                ListItem.objects.create(
                    list=list_obj,
                    item=item,
                    position=max_pos + 1,
                )

            # Redirect:
            if list_obj:
                return redirect("catalog:list_detail", slug=list_obj.slug)
            return redirect("core:home")
    else:
        form = ItemCreateForm(user=request.user)

    context = {
        "form": form,
    }
    return render(request, "catalog/add_item.html", context)


@login_required
def list_detail(request, slug):
    list_obj = get_object_or_404(List, slug=slug, owner=request.user)
    return render(request, "catalog/list_detail.html", {"list": list_obj})


@require_GET
@login_required
def external_search(request):
    """
    HTMX endpoint to search external APIs by item_type & query.
    Returns HTML snippet with search results.
    """
    # match the field names used in add_item.html
    item_type = request.GET.get("search_item_type")
    query = request.GET.get("search_query", "").strip()

    if not item_type or not query:
        html = render_to_string(
            "catalog/partials/search_results.html",
            {"results": [], "error": "Please choose a category and type something."},
            request=request,
        )
        return HttpResponseBadRequest(html)

    if item_type == "movie":
        results = tmdb.search_movies(query)
    elif item_type == "book":
        results = openlibrary.search_books(query)
    else:
        results = []

    html = render_to_string(
        "catalog/partials/search_results.html",
        {"results": results, "error": None, "item_type": item_type},
        request=request,
    )
    return HttpResponse(html)


@require_GET
@login_required
def prefill_from_external(request):
    """
    HTMX endpoint to prefill item fields from a chosen external result.
    Expects ?source=...&external_id=...&title=...&url=...&thumbnail=...
    For now we'll trust the client-provided data from the search results.
    """
    source = request.GET.get("source")
    title = request.GET.get("title", "")
    item_type = request.GET.get("item_type", "")
    url = request.GET.get("url", "")
    thumbnail_url = request.GET.get("thumbnail_url", "")

    if not title or not item_type:
        return HttpResponseBadRequest("Missing data")

    context = {
        "title": title,
        "item_type": item_type,
        "url": url,
        "thumbnail_url": thumbnail_url,
    }
    html = render_to_string(
        "catalog/partials/item_fields_prefilled.html",
        context,
        request=request,
    )
    return HttpResponse(html)
