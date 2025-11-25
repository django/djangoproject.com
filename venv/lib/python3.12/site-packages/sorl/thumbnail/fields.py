from django import forms
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from sorl.thumbnail import default

__all__ = ('ImageField', 'ImageFormField')


class ImageField(models.ImageField):
    def delete_file(self, instance, sender, **kwargs):
        """
        Adds deletion of thumbnails and key value store references to the
        parent class implementation. Only called in Django < 1.2.5
        """
        file_ = getattr(instance, self.attname)

        # If no other object of this type references the file, and it's not the
        # default value for future objects, delete it from the backend.
        query = Q(**{self.name: file_.name}) & ~Q(pk=instance.pk)
        qs = sender._default_manager.filter(query)

        if (file_ and file_.name != self.default and not qs):
            default.backend.delete(file_)
        elif file_:
            # Otherwise, just close the file, so it doesn't tie up resources.
            file_.close()

    def formfield(self, **kwargs):
        defaults = {'form_class': ImageFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def save_form_data(self, instance, data):
        if data is not None:
            setattr(instance, self.name, data or '')


class ImageFormField(forms.FileField):
    default_error_messages = {
        'invalid_image': _("Upload a valid image. The file you uploaded was "
                           "either not an image or a corrupted image."),
    }

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF,
        JPG, PNG, possibly others -- whatever the engine supports).
        """
        f = super().to_python(data)
        if f is None:
            return None

        # We need to get a file raw data to validate it.
        if hasattr(data, 'temporary_file_path'):
            with open(data.temporary_file_path(), 'rb') as fp:
                raw_data = fp.read()
        elif hasattr(data, 'read'):
            raw_data = data.read()
        else:
            raw_data = data['content']

        if not default.engine.is_valid_image(raw_data):
            raise forms.ValidationError(self.default_error_messages['invalid_image'])
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)

        return f
