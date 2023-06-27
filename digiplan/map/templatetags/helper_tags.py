"""Template tags for django templating."""

from django import template

register = template.Library()


@register.filter
def dict_lookup_filter(dictionary: dict, key: str):  # noqa: ANN201
    """Lookup key in dictionary."""
    return dictionary.get(key, "")
