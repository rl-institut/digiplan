from itertools import count

from django.db.models import Max, Min
from django.forms import (
    BooleanField,
    CharField,
    Form,
    IntegerField,
    MultipleChoiceField,
    MultiValueField,
    TextInput,
    renderers,
)
from django.utils.safestring import mark_safe
from django_select2.forms import Select2MultipleWidget

from . import models
from .widgets import BoxWidget, SwitchWidget, TitleWidget


class TemplateForm(Form):
    template_name = None

    def __str__(self):
        if self.template_name:
            renderer = renderers.get_default_renderer()
            return mark_safe(renderer.render(self.template_name, {"form": self}))  # noqa: S703, S308
        return super().__str__()


class StaticLayerForm(TemplateForm):
    template_name = "forms/layer.html"
    switch = BooleanField(
        label=False,
        widget=SwitchWidget(
            attrs={
                "switch_class": "form-check form-switch",
                "switch_input_class": "form-check-input",
            }
        ),
    )
    counter = count()

    def __init__(self, layer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer = layer
        self.fields["switch"].widget.attrs["id"] = layer.source

        if hasattr(layer.model, "filters"):
            self.has_filters = True
            for filter_ in layer.model.filters:
                if filter_.type == models.LayerFilterType.Range:
                    filter_min = layer.model.vector_tiles.aggregate(Min(filter_.name))[f"{filter_.name}__min"]
                    filter_max = layer.model.vector_tiles.aggregate(Max(filter_.name))[f"{filter_.name}__max"]
                    self.fields[filter_.name] = MultiValueField(
                        label=getattr(layer.model, filter_.name).field.verbose_name,
                        fields=[IntegerField(), IntegerField()],
                        widget=TextInput(
                            attrs={
                                "class": "js-slider",
                                "data-type": "double",
                                "data-min": filter_min,
                                "data-max": filter_max,
                                "data-from": filter_min,
                                "data-to": filter_max,
                                "data-grid": True,
                            }
                        ),
                    )
                elif filter_.type == models.LayerFilterType.Dropdown:
                    filter_values = (
                        layer.model.vector_tiles.values_list(filter_.name, flat=True).order_by(filter_.name).distinct()
                    )
                    self.fields[filter_.name] = MultipleChoiceField(
                        choices=[(value, value) for value in filter_values],
                        widget=Select2MultipleWidget(attrs={"id": f"{filter_.name}_{next(self.counter)}"}),
                    )
                else:
                    raise ValueError(f"Unknown filter type '{filter_.type}'")


class PanelForm(TemplateForm):
    template_name = "forms/panel.html"
    sidepanels = {}

    def __init__(self, parameters):
        super().__init__()

        self.fields = {item["name"]: item["field"] for item in self.generate_fields(parameters)}

    def generate_fields(self, parameters):
        for name, item in parameters.items():
            if item["type"] == "slider":
                attrs = {
                    "class": item["class"],
                    "data-min": item["min"],
                    "data-max": item["max"],
                    "data-from": item["start"],
                    "data-grid": "true" if "grid" in item and item["grid"] else "false",
                    "data-has-sidepanel": "true" if "sidepanel" in item else "false",
                    "data-color": item["color"] if "color" in item else "",
                }
                if "to" in item:
                    attrs["data-to"] = item["to"]
                if "step" in item:
                    attrs["data-step"] = item["step"]

                field = IntegerField(label=item["label"], widget=TextInput(attrs=attrs), help_text=item["tooltip"])
                yield {"name": name, "field": field}

                if "sidepanel" in item:
                    self.sidepanels[name] = PanelForm(item["sidepanel"])
            elif item["type"] == "switch":
                attrs = {
                    "class": item["class"],
                }
                field = BooleanField(label=item["label"], widget=SwitchWidget(attrs=attrs), help_text=item["tooltip"])
                yield {"name": name, "field": field}
            elif item["type"] == "box":
                attrs = {
                    "class": item["class"],
                }
                field = CharField(
                    label=item["label"], widget=BoxWidget(attrs=attrs), help_text=item["tooltip"], initial=item["text"]
                )
                yield {"name": name, "field": field}
            elif item["type"] == "title":
                field = CharField(
                    label=item["label"], widget=TitleWidget(), help_text=item["tooltip"], initial=item["text"]
                )
                yield {"name": name, "field": field}
            else:
                raise ValueError(f"Unknown parameter type '{item['type']}'")
