import json
import pathlib

from django.http import HttpRequest
from django.template import Template
from django.template.context import make_context


def get_translated_json_from_file(json_filename: str, request: HttpRequest = None):
    """
    Renders JSON using translations

    Parameters
    ----------
    json_filename: str
        Path to JSON file
    request: HttpRequest
        Used to create RequestContext and set language from request

    Returns
    -------
    dict
        translated JSON file as dictionary
    """
    with pathlib.Path(json_filename).open("r", encoding="utf-8") as json_file:
        # add {% load i18n %} to file to make django detect translatable strings
        t = Template("{% load i18n %}" + json_file.read())
        c = make_context({}, request)
        translated_json_string = t.render(c)
        return json.loads(translated_json_string)
