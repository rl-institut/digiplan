import json
import pathlib

from django.template import Context, Template


def get_translated_json_from_file(json_filename):
    with pathlib.Path(json_filename).open("r", encoding="utf-8") as json_file:
        # add {% load i18n %} to file to make django detect translatable strings
        t = Template("{% load i18n %}" + json_file.read())
        c = Context({})
        translated_json_string = t.render(c)
        return json.loads(translated_json_string)
