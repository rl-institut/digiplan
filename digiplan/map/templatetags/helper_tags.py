from django import template

register = template.Library()


@register.filter
def dict_lookup_filter(dictionary, key):
    return dictionary.get(key, "")
