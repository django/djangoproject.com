from django import template

from django_countries.fields import Country, countries

register = template.Library()


@register.simple_tag
def get_country(code):
    return Country(code=code)


@register.simple_tag
def get_countries():
    return list(countries)
