from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Item(models.Model):
    class ItemType(models.TextChoices):
        MOVIE = "movie", "Movie / TV / Anime"
        BOOK = "book", "Book"
        MUSIC = "music", "Music"
        GAME = "game", "Game"
        VIDEO = "video", "YouTube / Video"
        PODCAST = "podcast", "Podcast"
        ARTICLE = "article", "Article / Blog"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255)
    item_type = models.CharField(
        max_length=20,
        choices=ItemType.choices,
        default=ItemType.OTHER,
    )
    url = models.URLField(blank=True)
    thumbnail_url = models.URLField(
        blank=True,
        help_text="External thumbnail URL (e.g. from an API or the original site).",
    )
    # later: optional ImageField if we want uploads
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class List(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lists",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while List.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ListItem(models.Model):
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="list_items",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="in_lists",
    )
    position = models.PositiveIntegerField(default=0)
    note = models.CharField(max_length=255, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "-added_at"]
        unique_together = ("list", "item")

    def __str__(self):
        return f"{self.item} in {self.list}"
