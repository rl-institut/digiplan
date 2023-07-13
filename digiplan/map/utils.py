"""Module for smaller helper functions."""

import json
import pathlib

from django.http import HttpRequest
from django.template import Template
from django.template.context import make_context


def get_translated_json_from_file(json_filename: str, request: HttpRequest = None) -> dict:
    """
    Render JSON using translations.

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


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merge two dictionaries.

    Parameters
    ----------
    dict1: dict
        Containing the first chart structure. Objects will be first.
    dict2: dict
        Containing the second chart structure. Objects will be last and
        if they have the same name as ones from dict1 they overwrite the ones in first.

    Returns
    -------
    dict
        First chart modified and appended by second chart.
    """
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_dicts(dict1[key], dict2[key])
        elif key in dict1 and isinstance(dict1[key], list) and isinstance(dict2[key], list):
            dict1[key].extend(dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1
