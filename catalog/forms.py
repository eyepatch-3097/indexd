from django import forms
from .models import Item, List


class ItemCreateForm(forms.ModelForm):
    list = forms.ModelChoiceField(
        queryset=List.objects.none(),
        required=False,
        label="Add to existing list",
        help_text="Optionally choose a list to add this item to.",
    )
    new_list_title = forms.CharField(
        max_length=255,
        required=False,
        label="Or create a new list",
        help_text="If provided, a new list will be created with this title.",
    )
    new_list_is_public = forms.BooleanField(
        required=False,
        label="New list is public?",
        initial=True,
    )

    class Meta:
        model = Item
        fields = ["title", "item_type", "url", "thumbnail_url"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Limit list choices to lists owned by this user
        if user is not None:
            self.fields["list"].queryset = List.objects.filter(owner=user)

        # Add some Bootstrap classes for nicer forms
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-control"
            else:
                field.widget.attrs["class"] = "form-check-input"
