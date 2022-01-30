from typing import Any, List

from django import template


register = template.Library()


@register.filter  # type: ignore
def index(indexable: List[Any], i: int) -> Any:
    return indexable[i]
