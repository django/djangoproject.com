from pathlib import Path

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _, gettext_lazy
from sorl.thumbnail import get_thumbnail

from .models import ContentFormat, Entry, Event, ImageUpload


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("headline", "pub_date", "is_active", "is_published", "author")
    list_filter = ("is_active",)
    exclude = ("summary_html", "body_html")
    prepopulated_fields = {"slug": ("headline",)}
    raw_id_fields = ["social_media_card"]

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "content_format":
            formfield.help_text = _("Psst, we have markdown now 🤫")
        if db_field.name == "body":
            formfield.widget.attrs.update(
                {
                    "rows": 60,
                    "style": "font-family: monospace; width: 810px;",
                }
            )
            formfield.help_text = format_html(
                _(
                    "Want to include an image? "
                    '<a href="{}" target="_blank">Use the image upload helper!</a>'
                ),
                reverse("admin:blog_imageupload_changelist"),
            )
        return formfield


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "headline",
        "external_url",
        "date",
        "location",
        "pub_date",
        "is_active",
        "is_published",
    )
    list_filter = ("is_active",)


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "thumbnail",
        "uploaded_on",
        "link",
        "copy_buttons",
    )

    class Media:
        js = ["js/admin_blog_imageupload.js"]

    @admin.display(description=gettext_lazy("Thumbnail"))
    def thumbnail(self, obj):
        thumbnail = get_thumbnail(obj.image, "150x150", quality=90)
        return format_html('<img src="{}" alt="{}">', thumbnail.url, obj.alt_text)

    @admin.display(description=gettext_lazy("Link"))
    def link(self, obj):
        url = obj.image.url
        filename = Path(obj.image.name).name
        return format_html('<a href="{}">{}</a>', url, filename)

    def _get_copy_button(self, obj, contentformat):
        source = contentformat.img(obj.image.url, obj.alt_text)
        return format_html(
            '<button type="button" data-clipboard-content="{}">{}</button>',
            source,
            contentformat.label,
        )

    @admin.display(description=gettext_lazy("Copy buttons"))
    def copy_buttons(self, obj):
        buttons = ((self._get_copy_button(obj, cf),) for cf in ContentFormat)
        return format_html(
            "<ul>{}</ul>",
            format_html_join("\n", "<li>{}</li>", buttons),
        )

    def save_model(self, request, obj, form, change):
        obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "image":
            formfield.widget.attrs.update({"accept": "image/*"})
        return formfield
