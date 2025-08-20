from html.parser import HTMLParser

from django import template
from django.utils.html import format_html

register = template.Library()


class LazyLoadingHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            attrs_dict = dict(attrs)
            attrs_dict.setdefault("loading", "lazy")
            attrs_dict.setdefault("decoding", "async")
            attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs_dict.items())
            self.result.append(f"<{tag} {attrs_str}>")
        else:
            attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs)
            self.result.append(f"<{tag}{' ' + attrs_str if attrs_str else ''}>")

    def handle_endtag(self, tag):
        self.result.append(f"</{tag}>")

    def handle_data(self, data):
        self.result.append(data)

    def handle_startendtag(self, tag, attrs):
        # For self-closing tags like <img />
        if tag.lower() == "img":
            attrs_dict = dict(attrs)
            attrs_dict.setdefault("loading", "lazy")
            attrs_dict.setdefault("decoding", "async")
            attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs_dict.items())
            self.result.append(f"<{tag} {attrs_str} />")
        else:
            attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs)
            self.result.append(f"<{tag}{' ' + attrs_str if attrs_str else ''} />")


@register.filter
def add_lazy_loading(html):
    parser = LazyLoadingHTMLParser()
    parser.feed(html)
    return format_html("".join(parser.result))
