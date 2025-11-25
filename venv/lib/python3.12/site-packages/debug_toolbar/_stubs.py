from __future__ import annotations

from typing import Any, NamedTuple, Optional

from django import template as dj_template


class InspectStack(NamedTuple):
    frame: Any
    filename: str
    lineno: int
    function: str
    code_context: str
    index: int


TidyStackTrace = list[tuple[str, int, str, str, Optional[Any]]]


class RenderContext(dj_template.context.RenderContext):
    template: dj_template.Template


class RequestContext(dj_template.RequestContext):
    template: dj_template.Template
    render_context: RenderContext
