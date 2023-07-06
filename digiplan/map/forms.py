from itertools import count  # noqa: D100

from django.forms import BooleanField, Form, IntegerField, TextInput, renderers
from django.utils.safestring import mark_safe
from django_mapengine import legend

from . import charts
from .widgets import SwitchWidget


class TemplateForm(Form):  # noqa: D101
    template_name = None

    def __str__(self) -> str:  # noqa: D105
        if self.template_name:
            renderer = renderers.get_default_renderer()
            return mark_safe(renderer.render(self.template_name, {"form": self}))  # noqa: S308
        return super().__str__()


class StaticLayerForm(TemplateForm):  # noqa: D101
    template_name = "forms/layer.html"
    switch = BooleanField(
        label=False,
        widget=SwitchWidget(
            attrs={
                "switch_class": "form-check form-switch",
                "switch_input_class": "form-check-input",
            },
        ),
    )
    counter = count()

    def __init__(self, layer: legend.LegendLayer, *args, **kwargs) -> None:  # noqa: ANN002, D107
        super().__init__(*args, **kwargs)
        self.layer = layer


class PanelForm(TemplateForm):  # noqa: D101
    def __init__(self, parameters, additional_parameters=None, **kwargs) -> None:  # noqa: D107, ANN001
        super().__init__(**kwargs)
        self.fields = {item["name"]: item["field"] for item in self.generate_fields(parameters, additional_parameters)}

    @staticmethod
    def generate_fields(parameters, additional_parameters=None):  # noqa: ANN001, ANN205, D102
        if additional_parameters is not None:
            charts.merge_dicts(parameters, additional_parameters)
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
            elif item["type"] == "switch":
                attrs = {
                    "class": item["class"],
                }
                field = BooleanField(
                    label=item["label"],
                    widget=SwitchWidget(attrs=attrs),
                    help_text=item["tooltip"],
                    required=False,
                )
                yield {"name": name, "field": field}
            else:
                raise ValueError(f"Unknown parameter type '{item['type']}'")


class EnergyPanelForm(PanelForm):  # noqa: D101
    template_name = "forms/panel_energy.html"


class HeatPanelForm(PanelForm):  # noqa: D101
    template_name = "forms/panel_heat.html"


class TrafficPanelForm(PanelForm):  # noqa: D101
    template_name = "forms/panel_traffic.html"
