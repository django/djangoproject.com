"""
This allows usage of sorl-thumbnail in templates
by {% load sorl_thumbnail %} instead of traditional
{% load thumbnail %}. It's specifically useful in projects
that do make use of multiple thumbnailer libraries (for
instance `easy-thumbnails` alongside `sorl-thumbnail`).
"""
from .thumbnail import *  # noqa
