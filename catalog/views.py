from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import models
from .forms import ItemCreateForm
from .models import Item, List, ListItem


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
