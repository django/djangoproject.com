import re

from django import forms
from docutils.core import publish_parts

from blog.models import BLOG_DOCUTILS_SETTINGS, Entry

RE_RST = {
    'warning': r'System Message: WARNING/\d+ \([^\)]+(line \d+)\)</p>\s<p>([^<]+)</p>',
    'error': r'System Message: ERROR/\d+ \([^\)]+(line \d+)\)</p>\s<p>([^<]+)</p>',
}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = (
            'headline',
            'slug',
            'is_active',
            'pub_date',
            'content_format',
            'summary',
            'body',
            'author',
        )

    def add_rst_error(self, field, level, position, message):
        return self.add_error(
            field,
            'reStructuredText {} at {}: {}'.format(level, position, message)
        )

    def check_for_rst_error(self, field, level, html):
        if re.search(RE_RST[level], html):
            for match in re.findall(RE_RST[level], html):
                self.add_rst_error(field, level, *match)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('content_format') == 'reST':
            summary_html = publish_parts(
                source=cleaned_data.get('summary'),
                writer_name='html',
                settings_overrides=BLOG_DOCUTILS_SETTINGS
            )['fragment']

            self.check_for_rst_error('summary', 'error', summary_html)
            self.check_for_rst_error('summary', 'warning', summary_html)

            body_html = publish_parts(
                source=cleaned_data.get('body'),
                writer_name='html',
                settings_overrides=BLOG_DOCUTILS_SETTINGS
            )['fragment']

            self.check_for_rst_error('body', 'error', body_html)
            self.check_for_rst_error('body', 'warning', body_html)
