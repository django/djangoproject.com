"""
View which can render and send email from a contact form.

"""

# SPDX-License-Identifier: BSD-3-Clause

from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import ContactForm


class ContactFormView(FormView):
    """
    The base view class from which most custom contact-form views should inherit. If
    you don't need any custom functionality, and are content with the default
    :class:`~django_contact_form.forms.ContactForm` class, you can also use it as-is
    (and the provided URLConf, ``django_contact_form.urls``, does exactly this).

    This is a subclass of Django's :class:`~django.views.generic.edit.FormView`, so
    refer to the Django documentation for a list of attributes/methods which can be
    overridden to customize behavior.

    One non-standard attribute is defined here:

    .. attribute:: recipient_list

       The list of email addresses to send mail to. If not specified, defaults to the
       :attr:`~django_contact_form.forms.ContactForm.recipient_list` of the form.

    Additionally, the following standard (from
    :class:`~django.views.generic.edit.FormView`) attributes are commonly useful to
    override (all attributes below can also be passed to
    :meth:`~django.views.generic.base.View.as_view()` in the URLconf, permitting
    customization without the need to write a full custom subclass of
    :class:`ContactFormView`). Each of these can be supplied as an attribute, or as a
    method with the name prefixed with ``get_`` (for example, a ``get_form_class()``
    method instead of a ``form_class`` attribute):

    .. attribute:: form_class

       The form class to use. By default, will be
       :class:`~django_contact_form.forms.ContactForm`.

    .. attribute:: template_name

       A :class:`str`, the template to use when rendering the form. By default, will be
       ``django_contact_form/contact_form.html``.

    .. attribute:: success_url

       The URL to redirect to after successful form submission. Can be a hard-coded
       string, the string resulting from calling Django's :func:`~django.urls.reverse`
       helper, or the lazy object produced by Django's :func:`~django.urls.reverse_lazy`
       helper. Default value is the result of calling :func:`~django.urls.reverse_lazy`
       with the URL name ``"django_contact_form_sent"``.

    You can also override the following method for full customization of the form
    instance construction:

    .. automethod:: get_form_kwargs

    """

    form_class = ContactForm
    recipient_list = None
    success_url = reverse_lazy("django_contact_form_sent")
    template_name = "django_contact_form/contact_form.html"

    def form_valid(self, form):
        """
        Handle a valid form by sending the email.

        """
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self) -> dict:
        """
        Return additional keyword arguments (as a dictionary) to pass to the form class
        on initialization.

        By default, this will return a dictionary containing the current
        :class:`~django.http.HttpRequest` (as the key ``request``) and, if
        :attr:`~ContactFormView.recipient_list` was defined, its value (as the key
        ``recipient_list``).

        .. warning:: **Request is a required argument**

           If you override :meth:`get_form_kwargs`, you **must** ensure that, at the very
           least, the keyword argument ``request`` is still provided, or
           :class:`~django_contact_form.forms.ContactForm` initialization will raise
           :exc:`TypeError`. The easiest approach is to use :class:`super` to call the
           base implementation in :class:`ContactFormView`, and modify the dictionary it
           returns.

        """
        # ContactForm instances require instantiation with an
        # HttpRequest.
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})

        # We may also have been given a recipient list when
        # instantiated.
        if self.recipient_list is not None:
            kwargs.update({"recipient_list": self.recipient_list})
        return kwargs
